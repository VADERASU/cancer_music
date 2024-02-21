import random
from random import randint

import pytest
from music21.chord import Chord
from music21.clef import BassClef, TrebleClef
from music21.key import Key, KeySignature
from music21.meter.base import TimeSignature
from music21.note import GeneralNote, Note, Rest
from music21.stream.base import Measure, Part, Score

from processor import utils


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


@pytest.fixture
def s_stream():
    mes = [Measure() for _ in range(0, 5)]
    s = Part()
    [s.append(m) for m in mes]
    return s


@pytest.fixture
def s_score():
    s = Score()
    for i in range(1, 4):
        mes = [Measure() for _ in range(i)]
        p = Part()
        [p.append(m) for m in mes]
        s.append(p)
    return s


def test_get_length_score(s_score):
    num = utils.get_score_length_in_measures(s_score)
    assert num == 3


def test_choice_for_slices():
    rng = random.Random(12345)
    v = utils.choose_for_slices(5, 23, 4, rng)
    assert v == [8, 9, 15, 19]


def test_get_percentile_measure_number(s_stream):
    num = utils.get_percentile_measure_number(s_stream, 0.5)
    assert num == 2
