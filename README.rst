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
    from joblib_store import register_s3_store_backend

    if __name__ == '__main__':
        register_s3_store_backend()

        # we assume you S3 credentials are stored in ~/.aws/credentials, so no
        # need to pass them to Memory constructor.
        mem = Memory('s3://<your_bucker>/joblib_cache', verbose=100,
                     compress=True)

        multiply = mem.cache(np.multiply)
        array1 = np.arange(10000)
        array2 = np.arange(10000)

        result = multiply(array1, array2)
        print(result)


Licensing
---------
 
 Joblib-store is **BSD-licenced** (3 clause):
 
     This software is OSI Certified Open Source Software.
     OSI Certified is a certification mark of the Open Source Initiative.
 
     Copyright (c) 2009-2011, joblib developpers
     All rights reserved.
 
     Redistribution and use in source and binary forms, with or without
     modification, are permitted provided that the following conditions are met:
 
     * Redistributions of source code must retain the above copyright notice,
       this list of conditions and the following disclaimer.
 
     * Redistributions in binary form must reproduce the above copyright notice,
       this list of conditions and the following disclaimer in the documentation
       and/or other materials provided with the distribution.
 
     * Neither the name of Gael Varoquaux. nor the names of other joblib
       contributors may be used to endorse or promote products derived from
       this software without specific prior written permission.
 
     **This software is provided by the copyright holders and contributors
     "as is" and any express or implied warranties, including, but not
     limited to, the implied warranties of merchantability and fitness for
     a particular purpose are disclaimed. In no event shall the copyright
     owner or contributors be liable for any direct, indirect, incidental,
     special, exemplary, or consequential damages (including, but not
     limited to, procurement of substitute goods or services; loss of use,
     data, or profits; or business interruption) however caused and on any
     theory of liability, whether in contract, strict liability, or tort
     (including negligence or otherwise) arising in any way out of the use
     of this software, even if advised of the possibility of such
     damage.**

