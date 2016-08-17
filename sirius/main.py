import os.path
import sys

import fabric.main


def main():
    has_fabfile = any([v.startswith('-f') or v.startswith('--fabfile') for v in sys.argv])

    if not has_fabfile:
        fab_file = os.path.normpath(os.path.join(__file__, '..', 'sirius_fabfile.py'))
        sys.argv.insert(1, '--fabfile={0}'.format(fab_file))

    fabric.main.main()


if __name__ == '__main__':
    main()
