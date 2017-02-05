"""Sirius Administrator Task Tool
"""
from __future__ import print_function

from .docker import docker_build_image
from .docker import docker_deploy
from .docker import docker_dev_deploy
from .docker import docker_image_name
from .docker import docker_new_build_no
from .docker import docker_release
from .docker import docker_dfis_prd_deploy
from .ci import get_config
from .ci import update_config

__version__ = "0.0.4"
