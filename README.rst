This package provides store backends for joblib Memory object used for fast
caching of computation results.

Initially, only local (or network shares) file systems were supported with
joblib but now joblib offers the possibility to register extra store backend
matching the provided StoreBackendBase API.

If you don't know joblib, user documentation is located on:
https://pythonhosted.org/joblib

If you are only interested in computation result caching in joblib, the Memory
documentation is available
`here <https://pythonhosted.org/joblib/memory.html>`_.


Getting the latest code
=======================

To get the latest code using git, simply type::

    git clone git://github.com/aabadie/joblib-store.git


Using joblib-store to cache result
==================================

For the moment, joblib-store only provides a store backend for Amazon S3 cloud
storage. This backend relies on `boto3
<https://boto3.readthedocs.io/en/latest/>`_ and `dask s3fs
<https://s3fs.readthedocs.io/en/latest/index.html>`_ packages.

Here is an example of joblib cache usage with the S3 store backend provided by
joblib-store:

::

    # Import the required packages
    import numpy as np
    from joblib import Memory
    from joblibstore import register_s3_store_backend

    if __name__ == '__main__':
        register_s3_store_backend()

        # we assume you S3 credentials are stored in ~/.aws/credentials, so no
        # need to pass them to Memory constructor.
        mem = Memory('joblib_cache', backend='s3', bucket='<my_bucket>', verbose=100,
                     compress=True)

        multiply = mem.cache(np.multiply)
        array1 = np.arange(10000)
        array2 = np.arange(10000)

        result = multiply(array1, array2)
        print(result)
