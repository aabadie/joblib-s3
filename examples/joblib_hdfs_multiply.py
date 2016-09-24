"""Example showing how to use joblib-store to cache results in a HDFS store."""

import numpy as np
from joblib import Memory
from joblibstore import register_hdfs_store_backend

if __name__ == '__main__':
    register_hdfs_store_backend()

    mem = Memory('hdfs://joblib-aa/joblib_cache', host='hdfs.host.com',
                 port=8020, user='login', verbose=100, compress=True)

    multiply = mem.cache(np.multiply)
    array1 = np.arange(10000)
    array2 = np.arange(10000)

    result = multiply(array1, array2)
    print(result)
