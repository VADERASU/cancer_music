import io
import json
import math
import os
import time
import wave
import zipfile
from typing import Annotated
from zipfile import BadZipFile, ZipFile

import fluidsynth
import numpy as np
from fastapi import Body, FastAPI, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from music21 import converter
from music21.midi.translate import streamToMidiFile
from music21.musicxml.m21ToXml import GeneralObjectExporter
from music21.stream.base import Score

import api.utils as utils
from processor.parameters import Parameters, Therapy, TherapyParameters
from processor.process import mutate
from processor.synth import PatchedSynth

app = FastAPI()
this_dir = utils.get_this_dir()
origins = ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

default_file_loc = os.path.join(this_dir, "front", "src", "samples")
default_files = [f for f in os.listdir(default_file_loc) if f.endswith(".mxl")]


@app.get("/")
def redirect_to_index():
    return RedirectResponse(url="/index.html", status_code=303)


def to_score(file: UploadFile) -> Score:
    if file.filename is None:
        raise ValueError("File corrupt.")

    contents = None
    if file.filename.endswith(".mxl"):
        try:
            z = ZipFile(file.file)
        except BadZipFile:
            return ValueError("File corrupt.")
        files = [n for n in list(z.namelist()) if "META-INF" not in n]
        contents = z.read(files[0])
    elif file.filename.endswith(".musicxml"):
        contents = file.file.read()
    else:
        raise ValueError(
            "Invalid file type. Please provide either a .mxl or .musicxml file."
        )

    s = converter.parse(contents, format="musicxml")
    if type(s) is not Score:
        raise ValueError(
            "Invalid format. Please provide a score, not an opus or part."
        )

    return s


def drop_extension(fname: str):
    return fname.split(".")[0]


def log_error(
    file: UploadFile,
    seed: int,
    p: Parameters,
    t: TherapyParameters,
    error: str,
):
    ts = time.time()
    log_dir = os.path.join(this_dir, "logs")
    log_file = os.path.join(log_dir, "log.txt")
    utils.mkdir(log_dir)

    if file.filename not in default_files:
        fpath = os.path.join(log_dir, file.filename)
        if not os.path.exists(fpath):
            with open(fpath, "wb+") as f:
                f.write(file.file.read())

    with open(log_file, "a") as f:
        f.write(f"{ts}: Seed: {seed} fname: {file.filename}")
        f.write(f"{ts}: message: {error}")
        f.write(f"{ts}: mutant parameters: {p}")
        f.write(f"{ts}: therapy parameters: {t}")


def get_samples(fname: str):
    utils.mkdir(os.path.join(this_dir, "music_samples"))
    sample_dir = os.path.join(this_dir, "music_samples")

    mfp = os.path.join(sample_dir, f"{fname}.mid")
    wfp = os.path.join(sample_dir, f"{fname}.wav")

    if os.path.isfile(wfp) and os.path.isfile(mfp):
        mf = open(mfp, mode="rb")
        mfb = mf.read()

        wf = open(wfp, mode="rb")
        wfb = wf.read()

        return (mfb, wfb)
    return None


@app.post("/process_file")
def process_file(
    how_many: int,
    noop: float,
    insertion: float,
    transposition: float,
    deletion: float,
    translocation: float,
    inversion: float,
    mode: int,
    start: float,
    mutant_survival: float,
    maxParts: int,
    reproductionProbability: float,
    seed: int,
    cancerStart: float,
    file: UploadFile,
):
    # MIDI? https://pypi.org/project/defusedxml/

    try:
        s = to_score(file)
    except ValueError as e:
        return JSONResponse(status_code=422, content={"message": str(e)})

    mutation_parameters = Parameters(
        max_parts=maxParts,
        reproduction=reproductionProbability,
        how_many=how_many,
        noop=noop,
        insertion=insertion,
        transposition=transposition,
        deletion=deletion,
        translocation=translocation,
        inversion=inversion,
        start=cancerStart,
    )

    therapy_parameters = TherapyParameters(
        therapy_mode=Therapy(mode),
        mutant_survival=mutant_survival,
        start=start,
    )

    fname = drop_extension(file.filename)
    files = []
    try:
        # check if the hasn't already been saved

        data = get_samples(fname)
        mut_fname = f"mutant_{fname}"

        if data is None:
            mf = streamToMidiFile(s)
            files.append((f"{fname}.mid", mf.writestr()))
            files.append((f"{fname}.wav", midiToWav(mf)))
        else:
            mfb, wfb = data
            files.append((f"{fname}.mid", mfb))
            files.append((f"{fname}.wav", wfb))

        m, tree = mutate(
            s,
            mutation_parameters,
            therapy_parameters,
            seed=seed,
        )

        mf = streamToMidiFile(m)
        files.append((f"{mut_fname}.mid", mf.writestr()))
        files.append((f"{mut_fname}.wav", midiToWav(mf)))
        files.append(("metadata.json", json.dumps(tree)))

        gex = GeneralObjectExporter()
        content = gex.parse(m)
        files.append((f"{fname}.musicxml", content))

    except Exception as e:
        error_str = str(e)
        log_error(
            file, seed, mutation_parameters, therapy_parameters, error_str
        )
        return JSONResponse(
            status_code=500,
            content={
                "message": f"Error: Mutation failed. Please try again. {error_str}."
            },
        )

    zf = toZip(files)

    return Response(
        content=zf.getvalue(),
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment;filename={mut_fname}.zip"
        },
    )


def toZip(files):
    buf = io.BytesIO()

    with ZipFile(buf, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for fname, data in files:
            zip_file.writestr(fname, data)

    return buf


def toMidi(file):
    s = converter.parse(file, format="musicxml")
    mf = streamToMidiFile(s)
    return mf


@app.post("/playback")
def playback(file: Annotated[str, Body()]):
    mf = toMidi(file)
    return Response(content=mf.writestr())


def midiToWav(mf):
    midi = mf.writestr()
    fs = PatchedSynth()

    # need to provide example soundfont, or have user provide it
    sfid = fs.sfload("piano.sf2")
    fs.program_select(0, sfid, 0, 0)
    fs.play_from_mem(midi)

    data = []
    s = fs.get_samples(44100)
    # counts seconds of silence
    empty_frames = 0
    while empty_frames < 5:
        data = np.append(data, s)
        s = fs.get_samples(44100)
        if np.all(s < 2):
            empty_frames += 1
        else:
            empty_frames = 0

    samples = fluidsynth.raw_audio_string(data)
    fs.delete()

    wav = io.BytesIO()
    with wave.open(wav, "wb") as wr:
        wr.setframerate(44100)
        wr.setnchannels(2)
        wr.setsampwidth(2)
        wr.writeframes(samples)

    return wav.getvalue()


@app.post("/synthesize")
def synthesize(file: Annotated[str, Body()]):
    mf = toMidi(file)
    wav_data = midiToWav(mf)
    return Response(content=wav_data)


app.mount(
    "/",
    StaticFiles(directory=f"{this_dir}/front/dist"),
    name="static",
)
