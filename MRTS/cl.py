import sys
from .interface import interface


def main():
    exit_code = interface.main(sys.argv)
