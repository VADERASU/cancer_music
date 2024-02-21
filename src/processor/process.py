import copy
import math
import random
import sys
from fractions import Fraction
from typing import List, Optional, Union

from music21.note import GeneralNote, Rest
from music21.stream.base import Measure, Part, Score, Stream
from typeguard import typechecked

from processor import utils
from processor.parameters import Parameters, Therapy, TherapyParameters


def repair_stream(s):
    for el in s.flatten().notes:
        el.volume = utils.duplicate_volume(el)

    # make sure all parts have the same number of measures
    parts = s.getElementsByClass("Part")
    part_lengths = [len(p.getElementsByClass("Measures")) for p in parts]
    length = max(part_lengths)
    if any([pl != length for pl in part_lengths]):
        raise ValueError(
            "Not all part lengths are equal. Please modify your input file."
        )


@typechecked
def mutate(
    s: Score,
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
    ref = s.expandRepeats()
    repair_stream(ref)

    parts = list(ref.getElementsByClass("Part"))
    rng = utils.reseed(seed)

    tree = {}

    for i, p in enumerate(parts):
        p.id = i
        tree[p.id] = []
    parts.sort(key=lambda x: x.id)

    # possibility of multiple parts being chosen
    candidates = rng.sample(parts, rng.randint(1, len(parts)))
    candidates.sort(key=lambda x: x.id)
    available_id = len(parts)

    score_length = utils.get_score_length_in_measures(ref)
    cancer_start = math.floor(params["start"] * score_length)

    mutation_info = {}

    m = Score()
    all_parts = []
    mutants = []
    for p in parts:
        np = None
        if p in candidates:
            np = utils.duplicate_part_keep_measures(p, p.id, cancer_start)
            tumors = list(
                map(
                    lambda measure: utils.copy_measure(
                        measure,
                        ["Clef", "KeySignature", "TimeSignature"],
                        removeLyrics=True,
                    ),
                    p.getElementsByClass("Measure")[
                        cancer_start : cancer_start + params["how_many"]
                    ],
                )
            )
            mutants.append(np)
            mutation_info[np.id] = {"parent": p, "tumors": tumors}
        else:
            np = utils.duplicate_part_keep_measures(
                p, p.id, len(p.getElementsByClass("Measure"))
            )
            all_parts.append(np)
        f = utils.get_first_element(np.getElementsByClass("Measure")[0])
        f.addLyric(np.id)

    offspring_count = 0
    # slice
    for i in range(cancer_start, score_length, params["how_many"]):
        for mp in mutants:
            m_info = mutation_info[mp.id]
            tumors = m_info["tumors"]
            parent = m_info["parent"]

            dms = mp.getElementsByClass("Measure")[i : i + params["how_many"]]
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
                mutant_measure = mutation(t, rng, parent)
                mutant_measure.number = dm.number
                mutant_measure.makeBeams(inPlace=True)
                mp.replace(dm, mutant_measure)

                tumors[(i + j) % len(tumors)] = mutant_measure
                # check if we will reproduce this measure or not
            if (
                offspring_count < params["max_parts"]
                and rng.random() < params["reproduction"]
            ):
                dup = utils.duplicate_part(mp, available_id)
                f = utils.get_first_element(
                    dup.getElementsByClass("Measure")[0]
                )
                f.addLyric(available_id)
                mutants.append(dup)
                # take greatest ancestor as parent for transpositions
                mutation_info[dup.id] = {
                    "parent": parent,
                    "tumors": list(
                        map(
                            lambda measure: utils.copy_measure(
                                measure,
                                ["Clef", "KeySignature", "TimeSignature"],
                                removeLyrics=True,
                            ),
                            tumors,
                        )
                    ),
                }
                available_id += 1
                offspring_count += 1

    all_parts.extend(mutants)
    all_parts.sort(key=lambda x: x.id)
    for p in all_parts:
        p.makeBeams(inPlace=True)
        m.append(p)
    """ 
    if t_params["therapy_mode"] == Therapy.CURE:
        t_start = utils.get_percentile_measure_number(
            mutants[0], t_params["start"]
        )
        dead = rng.sample(
            mutants,
            int(len(mutants) * (1 - t_params["mutant_survival"])),
        )
        deadIDs = list(map(lambda e: e.id, dead))
        # don't apply treatment to mutants not in dead
        treated = []
        for mutant in mutants:
            if mutant.id in deadIDs:
                mutant = utils.clear_part(mutant, t_start)
                f = utils.get_first_element(
                    mutant.getElementsByClass("Measure")[0]
                )
                f.addLyric("c")
            treated.append(mutant)
        [s.append(mutant) for mutant in treated]
    else:
        [s.append(mutant) for mutant in mutants]
    """
    return m, tree


def mutate_part(
    mutant_part: Part,
    mutants: List[Part],
    rng: random.Random,
    params: Parameters,
    prev_start: int,
    offset: int,
    id: int,
    parent: Part,
) -> List[Part]:
    if len(mutants) < params["max_parts"]:
        measures = parent.getElementsByClass("Measure")

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

        dpm = mutant_part.getElementsByClass("Measure")[prev_start + offset :]

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
                mutant_measure = mutation(t, rng, parent)  # mutate it
                mutant_measure.number = dm.number
                mutant_measure.makeBeams(inPlace=True)
                mutant_part.replace(
                    dm, mutant_measure
                )  # replace in duplicate part

                # update tumor
                tumors[(i + j) % len(tumors)] = mutant_measure
                # check if we will reproduce this measure or not
                if rng.random() < params["reproduction"]:
                    to_duplicate.append(prev_start + params["how_many"] + i)

        # mark ancestry - can throw this into a function as well

        child_id = id + 1
        for i, child in enumerate(to_duplicate):
            dup = utils.duplicate_part(mutant_part, child_id)
            f = utils.get_first_element(dup.getElementsByClass("Measure")[0])
            f.addLyric(child_id)

            children = mutate_part(
                dup,
                [],
                rng,
                params,
                child,
                rng.randint(0, math.floor(params["how_many"] / 2)),
                child_id,
                mutant_part,
            )
            mutants.extend(children)
            mutants.append(dup)
            child_id += len(children) + 1

        mutant_part.makeBeams(inPlace=True)

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

    # filter out empty measures
    measures = list(
        filter(
            lambda m: not all(
                map(lambda n: n.isRest, m.getElementsByClass("GeneralNote"))
            ),
            list(s.getElementsByClass("Measure")),
        )
    )

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
    return rng.choices(mutations, weights, k=1)[0]
