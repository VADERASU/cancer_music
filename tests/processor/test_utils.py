from music21.chord import Chord
from music21.clef import BassClef, TrebleClef
from music21.key import Key, KeySignature
from music21.meter.base import TimeSignature
from music21.note import GeneralNote, Note, Rest
from music21.stream.base import Measure, Part

from processor import utils


def test_duplicate_part():
    p = Part()
    # four measures, two in 4/4 and two in 3/4
    m1 = Measure()
    m1.append(TimeSignature("4/4"))
    m1.repeatAppend(Note("C", quarterLength=1), 4)
    p.append(m1)

    # this measure switches to bass clef
    m2 = Measure()
    m2.append(BassClef())
    m2.repeatAppend(Note("C", quarterLength=1), 4)
    p.append(m2)

    m3 = Measure()
    m3.append(TimeSignature("3/4"))
    m3.repeatAppend(Note("C", quarterLength=1), 3)
    p.append(m3)

    # this measure switches back to treble clef
    # and changes the key signature to one sharp
    m4 = Measure()
    m4.append(TrebleClef())
    m4.append(KeySignature(sharps=1))
    m4.repeatAppend(Note("C", quarterLength=1), 3)
    p.append(m4)

    dup = utils.duplicate_part(p)
    measures = dup.getElementsByClass("Measure")

    assert isinstance(measures[0][0], TimeSignature)
    assert isinstance(measures[1][0], BassClef)
    assert isinstance(measures[2][0], TimeSignature)
    assert isinstance(measures[3][0], TrebleClef)
    assert isinstance(measures[3][1], KeySignature)
    assert measures[0].duration.quarterLength == 4
    assert measures[1].duration.quarterLength == 4
    assert measures[2].duration.quarterLength == 3
    assert measures[3].duration.quarterLength == 3
