import os
import random
from pathlib import Path
from typing import Union

from music21.chord import Chord
from music21.meter.base import TimeSignature
from music21.note import GeneralNote, Note
from music21.stream.base import Measure
from typeguard import typechecked


@typechecked
def get_time(m: Measure) -> TimeSignature:
    note = get_first_element(m)
    ts = note.getContextByClass("TimeSignature")
    if isinstance(ts, TimeSignature):
        return ts
    else:
        raise ValueError(f"No time signature found for measure {m.number}.")


@typechecked
def get_first_element(m: Measure) -> GeneralNote:
    notes = m.flat.notesAndRests
    if len(notes) == 0:
        raise ValueError(f"Error: No notes or rests in measure {m.number}.")
    return notes[0]


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
def duplicate_element(el: Union[Note, Chord]):
    """
    Duplicates a chord or note.

    :param el: The chord or note to duplicate.
    """
    if isinstance(el, Chord):
        c = Chord()
        for n in el.notes:
            c.add(Note(nameWithOctave=n.nameWithOctave))
        return c
    else:
        return Note(nameWithOctave=el.nameWithOctave)


@typechecked
def random_note(m: Measure) -> GeneralNote:
    elements = m.flat.notesAndRests
    return random.choice(elements)


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


def generate_random_note():
    raise NotImplementedError()


def reverse(m: Measure):
    notes = m.notesAndRests
    el = []
    for n in notes:
        el.insert(0, n)
    return el
