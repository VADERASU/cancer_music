import os
from pathlib import Path


def get_this_dir():
    f = Path(__file__)
    return f.parent


def mkdir(pt: str):
    if not os.path.exists(pt):
        os.makedirs(pt)
