"""Test the hdfs backend."""

import os.path

from pytest import mark, warns

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


@mark.parametrize("compress", [True, False])
def test_store_mmap_mode_raise_exception(tmpdir, compress):
    def func(arg):
        return arg

    register_hdfs_store_backend()

    with warns(None) as w:
        mem = Memory(location=os.path.basename(tmpdir.strpath),
                     backend='hdfs', host='localhost', port=8020, user='test',
                     verbose=100, compress=compress, mmap_mode='r+')

    assert len(w) == 1
    assert w[0].message.args[0] == ('Memory mapping cannot be used on HDFS '
                                    'store. This option will be ignored.')

    cached_func = mem.cache(func)
    result = cached_func("test")
    assert result == "test"
