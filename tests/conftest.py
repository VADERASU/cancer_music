import os

import pytest
from music21 import converter


@pytest.fixture
def sample_stream():
    p = os.path.abspath("tests/data/twinkle.mxl")
    return converter.parse(p)


@pytest.fixture
def finale_stream():
    p = os.path.abspath("tests/data/hbd.mxl")
    return converter.parse(p)
