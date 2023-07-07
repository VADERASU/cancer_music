from music21.note import Rest
from music21.stream.base import Stream

from processor import utils
from processor.constants import mutation_markers
from processor.parameters import Therapy, TherapyParameters


def no_therapy(s: Stream, _: TherapyParameters):
    return s


def _cure(s: Stream, tp: TherapyParameters):
    notes = s.getElementsByClass("GeneralNote")
    for n in notes:
        lyrics = n.lyrics
        if len(lyrics) > 0:
            for lyric in lyrics:
                if lyric.text in mutation_markers.values():
                    if utils.get_probability() >= tp["resistance_probability"]:
                        offset = n.offset
                        s.remove(n)

                        rest = Rest(length=n.duration.quarterLength)
                        rest.addLyric("c")
                        s.insert(offset, rest)


def cure(s: Stream, tp: TherapyParameters):
    start = utils.get_percentile_measure_number(s, tp["start"])
    measures = s.measures(start, None).getElementsByClass("Measure")

    for m in measures:
        if len(m.voices) > 0:
            for nv in m.voices:
                _cure(nv, tp)
        else:
            _cure(m, tp)
        s.makeRests(fillGaps=True, inPlace=True)
    return s


def get_therapy(t: Therapy):
    if t.value == 0:
        return no_therapy
    return cure
