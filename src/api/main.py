import io
import math
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

from processor.parameters import Parameters, Therapy, TherapyParameters
from processor.process import mutate
from processor.synth import PatchedSynth

from .utils import get_this_dir

app = FastAPI()
this_dir = get_this_dir()
origins = ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def redirect_to_index():
    return RedirectResponse(url="/index.html", status_code=303)


def toStream(file: UploadFile):
    if file.filename is None:
        raise ValueError("File corrupt.")

    if not file.filename.endswith(".mxl"):
        raise ValueError("Wrong file type. Please provide a .mxl file.")

    try:
        z = ZipFile(file.file)
    except BadZipFile:
        return ValueError("File corrupt.")

    files = [n for n in list(z.namelist()) if "META-INF" not in n]
    contents = z.read(files[0])
    s = converter.parse(contents, format="musicxml")

    return s


def mutant_filename(fname: str):
    return f"mutant_{fname.split('.')[0]}"


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
    midi: bool = False,
    wav: bool = False,
):
    # MIDI? https://pypi.org/project/defusedxml/

    try:
        s = toStream(file)
    except ValueError as e:
        return JSONResponse(status_code=422, content={"message": str(e)})

    try:
        mutate(
            s,
            Parameters(
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
            ),
            TherapyParameters(
                therapy_mode=Therapy(mode),
                mutant_survival=mutant_survival,
                start=start,
            ),
            seed=seed,
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})

    fname = mutant_filename(file.filename)
    files = []

    mf = None
    if midi:
        mf = streamToMidiFile(s)
        files.append((f"{fname}.mid", mf.writestr()))

    print("past midi")
    if wav:
        mf = streamToMidiFile(s) if mf is None else mf
        files.append((f"{fname}.wav", midiToWav(mf)))

    gex = GeneralObjectExporter()
    try:
        content = gex.parse(s)
        files.append((f"{fname}.mxl", content))
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})

    if len(files) == 1:
        return Response(
            content=content, media_type="application/vnd.recordare.musicxml"
        )

    zf = toZip(files)

    return Response(content=zf.getvalue(), media_type="application/zip",
                    headers={'Content-Disposition': f'attachment;filename={mutant_filename}.zip'})


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
