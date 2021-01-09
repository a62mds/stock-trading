"""
Unit tests for the src.conversions module.
"""
from datetime import date
import unittest

from src.conversions import date_to_unix_time, START_EPOCH


class TestDateToUnixTime(unittest.TestCase):
    """
    Unit tests for the date_to_unit_time function.
    """

    def test_start_of_epoch(self) -> None:
        """
        Verify that the computed unix time of the start epoch is 0.
        """
        self.assertEqual(date_to_unix_time(START_EPOCH), "0")

    def test_2020_01_08(self) -> None:
        """
        Verify that computed unix time of 2020-01-08 agrees with the value 1610064000 computed using the website
        https://www.unixtimestamp.com/ on 2021-01-08 at approx 22:00 NDT.
        """
        self.assertEqual(date_to_unix_time(date(2021, 1, 8)), "1610064000")


if __name__ == "__main__":
    unittest.main()
