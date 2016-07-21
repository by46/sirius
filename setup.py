from __future__ import print_function

import io
import os.path
import re
import sys
from distutils.text_file import TextFile

from setuptools import find_packages, setup

home = os.path.abspath(os.path.dirname(__file__))
missing = object()


def read_description(*files, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = [io.open(name, encoding=encoding).read() for name in files]
    return sep.join(buf)


def read_dependencies(requirements=missing):
    if requirements is None:
        return []
    if requirements is missing:
        requirements = 'requirements.txt'
    if not os.path.isfile(requirements):
        return []
    text = TextFile(requirements, lstrip_ws=True)
    try:
        return text.readlines()
    finally:
        text.close()


def read_version(version_file):
    with open(version_file, 'rb') as fd:
        result = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                           fd.read(), re.MULTILINE)
        return result.group(1) if result else '0.0.1'


setup(
    name='sirius',
    version=read_version('sirius/__init__.py'),
    url="http://trgit2/dfis/sirius",
    license='The MIT License',
    description='just a simplesirius',
    author='DFIS',
    install_requires=read_dependencies(),
    include_package_data=True,
    packages=find_packages(),
    data_files=[("/etc/python", ['fabfile.py']),
                ('/etc/profile.d', ['sirius.sh'])],
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 3 - Alpha',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ]
)

# if sys.platform.startswith('linux'):
#     import os.path
#     import site
#
#     success = False
#     name = "sirius"
#     for p in site.getsitepackages():
#         full_path = os.path.join(p, name, 'fabfile.py')
#         print(full_path)
#         if os.path.isfile(full_path):
#             command = '#! /bin/sh\nalias sirius="fab --fabfile={0}"\n'.format(full_path)
#             with open('/etc/profile.d/sirius.sh', 'wb') as f:
#                 f.write(command)
#             success = True
#             break
#
#     if not success:
#         raise Exception("Could not find site package")
