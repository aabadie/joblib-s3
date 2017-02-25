"""Test S3FS store backend."""

import os.path
import array

import pytest
import numpy as np
from s3fs import S3FileSystem
from joblib import Memory
from joblib.disk import mkdirp, rm_subdirs
from joblibstore import register_s3fs_store_backend


@pytest.fixture(autouse=True)
def s3fs_mock(monkeypatch):
    """Mock fixture for S3FileSystem."""
    def mock_open(self, *args, **kwargs):
        # pylint: disable=unused-argument
        """Mock open."""
        return open(*args, **kwargs)

    def mock_exists(self, directory):
        # pylint: disable=unused-argument
        """Mock exists."""
        return os.path.exists(directory)

    def mock_rm(self, directory, *args, **kwargs):
        """Mock rm."""
        # pylint: disable=unused-argument
        rm_subdirs(directory)

    def mock_mkdir(self, directory):
        # pylint: disable=unused-argument
        """Mock mkdir."""
        if directory.startswith("s3://"):
            # Skip bucket creation on purpose
            return
        return mkdirp(directory)

    def mock_init(self, *args, **kwargs):
        # pylint: disable=unused-argument
        """Mock constructor."""
        pass

    monkeypatch.setattr(S3FileSystem, "__init__", mock_init)
    monkeypatch.setattr(S3FileSystem, "mkdir", mock_mkdir)
    monkeypatch.setattr(S3FileSystem, "rm", mock_rm)
    monkeypatch.setattr(S3FileSystem, "open", mock_open)
    monkeypatch.setattr(S3FileSystem, "exists", mock_exists)


@pytest.mark.parametrize("compress", [True, False])
@pytest.mark.parametrize("arg", ["test",
                                 b"test",
                                 array.array('d', [1, 2, 3, 4]),
                                 (1, 2, 3),
                                 {"1": 1, "2": 2},
                                 [1, 2, 3, 4]])
def test_store_standard_types(capsys, tmpdir, compress, arg):
    """Test that standard types can be cached in s3fs store."""
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

    out, err = capsys.readouterr()
    assert out == "executing function\n"
    assert not err

    # Second call should also return the cached result
    result2 = cached_func(arg)

    assert result2 == arg

    out, err = capsys.readouterr()
    assert not out
    assert not err


@pytest.mark.parametrize("compress", [True, False])
def test_store_np_array(capsys, tmpdir, compress):
    """Test that any types can be cached in s3fs store."""
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

    out, err = capsys.readouterr()
    assert out == "executing function\n"
    assert not err

    # Second call should also return the cached result
    result2 = cached_func(arg)

    np.testing.assert_array_equal(result2, arg)

    out, err = capsys.readouterr()
    assert not out
    assert not err


def test_clear_cache(capsys, tmpdir):
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

    out, _ = capsys.readouterr()
    assert out == "executing function\n"

    mem.clear()

    cached_func("test")
    out, _ = capsys.readouterr()
    assert out == "executing function\n"

    mem.clear()
    print(mem.store.cachedir)
    assert not os.listdir(mem.store.cachedir)


def test_get_cache_items(tmpdir):
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
