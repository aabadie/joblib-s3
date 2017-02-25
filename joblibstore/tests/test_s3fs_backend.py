"""Test S3FS store backend."""

import os.path
import array

import pytest
import numpy as np
from s3fs import S3FileSystem
from joblib import Memory
from joblib.disk import mkdirp, rm_subdirs
from joblibstore import register_s3fs_store_backend


@pytest.fixture()
def s3fs_custom(monkeypatch):
    """open fixture"""
    def custom_open(self, *args, **kwargs):
        # pylint: disable=unused-argument
        """Dummy constructor."""
        return open(*args, **kwargs)

    def custom_exists(self, directory):
        # pylint: disable=unused-argument
        """Dummy constructor."""
        return os.path.exists(directory)

    def custom_rm(self, directory, *args, **kwargs):
        """Dummy constructor."""
        # pylint: disable=unused-argument
        rm_subdirs(directory)

    def custom_mkdir(self, directory):
        # pylint: disable=unused-argument
        """Dummy constructor."""
        if directory.startswith("s3://"):
            # Skip bucket creation on purpose
            return
        return mkdirp(directory)

    def custom_init(self, *args, **kwargs):
        # pylint: disable=unused-argument
        """Dummy constructor."""
        pass

    monkeypatch.setattr(S3FileSystem, "__init__", custom_init)
    monkeypatch.setattr(S3FileSystem, "mkdir", custom_mkdir)
    monkeypatch.setattr(S3FileSystem, "rm", custom_rm)
    monkeypatch.setattr(S3FileSystem, "open", custom_open)
    monkeypatch.setattr(S3FileSystem, "exists", custom_exists)


@pytest.mark.usefixtures("s3fs_custom")
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


@pytest.mark.usefixtures("s3fs_custom")
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


@pytest.mark.usefixtures("s3fs_custom")
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


@pytest.mark.usefixtures("s3fs_custom")
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


@pytest.mark.usefixtures("s3fs_custom")
def test_no_bucket_raises_exception(tmpdir):
    """Check correct exception is set when no bucket is set."""

    with pytest.raises(ValueError) as excinfo:
        Memory(location=tmpdir.strpath, backend='s3', verbose=0)
    excinfo.match("No valid S3 bucket set")
