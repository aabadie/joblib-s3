"""Joblib storage backend for S3"""

import time
import os.path
import json
import s3fs
import warnings
from joblib._compat import _basestring
from joblib.logger import format_time
from joblib import numpy_pickle
from joblib._store_backends import StoreBackendBase


class S3StoreBackend(StoreBackendBase):
    """A StoreBackend for S3 cloud storage file system."""

    def load_result(self, func_id, args_id, **kwargs):
        """Load computation output from store."""
        full_path = os.path.join(self.cachedir, func_id, args_id)
        filename = os.path.join(full_path, 'output.pkl')
        if not self.fs.exists(filename):
            raise KeyError("Non-existing cache value (may have been "
                           "cleared).\nFile %s does not exist" % filename)

        if 'verbose' in kwargs and kwargs['verbose'] > 1:
            verbose = kwargs['verbose']
            signature = ""
            try:
                if 'metadata' in kwargs and kwargs['metadata'] is not None:
                    metadata = kwargs['metadata']
                    args = ", ".join(['%s=%s' % (name, value)
                                      for name, value
                                      in metadata['input_args'].items()])
                    signature = "%s(%s)" % (os.path.basename(func_id), args)
                else:
                    signature = os.path.basename(func_id)
            except KeyError:
                pass

            if 'timestamp' in kwargs and kwargs['timestamp'] is not None:
                ts_string = ("{0: <16}"
                             .format(format_time(time.time() -
                                                 kwargs['timestamp'])))
            else:
                ts_string = ""

            if verbose < 10:
                print('[Memory]{0}: Loading {1}...'.format(ts_string,
                                                           str(signature)))
            else:
                print('[Memory]{0}: '
                      'Loading {1} from {2}'.format(ts_string,
                                                    str(signature),
                                                    full_path))

        mmap_mode = None if 'mmap_mode' not in kwargs else kwargs['mmap_mode']
        with self.fs.open(filename, 'rb') as f:
            result = numpy_pickle.load(f, mmap_mode=mmap_mode)
        return result

    def dump_result(self, func_id, args_id, result, compress=False, **kwargs):
        """Dump computation output in store."""
        try:
            result_dir = os.path.join(self.cachedir, func_id, args_id)
            if not os.path.exists(result_dir):
                self._mkdirp(os.path.join(func_id, args_id))
            filename = os.path.join(result_dir, 'output.pkl')

            if 'verbose' in kwargs and kwargs['verbose'] > 10:
                print('Persisting in %s' % result_dir)

            with self.fs.open(filename, 'wb') as f:
                numpy_pickle.dump(result, f, compress=compress)
        except:
            " Race condition in the creation of the directory "

    def clear_result(self, func_id, args_id, **kwargs):
        """Clear computation output in store."""
        result_dir = os.path.join(self.cachedir, func_id, args_id)
        if os.path.exists(result_dir):
            self.fs.rm(result_dir, recursive=True)

    def contains_result(self, func_id, args_id, **kwargs):
        """Check computation output is available in store."""
        result_dir = os.path.join(self.cachedir, func_id, args_id)
        filename = os.path.join(result_dir, 'output.pkl')

        return self.fs.exists(filename)

    def get_result_info(self, func_id, args_id):
        """Return information about cached result."""
        return {'location': os.path.join(self.cachedir, func_id, args_id)}

    def get_metadata(self, func_id, args_id):
        """Return actual metadata of a computation."""
        try:
            directory = os.path.join(self.cachedir, func_id, args_id)
            filename = os.path.join(directory, 'metadata.json')
            with self.fs.open(filename, 'rb') as f:
                return json.load(f)
        except:
            return {}

    def store_metadata(self, func_id, args_id, metadata):
        """Store metadata of a computation."""
        try:
            directory = os.path.join(self.cachedir, func_id, args_id)
            self._mkdirp(os.path.join(func_id, args_id))
            with open(os.path.join(directory, 'metadata.json'), 'w') as f:
                json.dump(metadata, f)
        except:
            pass

    def contains_cached_func(self, func_id):
        """Check cached function is available in store."""
        func_dir = os.path.join(self.cachedir, func_id)
        return self.fs.exists(func_dir)

    def clear_cached_func(self, func_id):
        """Clear all references to a function in the store."""
        func_dir = os.path.join(self.cachedir, func_id)
        if self.fs.exists(func_dir):
            self.fs.rm(func_dir, recursive=True)

    def store_cached_func_code(self, func_id, func_code=None):
        """Store the code of the cached function."""
        func_dir = os.path.join(self.cachedir, func_id)
        if not self.fs.exists(func_dir):
            self._mkdirp(func_id)

        if func_code is not None:
            filename = os.path.join(func_dir, "func_code.py")
            with self.fs.open(filename, 'wb') as f:
                f.write(func_code.encode('utf-8'))

    def get_cached_func_code(self, func_id):
        """Return the code of the cached function if it exists."""
        filename = os.path.join(self.cachedir, func_id, "func_code.py")
        try:
            with self.fs.open(filename, 'rb') as f:
                return f.read().decode('utf-8')
        except:
            raise

    def get_cached_func_info(self, func_id):
        """Return information related to the cached function if it exists."""
        return {'location': os.path.join(self.cachedir, func_id)}

    def clear(self):
        """Clear the whole store content."""
        self.fs.rm(self.cachedir, recursive=True)

    def configure(self, location,
                  anon=False, key=None, secret=None, token=None, use_ssl=True,
                  **kwargs):
        """Configure the store backend."""
        self.fs = s3fs.S3FileSystem(anon=anon, key=key, secret=secret,
                                    token=token, use_ssl=True)

        if isinstance(location, _basestring):
            self.cachedir = os.path.join(location, 'joblib')
            self.fs.mkdir(location)
            self.fs.mkdir(self.cachedir)
        elif isinstance(location, S3StoreBackend):
            self.cachedir = location.cachedir

        # computation results can be stored compressed for faster I/O
        self.compress = (False if 'compress' not in kwargs
                         else kwargs['compress'])

        # FileSystemStoreBackend can be used with mmap_mode options under
        # certain conditions.
        if 'mmap_mode' in kwargs and kwargs['mmap_mode'] is not None:
            warnings.warn('Memory mapping cannot be used on S3 store. '
                          'This option will be ignored.',
                          stacklevel=2)
        self.mmap_mode = None

    def _mkdirp(self, directory):
        """Recursively create a directory on the S3 store."""
        current_path = self.cachedir
        for sub_dir in directory.split('/'):
            current_path = os.path.join(current_path, sub_dir)
            self.fs.mkdir(current_path)
