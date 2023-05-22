import pytest
from music21 import corpus
from music21.chord import Chord
from music21.duration import Duration
from music21.meter.base import TimeSignature
from music21.note import Note, Rest
from music21.stream.base import Measure

from processor.process import delete_substring, inversion, mutate, subdivide


def assert_expected_length(expected, notes):
    for note in notes:
        assert note.duration.quarterLength == expected


# TODO: implement
def test_replace_rest():
    pass


"""
def test_inversion():
    m = Measure()
    m.append(TimeSignature("4/4"))
    m.append(Note("C", type="quarter"))
    m.append(Note("D", type="quarter"))
    m.append(Note("E", type="quarter"))
    m.append(Note("F", type="quarter"))

    m.show("text")
    inversion(m, None)
    m.show("text")
    assert m[1].name == "F"
    assert m[2].name == "E"
    assert m[3].name == "D"
    assert m[4].name == "C"
"""


def test_translocation():
    pass


def test_transposition():
    pass


"""
def test_delete_substring():
    m = Measure()
    m.repeatAppend(Note("C", type="quarter"), 4)
    to_delete = m[0:2]
    delete_substring(m, to_delete)
    assert m[0].duration.quarterLength == 2
    assert isinstance(m[0], Rest)
    assert m[1].duration.quarterLength == 1
    assert m[2].duration.quarterLength == 1
"""


# measure we use for subdivision testing
@pytest.fixture
def sm():
    m = Measure()
    m.append(Note("C", type="quarter"))
    m.append(Note("D", type="quarter"))
    m.append(Note("E", type="quarter"))
    m.append(Note("F", type="quarter"))
    return m


def test_subdivide_begin(sm):
    m = subdivide(sm, [0.0, 1.0])
    assert m[0] == Note("C", type="eighth")
    assert m[1] == Note("D", type="eighth")
    assert m[2] == Note("C", type="eighth")
    assert m[3] == Note("D", type="eighth")
    assert m[4] == Note("E", type="quarter")
    assert m[5] == Note("F", type="quarter")


def test_subdivide_mid(sm):
    m = subdivide(sm, [1.0, 2.0])
    assert m[0] == Note("C", type="quarter")
    assert m[1] == Note("D", type="eighth")
    assert m[2] == Note("E", type="eighth")
    assert m[3] == Note("D", type="eighth")
    assert m[4] == Note("E", type="eighth")
    assert m[5] == Note("F", type="quarter")


# TODO: add test with voices and chords


# TODO: make this test compare the new measure
# with the original
@pytest.mark.usefixtures("streams")
def test_mutate(streams):
    for filename, stream in streams:
        part, mutant = mutate(stream)

        # og = part.getElementsByClass("Measure")
        # mutants = mutant.getElementsByClass("Measure")

        # for o, m in zip(og, mutants):
        # every measure should be the exact same length
        # assert o.duration.quarterLength == m.duration.quarterLength

        stream.write("musicxml", f"mutant_{filename}")
