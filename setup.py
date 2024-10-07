"""joblib-s3 package installation module."""

from setuptools import setup

if __name__ == "__main__":

    setup(
        name="joblibs3",
        version="0.1",
        description=("Provides AWS S3 store backend for joblib cache."),
        url="https://github.com/aabadie/joblib-s3",
        author="Alexandre Abadie",
        author_email="alexandre.abadie@inria.fr",
        license="BSD",
        platforms="any",
        packages=["joblibs3"],
        install_requires=["joblib>=0.10", "s3fs>=0.0.7"],
        zip_safe=False,
    )
