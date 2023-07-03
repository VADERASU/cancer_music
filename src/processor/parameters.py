from enum import Enum
from typing import TypedDict


class Therapy(Enum):
    OFF = 0
    CURED = 1
    FAILED = 2


class TherapyParameters(TypedDict):
    therapy_mode: Therapy
    resistance_probability: float
    start: float


class Parameters(TypedDict):
    how_many: int
    noop: float
    insertion: float
    transposition: float
    deletion: float
    translocation: float
    inversion: float
