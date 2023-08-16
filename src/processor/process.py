import math
import random
import sys
from fractions import Fraction
from typing import List, Optional, Union

from music21.note import GeneralNote, Rest
from music21.stream.base import Measure, Part, Stream
from typeguard import typechecked

from processor import utils
from processor.parameters import Parameters, Therapy, TherapyParameters
from processor.therapy import cure


@typechecked
def mutate(
    s: Stream,
    params: Parameters = Parameters(
        how_many=4,
        max_parts=4,
        reproduction=0.1,
        noop=0.2,
        insertion=0.2,
        transposition=0.1,
        deletion=0.25,
        translocation=0.05,
        inversion=0.2,
        start=0.1,
    ),
    t_params: TherapyParameters = TherapyParameters(
        therapy_mode=Therapy.OFF, mutant_survival=0.0, start=0.0
    ),
    seed: int = random.randrange(sys.maxsize),
):
    """
    Main method for mutating a file.

    :param s: Music21 stream for a file.
    """
    parts = s.getElementsByClass("Part")
    rng = utils.reseed(seed)

    mutants = []
    # possibility of multiple parts being chosen
    candidates = rng.sample(parts, rng.randint(1, len(parts)))
    for i, candidate in enumerate(candidates):
        start = utils.get_percentile_measure_number(candidate, params["start"])
        mutants.extend(
            mutate_part(candidate, [], rng, params, start, 0, str(i))
        )

        f = utils.get_first_element(candidate.getElementsByClass("Measure")[0])
        f.addLyric(i)

        # clear the rest of the part
        cleared = utils.clear_part(candidate, start)
        s.replace(candidate, cleared)

    if t_params["therapy_mode"] == Therapy.CURE:
        t_start = utils.get_percentile_measure_number(
            parts[0], t_params["start"]
        )
        dead = rng.sample(
            mutants,
            int(len(mutants) * (1 - t_params["mutant_survival"])),
        )
        deadIDs = list(map(lambda e: e.partId, dead))
        # don't apply treatment to mutants not in dead
        treated = [
            mutant for mutant in mutants if mutant.partId not in deadIDs
        ]
        for mutant in dead:
            treated.append(cure(mutant, t_start))
        [s.append(mutant) for mutant in treated]
    else:
        [s.append(mutant) for mutant in mutants]


def mutate_part(
    p: Part,
    mutants: List[Part],
    rng: random.Random,
    params: Parameters,
    prev_start: int,
    offset: int,
    parentID: str,
    thisID: str = "0",
    mutate_parent: bool = False,
) -> List[Part]:
    if len(mutants) < params["max_parts"]:
        measures = p.getElementsByClass("Measure")

        tumors = list(
            map(
                lambda m: utils.copy_measure(
                    m,
                    ["Clef", "KeySignature", "TimeSignature"],
                    removeLyrics=True,
                ),
                measures[prev_start : prev_start + params["how_many"]],
            )
        )

        # early exit if we're at the end
        if len(tumors) < params["how_many"]:
            return mutants

        dup = utils.duplicate_part(p)
        dpm = dup.getElementsByClass("Measure")[prev_start + offset :]

        to_duplicate = []
        for i in range(0, len(dpm), params["how_many"]):
            dms = dpm[i : i + params["how_many"]]
            # choose one of how_many to be the mutant
            candidate = rng.choice([k for k in range(0, params["how_many"])])
            for j, dm in enumerate(dms):
                t = tumors[(i + j) % len(tumors)]
                if j == candidate:
                    mutation = choose_mutation(
                        rng,
                        [
                            params["noop"],
                            params["insertion"],
                            params["transposition"],
                            params["deletion"],
                            params["translocation"],
                            params["inversion"],
                        ],
                    )
                else:
                    mutation = noop
                mutant = mutation(t, rng, p)  # mutate it
                mutant.number = dm.number
                mutant.makeBeams(inPlace=True)
                dup.replace(dm, mutant)  # replace in duplicate part

                # update tumor
                tumors[(i + j) % len(tumors)] = mutant
                # check if we will reproduce this measure or not
                if rng.random() < params["reproduction"]:
                    to_duplicate.append(prev_start + params["how_many"] + i)

        id = f"{parentID}.{thisID}"
        # mark ancestry
        f = utils.get_first_element(dup.getElementsByClass("Measure")[0])
        f.addLyric(id)

        mutants.append(dup)
        for i, child in enumerate(to_duplicate):
            mutate_part(
                dup,
                mutants,
                rng,
                params,
                child,
                rng.randint(1, params["how_many"]),
                id,
                str(i),
                True,
            )
        dup.makeBeams(inPlace=True)

        if mutate_parent:
            tumors = measures[prev_start : prev_start + params["how_many"]]
            candidate = rng.choice(tumors)
            mutation = choose_mutation(
                rng,
                [
                    params["noop"],
                    params["insertion"],
                    params["transposition"],
                    params["deletion"],
                    params["translocation"],
                    params["inversion"],
                ],
            )
            mutant = mutation(candidate, rng, p)  # mutate it
            mutant.makeBeams(inPlace=True)
            p.replace(candidate, mutant)

    return mutants


def noop(m: Measure, __: random.Random, _: Stream):
    return utils.copy_measure(m)


