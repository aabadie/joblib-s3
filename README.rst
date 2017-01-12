This package provides store backends for joblib Memory object used for fast
caching of computation results.

Initially, only local (or network shares) file systems were supported with
joblib but now joblib offers the possibility to register extra store backends
matching the provided StoreBackendBase API.

If you don't know joblib already, user documentation is located on
https://pythonhosted.org/joblib

If you are only interested in computation result caching in joblib, the Memory
documentation is available
`here <https://pythonhosted.org/joblib/memory.html>`_.


Getting the latest code
=======================

To get the latest code using git, simply type::

    git clone git://github.com/aabadie/joblibstore.git


Using joblibstore to cache result
=================================

For the moment, joblibstore provides store backends for Amazon S3 cloud
storage and Hadoop file systems (HDFS). The S3 backend relies on `boto3
<https://boto3.readthedocs.io/en/latest/>`_ and `dask s3fs
<https://s3fs.readthedocs.io/en/latest/index.html>`_ packages. The HDFS backend
relies on the `hdfs3 <https://hdfs3.readthedocs.io/en/latest/>`_ package.

We provide here an example of joblib cache usage with the S3 store backend
provided by joblibstore:

..  code-block:: python

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


Installing the hdfs3 package
============================

`hdfs3 <https://hdfs3.readthedocs.io/en/latest/>`_ can be installed using 2
ways.


Using Conda Forge
-----------------

A prebuilt version of all `hdfs3` dependencies is available on Conda Forge. If
you are already using Conda, this method is recommanded :

.. code-block:: bash
    $ conda install hdfs3 libhdfs3 -c conda-forge


Building `hdfs` dependencies by hand
------------------------------------
 
The following notes are specific to Ubuntu 16.04 but can also be adapted to
Fedora (packages names are slightly different).

`hdfs3 <https://hdfs3.readthedocs.io/en/latest/>`_ is based on the C++ libhdfs3
library which cannot be installed directly with apt-get on Ubuntu. You need to
fetch code with git and build it locally the computer that runs joblib.

1. Clone libhdfs3 from github:

.. code-block:: bash

    $ sudo mkdir /opt/hdfs3
    $ sudo chown <login>:<login> /opt/hdfs3
    $ cd /opt/hdfs3
    $ git clone git@github.com:Pivotal-Data-Attic/pivotalrd-libhdfs3.git libhdfs3


2. Install required packages

.. code-block:: bash

    $ sudo apt-get install cmake cmake-curses-gui libxml2-dev libprotobuf-dev \
    libkrb5-dev uuid-dev libgsasl7-dev protobuf-compiler protobuf-c-compiler \
    build-essential -y


3. Use CMake to configure and build

.. code-block:: bash

   $ cd /opt/hdfs3/libhdfs3
   $ mkdir build
   $ cd build
   $ ../bootstrap
   $ make
   $ make install


4. Add the following to your **~/.bashrc** environment file:

::

   export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/hdfs3/libhdfs3/dist


and reload it:


.. code-block:: bash

   $ source ~/.bashrc


5. Finally you can use **pip** to install the *hdfs3* package (use `sudo` if
needed):

.. code-block:: bash

   $ pip install hdfs3
