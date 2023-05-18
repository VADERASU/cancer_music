import copy
import random
from typing import Dict, List, Optional, Union

from music21.chord import Chord
from music21.duration import Duration
from music21.note import GeneralNote, Note, Rest
from music21.stream.base import Measure, Part, Stream
from typeguard import typechecked

from processor import utils


@typechecked
def mutate(s: Stream, how_many: int = 4):
    """
    Main method for mutating a file.

    :param s: Music21 stream for a file.
    """
    parts = s.getElementsByClass("Part")
    p = random.choice(list(parts))

    measures = p.getElementsByClass("Measure")
    start = random.randint(0, len(measures) - how_many)
    tumors = measures[start : start + how_many]

    dup = utils.duplicate_part(p)
    # start adding mutant measures at the first measure
    dpm = dup.getElementsByClass("Measure")[start:]

    for i, dm in enumerate(dpm):
        t = tumors[i % len(tumors)]  # pick tumor measure

        mutation = choose_mutation()
        mutant = mutation(t, p)  # mutate it
        mutant.number = dm.number
        dup.replace(dm, mutant)  # replace in duplicate part

    s.append(dup)


def noop(m: Measure, _: Stream):
    # do not remove, lets us skip performing mutations
    return copy.deepcopy(m)


@typechecked
def insertion(measure: Measure, _: Stream):
    """
    Inserts a note into the measure, either by replacing a rest
    or subdividing an already existing note.

    :param m: Measure to insert a note into.
    :param _: Stream, unused but do not remove.
    """
    # pick a random note or rest
    m = copy.deepcopy(measure)
    s = utils.random_notes(m)
    return subdivide(m, s)


@typechecked
def subdivide(measure: Measure, offsets: Dict[float, List[GeneralNote]]):
    """
    Divides a note or chord in half and duplicates it in place.

    :param m: Measure containing the note or chord.
    :param el: The note or chord to subdivide.
    """
    m = Measure()
    # copy measure except for substring
    for n in measure.notesAndRests:
        if n.offset not in offsets.keys():
            m.insert(n.offset, n)

    off = None
    for offset in offsets.keys():
        els = offsets[offset]

        if off is None:
            off = offset

        lengths = []
        for el in els:
            new_el = utils.subdivide_element(el)
            m.insertIntoNoteOrChord(off, new_el)
            lengths.append(new_el.duration.quarterLength)
        off += min(lengths)

    sub_offset = 0
    for offset in offsets.keys():
        els = offsets[offset]

        lengths = []
        for el in els:
            new_el = utils.subdivide_element(el)
            new_el.addLyric("i")
            m.insertIntoNoteOrChord(off + sub_offset, new_el)
            lengths.append(new_el.duration.quarterLength)

        sub_offset += min(lengths)

    n = utils.get_first_element(m)
    n.addLyric(str(len(offsets.keys())))
    m.makeBeams(inPlace=True)
    return m


@typechecked
def transposition(measure: Measure, _: Stream) -> Measure:
    """
    Transposes the measure by either 1 or -1 half-steps.

    :param m: The measure to transpose.
    :param _: Stream, unused, do not remove.
    """
    options = [-1, 1]
    choice = random.choice(options)
    return transpose_measure(measure, choice)


@typechecked
def transpose_measure(measure: Measure, degree: int) -> Measure:
    transposed = measure.transpose(degree, classFilterList=GeneralNote)
    if transposed is None:
        raise ValueError("Measure does not exist.")
    n = utils.get_first_element(transposed)
    n.addLyric("t")

    return transposed


@typechecked
def deletion(measure: Measure, _: Stream):
    """
    Replaces a random note from the measure with a rest.
    This ensures that the measures are the correct duration.

    :param m: Measure to delete a note from.
    :param _: Stream, unused, do not remove.
    """
    m = copy.deepcopy(measure)
    to_delete = utils.random_notes(m)
    delete_substring(m, to_delete)

    return m


@typechecked
def delete_substring(m: Measure, to_delete: List[GeneralNote]):
    # sum all of the durations up and delete each note
    length = utils.get_substring_length(to_delete)
    rest = Rest(length=length)
    rest.addLyric("d")
    m.insert(to_delete[0].offset, rest)
    for n in to_delete:
        m.remove(n, recurse=True)


# TODO: move these operations to another file, write tests
@typechecked
def translocation(m: Measure, s: Stream):
    # TODO: make sure translocation does not copy final bar line
    measures = list(s.getElementsByClass("Measure"))
    choice = copy.deepcopy(random.choice(measures))
    replace_measure(m, choice, s)
    # first = utils.get_first_element(m)
    # first.addLyric("tl")


@typechecked
def inversion(m: Measure, _: Optional[Stream]):
    measure = copy.deepcopy(m)

    # clear all notes in the measure
    notes = m.flat.notesAndRests

    ts = utils.get_time(m)
    count = ts.beatCount

    for n in notes:
        new_note = utils.duplicate_element(n)
        measure.insertIntoNoteOrChord(
            count - n.offset - n.quarterLength, new_note
        )

    n = utils.get_first_element(measure)
    n.addLyric("inv")

    return measure


@typechecked
def replace_measure(m: Measure, replacement: Measure, s: Stream):
    replacement.number = m.number
    s.replace(m, replacement)
    first = utils.get_first_element(replacement)
    first.addLyric("tl")


def choose_mutation(weights: List[float] = [0.1, 0.5, 0.4]):
    """
    Randomly picks a mutation to perform on a measure.

    :param weights: Weights to pick the mutations with.
    :raises ValueError: Thrown if the weights do not sum to one.
    """

    if sum(weights) != 1.0:
        raise ValueError("Mutation weights do not sum to 1.")

    mutations = [
        noop,
        insertion,
        transposition,
        # deletion,
        # translocation,
        # inversion,
    ]
    # need to return 0th element because random.choices() returns a list
    return random.choices(mutations, weights)[0]
