"""Helpers for easy registration of joblib store backends."""

from joblib import register_store_backend
from .s3_backend import S3StoreBackend


def register_s3_store_backend():
    """Register a S3 store backend for joblib memory caching."""
    register_store_backend('s3://', S3StoreBackend)
