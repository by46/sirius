from sirius import deploy
from sirius import image_name

__all__ = ['deploy', 'image_name', 'usage']


def usage(cmd=None):
    if cmd is None:
        print __all__
    print deploy.__doc__


def version():
    pass
