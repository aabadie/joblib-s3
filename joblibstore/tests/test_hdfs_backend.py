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
    print(os.path.basename(tmpdir.strpath))
    mem = Memory(location=os.path.basename(tmpdir.strpath),
                 backend='hdfs', host='localhost', port=8020, user='test',
                 verbose=100, compress=compress)

    cached_func = mem.cache(func)
    result = cached_func(arg)
    assert result == arg

    # Second call should return the cached result
    result2 = cached_func(arg)
    assert result2 == arg
