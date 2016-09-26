"""Helpers for easy registration of joblib store backends."""

from joblib import register_store_backend
from .s3_backend import S3StoreBackend

try:
    from .hdfs_backend import HDFSStoreBackend
except ImportError:
    HDFSStoreBackend = None


def register_s3_store_backend():
    """Register a S3 store backend for joblib memory caching."""
    register_store_backend('s3://', S3StoreBackend)


if HDFSStoreBackend is not None:
    def register_hdfs_store_backend():
        """Register a HDFS store backend for joblib memory caching."""
        register_store_backend('hdfs://', HDFSStoreBackend)
