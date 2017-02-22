"""Example showing how to use joblib-store to cache results in a HDFS store."""

import numpy as np
from joblib import Memory
from joblibstore import register_hdfs_store_backend

if __name__ == '__main__':
    register_hdfs_store_backend()

    mem = Memory(location='joblib_cache_hdfs',
                 backend='hdfs', host='localhost', port=8020, user='test',
                 verbose=100, compress=True)

    multiply = mem.cache(np.multiply)
    array1 = np.arange(10000)
    array2 = np.arange(10000)

    result = multiply(array1, array2)

    # Second call should return the cached result
    result = multiply(array1, array2)
    print(result)
