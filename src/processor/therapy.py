import random

from music21.note import Rest
from music21.stream.base import Stream

from processor import utils
from processor.constants import mutation_markers
from processor.parameters import Therapy, TherapyParameters


def no_therapy(s: Stream, _: TherapyParameters, __: random.Random):
    return s


def _cure(s: Stream, tp: TherapyParameters, rng: random.Random):
    notes = s.getElementsByClass("GeneralNote")
    for n in notes:
        if rng.random() >= tp["resistance_probability"]:
            offset = n.offset
            s.remove(n)

            rest = Rest(length=n.duration.quarterLength)
            rest.addLyric("c")
            s.insert(offset, rest)


def cure(s: Stream, tp: TherapyParameters, rng: random.Random):
    start = utils.get_percentile_measure_number(s, tp["start"])
    measures = s.measures(start, None).getElementsByClass("Measure")

    for m in measures:
        if len(m.voices) > 0:
            for nv in m.voices:
                _cure(nv, tp, rng)
        else:
            _cure(m, tp, rng)
    return s


def get_therapy(t: Therapy):
    if t.value == 0:
        return no_therapy
    return cure
