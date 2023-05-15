import pytest
from music21.chord import Chord
from music21.duration import Duration
from music21.note import Note
from music21.stream.base import Measure
from music21.meter.base import TimeSignature
from processor.process import inversion, mutate, subdivide


def assert_expected_length(expected, notes):
    for note in notes:
        assert note.duration.quarterLength == expected


# TODO: implement
def test_replace_rest():
    pass


def test_inversion():
    m = Measure()
    m.append(TimeSignature('4/4'))
    m.append(Note("C", type="quarter"))
    m.append(Note("D", type="quarter"))
    m.append(Note("E", type="quarter"))
    m.append(Note("F", type="quarter"))

    inversion(m, None)

    assert m[1].name == "F"
    assert m[2].name == "E"
    assert m[3].name == "D"
    assert m[4].name == "C"


def test_translocation():
    pass


def test_transposition():
    pass


def test_deletion():
    pass


def test_subdivide_note():
    s = Measure()
    n = Note("C", type="whole")
    expected = n.duration.quarterLength / 2
    s.append(n)
    subdivide(s, n)

    assert_expected_length(expected, s.notes)
    assert s.duration.quarterLength == 4.0


def test_subdivide_chord():
    s = Measure()
    n = Chord("C5 E5 G5", quarterLength=4)
    expected = n.duration.quarterLength / 2
    s.append(n)
    subdivide(s, n)

    assert_expected_length(expected, s.notes)
    assert s.duration.quarterLength == 4.0


@pytest.mark.usefixtures("sample_stream")
def test_mutate(sample_stream):
    mutate(sample_stream)
    sample_stream.write("musicxml", "mutant_twinkle.mxl")


@pytest.mark.usefixtures("finale_stream")
def test_finale_mutate(finale_stream):
    mutate(finale_stream)
    finale_stream.write("musicxml", "mutant_hbd.mxl")


# TODO: add a bunch of test examples to see how well the system holds up
