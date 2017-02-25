"""Joblib storage backend for S3."""

import os.path
import s3fs
from joblib._store_backends import StoreBackendBase, StoreManagerMixin


class S3FSStoreBackend(StoreBackendBase, StoreManagerMixin):
    """A StoreBackend for S3 cloud storage file system."""

    def __init__(self):
        self.storage = None
        self.cachedir = None
        self.compress = False
        self.mmap_mode = None

    def clear_location(self, location):
        """Check if object exists in store."""
        self.storage.rm(location, recursive=True)

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
        self.storage = s3fs.S3FileSystem(anon=anon, key=key, secret=secret,
                                         token=token, use_ssl=use_ssl)

        if bucket is None:
            raise ValueError("No valid S3 bucket set")

        # Ensure the given bucket exists.
        root_bucket = os.path.join("s3://", bucket)
        if not self.storage.exists(root_bucket):
            self.storage.mkdir(root_bucket)

        if location.startswith('/'):
            location.replace('/', '')
        self.cachedir = os.path.join(root_bucket, location, 'joblib')
        if not self.storage.exists(self.cachedir):
            self.storage.mkdir(self.cachedir)

        # attach required methods using monkey patching trick.
        self.open_object = self.storage.open
        self.object_exists = self.storage.exists

        # computation results can be stored compressed for faster I/O
        self.compress = (False if 'compress' not in kwargs
                         else kwargs['compress'])

        # Memory map mode is not supported
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
            self.storage.mkdir(current_path)
