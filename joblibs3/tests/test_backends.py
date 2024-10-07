"""Test the backend registration functions"""

from joblib.memory import _STORE_BACKENDS

from joblibs3 import register_s3fs_store_backend
from joblibs3.s3fs_backend import S3FSStoreBackend


def test_s3fs_store_backend_registration():
    """Smoke test for S3 backend registration."""
    register_s3fs_store_backend()
    assert "s3" in _STORE_BACKENDS
    assert _STORE_BACKENDS["s3"] == S3FSStoreBackend
