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

MAX_SUBDIVISION_QUARTER_LENGTH = 0.125


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
        therapy_mode=Therapy.OFF,
        mutant_survival=0.0,
        start=0.0,
        adaptive_threshold=2,
        adaptive_interval=8,
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
    cancer_start = math.floor(params["start"] * score_length) - 1
    therapy_start = math.floor(t_params["start"] * score_length) - 1

    mutation_info = {}

    m = Score()
    all_parts = []
    mutants = []
    for p in parts:
        np = None
        if p in candidates:
            np = utils.duplicate_part_keep_measures(p, p.id, cancer_start)
            tumors = utils.slice_part(
                p,
                cancer_start,
                cancer_start + params["how_many"],
                dropList=["Clef", "KeySignature", "TimeSignature"],
                removeLyrics=True,
            )

            mutants.append(np)
            mutation_info[np.id] = {
                "parent": p,
                "tumors": tumors,
                "alive": True,
                "start": cancer_start,
                "mutants": utils.choose_for_slices(
                    cancer_start, score_length, params["how_many"], rng
                ),
            }
        else:
            np = utils.duplicate_part_keep_measures(
                p, p.id, len(p.getElementsByClass("Measure"))
            )
            all_parts.append(np)
        f = utils.get_first_element(np.getElementsByClass("Measure")[0])
        f.addLyric(np.id)

    offspring_count = 0

    # slice
    therapy_started = False
    for i in range(cancer_start, score_length):
        # have adaptive therapy check every 2
        if (
            t_params["therapy_mode"] == Therapy.ADAPTIVE
            and (i - cancer_start) % t_params["adaptive_interval"] == 0
        ):
            # try to keep the number of mutants down
            alive = [mut for mut in mutants if mutation_info[mut.id]["alive"]]
            if len(alive) > t_params["adaptive_threshold"]:
                to_kill = rng.sample(
                    alive, len(alive) - t_params["adaptive_threshold"]
                )
                for mp in to_kill:
                    mutation_info[mp.id]["alive"] = False
                    utils.annotate_first_of_measure(mp, i, "c")

        elif i == therapy_start and not therapy_started:
            if t_params["therapy_mode"] == Therapy.CURE:
                for mp in mutants:
                    mutation_info[mp.id]["alive"] = False

            if t_params["therapy_mode"] == Therapy.PARTIAL_CURE:
                # all but one die
                survivor = rng.choice(mutants)
                utils.annotate_first_of_measure(survivor, i, "s")

                for mp in mutants:
                    if mp.id != survivor.id:
                        mutation_info[mp.id]["alive"] = False
                        utils.annotate_first_of_measure(mp, i, "c")
            therapy_started = True

        for mp in mutants:
            m_info = mutation_info[mp.id]
            tumors = m_info["tumors"]
            parent = m_info["parent"]
            is_alive = m_info["alive"]
            start = m_info["start"]
            to_mutate = m_info["mutants"]

            if is_alive:
                dm = mp.getElementsByClass("Measure")[i]
                t = tumors[i % len(tumors)]
                if i in to_mutate:
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
                tumors[i % len(tumors)] = mutant_measure

                if (i - start) % params[
                    "how_many"
                ] == 0 and rng.random() < params["reproduction"]:
                    # if there's still room, create a new part
                    if offspring_count < params["max_parts"]:
                        dup = utils.duplicate_part(mp, available_id)
                        utils.annotate_first_of_measure(
                            dup, 0, f"a.{mp.id}", str(available_id)
                        )
                        mutants.append(dup)
                        new_start = i + rng.randint(
                            0, math.floor(params["how_many"] / 2)
                        )

                        # take greatest ancestor as parent for transpositions
                        mutation_info[dup.id] = {
                            "parent": parent,
                            "tumors": list(
                                map(
                                    lambda measure: utils.copy_measure(
                                        measure,
                                        [
                                            "Clef",
                                            "KeySignature",
                                            "TimeSignature",
                                        ],
                                        removeLyrics=True,
                                    ),
                                    tumors,
                                ),
                            ),
                            "start": new_start,
                            "alive": True,
                            "mutants": utils.choose_for_slices(
                                cancer_start,
                                score_length,
                                params["how_many"],
                                rng,
                            ),
                        }
                        available_id += 1
                        offspring_count += 1
                    else:
                        # otherwise, look for parts we can bring back to life
                        dead = [
                            p
                            for p in mutants
                            if not mutation_info[p.id]["alive"]
                            and mutation_info[p.id]["parent"] == parent
                            and p.id != mp.id
                        ]
                        if len(dead) > 0:
                            new_child = rng.choice(dead)
                            mutation_info[new_child.id]["alive"] = True
                            mutation_info[new_child.id]["start"] = i
                            utils.annotate_first_of_measure(
                                new_child, 0, f"r.{mp.id}"
                            )

    all_parts.extend(mutants)
    all_parts.sort(key=lambda x: x.id)
    for p in all_parts:
        p.makeBeams(inPlace=True)
        m.append(p)

    return m, tree


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
                # don't divide more than a 32nd
                if el.duration.quarterLength >= MAX_SUBDIVISION_QUARTER_LENGTH:
                    new_el = utils.subdivide_element(el)
                else:
                    new_el = utils.duplicate_element(el)

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
                if el.duration.quarterLength >= MAX_SUBDIVISION_QUARTER_LENGTH:
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
    options = [-1, 1]
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
def translocation(og: Measure, rng: random.Random, s: Stream):
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

    # filter out measures that don't match the timesignature of the original measure
    ts = utils.get_time(og)

    def comp(a, b):
        return a.numerator == b.numerator and a.denominator == b.denominator

    safe = list(filter(lambda m: comp(ts, m), measures))

    choice = utils.copy_measure(
        rng.choice(safe), ["Clef", "KeySignature", "TimeSignature"]
    )
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
