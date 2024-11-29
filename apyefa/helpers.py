import datetime
import re
from zoneinfo import ZoneInfo

TZ_INFO = ZoneInfo("Europe/Berlin")


def parse_datetime(date: str) -> datetime.datetime:
    dt = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%z")

    return dt.astimezone(TZ_INFO)


def parse_date(date: str) -> datetime.date:
    return datetime.datetime.strptime(date, "%Y-%m-%d").date()


def is_datetime(date: str):
    if not isinstance(date, str) or not date:
        return False

    pattern = re.compile(r"\d{8} \d{2}:\d{2}")

    if not bool(pattern.match(date)):
        return False

    date_str = date.split(" ")[0]
    time_str = date.split(" ")[1]

    return is_date(date_str) and is_time(time_str)


def is_date(date: str):
    if not isinstance(date, str) or not date:
        return False

    pattern = re.compile(r"(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})")

    if not bool(pattern.match(date)):
        return False

    matches = pattern.search(date)

    month = int(matches.group("month"))
    day = int(matches.group("day"))

    return (month >= 1 and month <= 12) and (day >= 1 and day <= 31)


def is_time(time: str):
    if not isinstance(time, str) or not time:
        return False

    pattern = re.compile(r"(?P<hours>\d{2}):(?P<minutes>\d{2})")

    if not bool(pattern.match(time)):
        return False

    matches = pattern.search(time)

    hours = int(matches.group("hours"))
    minutes = int(matches.group("minutes"))

    return (hours >= 0 and hours < 24) and (minutes >= 0 and minutes < 60)
