import sirius
from sirius import deploy
from sirius import image_name

__all__ = ['deploy', 'image_name', 'usage', 'version']

HELP_LINE = """
Usage Example:

    sirius -l
        print list of possible commands and exit
    sirius -d NAME
        print detailed info about command NAME
    sirius COMMAND
        execute COMMAND
"""


def usage(cmd=None):
    print(HELP_LINE)


def version():
    print("Sirius Administrator Task Tool Version {0}".format(sirius.__version__))
