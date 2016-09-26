from setuptools import setup

if __name__ == '__main__':

    setup(name='joblib-store',
          version='0.1',
          description=('Provides extra store backends for joblib cache.'),
          url='https://github.com/aabadie/joblib-store',
          author='Alexandre Abadie',
          author_email='alexandre.abadie@inria.fr',
          license='BSD',
          platforms='any',
          packages=['joblibstore'],
          install_requires=[
            's3fs', 'apache-libcloud',
          ],
          zip_safe=False,
          )
