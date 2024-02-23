from enum import Enum
from typing import TypedDict


class Therapy(Enum):
    OFF = 0
    CURE = 1
    PARTIAL_CURE = 2
    ADAPTIVE = 3


class TherapyParameters(TypedDict):
    therapy_mode: Therapy
    mutant_survival: float
    start: float
    adaptive_threshold: int
    adaptive_interval: int


class Parameters(TypedDict):
    how_many: int
    max_parts: int
    reproduction: float
    noop: float
    insertion: float
    transposition: float
    deletion: float
    translocation: float
    inversion: float
    start: float
