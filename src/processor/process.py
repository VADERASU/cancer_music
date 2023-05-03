import random

from music21.chord import Chord
from music21.duration import Duration
from music21.note import Note
from music21.stream.base import Stream


def correct_measure(m):
    # create chords if notes occur at the same time
    # remove rests if a note occurs at the same time

    return m


def mutate(s: Stream):
    # print(s.metadata.software)

    # a stream has seperate instruments
    # measures (1st measure contains info like time and key)
    # voice seperating notes in chords
    # two seperate staffs depending on the piece...
    # staff group object that helps identify what staffs go with what
    piece = s.flatten(retainContainers=True)
    # allMeasures = piece.getElementsByClass("Measure")
    # for m in allMeasures:
    #    print(m.parts)
    parts = piece.getElementsByClass("Part")
    # do we treat lh / rh piano as seperate parts? for now yes
    for p in parts:
        measures = p.getElementsByClass("Measure")
        for m in measures:
            correct_measure(m)
            mutation = choose_mutation()
            mutation(m)
    s.makeNotation()
    return s


# do not remove, lets us skip performing mutations
def noop(_):
    pass


def duplicate_element(el):
    if el.isChord:
        c = Chord()
        for n in el.notes:
            c.add(Note(nameWithOctave=n.nameWithOctave))
        return c
    else:
        return Note(nameWithOctave=el.nameWithOctave)


def subdivide(measure, element):
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
    measure.makeBeams(inPlace=True)


def replace_rest(measure, rest):
    new_note = Note()
    new_note.addLyric("r")
    new_note.duration = Duration(rest.duration.quarterLength)
    measure.insertIntoNoteOrChord(rest.offset, new_note)


def insertion(measure):
    """
    Inserts a note into the measure, either by replacing a rest
    or subdividing an already existing note.

    :param measure: [TODO:description]
    """
    # pick a random note or rest
    elements = list(measure.flat.notesAndRests)
    choice = random.choice(elements)
    if choice.isRest:
        replace_rest(measure, choice)
    else:
        subdivide(measure, choice)


def choose_mutation():
    mutations = [noop, insertion]
    return random.choice(mutations)
