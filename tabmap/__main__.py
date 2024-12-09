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
    parser.add_argument("-o", help="output file")
    parser.add_argument("--notes", help="yaml notes and colors for tables and columns")
    args = parser.parse_args()

    if args.latex: # output latex
        notes = {}
        # read the annotation if given
        if args.notes:
            with open(args.notes, "r") as f:
                notes = yaml.safe_load(f)
        print(makelatex(args.target, notes))
    else: # output plain text
        print(maketext(args.target))

sys.exit(main())
