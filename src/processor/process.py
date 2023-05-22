import copy
import random
from typing import Dict, List, Optional, Union

from music21.chord import Chord
from music21.duration import Duration
from music21.instrument import Instrument
from music21.note import GeneralNote, Note, Rest
from music21.stream.base import Measure, Part, Stream, Voice
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

    dup = Stream.template(
        p,
        removeClasses=[Instrument, GeneralNote, "Dynamic", "Expression"],
        fillWithRests=True,
    )
    dup.insert(0, Instrument(p.getInstrument().instrumentName))
    # start adding mutant measures at the first measure
    dpm = dup.getElementsByClass("Measure")[start:]

    for i, dm in enumerate(dpm):
        t = tumors[i % len(tumors)]  # pick tumor measure
        # each mutation should be equal length to its original measure
        mutation = choose_mutation()
        mutant = mutation(t, p)  # mutate it
        mutant.number = dm.number
        mutant.makeBeams(inPlace=True)
        dup.replace(dm, mutant)  # replace in duplicate part

    dup.id = "mutant"
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
    s = utils.random_offsets(measure)
    m = subdivide(measure, s)
    n = utils.get_first_element(m)
    n.addLyric("ins")

    return m


@typechecked
def subdivide(measure: Measure, offsets: List[float]):
    """
    Divides a note or chord in half and duplicates it in place.

    :param m: Measure containing the note or chord.
    :param el: The note or chord to subdivide.
    """
    m = utils.copy_inverse(measure, offsets)
    subdivide_stream(m, measure, offsets)

    return m


def subdivide_stream(s: Stream, og: Stream, offsets: List[float]):
    """
    Takes a stream to modify, a stream containing the relevant info,
    and a list of offsets. Subdivides the elements specifed in
    offsets and then makes a copy of the passage in the empty
    space left by the offsets.

    :param s: Stream to modify.
    :param og: Stream containing note information.
    :param offsets: The offsets to modify.
    """
    # TODO: make this more general
    # find all child streams and recurse over them
    if len(og.voices) > 0:
        for i, v in enumerate(og.voices):
            nv = s.voices[i]
            subdivide_stream(nv, v, offsets)
    else:
        off = None
        for offset in offsets:
            el = (
                og.getElementsByOffset(offset)
                .getElementsByClass(GeneralNote)
                .first()
            )

            if el is not None:
                new_el = utils.subdivide_element(el)
                if off is None:
                    off = el.offset

                s.insert(off, new_el)
                off += new_el.duration.quarterLength

        sub_offset = 0
        for offset in offsets:
            el = (
                og.getElementsByOffset(offset)
                .getElementsByClass(GeneralNote)
                .first()
            )
            if el is not None:
                new_el = utils.subdivide_element(el)
                new_el.addLyric("i")
                s.insert(off + sub_offset, new_el)
                sub_offset += new_el.duration.quarterLength


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
    offsets = utils.random_offsets(measure)
    m = utils.copy_inverse(measure, offsets)
    delete_substring(m, measure, offsets)
    n = utils.get_first_element(m)
    n.addLyric("del")

    return m


@typechecked
def delete_substring(s: Stream, og: Stream, offsets: List[float]):
    if len(og.voices) > 0:
        for i, v in enumerate(og.voices):
            nv = s.voices[i]
            delete_substring(nv, v, offsets)
    else:
        el = og.getElementAtOrBefore(max(offsets), [GeneralNote])
        rest = Rest(
            length=el.offset - min(offsets) + el.duration.quarterLength
        )
        rest.addLyric("d")
        s.insert(min(offsets), rest)


@typechecked
def translocation(_: Measure, s: Stream):
    measures = list(s.getElementsByClass("Measure"))
    choice = copy.deepcopy(random.choice(measures))
    first = utils.get_first_element(choice)
    first.addLyric("tl")
    return choice


@typechecked
def inversion(measure: Measure, _: Optional[Stream]):
    offsets = utils.random_offsets(measure)
    m = utils.copy_inverse(measure, offsets)
    invert_stream(m, measure, offsets)
    n = utils.get_first_element(m)
    n.addLyric("inv")

    return m


def invert_stream(s: Stream, og: Stream, offsets: List[float]):
    if len(og.voices) > 0:
        for i, v in enumerate(og.voices):
            nv = s.voices[i]
            invert_stream(nv, v, offsets)
    else:
        notes = list(
            filter(
                lambda e: e is not None,
                map(
                    lambda o: og.getElementsByOffset(o)
                    .getElementsByClass(GeneralNote)
                    .first(),
                    offsets,
                ),
            )
        )
        if len(notes) > 0:
            off = notes[0].offset
            notes.reverse()
            for el in notes:
                new_el = utils.duplicate_element(el)
                new_el.addLyric(str(el.offset))
                s.insert(off, new_el)
                off += new_el.duration.quarterLength


# [0.2, 0.2, 0.1, 0.25, 0.05, 0.2]
def choose_mutation(weights: List[float] = [0.2, 0.0, 0.0, 0.0, 0.0, 0.8]):
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
        deletion,
        translocation,
        inversion,
    ]
    # need to return 0th element because random.choices() returns a list
    return random.choices(mutations, weights)[0]
