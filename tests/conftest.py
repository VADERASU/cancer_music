import os

import pytest
from music21 import converter


@pytest.fixture
def sample_stream():
    p = os.path.abspath("tests/data/hbd.mxl")
    return converter.parse(p)
