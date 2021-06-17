import sys

from dotenv import load_dotenv

from unifier import Unifier


def main():
    load_dotenv()
    Unifier(sys.argv[1]).process()


if __name__ == '__main__':
    main()
