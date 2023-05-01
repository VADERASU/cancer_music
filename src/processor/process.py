import random

from music21.note import Note
from music21.duration import Duration
from music21.stream.base import Stream


def mutate(s: Stream):
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
            mutation = choose_mutation()
            mutation(m)
    s.write("musicxml", "complete.mxl")


# do not remove, lets us skip performing mutations
def noop(_):
    pass


def subdivide(measure, note):
    # cut the note in half to make room for the new one
    note.augmentOrDiminish(0.5, inPlace=True)
    # figure out where the next note will be
    offset = note.offset + note.duration.quarterLength
    # insert at new location with the same pitch and length
    # as the note we subdivided
    new_note = Note(note.name)
    new_note.duration = Duration(note.duration.quarterLength)
    measure.insert(offset, new_note)


def replace_rest(measure, rest):
    # figure out how to replace a rest with a note
    pass


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
