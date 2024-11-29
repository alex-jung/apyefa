import pytest

from apyefa.helpers import is_time


@pytest.mark.parametrize(
    "time", [None, 123, "123:3", "-12:45", "24:10", "12:79", "12:0"]
)
def test_is_time_invalid_arg(time):
    assert not is_time(time)


@pytest.mark.parametrize("time", ["23:00", "12:59", "06:00"])
def test_is_time_valid_arg(time):
    assert is_time(time)
