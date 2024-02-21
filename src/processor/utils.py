import copy
import math
import os
import random
import sys
import uuid
from fractions import Fraction
from pathlib import Path
from typing import List, Optional, Union

from music21.chord import Chord
from music21.duration import Duration
from music21.instrument import Instrument
from music21.key import Key
from music21.meter.base import TimeSignature
from music21.note import GeneralNote, Lyric, Note, Rest
from music21.stream.base import Measure, Part, PartStaff, Stream, Voice, Score
from music21.volume import Volume
from typeguard import typechecked


def reseed(seed: Optional[int] = None):
    if not seed:
        seed = random.randrange(sys.maxsize)
    rng = random.Random(seed)
    print("Seed", seed)
    return rng


@typechecked
def get_time(m: Measure) -> TimeSignature:
    """
    Gets the time signature for a measure.

    :param m: Measure to get time signature for.
    :return: The measure's time signature.
    :raises ValueError: Raised if no time signature exists.
    """
    ts = m.getTimeSignatures()[0]
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
def get_first_element(m: Stream) -> GeneralNote:
    """
    Gets the first note from the stream.

    :param m: The measure to get the first note for.
    :return: The first note in the measure.
    :raises ValueError: Raised if no notes or rests are present in the measure.
    """
    first = m.flat.notesAndRests.first()
    if first is None:
        raise ValueError(f"Error: No notes or rests in measure {m.number}.")
    return first


def add_lyric_for_measure(m: Stream, annotation: str):
    notes = m.flat.notesAndRests
    for n in notes:
        add_lyric_for_note(n, annotation)


def add_lyric_for_note(n: GeneralNote, annotation: str):
    n.lyric = None
    n.addLyric(annotation)


@typechecked
def random_offsets(
    m: Measure, rng: random.Random
) -> List[Union[Fraction, float]]:
    """
    Picks a subset of offsets from the measure.

    :param m: The measure to pick a note from.
    :return: A list of random offsets from the measure.
    """
    timing = list(set([el.offset for el in m.flat.notesAndRests]))
    timing.sort()
    start = rng.randint(0, len(timing) - 1)
    return timing[start:]


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


@typechecked
def duplicate_note(n: Note) -> Note:
    """
    Duplicates a note. Again, need this because copy.deepcopy
    copies over additional unnecessary information.

    :param n: Note to duplicate.
    :return: Copy of note.
    """
    dn = Note(nameWithOctave=n.nameWithOctave)
    dn.duration = Duration(n.quarterLength)
    dn.volume = duplicate_volume(n)
    return dn


def duplicate_volume(n: Union[Chord, Note]) -> Volume:
    if n.volume.velocity is not None:
        return Volume(
            velocity=n.volume.velocity,
            velocityScalar=n.volume.velocityScalar,
            velocityIsRelative=n.volume.velocityIsRelative,
        )
    else:
        # else assume max velocity
        return Volume(velocity=127)


@typechecked
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
        c.duration.quarterLength = el.duration.quarterLength
        c.volume = duplicate_volume(el)
        return c
    elif isinstance(el, Note):
        return duplicate_note(el)
    else:
        return Rest(length=el.duration.quarterLength)


@typechecked
def subdivide_element(el: GeneralNote) -> GeneralNote:
    """
    Subdivides an element. This is necessary because copy.deepcopy
    copies over stream information which leads to weird errors.

    :param el: Element to subdivide.
    :return: A copy of the element with half its duration.
    """
    divided = el.augmentOrDiminish(0.5)
    dup = duplicate_element(el)
    dup.duration.quarterLength = divided.duration.quarterLength
    return dup


@typechecked
def copy_stream_inverse(
    s: Stream, og: Stream, offsets: List[Union[Fraction, float]]
):
    """
    Recursive helper method for copy_inverse.

    :param s: Stream to copy.
    :param og: Original note information.
    :param offsets: List of offsets to avoid copying.
    """
    for n in og.getElementsByClass(GeneralNote):
        if n.offset < min(offsets) or n.offset > max(offsets):
            new_el = duplicate_element(n)
            s.insert(n.offset, new_el)


@typechecked
def copy_inverse(measure: Measure, offsets: List[Union[Fraction, float]]):
    """
    Given a measure and a list of offsets, copies over all notes
    NOT in the offsets list.

    :param measure: Measure to make an inverse copy of.
    :param offsets: List of offsets to not copy.
    :returns: Measure without elements in offsets.
    """
    m = Measure()
    if len(measure.voices) > 0:
        for v in measure.voices:
            nv = Voice()
            copy_stream_inverse(nv, v, offsets)
            m.insert(0, nv)
    else:
        copy_stream_inverse(m, measure, offsets)

    return m


def get_percentile_measure_number(s: Stream, percentile: float):
    length = len(s.getElementsByClass("Measure"))
    return math.floor(percentile * length)

def get_score_length_in_measures(s: Score):
    parts = list(s.getElementsByClass("Part"))
    return max([len(p.getElementsByClass("Measure")) for p in parts])


def slice_part(p, start, end):
        measures = p.getElementsByClass("Measure")

        return list(
            map(
                lambda m: copy_measure(
                    m,
                    ["Instrument"]
                ),
                measures[start : end],
            )
        )
@typechecked
def duplicate_part_keep_measures(p, id, to) -> Part:
    dup = duplicate_part(p, id)
    og = slice_part(p, 0, to)
    region = dup.measures(0, to)
    for old_measure, new_measure in zip(region, og):
        dup.replace(old_measure, new_measure)
    return dup

def copy_measure(
    measure: Measure, dropList: Optional[List[str]] = [], removeLyrics=False
):
    """
    Copies a measure and drops all extraneous information.
    TODO: detect if clef / key signature is necessary when copying.
    Don't drop clefs and key signatures until there is code to make sure
    you don't need it!

    :param measure: Measure to copy.
    :returns: Measure without unnecessary information.
    """
    cloned = copy.deepcopy(measure)
    cloned.removeByClass(["Barline"] + dropList)
    if removeLyrics:
        notes = cloned.flat.notesAndRests
        for n in notes:
            n.lyric = ""
    return cloned


def duplicate_part(p: Union[Part, PartStaff], id) -> Part:
    dup = Part.template(
        p,
        removeClasses=[
            Instrument,
            GeneralNote,
            Lyric,
        ],
        fillWithRests=True,
    )

    p_ins = p.getInstrument()
    if p_ins is not None:
        ins = Instrument(p_ins.instrumentName)
        dup.id = id
        dup.insert(0, ins)
    else:
        raise ValueError(f"Part {p.id} missing an instrument!")
    return dup


def clear_part(p: Part, start) -> Part:
    dup = duplicate_part(p, p.id)

    measures = p.getElementsByClass("Measure")
    dup_measures = dup.getElementsByClass("Measure")

    for i in range(0, start):
        dup.replace(dup_measures[i], measures[i])
    return dup


def consolidate_rests(s: Stream):
    # tricky, need to see what the measures look like with voices
    pass
