from setuptools import setup
from Cython.Build import cythonize

setup(
    name='Backend',
    ext_modules=cythonize("api/main.pyx"),
    zip_safe=False,
)
