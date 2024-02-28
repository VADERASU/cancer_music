"""
Command-line script for running the mutation on a file.
"""

import argparse
import random
import sys
from datetime import datetime

from music21 import converter

from processor import process, utils
from processor.parameters import Parameters, Therapy, TherapyParameters


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

    parser.add_argument(
        "-s",
        "--seed",
        help="Seed of the mutation",
        type=int,
        required=False,
        default=random.randrange(sys.maxsize),
    )

    args = parser.parse_args()
    fp = utils.build_file_path(args.sheet_music)
    s = None
    try:
        s = converter.parseFile(fp, storePickle=False, quantizePost=False)
    except Exception as e:
        raise ValueError(f"{fp} could not be parsed: {str(e)}.")

    maxParts = 4
    reproductionProbability = 0.3
    how_many = 4

    noop = 0.05
    insertion = 0.25
    transposition = 0.15
    deletion = 0.15
    inversion = 0.25
    translocation = 0.15

    cancerStart = 0.25
    mode = 1
    mutant_survival = 0.5
    start = 0.75

    s, tree = process.mutate(
        s,
        Parameters(
            max_parts=maxParts,
            reproduction=reproductionProbability,
            how_many=how_many,
            noop=noop,
            insertion=insertion,
            transposition=transposition,
            deletion=deletion,
            translocation=translocation,
            inversion=inversion,
            start=cancerStart,
        ),
        TherapyParameters(
            therapy_mode=Therapy(mode),
            mutant_survival=mutant_survival,
            start=start,
            adaptive_threshold=2,
            adaptive_interval=8,
        ),
        seed=args.seed,
    )

    s.write("musicxml", args.output)
    # s.write("midi", args.output + ".mid")

    print(f"Wrote output to {args.output}")


if __name__ == "__main__":
    main()
