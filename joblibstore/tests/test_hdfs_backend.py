"""Test the hdfs backend."""

import os.path

from pytest import mark

from joblib import Memory
from joblibstore import register_hdfs_store_backend


@mark.parametrize("compress", [True, False])
@mark.parametrize("arg", ["test",
                          (1, 2, 3),
                          {"1": 1, "2": 2},
                          [1, 2, 3, 4]])
def test_store_standard_types(tmpdir, compress, arg):
    def func(arg):
        print("executing function")
        return arg

    register_hdfs_store_backend()

    mem = Memory(location=os.path.basename(tmpdir.strpath),
                 backend='hdfs', host='localhost', port=8020, user='test',
                 verbose=100, compress=compress)

    cached_func = mem.cache(func)
    result = cached_func(arg)
    assert result == arg

    # Second call should return the cached result
    result2 = cached_func(arg)
    assert result2 == arg


def test_clear_cache(tmpdir):
    def func(arg):
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
    def func(arg):
        return arg

    register_hdfs_store_backend()

    mem = Memory(location=os.path.basename(tmpdir.strpath),
                 backend='hdfs', host='localhost', port=8020, user='test',
                 verbose=100, compress=False)
    assert len(mem.store.get_cache_items()) == 0

    cached_func = mem.cache(func)
    for arg in ["test1", "test2", "test3"]:
        cached_func("test")

    # get_cache_items always returns an empty list for the moment
    assert len(mem.store.get_cache_items()) == 0

    mem.clear()
    assert len(mem.store.get_cache_items()) == 0
