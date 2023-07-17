import random

from music21.note import Rest
from music21.stream.base import Stream

from processor import utils
from processor.constants import mutation_markers
from processor.parameters import Therapy, TherapyParameters


def _cure(
    s: Stream,
):
    notes = s.getElementsByClass("GeneralNote")
    for n in notes:
        offset = n.offset
        s.remove(n)

        rest = Rest(length=n.duration.quarterLength)
        rest.addLyric("c")
        s.insert(offset, rest)


def cure(s: Stream, start: int):
    measures = s.measures(start, None).getElementsByClass("Measure")
    for m in measures:
        if len(m.voices) > 0:
            for nv in m.voices:
                _cure(nv)
        else:
            _cure(m)
    return s
