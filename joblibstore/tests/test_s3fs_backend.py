"""Test S3FS store backend."""

import os.path
import array
from unittest.mock import patch

import pytest
import numpy as np
from s3fs import S3FileSystem
from joblib import Memory
from joblib.disk import mkdirp, rm_subdirs
from joblibstore import register_s3fs_store_backend


@pytest.fixture()
def s3fs_mkdirp(monkeypatch):
    """mkdirp fixture"""
    monkeypatch.setattr(S3FileSystem, "mkdir", mkdirp)


@pytest.fixture()
def s3fs_exists(monkeypatch):
    """exists fixture"""
    monkeypatch.setattr(S3FileSystem, "exists", os.path.exists)


@pytest.fixture()
def s3fs_open(monkeypatch):
    """open fixture"""
    monkeypatch.setattr(S3FileSystem, "open", open)


@pytest.fixture()
def s3fs_rm(monkeypatch):
    """open fixture"""
    monkeypatch.setattr(S3FileSystem, "rm", rm_subdirs)


@pytest.mark.usefixtures("s3fs_open", "s3fs_mkdirp", "s3fs_exists")
@patch("s3fs.S3FileSystem")
@pytest.mark.parametrize("compress", [True, False])
@pytest.mark.parametrize("arg", ["test",
                                 b"test",
                                 array.array('d', [1, 2, 3, 4]),
                                 (1, 2, 3),
                                 {"1": 1, "2": 2},
                                 [1, 2, 3, 4]])
def test_store_standard_types(s3, capsys, tmpdir, compress, arg):
    # pylint: disable=unused-argument
    """Test that any types can be cached in hdfs store."""
    def func(arg):
        """Dummy function."""
        print("executing function")
        return arg

    register_s3fs_store_backend()

    mem = Memory(location=tmpdir.strpath,
                 backend='s3', bucket="test",
                 verbose=0, compress=compress)

    assert mem.store.cachedir == os.path.join("s3:/", tmpdir.strpath, "joblib")

    cached_func = mem.cache(func)
    result = cached_func(arg)

    assert result == arg

    # Second call should also return the cached result
    result2 = cached_func(arg)

    assert result2 == arg


@pytest.mark.usefixtures("s3fs_open", "s3fs_mkdirp", "s3fs_exists")
@patch("s3fs.S3FileSystem")
@pytest.mark.parametrize("compress", [True, False])
def test_store_np_array(s3, capsys, tmpdir, compress):
    # pylint: disable=unused-argument
    """Test that any types can be cached in hdfs store."""
    def func(arg):
        """Dummy @mark.parametrize("arg", ["test",
                          b"test",
                          array.array('d', [1, 2, 3, 4]),
                          (1, 2, 3),
                          {"1": 1, "2": 2},
                          [1, 2, 3, 4]])@mark.parametrize("arg", ["test",
                          b"test",
                          array.array('d', [1, 2, 3, 4]),
                          (1, 2, 3),
                          {"1": 1, "2": 2},
                          [1, 2, 3, 4]])function."""
        print("executing function")
        return arg

    register_s3fs_store_backend()

    mem = Memory(location=tmpdir.strpath,
                 backend='s3', bucket="test",
                 verbose=0, compress=compress)

    assert mem.store.cachedir == os.path.join("s3:/", tmpdir.strpath, "joblib")

    arg = np.arange(100)
    cached_func = mem.cache(func)
    result = cached_func(arg)

    np.testing.assert_array_equal(result, arg)

    # Second call should also return the cached result
    result2 = cached_func(arg)

    np.testing.assert_array_equal(result2, arg)


@pytest.mark.usefixtures("s3fs_rm")
@patch("s3fs.S3FileSystem")
def test_clear_cache(s3, tmpdir):
    # pylint: disable=unused-argument
    """Check clearing the cache."""
    def func(arg):
        """Dummy function."""
        print("executing function")
        return arg

    register_s3fs_store_backend()

    mem = Memory(location=tmpdir.strpath, backend='s3', bucket="test",
                 verbose=0)
    cached_func = mem.cache(func)
    cached_func("test")

    mem.clear()

    assert not os.path.exists(mem.store.cachedir)


@pytest.mark.usefixtures("s3fs_rm")
@patch("s3fs.S3FileSystem")
def test_get_cache_items(s3, tmpdir):
    # pylint: disable=unused-argument
    """Test cache items listing."""
    def func(arg):
        """Dummy function."""
        return arg

    register_s3fs_store_backend()

    mem = Memory(location=tmpdir.strpath, backend='s3', bucket="test",
                 verbose=0)
    assert len(mem.store.get_cache_items()) == 0

    cached_func = mem.cache(func)
    for arg in ["test1", "test2", "test3"]:
        cached_func(arg)

    # get_cache_items always returns an empty list for the moment
    assert len(mem.store.get_cache_items()) == 0

    mem.clear()
    assert len(mem.store.get_cache_items()) == 0


def test_no_bucket_raises_exception(tmpdir):
    """Check correct exception is set when no bucket is set."""

    with pytest.raises(ValueError) as excinfo:
        Memory(location=tmpdir.strpath, backend='s3', verbose=0)
    excinfo.match("No valid S3 bucket set")
