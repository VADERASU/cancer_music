from music21.expressions import TextExpression
from music21.stream.base import Measure, Stream

from processor import utils
from processor.parameters import Therapy, TherapyParameters

def no_therapy(s: Stream, _: TherapyParameters):
    return s


def cure(s: Stream, tp: TherapyParameters):
    start = utils.get_percentile_measure_number(s, tp["start"])

    measures = s.measures(start, None).getElementsByClass("Measure")

    for m in measures:
        m.removeByClass(["GeneralNote", "Lyric"])

    s.makeRests(fillGaps=True, inPlace=True)
    return s


def partial_cure(s: Stream, tp: TherapyParameters):
    start = utils.get_percentile_measure_number(s, tp["start"])
    measures = s.measures(start, None).getElementsByClass("Measure")

    for m in measures:
        notes = m.getElementsByClass("GeneralNote")
        for n in notes:
            lyrics = n.lyrics
            # TODO: check if lyrics are markers or not
            if len(lyrics) > 0:
                if utils.get_probability() >= tp["resistance_probability"]:
                    m.remove(n, recurse=True)
    s.makeRests(fillGaps=True, inPlace=True)
    return s


def get_therapy(t: Therapy):
    if t.value == 0:
        return no_therapy
    if t.value == 1:
        return cure
    return partial_cure
