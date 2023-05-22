import copy
import functools as f
import os
import random
from pathlib import Path
from typing import Dict, List, Union

from music21.chord import Chord
from music21.clef import Clef
from music21.duration import Duration
from music21.instrument import Instrument
from music21.key import Key, KeySignature
from music21.meter.base import TimeSignature
from music21.note import GeneralNote, Note, Rest
from music21.stream.base import Measure, Part, Stream, Voice
from typeguard import typechecked

OffsetDict = Dict[float, List[GeneralNote]]


@typechecked
def get_time(m: Measure) -> TimeSignature:
    """
    Gets the time signature for a measure.

    :param m: Measure to get time signature for.
    :return: The measure's time signature.
    :raises ValueError: Raised if no time signature exists.
    """
    note = get_first_element(m)
    ts = note.getContextByClass("TimeSignature")
    if isinstance(ts, TimeSignature):
        return ts
    else:
        raise ValueError(f"No time signature found for measure {m.number}.")


@typechecked
def get_key(m: Measure) -> Key:
    """
    Gets the key of the measure. If none is found, returns C major.

    :param m: Measure to get the key for.
    :return: Key signature of the measure.
    """
    note = get_first_element(m)
    # can get key with stream.analyze('key')
    # could use this on the entire stream,
    # but keep in mind keys can change in the middle of a piece
    key = note.getContextByClass("Key")
    if isinstance(key, Key):
        return key
    else:
        return Key("C")


@typechecked
def get_first_element(m: Measure) -> GeneralNote:
    """
    Gets the first note from the measure.

    :param m: The measure to get the first note for.
    :return: The first note in the measure.
    :raises ValueError: Raised if no notes or rests are present in the measure.
    """
    first = m.flat.notesAndRests.first()
    if first is None:
        raise ValueError(f"Error: No notes or rests in measure {m.number}.")
    return first


@typechecked
def correct_measure(m: Measure):
    """
    Preprocessing step for a measure. Ensures that its length is equal to
    the time signature's length by deleting extraneous
    elements. Modifies the measure in place.

    :param m: Measure to modify.
    :raises ValueError: Raised if the measure is too short.
    """

    # TODO: Add a check to see if a measure is an anacrusis
    # https://en.wikipedia.org/wiki/Anacrusis
    ts = get_time(m)
    length = m.duration.quarterLength
    if length != ts.beatCount:
        if length > ts.beatCount:
            too_long = m.flatten().getElementsByOffset(ts.beatCount)
            for el in too_long.notesAndRests:
                m.remove(el, recurse=True)
        else:
            # TODO: implement fix for measures that are too short
            raise ValueError(
                f"Error: Measure {m.number} too short! Is {length}, should be {ts.beatCount}."
            )


@typechecked
def random_offsets(m: Measure) -> List[float]:
    """
    Picks a subset of offsets from the measure.

    :param m: The measure to pick a note from.
    :return: A random note from the measure.
    """
    timing = list(set([el.offset for el in m.flat.notesAndRests]))
    timing.sort()
    start = random.randint(0, len(timing) - 1)
    return timing[start:]


def get_substring_length(offsets: OffsetDict) -> float:
    total = 0
    for off in offsets.keys():
        durations = [el.duration.quarterLength for el in offsets[off]]
        total += min(durations)
    return total


@typechecked
def build_file_path(path: Union[Path, str]) -> Path:
    """
    Builds an absolute path from a string.

    :param path: The name of the path.
    :raises ValueError: If the path was empty.
    """
    if path == "":
        raise ValueError("Specified path was empty.")

    fp = Path(os.path.abspath(path))
    if not fp.exists():
        raise FileNotFoundError(f"{fp} does not exist.")

    if not fp.is_file():
        raise ValueError(f"{fp} is not a file.")

    return fp


def generate_note(key: Key = Key("C")):
    """
    Generates a random note from the optionally provided key.
    Assumes key is C major by default.

    :param key: Key to generate notes from.
    :returns: Note picked from the scale.
    """
    degree = random.randint(0, 7)
    p = key.pitchFromDegree(degree)
    return Note(p)


def reverse(m: Measure):
    """
    Returns the notes in a measure in reverse order.

    :param m: The measure to get the notes from.
    """
    notes = m.notesAndRests
    el = []
    for n in notes:
        el.insert(0, n)
    return el


def duplicate_note(n: Note):
    dn = Note(nameWithOctave=n.nameWithOctave)
    dn.duration = Duration(n.quarterLength)
    return dn


def duplicate_element(el: GeneralNote) -> GeneralNote:
    """
    Duplicates a GeneralNote. Different than copy.deepcopy,
    as it ensures that we remove all stream information from the element.

    :param el: The element to copy.
    :return: A stream-free copy of the element.
    """
    if isinstance(el, Chord):
        c = Chord()
        for n in el.notes:
            c.add(duplicate_note(n))
        return c
    elif isinstance(el, Note):
        return duplicate_note(el)
    else:
        return Rest(length=el.duration.quarterLength)


# need to do this because notes are heavily coupled with streams
def subdivide_element(el: GeneralNote) -> GeneralNote:
    divided = el.augmentOrDiminish(0.5)
    dup = duplicate_element(el)
    dup.duration.quarterLength = divided.duration.quarterLength
    return dup


def copy_stream_inverse(s: Stream, og: Stream, offsets):
    for n in og.getElementsByClass(GeneralNote):
        if n.offset < min(offsets) or n.offset > max(offsets):
            new_el = duplicate_element(n)
            s.insert(n.offset, new_el)


def copy_inverse(measure, offsets):
    m = Measure()
    if len(measure.voices) > 0:
        for v in measure.voices:
            nv = Voice()
            copy_stream_inverse(nv, v, offsets)
            m.insert(0, nv)
    else:
        copy_stream_inverse(m, measure, offsets)

    return m
