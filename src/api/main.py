import io
import wave
from typing import Annotated
from zipfile import BadZipFile, ZipFile

import fluidsynth
import numpy as np
from fastapi import Body, FastAPI, HTTPException, Response, UploadFile
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


@app.get("/")
def redirect_to_index():
    return RedirectResponse(url="/index.html", status_code=303)


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
    # this should be handled by music21's archive manager
    # but it doesn't support byte objects

    # TODO: midi files?
    # https://pypi.org/project/defusedxml/
    try:
        z = ZipFile(file.file)
    except BadZipFile:
        return JSONResponse(
            status_code=422, content={"message": "File corrupt"}
        )

    files = [n for n in list(z.namelist()) if "META-INF" not in n]
    contents = z.read(files[0])
    s = converter.parse(contents, format="musicxml")

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

    gex = GeneralObjectExporter()
    try:
        content = gex.parse(s)
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})

    return Response(
        content=content, media_type="application/vnd.recordare.musicxml"
    )


def toMidi(file):
    s = converter.parse(file, format="musicxml")
    mf = streamToMidiFile(s)
    return mf


@app.post("/playback")
def playback(file: Annotated[str, Body()]):
    mf = toMidi(file)
    return Response(content=mf.writestr())


@app.post("/synthesize")
def synthesize(file: Annotated[str, Body()]):
    mf = toMidi(file)
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

    with io.BytesIO() as wav:
        wav_writer = wave.open(wav, "wb")
        wav_writer.setframerate(44100)
        wav_writer.setnchannels(2)
        wav_writer.setsampwidth(2)
        wav_writer.writeframes(samples)
        wav_data = wav.getvalue()

    return Response(content=wav_data)


app.mount(
    "/",
    StaticFiles(directory=f"{this_dir}/front/dist"),
    name="static",
)
