import os

import pytest
from music21 import converter


@pytest.fixture
def streams():
    streams = []
    for f in os.listdir("tests/data/"):
        p = os.path.abspath(f"tests/data/{f}")
        streams.append((f, converter.parse(p)))
    return streams
