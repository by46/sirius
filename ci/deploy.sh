#!/bin/sh

python setup.py sdist upload -r http://scmesos06

pip uninstall sirius

pip --trusted-host scmesos06 install -i http://scmesos06/simple sirius
