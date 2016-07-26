import sirius
from sirius import docker_build_image
from sirius import docker_deploy
from sirius import docker_image_name
from sirius import docker_new_build_no
from sirius import docker_prepare_build

__all__ = ['usage', 'version',
           'docker_deploy', 'docker_image_name', 'docker_build_image',
           'docker_new_build_no', 'docker_prepare_build']

HELP_LINE = """
Usage Example:

    sirius -l
        print list of possible commands and exit
    sirius -d NAME
        print detailed info about command NAME
    sirius COMMAND
        execute COMMAND
"""


def usage():
    """help information

    :return: None
    """
    print(HELP_LINE)


def version():
    """version information

    :return:
    """
    print("Sirius Administrator Task Tool Version {0}".format(sirius.__version__))
