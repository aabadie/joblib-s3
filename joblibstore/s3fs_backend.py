"""Joblib storage backend for S3."""

import os.path
import s3fs
import warnings
from joblib._compat import _basestring
from joblib._store_backends import StoreBackendBase, StoreManagerMixin


class S3FSStoreBackend(StoreBackendBase, StoreManagerMixin):
    """A StoreBackend for S3 cloud storage file system."""

    def clear_location(self, location):
        """Check if object exists in store."""
        self.fs.rm(location, recursive=True)

    def create_location(self, location):
        """Create object location on store."""
        self._mkdirp(location)

    def get_cache_items(self):
        """Return the whole list of items available in cache."""
        return []

    def configure(self, location, bucket=None,
                  anon=False, key=None, secret=None, token=None, use_ssl=True,
                  **kwargs):
        """Configure the store backend."""
        self.fs = s3fs.S3FileSystem(anon=anon, key=key, secret=secret,
                                    token=token, use_ssl=True)

        if isinstance(location, _basestring):
            if bucket is None:
                raise ValueError("No valid S3 bucket set")

            # Ensure the given bucket exists.
            root_bucket = os.path.join("s3://", bucket)
            if not self.fs.exists(root_bucket):
                self.fs.mkdir(root_bucket)

            if location.startswith('/'):
                location.replace('/', '')
            self.cachedir = os.path.join(root_bucket, location, 'joblib')
            if not self.fs.exists(self.cachedir):
                self.fs.mkdir(self.cachedir)
        elif isinstance(location, S3FSStoreBackend):
            self.cachedir = location.cachedir

        # attach required methods using monkey patching trick.
        self.open_object = self.fs.open
        self.object_exists = self.fs.exists

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
        """Create recursively a directory on the S3 store."""
        # remove root cachedir from input directory to create as it should
        # have already been created in the configure function.
        if directory.startswith(self.cachedir):
            directory = directory.replace(self.cachedir + '/', "")

        current_path = self.cachedir
        for sub_dir in directory.split('/'):
            current_path = os.path.join(current_path, sub_dir)
            self.fs.mkdir(current_path)
