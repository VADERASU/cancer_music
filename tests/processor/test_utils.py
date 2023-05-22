import pytest
from music21.chord import Chord
from music21.clef import BassClef, TrebleClef
from music21.key import Key, KeySignature
from music21.meter.base import TimeSignature
from music21.note import GeneralNote, Note, Rest
from music21.stream.base import Measure, Part

from processor import utils


def clean_measure_voiced():
    pass


def clean_measure_clean():
    pass


@pytest.fixture
def mes():
    m = Measure()
    m.append(Note("C", type="quarter"))
    m.append(Note("C", type="quarter"))
    m.append(Note("C", type="quarter"))
    m.append(Note("C", type="quarter"))
    return m


def test_copy_stream_inverse_first(mes):
    m = Measure()
    utils.copy_stream_inverse(m, mes, [0.0])

    assert len(m) == 3
    assert m[0].offset == 1.0
    assert m[1].offset == 2.0
    assert m[2].offset == 3.0


def test_copy_stream_inverse_mid(mes):
    m = Measure()
    utils.copy_stream_inverse(m, mes, [1.0, 2.0])

    assert len(m) == 2
    assert m[0].offset == 0.0
    assert m[1].offset == 3.0


def test_copy_stream_inverse_last(mes):
    m = Measure()
    utils.copy_stream_inverse(m, mes, [3.0])

    assert len(m) == 3
    assert m[0].offset == 0.0
    assert m[1].offset == 1.0
    assert m[2].offset == 2.0


def test_copy_stream_inverse_whole(mes):
    m = Measure()
    utils.copy_stream_inverse(m, mes, [0.0, 3.0])

    assert len(m) == 0
