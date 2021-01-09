"""
Tools for performing conversions between various quantities.
"""
from datetime import date


START_EPOCH: date = date(1970, 1, 1)


def date_to_unix_time(the_date: date) -> str:
    """
    Convert the date to the Unix timestamp of midnight on that day.
    """
    seconds_elapsed = (the_date - START_EPOCH).total_seconds()
    return f"{seconds_elapsed:.0f}"
