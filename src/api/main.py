from fastAPI import FastAPI, UploadFile
from music21 import converter

from cancer_music.processor.process import mutate

app = FastAPI()


@app.post("/process_file")
def process_file(file: UploadFile):
    contents = file.file.read()
    s = converter.parseData(contents)
    mutate(s)
