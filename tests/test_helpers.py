import datetime
from zoneinfo import ZoneInfo

import pytest

from apyefa.helpers import is_date, is_time, parse_date, parse_datetime, to_date

TZ_INFO = ZoneInfo("Europe/Berlin")


@pytest.mark.parametrize(
    "time", [None, 123, "123:3", "-12:45", "24:10", "12:79", "12:0"]
)
def test_is_time_invalid_arg(time):
    assert not is_time(time)


@pytest.mark.parametrize("time", ["23:00", "12:59", "06:00"])
def test_is_time_valid_arg(time):
    assert is_time(time)


@pytest.mark.parametrize("date", [None, 123, "20242012", "2024 March 30", "2024-12-12"])
def test_is_date_invalid_arg(date):
    assert not is_date(date)


def test_parse_date():
    assert parse_date("2024-12-12") == datetime.date(2024, 12, 12)
    assert parse_date("2024-03-30") == datetime.date(2024, 3, 30)


def test_parse_date_invalid():
    assert parse_date(None) is None


def test_to_date():
    assert to_date(datetime.date(2024, 12, 12)) == "2024-12-12"
    assert to_date(datetime.date(2024, 3, 30)) == "2024-03-30"


def test_parse_datetime():
    assert parse_datetime("2024-12-12T12:00:00+0100") == datetime.datetime(
        2024, 12, 12, 12, 0, 0, tzinfo=TZ_INFO
    )
    assert parse_datetime("2024-03-30T06:00:00+0100") == datetime.datetime(
        2024, 3, 30, 6, 0, 0, tzinfo=TZ_INFO
    )


def test_parse_datetime_None():
    assert parse_datetime(None) is None
