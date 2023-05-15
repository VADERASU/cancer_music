import copy
import random
from typing import Union, Optional

from music21.chord import Chord
from music21.duration import Duration
from music21.note import GeneralNote, Note, Rest
from music21.stream.base import Measure, Stream
from typeguard import typechecked

from processor import utils


@typechecked
def mutate(s: Stream):
    """
    Main method for mutating a file.

    :param s: Music21 stream for a file.
    """
    parts = s.getElementsByClass("Part")
    # TODO: can use measureOffsetMap
    # can iterate through multiple measures this way
    for p in parts:
        measures = p.getElementsByClass("Measure")
        for m in measures:
            utils.correct_measure(m)
            mutation = choose_mutation()
            mutation(m, p)

    s.makeNotation(inPlace=True)


def noop(_: Measure, __: Stream):
    # do not remove, lets us skip performing mutations
    pass


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
    measure.makeBeams(inPlace=True)  # cleans up notation


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
    # replace measure with another random measure
    measures = list(s.getElementsByClass("Measure"))
    choice = copy.deepcopy(random.choice(measures))
    replace_measure(m, choice, s)


@typechecked
def inversion(m: Measure, _: Optional[Stream]):
    notes = m.flat.notesAndRests
    print("------old------")
    m.show("text")
    ts = utils.get_time(m)
    count = ts.beatCount
    for n in notes:
        new_note = copy.deepcopy(n)
        m.insert(count - n.offset - n.quarterLength, new_note)
        m.remove(n, recurse=True)
    print("-----new------")
    m.show("text")
    n = utils.get_first_element(m)
    n.addLyric("inv")


@typechecked
def transpose_measure(measure: Measure, degree: int):
    n = utils.get_first_element(measure)
    n.addLyric("t")
    measure.transpose(degree, inPlace=True, classFilterList=GeneralNote)


@typechecked
def delete_note(m: Measure, n: GeneralNote):
    rest = Rest(length=n.duration.quarterLength)
    rest.addLyric("d")
    m.insert(n.offset, rest)
    m.remove(n, recurse=True)


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
    # TODO: write generate_random_note in utils
    n = Note()
    n.addLyric("r")
    n.duration = Duration(r.duration.quarterLength)
    m.insertIntoNoteOrChord(r.offset, n)


def choose_mutation():
    """
    Randomly picks a mutation to perform on a measure.
    """
    # TODO: choice should be made from a set of probabilities
    # instead of each mutation being equally likely
    mutations = [
        noop,
        insertion,
        transposition,
        deletion,
        translocation,
        inversion,
    ]
    return random.choice(mutations)
