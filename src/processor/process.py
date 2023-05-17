import copy
import random
from itertools import cycle
from typing import List, Optional, Union

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
    choice = utils.random_note(measure)
    if isinstance(choice, Rest):
        replace_rest(measure, choice)
    else:
        subdivide(measure, choice)


@typechecked
def transposition(measure: Measure, _: Stream):
    """
    Transposes the measure by either 1 or -1 half-steps.

    :param m: The measure to transpose.
    :param _: Stream, unused, do not remove.
    """
    # TODO: transpose both parts at once?
    options = [-1, 1]
    choice = random.choice(options)
    transpose_measure(measure, choice)


@typechecked
def deletion(measure: Measure, _: Stream):
    """
    Replaces a random note from the measure with a rest.
    This ensures that the measures are the correct duration.

    :param m: Measure to delete a note from.
    :param _: Stream, unused, do not remove.
    """
    choice = utils.random_note(measure)
    delete_note(measure, choice)


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
def transpose_measure(measure: Measure, degree: int):
    n = utils.get_first_element(measure)
    n.addLyric("t")
    measure.transpose(degree, inPlace=True, classFilterList=GeneralNote)


@typechecked
def delete_note(m: Measure, n: GeneralNote):
    measure = copy.deepcopy(m)

    rest = Rest(length=n.duration.quarterLength)
    rest.addLyric("d")

    measure.insert(n.offset, rest)
    measure.remove(n, recurse=True)

    return measure


@typechecked
def replace_measure(m: Measure, replacement: Measure, s: Stream):
    replacement.number = m.number
    s.replace(m, replacement)
    first = utils.get_first_element(replacement)
    first.addLyric("tl")


@typechecked
def subdivide(m: Measure, el: Union[Note, Chord]):
    """
    Divides a note or chord in half and duplicates it in place.

    :param m: Measure containing the note or chord.
    :param el: The note or chord to subdivide.
    """
    # TODO: cannot divide to less than 2048th
    # cut the note in half to make room for the new one
    el.augmentOrDiminish(0.5, inPlace=True)
    # figure out where the next note will be
    off = el.offset + el.duration.quarterLength
    # insert at new location with the same pitch and length
    new_el = utils.duplicate_element(el)
    new_el.addLyric("i")
    new_el.duration = Duration(el.duration.quarterLength)
    # offset is number of quarter notes from beginning of measure
    m.insertIntoNoteOrChord(off, new_el)


@typechecked
def replace_rest(m: Measure, r: Rest):
    """
    Replaces a rest with a random note.

    :param m: The measure containing the rest.
    :param r: The rest to replace.
    """
    n = utils.generate_note(utils.get_key(m))
    n.addLyric("r")
    n.duration = Duration(r.duration.quarterLength)
    m.insertIntoNoteOrChord(r.offset, n)


def choose_mutation(weights: List[float] = [1.0]):
    """
    Randomly picks a mutation to perform on a measure.

    :param weights: Weights to pick the mutations with.
    :raises ValueError: Thrown if the weights do not sum to one.
    """

    if sum(weights) != 1.0:
        raise ValueError("Mutation weights do not sum to 1.")

    mutations = [
        noop,
        # insertion,
        # transposition,
        # deletion,
        # translocation,
        # inversion,
    ]
    # need to return 0th element because random.choices() returns a list
    return random.choices(mutations, weights)[0]
