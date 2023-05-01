import pytest

from processor.process import mutate


@pytest.mark.usefixtures("sample_stream")
def test_mutate(sample_stream):
    mutate(sample_stream)
