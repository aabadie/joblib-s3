"""Helpers for easy registration of joblib store backends."""

from joblib import register_store_backend
from .s3fs_backend import S3FSStoreBackend


def register_s3fs_store_backend():
    """Register the S3 store backend for joblib memory caching."""
    register_store_backend('s3', S3FSStoreBackend)
