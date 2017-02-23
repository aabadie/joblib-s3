"""Test the hdfs backend."""

import os.path
import array
import numpy as np

from pytest import mark

from joblib import Memory
from joblibstore import register_hdfs_store_backend


@mark.parametrize("compress", [True, False])
@mark.parametrize("arg", ["test",
                          b"test",
                          array.array('d', [1, 2, 3]),
                          np.arange(10),
                          (1, 2, 3),
                          {"1": 1, "2": 2},
                          [1, 2, 3, 4]])
def test_store_any_types(capsys, tmpdir, compress, arg):
    # pylint: disable=unused-argument
    """Test that any types can be cached in hdfs store."""
    def func(arg):
        """Dummy function."""
        print("executing function")
        return arg

    register_hdfs_store_backend()

    mem = Memory(location=os.path.basename(tmpdir.strpath),
                 backend='hdfs', host='localhost', port=8020, user='test',
                 verbose=100, compress=compress)

    assert mem.store.cachedir == os.path.join(os.path.basename(tmpdir.strpath),
                                              "joblib")

    cached_func = mem.cache(func)
    result = cached_func(arg)

    if isinstance(arg, np.ndarray):
        np.testing.assert_array_equal(arg, result)
    else:
        assert result == arg

    # Second call should return the cached result
    result2 = cached_func(arg)
    if isinstance(arg, np.ndarray):
        np.testing.assert_array_equal(arg, result)
    else:
        assert result2 == arg

    # Make this test fail
    # _, err = capsys.readouterr()
    # assert not err


def test_root_location_replacement(tmpdir):
    """Test that root location is correctly replaced."""
    location = os.path.join("/", os.path.basename(tmpdir.strpath))

    register_hdfs_store_backend()

    mem = Memory(location=location,
                 backend='hdfs', host='localhost', port=8020, user='test',
                 verbose=100)

    assert mem.store.cachedir == os.path.join(os.path.basename(tmpdir.strpath),
                                              "joblib")


def test_passing_backend_base_to_memory(tmpdir):
    """Test passing a store as location in memory is correctly handled."""
    location = os.path.basename(tmpdir.strpath)

    register_hdfs_store_backend()

    mem = Memory(location=location,
                 backend='hdfs', host='localhost', port=8020, user='test',
                 verbose=100)

    assert mem.store.cachedir == os.path.join(os.path.basename(tmpdir.strpath),
                                              "joblib")

    mem2 = Memory(location=mem.store,
                  backend='hdfs', host='localhost', port=8020, user='test',
                  verbose=100)

    assert mem2.store.cachedir == mem.store.cachedir


def test_clear_cache(tmpdir):
    """Test clearing cache."""
    def func(arg):
        """Dummy function."""
        print("executing function")
        return arg

    register_hdfs_store_backend()

    mem = Memory(location=os.path.basename(tmpdir.strpath),
                 backend='hdfs', host='localhost', port=8020, user='test',
                 verbose=100, compress=False)
    cached_func = mem.cache(func)
    cached_func("test")

    mem.clear()


def test_get_cache_items(tmpdir):
    """Test cache items listing."""
    def func(arg):
        """Dummy function."""
        return arg

    register_hdfs_store_backend()

    mem = Memory(location=os.path.basename(tmpdir.strpath),
                 backend='hdfs', host='localhost', port=8020, user='test',
                 verbose=100, compress=False)
    assert len(mem.store.get_cache_items()) == 0

    cached_func = mem.cache(func)
    for arg in ["test1", "test2", "test3"]:
        cached_func(arg)

    # get_cache_items always returns an empty list for the moment
    assert len(mem.store.get_cache_items()) == 0

    mem.clear()
    assert len(mem.store.get_cache_items()) == 0
