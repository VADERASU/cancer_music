import pytest
from music21.chord import Chord
from music21.duration import Duration
from music21.note import Note
from music21.stream.base import Stream

from processor.process import mutate, subdivide


def assert_expected_length(expected, notes):
    for note in notes:
        assert note.duration.quarterLength == expected


# should tie the two notes together, a bit tricky
# quarter note becomes two eighth notes with bar between them
def test_subdivide_q_note():
    pass


# should split one eighth note and tie both eighth notes
# to new notes
def test_subdivide_e_note():
    pass


def test_subdivide_w_note():
    s = Stream()
    n = Note("C", type="whole")
    expected = n.duration.quarterLength / 2
    s.append(n)
    subdivide(s, n)

    assert_expected_length(expected, s.notes)
    assert s.duration.quarterLength == 4.0


def test_subdivide_chord():
    s = Stream()
    n = Chord("C5 E5 G5", quarterLength=4)
    expected = n.duration.quarterLength / 2
    s.append(n)
    subdivide(s, n)

    assert_expected_length(expected, s.notes)
    assert s.duration.quarterLength == 4.0


@pytest.mark.usefixtures("sample_stream")
def test_mutate(sample_stream):
    s = mutate(sample_stream)
    s.write("musicxml", "complete.mxl")
