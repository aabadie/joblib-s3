from setuptools import setup

import joblib_store.joblib_backends

if __name__ == '__main__':
    setup(name='joblib-store',
          version='0.1',
          description=('Provides extra store backends for joblib cache.'),
          long_description=joblib_store.__doc__,
          url='https://github.com/aabadie/joblib-store',
          author='Alexandre Abadie',
          author_email='alexandre.abadie@inria.fr',
          license='BSD',
          platforms='any',
          packages=['joblib_store']
          )
