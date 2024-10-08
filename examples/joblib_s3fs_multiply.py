"""Example showing how to joblib-s3 to cache results in a S3 store."""

import numpy as np
from joblib import Memory

from joblibs3 import register_s3fs_store_backend

if __name__ == "__main__":
    register_s3fs_store_backend()

    # we assume you S3 credentials are stored in ~/.aws/credentials, so no
    # need to pass them to Memory constructor (even if it's possible).
    mem = Memory(
        location="joblib_cache_s3",
        backend="s3fs",
        verbose=100,
        compress=True,
        backend_options=dict(bucket="joblib-example"),
    )
    mem.clear()

    multiply = mem.cache(np.multiply)
    array1 = np.arange(10000)
    array2 = np.arange(10000)

    print("# First call")
    _ = multiply(array1, array2)

    # Second call should return the cached result
    print("# Second call")
    result = multiply(array1, array2)

    print(result)
