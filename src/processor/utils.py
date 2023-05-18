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
from music21.stream.base import Measure, Part, Voice
from typeguard import typechecked


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
def random_notes(m: Measure) -> Dict[float, List[GeneralNote]]:
    """
    Picks a subset of notes from the measure.

    :param m: The measure to pick a note from.
    :return: A random note from the measure.
    """
    elements = m.flat.notesAndRests
    timing = [el.offset for el in m.flat.notesAndRests]
    start = random.choice(timing)
    offsets = group_by_offset(list(elements))
    trunc = {}
    for off in offsets.keys():
        if off >= start and off <= max(timing):
            trunc[off] = offsets[off]

    return trunc


def get_substring_length(el: List[GeneralNote]) -> float:
    # fails when you have multiple voices...
    return f.reduce(lambda a, b: a + b.duration.quarterLength, el, 0)


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


def get_signs(m: Measure):
    ts = m.getElementsByClass(TimeSignature).first()
    clef = m.getElementsByClass(Clef).first()
    ks = m.getElementsByClass(KeySignature).first()
    return ts, clef, ks


def duplicate_part(p: Part) -> Part:
    """
    Duplicates a part, returning a part with the same length.
    Only saves the time changes throughout the part to match the rest
    of the piece.

    :param p: Part to duplicate.
    :return: A part of the same length with the same time changes.
    """

    dup = Part(Instrument(p.getInstrument().instrumentName))
    measures = p.getElementsByClass("Measure")

    for m in measures:
        dup_m = Measure()
        # replace with music21 function that gets all signs?
        # theoretically, could do get elements by class
        # and just put the classes we want...
        ts, clef, ks = get_signs(m)

        if clef is not None:
            dup_m.append(copy.deepcopy(clef))

        if ks is not None:
            dup_m.append(copy.deepcopy(ks))

        if ts is None:
            ts = m.getContextByClass(TimeSignature)
        else:
            dup_m.append(copy.deepcopy(ts))

        dup_m.number = m.number
        dup_m.append(Rest(length=ts.beatCount))
        dup.append(dup_m)

    return dup


def group_by_offset(els: List[GeneralNote]) -> Dict[float, List[GeneralNote]]:
    d = {}
    for el in els:
        this_off = d.get(el.offset, None)
        if this_off is None:
            d[el.offset] = [el]
        else:
            d[el.offset].append(el)
    return d


def duplicate_note(n: Note):
    dn = Note(nameWithOctave=n.nameWithOctave)
    dn.duration = Duration(n.quarterLength)
    return dn


# different than deepcopy, ensures that we don't copy any voice info
def duplicate_element(el: GeneralNote) -> GeneralNote:
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


def duplicate_measure(measure: Measure, includeNotes=False):
    m = Measure()
    if includeNotes:
        m = copy.deepcopy(measure)
    else:
        # Voices are not generalNotes, so they also need to be excluded
        els = measure.getElementsNotOfClass([GeneralNote, Voice])
        for el in els:
            m.append(el)
    return m


# could be used if chords could have multiple durations...
# doesn't work unfortunately
def clean_measure(m: Measure):
    clean = duplicate_measure(m)
    offsets = group_by_offset(list(m.flat.notesAndRests))

    for offset in offsets.keys():
        els = offsets[offset]

        durations = [el.duration.quarterLength for el in els]

        for el in els:
            dup = duplicate_element(el)
            # if we can make chords have varied durations for notes
            # we solve the issue
            clean.insertIntoNoteOrChord(offset, dup)

        cleaned = clean.getElementsByOffset(offset)

        for c in cleaned:
            if isinstance(c, Chord):
                notes = list(filter(lambda e: not e.isRest, els))
                for i, el in enumerate(notes):
                    c[i].duration = Duration(el.duration.quarterLength)
                # c.duration = Duration(min(durations))

    return clean
