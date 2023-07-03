"""
Command-line script for running the mutation on a file.
"""

import argparse
from datetime import datetime

from music21 import converter

from processor import process, utils


def main():
    parser = argparse.ArgumentParser(prog="SheetMusicMutator")
    parser.add_argument(
        "sheet_music",
        help="Sheet music to mutate. \
        Refer to music21's documentation [https://web.mit.edu/music21/doc/] \
        for supported filetypes.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Name of the output file. Optional; \
        if not provided, named with unix timestamp.",
        required=False,
        default=f"mutant_{int(datetime.timestamp(datetime.now()))}.mxl",
    )
    args = parser.parse_args()
    fp = utils.build_file_path(args.sheet_music)
    s = None
    try:
        s = converter.parseFile(fp, storePickle=False, quantizePost=False)
    except:
        raise ValueError(f"{fp} could not be parsed.")
    process.mutate(s)
    s.write("musicxml", args.output)

    print(f"Wrote output to {args.output}")


if __name__ == "__main__":
    main()
