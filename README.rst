Joblibs3
========

|Travis| |Codecov|

.. |Travis| image:: https://travis-ci.org/aabadie/joblib-s3.svg?branch=master
    :target: https://travis-ci.org/aabadie/joblib-s3

.. |Codecov| image:: https://codecov.io/gh/aabadie/joblib-s3/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/aabadie/joblib-s3

This package provides an AWS store backend for the joblib Memory object used
for fast caching of computation results.

Initially, only local (or network shares) file systems were supported with
joblib but now joblib offers the possibility to register extra store backends
matching the provided StoreBackendBase API.

If you don't know joblib already, user documentation is located on
https://pythonhosted.org/joblib

If you are only interested in computation result caching in joblib, the Memory
documentation is available
`here <https://pythonhosted.org/joblib/memory.html>`_.

The AWS S3 backend relies on the `dask s3fs
<https://s3fs.readthedocs.io/en/latest/index.html>`_ package.

Joblibs3 supports Python 2.7, 3.4 and 3.5.

Getting the latest code
=======================

To get the latest code use git::

    git clone git://github.com/aabadie/joblib-s3.git

Installing joblibs3
===================

Simply use pip:

..  code-block:: bash

    $ cd joblib-s3
    $ pip install -r requirements.txt .


Using joblibs3 to cache computation results in AWS S3
=====================================================

See the following example:

..  code-block:: python

    # Import the required packages
    import numpy as np
    from joblib import Memory
    from joblibs3 import register_s3_store_backend

    if __name__ == '__main__':
        register_s3_store_backend()

        # we assume you S3 credentials are stored in ~/.aws/credentials, so no
        # need to pass them to Memory constructor.
        mem = Memory('joblib_cache', backend='s3', verbose=100, compress=True,
                     store_options=dict(bucket="joblib-example"))

        multiply = mem.cache(np.multiply)
        array1 = np.arange(10000)
        array2 = np.arange(10000)

        result = multiply(array1, array2)
        print(result)

This example is available in the `examples <examples>`_ directory.
