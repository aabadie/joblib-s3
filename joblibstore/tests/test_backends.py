"""Test the backend registration functions"""

from joblibstore import (register_hdfs_store_backend,
                         register_s3fs_store_backend)
from joblibstore.hdfs_backend import HDFSStoreBackend
from joblibstore.s3fs_backend import S3FSStoreBackend
from joblib.memory import _STORE_BACKENDS


def test_hdfs_store_backend_registration():
    """Smoke test for hdfs backend registration."""
    register_hdfs_store_backend()
    assert "hdfs" in _STORE_BACKENDS
    assert _STORE_BACKENDS["hdfs"] == HDFSStoreBackend


def test_s3fs_store_backend_registration():
    """Smoke test for hdfs backend registration."""
    register_s3fs_store_backend()
    assert "s3fs" in _STORE_BACKENDS
    assert _STORE_BACKENDS["s3fs"] == S3FSStoreBackend
