"""Joblib storage backend for HDFS."""

import os.path
import hdfs3
from joblib._store_backends import StoreBackendBase, StoreManagerMixin


class HDFSStoreBackend(StoreBackendBase, StoreManagerMixin):
    """A StoreBackend for Hadoop storage file system (HDFS)."""

    def __init__(self):
        self.storage = None
        self.cachedir = None
        self.compress = None
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

    def configure(self, location, host=None, port=None, user=None,
                  ticket_cache=None, token=None, pars=None, connect=True,
                  **kwargs):
        """Configure the store backend."""
        self.storage = hdfs3.HDFileSystem(host=host, port=port, user=user,
                                          ticket_cache=ticket_cache,
                                          token=token, pars=pars,
                                          connect=connect)
        if location.startswith('/'):
            location = location[1:]
        self.cachedir = os.path.join(location, 'joblib')
        self.storage.mkdir(self.cachedir)

        # attach required methods using monkey patching trick.
        self.open_object = self.storage.open
        self.object_exists = self.storage.exists

        # computation results can be stored compressed for faster I/O
        self.compress = (False if 'compress' not in kwargs
                         else kwargs['compress'])

        self.mmap_mode = None

    def _mkdirp(self, directory):
        """Create recursively a directory on the HDFS file system."""
        current_path = ""
        for sub_dir in directory.split('/'):
            current_path = os.path.join(current_path, sub_dir)
            self.storage.mkdir(current_path)
