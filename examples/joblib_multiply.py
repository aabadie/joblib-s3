"""Example showing how to joblib-store to cache results in a S3 store."""

import numpy as np
from joblib import Memory
from joblibstore import register_s3_store_backend

if __name__ == '__main__':
    register_s3_store_backend()

    # we assume you S3 credentials are stored in ~/.aws/credentials, so no
    # need to pass them to Memory constructor.
    mem = Memory('s3://joblib-aa/joblib_cache', verbose=100,
                 compress=True)

    multiply = mem.cache(np.multiply)
    array1 = np.arange(10000)
    array2 = np.arange(10000)

    result = multiply(array1, array2)
    print(result)