@typechecked
def insertion(measure: Measure, rng: random.Random, _: Optional[Stream]):
    """
    Inserts a note into the measure, either by replacing a rest
    or subdividing an already existing note.

    :param m: Measure to insert a note into.
    :param _: Stream, unused but do not remove.
    """
    offsets = utils.random_offsets(measure, rng)
    m = utils.copy_inverse(measure, offsets)

    subdivide_stream(m, measure, offsets)
    # n = utils.get_first_element(m)
    # n.addLyric("ins")

    return m


@typechecked
def subdivide_stream(
    s: Stream, og: Stream, offsets: List[Union[Fraction, float]]
):
    """
    Takes a stream to modify, a stream containing the relevant info,
    and a list of offsets. Subdivides the elements specifed in
    offsets and then makes a copy of the passage in the empty
    space left by the offsets.

    :param s: Stream to modify.
    :param og: Stream containing note information.
    :param offsets: The offsets to modify.
    """
    # could try taking a look at recurse()
    # but need to guarantee that everything will be
    # in its right place
    if len(og.voices) > 0:
        for i, v in enumerate(og.voices):
            nv = s.voices[i]
            subdivide_stream(nv, v, offsets)
    else:
        off = None
        # original notes getting subdivided
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
                # new_el.addLyric("i")
                off += new_el.duration.quarterLength

        # the copy appended after
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
def transposition(measure: Measure, rng: random.Random, _: Stream) -> Measure:
    """
    Transposes the measure by either 1 or -1 half-steps.

    :param m: The measure to transpose.
    :param _: Stream, unused, do not remove.
    :returns: A tranposed copy of the measure.
    """
    options = [i for i in range(-12, 13)]
    choice = rng.choice(options)
    offsets = utils.random_offsets(measure, rng)

    return transpose_measure(measure, offsets, choice)


@typechecked
def transpose_measure(
    measure: Measure, offsets: List[Union[Fraction, float]], degree: int
) -> Measure:
    """
    Transposes a measure by the provided number of steps.

    :param measure: The measure to transpose.
    :param degree: How many steps to transpose it by.
    :return: A tranposed copy of the measure.
    :raises ValueError: Raised if measure does not exist.
    """
    transposed = utils.copy_measure(measure)
    notes = transposed.getElementsByClass("Note")
    for n in notes:
        if n.offset in offsets:
            n.transpose(degree, inPlace=True)
            utils.add_lyric_for_note(n, "t")
    if transposed is None:
        raise ValueError("Measure does not exist.")
    # utils.add_lyric_for_measure(transposed, "t")
    return transposed


@typechecked
def deletion(measure: Measure, rng: random.Random, _: Stream):
    """
    Picks a random substring of the measure and
    returns a copy with that substring replaced
    with a rest.

    :param measure: The measure to delete a substring from.
    :param _: Stream, unused.
    :returns: A measure with random offsets deleted.
    """
    offsets = utils.random_offsets(measure, rng)
    m = utils.copy_inverse(measure, offsets)

    delete_substring(m, measure, offsets)
    # n = utils.get_first_element(m)
    # n.addLyric("del")

    return m


@typechecked
def delete_substring(
    s: Stream, og: Stream, offsets: List[Union[Fraction, float]]
):
    """
    Recursively deletes the offsets provided by the offsets parameter.
    The entire substring is replaced with a rest.

    :param s: The stream to perform this operation on.
    :param og: The original stream containing note information.
    :param offsets: The offsets to delete.
    """
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
def translocation(_: Measure, rng: random.Random, s: Stream):
    """
    Picks a random measure from the part to replace
    the measure with.

    :param _: Measure, unused.
    :param s: The stream to pick a new measure from.
    :returns: A random measure from the stream.
    """
    measures = list(s.getElementsByClass("Measure"))
    choice = utils.copy_measure(rng.choice(measures))
    utils.add_lyric_for_measure(choice, "tl")
    return choice


@typechecked
def inversion(measure: Measure, rng: random.Random, _: Optional[Stream]):
    """
    Picks a set of offsets to invert in a measure and returns
    a copy with the inverted measure.

    :param measure: The measure to invert.
    :param _: Stream, unused.
    :returns: A measure with a random offset inverted.
    """
    offsets = utils.random_offsets(measure, rng)
    # skip inversion if only one element is selected
    if len(offsets) > 1:
        m = utils.copy_inverse(measure, offsets)
        invert_stream(m, measure, offsets)
        # n = utils.get_first_element(m)
        # n.addLyric("inv")
    else:
        m = noop(measure, rng, _)
    return m


@typechecked
def invert_stream(
    s: Stream, og: Stream, offsets: List[Union[Fraction, float]]
):
    """
    Recursively inverts a stream at the given offsets.

    :param s: The stream to invert.
    :param og: Stream containing original note information.
    :param offsets: The offsets to invert.
    """
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
                new_el.addLyric(str("iv"))
                s.insert(off, new_el)
                off += new_el.duration.quarterLength


def choose_mutation(
    rng: random.Random, weights: List[float] = [0.2, 0.2, 0.1, 0.25, 0.05, 0.2]
):
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
    return rng.choices(mutations, weights)[0]
