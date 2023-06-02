from pathlib import Path


def get_this_dir():
    f = Path(__file__)
    return f.parent
