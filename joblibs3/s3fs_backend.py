"""Joblib storage backend for S3."""

import os.path
import s3fs
from joblib._store_backends import StoreBackendBase, StoreBackendMixin


class S3FSStoreBackend(StoreBackendBase, StoreBackendMixin):
    """A StoreBackend for S3 cloud storage file system."""

    def _open_item(self, fd, mode):
        return self.storage.open(fd, mode)

    def _item_exists(self, path):
        return self.storage.exists(path)

    def _move_item(self, src, dst):
        self.storage.mv(src, dst)

    def clear_location(self, location):
        """Check if object exists in store."""
        self.storage.rm(location, recursive=True)

    def create_location(self, location):
        """Create object location on store."""
        self._mkdirp(location)

    def get_items(self):
        """Return the whole list of items available in cache."""
        return []

    def _prepare_options(self, store_options):
        if 'anon' not in store_options:
            store_options['anon'] = False

        if 'key' not in store_options:
            store_options['key'] = None

        if 'secret' not in store_options:
            store_options['secret'] = None

        if 'token' not in store_options:
            store_options['token'] = None

        if 'use_ssl' not in store_options:
            store_options['use_ssl'] = True

        return store_options

    def configure(self, location, verbose=0,
                  backend_options=dict(compress=False, bucket=None,
                                       anon=False, key=None, secret=None,
                                       token=None, use_ssl=True)):
        """Configure the store backend."""
        compress = backend_options['compress']
        store_options = self._prepare_options(backend_options)

        self.storage = s3fs.S3FileSystem(anon=backend_options['anon'],
                                         key=backend_options['key'],
                                         secret=backend_options['secret'],
                                         token=backend_options['token'],
                                         use_ssl=backend_options['use_ssl'])

        if 'bucket' not in backend_options:
            raise ValueError("No valid S3 bucket set")

        bucket = backend_options['bucket']

        # Ensure the given bucket exists.
        root_bucket = os.path.join("s3://", bucket)
        if not self.storage.exists(root_bucket):
            self.storage.mkdir(root_bucket)

        if location.startswith('/'):
            location.replace('/', '')
        self.location = os.path.join(root_bucket, location)
        if not self.storage.exists(self.location):
            self.storage.mkdir(self.location)

        # computation results can be stored compressed for faster I/O
        self.compress = compress

        # Memory map mode is not supported
        self.mmap_mode = None

    def _mkdirp(self, directory):
        """Create recursively a directory on the S3 store."""
        # remove root cachedir from input directory to create as it should
        # have already been created in the configure function.
        if directory.startswith(self.location):
            directory = directory.replace(self.location + '/', "")

        current_path = self.location
        for sub_dir in directory.split('/'):
            current_path = os.path.join(current_path, sub_dir)
            self.storage.mkdir(current_path)
