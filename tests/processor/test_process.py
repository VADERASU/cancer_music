import pytest
from music21.note import Note, Rest
from music21.stream.base import Measure, Voice

from processor import utils
from processor.parameters import Therapy, TherapyParameters
from processor.process import (
    delete_substring,
    invert_stream,
    mutate,
    subdivide_stream,
    transpose_measure,
)


def test_translocation():
    pass


def test_transposition():
    pass


@pytest.fixture
def sm():
    m = Measure()
    m.append(Note("C", type="quarter"))
    m.append(Note("D", type="quarter"))
    m.append(Note("E", type="quarter"))
    m.append(Note("F", type="quarter"))
    return m


@pytest.fixture
def voiced():
    m = Measure()
    v1 = Voice()
    v1.append(Note("C", type="quarter"))
    v1.append(Note("D", type="quarter"))
    v1.append(Note("E", type="quarter"))
    v1.append(Note("F", type="quarter"))
    v2 = Voice()
    v2.append(Note("G", type="half"))
    v2.append(Note("G", type="half"))
    m.insert(0, v1)
    m.insert(0, v2)
    return m


def test_subdivide_begin(sm):
    offsets = [0.0, 1.0]
    m = utils.copy_inverse(sm, offsets)
    subdivide_stream(m, sm, offsets)

    assert m[0] == Note("C", type="eighth")
    assert m[1] == Note("D", type="eighth")
    assert m[2] == Note("C", type="eighth")
    assert m[3] == Note("D", type="eighth")
    assert m[4] == Note("E", type="quarter")
    assert m[5] == Note("F", type="quarter")


def test_subdivide_voiced(voiced):
    offsets = [0.0, 1.0, 2.0]
    m = utils.copy_inverse(voiced, offsets)
    subdivide_stream(m, voiced, offsets)
    v1 = m.voices[0]
    v2 = m.voices[1]

    assert v1[0] == Note("C", type="eighth")
    assert v1[1] == Note("D", type="eighth")
    assert v1[2] == Note("E", type="eighth")
    assert v1[3] == Note("C", type="eighth")
    assert v1[4] == Note("D", type="eighth")
    assert v1[5] == Note("E", type="eighth")
    assert v1[6] == Note("F", type="quarter")

    assert v2[0] == Note("G", type="quarter")
    assert v2[1] == Note("G", type="quarter")
    assert v2[2] == Note("G", type="quarter")
    assert v2[3] == Note("G", type="quarter")


def test_subdivide_mid(sm):
    offsets = [1.0, 2.0]
    m = utils.copy_inverse(sm, offsets)
    subdivide_stream(m, sm, offsets)
    assert m[0] == Note("C", type="quarter")
    assert m[1] == Note("D", type="eighth")
    assert m[2] == Note("E", type="eighth")
    assert m[3] == Note("D", type="eighth")
    assert m[4] == Note("E", type="eighth")
    assert m[5] == Note("F", type="quarter")


def test_transpose_measure(sm):
    m = transpose_measure(sm, 2)
    assert m[0] == Note("D", type="quarter")
    assert m[1] == Note("E", type="quarter")
    assert m[2] == Note("F#", type="quarter")
    assert m[3] == Note("G", type="quarter")


def test_transpose_voiced(voiced):
    m = transpose_measure(voiced, 2)
    v1 = m.voices[0]
    v2 = m.voices[1]

    assert v1[0] == Note("D", type="quarter")
    assert v1[1] == Note("E", type="quarter")
    assert v1[2] == Note("F#", type="quarter")
    assert v1[3] == Note("G", type="quarter")

    assert v2[0] == Note("A", type="half")
    assert v2[1] == Note("A", type="half")


def test_delete_substring(sm):
    offsets = [0.0, 1.0]
    m = utils.copy_inverse(sm, offsets)
    delete_substring(m, sm, offsets)
    assert m[0] == Rest(type="half")
    assert m[1] == Note("E", type="quarter")
    assert m[2] == Note("F", type="quarter")


def test_delete_substring_voiced(voiced):
    offsets = [0.0, 1.0]
    m = utils.copy_inverse(voiced, offsets)
    delete_substring(m, voiced, offsets)
    v1 = m.voices[0]
    v2 = m.voices[1]

    assert v1[0] == Rest(type="half")
    assert v2[0] == Rest(type="half")


def test_invert_stream(sm):
    offsets = [0.0, 1.0]
    m = utils.copy_inverse(sm, offsets)
    invert_stream(m, sm, offsets)
    assert m[0] == Note("D", type="quarter")
    assert m[1] == Note("C", type="quarter")
    assert m[2] == Note("E", type="quarter")
    assert m[3] == Note("F", type="quarter")


def test_invert_stream_voiced(voiced):
    offsets = [0.0, 1.0]
    m = utils.copy_inverse(voiced, offsets)
    invert_stream(m, voiced, offsets)

    v1 = m.voices[0]
    v2 = m.voices[1]

    assert v1[0] == Note("D", type="quarter")
    assert v1[1] == Note("C", type="quarter")
    assert v1[2] == Note("E", type="quarter")
    assert v1[3] == Note("F", type="quarter")

    assert v2[0] == Note("G", type="half")
    assert v2.offset == 0.0
    assert v2[1] == Note("G", type="half")


@pytest.mark.usefixtures("streams")
def test_mutate(streams):
    for filename, stream in streams:
        mutate(stream)
        for p in stream.parts:
            if p.id == "mutant":
                for m in p.getElementsByClass(Measure):
                    ts = m.getTimeSignatures()[0]
                    assert m.duration.quarterLength == ts.beatCount
        stream.write("musicxml", f"mutant_{filename}")


@pytest.mark.usefixtures("streams")
def test_cure(streams):
    for filename, stream in streams:
        mutate(
            stream,
            therapy_params=TherapyParameters(
                therapy_mode=Therapy.CURED,
                resistance_probability=0.2,
                start=0.5,
            ),
        )
        stream.write("musicxml", f"cured_{filename}")
