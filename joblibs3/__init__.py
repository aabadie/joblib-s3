"""Joblibs3 module"""

import warnings

from .backends import register_s3fs_store_backend

__all__ = ['register_s3fs_store_backend']

__version__ = "0.1.0-dev"
