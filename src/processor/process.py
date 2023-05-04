import random
from typing import Union

from music21.chord import Chord
from music21.duration import Duration
from music21.note import Note, Rest
from music21.stream.base import Measure, Stream
from typeguard import typechecked

from processor import utils


@typechecked
def mutate(s: Stream):
    """
    Main method for mutating a file.

    :param s: Music21 stream containing information about the file to mutate.
    """
    parts = s.getElementsByClass("Part")
    # TODO: can use measureOffsetMap
    # can iterate through multiple measures this way
    for p in parts:
        measures = p.getElementsByClass("Measure")
        for m in measures:
            utils.correct_measure(m)
            mutation = choose_mutation()
            mutation(m)

    s.makeNotation(inPlace=True)


def noop(_: Stream):
    # do not remove, lets us skip performing mutations
    pass


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
def subdivide(measure: Measure, element: Union[Note, Chord]):
    """
    Divides a GeneralNote in half and duplicates it in place.

    :param measure: Measure containing the note or chord.
    :param element: The note or chord to subdivide.
    """
    # cut the note in half to make room for the new one
    element.augmentOrDiminish(0.5, inPlace=True)
    # figure out where the next note will be
    offset = element.offset + element.duration.quarterLength
    # insert at new location with the same pitch and length
    new_note = duplicate_element(element)
    new_note.addLyric("i")
    new_note.duration = Duration(element.duration.quarterLength)
    # offset is number of quarter notes from beginning of measure
    measure.insertIntoNoteOrChord(offset, new_note)


@typechecked
def replace_rest(measure: Measure, element: Rest):
    """
    Replaces a rest with a random note.

    :param measure: The measure containing the rest.
    :param element: The rest to replace.
    """
    # TODO: write a function that returns a random pitch and use it here
    new_note = Note()
    new_note.addLyric("r")
    new_note.duration = Duration(element.duration.quarterLength)
    measure.insertIntoNoteOrChord(element.offset, new_note)


@typechecked
def insertion(measure: Measure):
    """
    Inserts a note into the measure, either by replacing a rest
    or subdividing an already existing note.

    :param measure: Measure to insert a note into.
    """
    # pick a random note or rest
    elements = list(measure.flat.notesAndRests)
    choice = random.choice(elements)
    if isinstance(choice, Rest):
        replace_rest(measure, choice)
    else:
        subdivide(measure, choice)
    measure.makeBeams(inPlace=True)  # cleans up notation


def choose_mutation():
    """
    Randomly picks a mutation to perform on a measure.

    """
    mutations = [noop, insertion]
    return random.choice(mutations)
