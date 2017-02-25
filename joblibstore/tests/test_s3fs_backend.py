"""Test S3FS store backend."""

import os.path
import array
from unittest.mock import patch

import numpy as np
from pytest import mark, fixture, raises
from s3fs import S3FileSystem
from joblib import Memory
from joblib.disk import mkdirp, rm_subdirs
from joblibstore import register_s3fs_store_backend


def custom_mkdirp(directory):
    """Replace S3 'mkdir' function with a custom local filesystem one."""
    if directory.startswith("s3:"):
        directory = directory.replace("s3:/", "")
    mkdirp(directory)


def custom_rm(directory):
    """Replace S3 'rm' function with a custom local filesystem one."""
    if directory.startswith("s3:"):
        directory = directory.replace("s3:/", "")
    rm_subdirs(directory)


def custom_exists(location):
    """Replace S3 'exists' function with a custom local filesystem one."""
    if location.startswith("s3:"):
        location = location.replace("s3:/", "")
    return os.path.exists(location)


@fixture(scope="module")
def s3fs_mkdirp(monkeypatch):
    """mkdirp fixture"""
    monkeypatch.setattr(S3FileSystem, "mkdir", custom_mkdirp)


@fixture(scope="module")
def s3fs_exists(monkeypatch):
    """exists fixture"""
    monkeypatch.setattr(S3FileSystem, "exists", custom_exists)


@fixture(scope="module")
def s3fs_open(monkeypatch):
    """open fixture"""
    monkeypatch.setattr(S3FileSystem, "open", open)


@fixture(scope="module")
def s3fs_rm(monkeypatch):
    """open fixture"""
    monkeypatch.setattr(S3FileSystem, "rm", custom_rm)


@patch("s3fs.S3FileSystem")
@mark.parametrize("compress", [True, False])
@mark.parametrize("arg", ["test",
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


@patch("s3fs.S3FileSystem")
@mark.parametrize("compress", [True, False])
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

    assert not custom_exists(mem.store.cachedir)


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

    with raises(ValueError) as excinfo:
        Memory(location=tmpdir.strpath, backend='s3', verbose=0)
    excinfo.match("No valid S3 bucket set")
