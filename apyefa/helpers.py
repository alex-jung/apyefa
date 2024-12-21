import datetime
import re
from zoneinfo import ZoneInfo

TZ_INFO = ZoneInfo("Europe/Berlin")


def parse_datetime(date: str) -> datetime.datetime:
    """
    Parses a date string in ISO 8601 format and converts it to a timezone-aware datetime object.

    Args:
        date (str): The date string to parse in the format "%Y-%m-%dT%H:%M:%S%z".

    Returns:
        datetime.datetime: A timezone-aware datetime object if the input date is valid, otherwise None.
    """
    if not date:
        return None

    dt = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%z")

    return dt.astimezone(TZ_INFO)


def parse_date(date: str) -> datetime.date:
    """
    Parses a date string in the format 'YYYY-MM-DD' and returns a datetime.date object.

    Args:
        date (str): The date string to parse.

    Returns:
        datetime.date: The parsed date object, or None if the input date string is empty.
    """
    if not date:
        return None

    return datetime.datetime.strptime(date, "%Y-%m-%d").date()


def to_date(date: datetime.date) -> datetime.date:
    """
    Convert a datetime.date object to a string in the format 'YYYY-MM-DD'.

    Args:
        date (datetime.date): The date object to be converted.

    Returns:
        str: The date as a string in the format 'YYYY-MM-DD'.
    """
    return datetime.datetime.strftime(date, "%Y-%m-%d")


def is_datetime(date: str):
    """
    Check if the given string is in the format of a datetime.

    The expected format is "YYYYMMDD HH:MM".

    Args:
        date (str): The date string to check.

    Returns:
        bool: True if the string is in the correct datetime format, False otherwise.
    """
    if not isinstance(date, str) or not date:
        return False

    pattern = re.compile(r"\d{8} \d{2}:\d{2}")

    if not bool(pattern.match(date)):
        return False

    date_str = date.split(" ")[0]
    time_str = date.split(" ")[1]

    return is_date(date_str) and is_time(time_str)


def is_date(date: str):
    """
    Check if the given string is a valid date in the format YYYYMMDD.

    Args:
        date (str): The date string to be validated.

    Returns:
        bool: True if the string is a valid date, False otherwise.

    The function checks if the input string matches the pattern YYYYMMDD,
    where YYYY is a four-digit year, MM is a two-digit month (01-12), and
    DD is a two-digit day (01-31). It ensures that the month and day values
    fall within the valid ranges.
    """
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
    """
    Check if the given string is a valid time in HH:MM format.

    Args:
        time (str): The time string to validate.

    Returns:
        bool: True if the string is a valid time in HH:MM format, False otherwise.
    """
    if not isinstance(time, str) or not time:
        return False

    pattern = re.compile(r"(?P<hours>\d{2}):(?P<minutes>\d{2})")

    if not bool(pattern.match(time)):
        return False

    matches = pattern.search(time)

    hours = int(matches.group("hours"))
    minutes = int(matches.group("minutes"))

    return (hours >= 0 and hours < 24) and (minutes >= 0 and minutes < 60)
