"""joblib-store package installation module."""

from setuptools import setup

if __name__ == '__main__':

    setup(name='joblibstore',
          version='0.1',
          description=('Provides extra store backends for joblib cache.'),
          url='https://github.com/aabadie/joblib-store',
          author='Alexandre Abadie',
          author_email='alexandre.abadie@inria.fr',
          license='BSD',
          platforms='any',
          packages=['joblibstore'],
          install_requires=[
            'joblib>=0.10',
            's3fs>=0.0.7',
            'apache-libcloud>=1.2.1',
          ],
          zip_safe=False,
          )
