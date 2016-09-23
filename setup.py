from setuptools import setup

import joblibstore

if __name__ == '__main__':
    setup(name='joblib-store',
          version='0.1',
          description=('Provides extra store backends for joblib cache.'),
          long_description=joblibstore.__doc__,
          url='https://github.com/aabadie/joblib-store',
          author='Alexandre Abadie',
          author_email='alexandre.abadie@inria.fr',
          license='BSD',
          platforms='any',
          packages=['joblibstore']
          )
