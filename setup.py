from setuptools import setup, find_packages
import site

setup(
    name='sirius',
    version='0.0.1',
    description='just a simplesirius',

    author='jj',

    packages=find_packages(),
    platforms='any'
)

print site.getsitepackages()
