"""Joblibstore module"""

import warnings

from .backends import register_s3fs_store_backend
try:
    from .backends import register_hdfs_store_backend
except ImportError:
    register_hdfs_store_backend = None
    warnings.warn("libhdfs3 was not found on the system, cannot register"
                  "'register_hdfs_store_backend function.'")

__all__ = ['register_s3fs_store_backend']

__version__ = "0.1.0-dev"

if register_hdfs_store_backend is not None:
    __all__.append('register_hdfs_store_backend')
