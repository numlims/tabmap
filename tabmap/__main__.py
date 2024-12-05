# main is the entry point for the cmd line interface

import argparse
import sys

from tabmap import *

# main parses args and starts tabmap accordingly
def main():
    # parse arguments
    parser = argparse.ArgumentParser(description="table info for db")
    parser.add_argument("target", help="a database target in .dbc file")
    parser.add_argument("--latex", help="produce tabmap latex", required=False, action="store_true")
    args = parser.parse_args()

    if args.latex: # output latex
        print(makelatex(args.target))
    else: # output plain text
        print(maketext(args.target))

sys.exit(main())
