import sys

from unifier import Unifier


def main():
    Unifier(sys.argv[1]).process()


if __name__ == '__main__':
    main()
