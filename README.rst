Joblibstore
===========

|Travis| |Codecov|

.. |Travis| image:: https://travis-ci.org/aabadie/joblibstore.svg?branch=master
    :target: https://travis-ci.org/aabadie/joblibstore

.. |Codecov| image:: https://codecov.io/gh/aabadie/joblibstore/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/aabadie/joblibstore

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

For the moment, joblibstore provides store backends for Amazon S3 cloud
storage and Hadoop file systems (HDFS). The S3 backend relies on `boto3
<https://boto3.readthedocs.io/en/latest/>`_ and `dask s3fs
<https://s3fs.readthedocs.io/en/latest/index.html>`_ packages. The HDFS backend
relies on the `hdfs3 <https://hdfs3.readthedocs.io/en/latest/>`_ package.

We plan to add support for other cloud storage providers: Google Cloud Storage,
Azure, etc

Getting the latest code
=======================

To get the latest code use git::

    git clone git://github.com/aabadie/joblibstore.git

Installing joblibstore
======================

We recommend using
`Python Anaconda 3 distribution <https://www.continuum.io/Downloads>`_ for
full support of available store backends : S3 and HDFS.

1. Create a Python 3.4 Anaconda environment and activate it:

..  code-block:: bash

    $ conda create -n py34-joblibstore python==3.4 s3fs hdfs3 libhdfs3 -c conda-forge
    $ . activate py34-joblibstore

2. From the `py34-joblistore` environment, use pip to install joblibstore:

..  code-block:: bash

    $ cd joblibstore
    $ pip install .


Using joblibstore to cache computation results in the Cloud
===========================================================

Here are 2 examples of joblib cache usage with the store backends provided by
joblibstore:

1. Using S3 backend:

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

2. Using HDFS backend:

..  code-block:: python

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


All examples are available in the `examples <examples>`_ directory.

Developping in joblibstore
==========================

Prerequisites
-------------

In order to run the test suite, you need to setup a local hadoop cluster. This
can be achieved very easily using the docker and docker-compose recipes given
in the `docker <docker>`_ directory:

1. `Install docker-engine <https://docs.docker.com/engine/installation/>`_:

You have to be able to run the hello-world container:

..  code-block:: bash

    $ docker run hello-world

2. Install docker-compose using pip in your anaconda environment:

..  code-block:: bash

    $ . activate py34-joblibstore
    $ pip install docker-compose


3. Build the hadoop cluster using docker-compose:

..  code-block:: bash

    $ cd joblistore/docker
    $ docker-compose run namenode hdfs namenode -format

Running the test suite
----------------------

1. Start your hadoop cluster:

..  code-block:: bash

   $ cd joblibstore/docker
   $ docker-compose up

2. Run pytest (from another terminal):

..  code-block:: bash

    $ pytest


Installing the hdfs3 package by hand
====================================

For the moment hdfs3 cannot be directly installed using pip : the reason is
because hdfs3 depends on a C++ based library that is not available in the
Linux distros and that one needs to build by hand first.

The following notes are specific to Ubuntu 16.04 but can also be adapted to
Fedora (packages names are slightly different).

1. Clone libhdfs3 from github:

..  code-block:: bash

    $ sudo mkdir /opt/hdfs3
    $ sudo chown <login>:<login> /opt/hdfs3
    $ cd /opt/hdfs3
    $ git clone git@github.com:Pivotal-Data-Attic/pivotalrd-libhdfs3.git libhdfs3


2. Install required packages

..  code-block:: bash

    $ sudo apt-get install cmake cmake-curses-gui libxml2-dev libprotobuf-dev \
    libkrb5-dev uuid-dev libgsasl7-dev protobuf-compiler protobuf-c-compiler \
    build-essential -y


3. Use CMake to configure and build

..  code-block:: bash

   $ cd /opt/hdfs3/libhdfs3
   $ mkdir build
   $ cd build
   $ ../bootstrap
   $ make
   $ make install


4. Add the following to your **~/.bashrc** environment file:

::

   export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/hdfs3/libhdfs3/dist

5. reload your environment:

..  code-block:: bash

   $ source ~/.bashrc

6. Use **pip** to install *hdfs3* (use `sudo` if needed):

..  code-block:: bash

   $ pip install hdfs3
