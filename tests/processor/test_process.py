import pytest
from music21.chord import Chord
from music21.duration import Duration
from music21.note import Note
from music21.stream.base import Measure

from processor.process import mutate, subdivide


def assert_expected_length(expected, notes):
    for note in notes:
        assert note.duration.quarterLength == expected


# TODO: implement
def test_replace_rest():
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
