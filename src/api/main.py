from zipfile import BadZipFile, ZipFile

from fastapi import FastAPI, HTTPException, Response, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from music21 import converter
from music21.musicxml.m21ToXml import GeneralObjectExporter

from processor.process import mutate

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
    file: UploadFile,
):
    # this should be handled by music21's archive manager
    # but it doesn't support byte objects
    try:
        z = ZipFile(file.file)
    except BadZipFile:
        raise HTTPException(422, "File corrupt")

    files = [n for n in list(z.namelist()) if "META-INF" not in n]
    contents = z.read(files[0])
    s = converter.parse(contents, format="musicxml")

    mutate(
        s,
        {
            "how_many": how_many,
            "noop": noop,
            "insertion": insertion,
            "transposition": transposition,
            "deletion": deletion,
            "translocation": translocation,
            "inversion": inversion,
        },
    )

    gex = GeneralObjectExporter()
    return Response(
        content=gex.parse(s), media_type="application/vnd.recordare.musicxml"
    )


app.mount(
    "/",
    StaticFiles(directory=f"{this_dir}/front/dist"),
    name="static",
)
