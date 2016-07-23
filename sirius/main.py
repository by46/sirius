import sys

import fabric.main


def main():
    has_fabfile = any([v.startswith('-f') or v.startswith('--fabfile') for v in sys.argv])

    if not has_fabfile:
        sys.argv.insert(1, '--fabfile=/etc/python/sirius_fabfile.py')

    fabric.main.main()


if __name__ == '__main__':
    main()
