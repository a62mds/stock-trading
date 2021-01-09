"""
Unit tests for the src.stock_price_data module.
"""
from datetime import date
from pathlib import Path
import unittest

from src.stock_price_data import StockPriceDataset


TEST_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PNG_V_CSV_PATH = TEST_DATA_DIR / "PNG.V.csv"


class TestStockPriceDataset(unittest.TestCase):
    """
    Unit tests for the StockPriceDataset class.
    """

    def test_bool_dunder_method_empty_dataset(self) -> None:
        """
        Basic test of the `StockPriceDataset.__bool__` method.

        Create a StockPriceDataset object using the `StockPriceDataset.__init__` method with no arguments supplied and
        ensure that `StockPriceDataset.__bool__` returns `True`.
        """
        stock_price_data = StockPriceDataset("symbol")
        self.assertFalse(bool(stock_price_data))

    def test_earliest_date_method_empty_dataset(self) -> None:
        """
        Basic test of the `StockPriceDataset.earliest_date` property when the StockPriceDataset object is Empty.
        """
        stock_price_data = StockPriceDataset("symbol")
        self.assertIsNone(stock_price_data.earliest_date)

    def test_earliest_date_method_png_v_dataset(self) -> None:
        """
        Basic test of the `StockPriceDataset.earliest_date` property for StockPriceDataset object populated with PNG.V
        data. As noted in ..\data\README.md, the date of the oldest datapoint is 2017-01-03.
        """
        stock_price_data = StockPriceDataset.from_csv("PNG.V", PNG_V_CSV_PATH)
        self.assertEqual(stock_price_data.earliest_date, date(2017, 1, 3))

    def test_latest_date_method_empty_dataset(self) -> None:
        """
        Basic test of the `StockPriceDataset.latest_date` property when the StockPriceDataset object is empty.
        """
        stock_price_data = StockPriceDataset("symbol")
        self.assertIsNone(stock_price_data.latest_date)

    def test_latest_date_method_png_v_dataset(self) -> None:
        """
        Basic test of the `StockPriceDataset.latest_date` property for StockPriceDataset object populated with PNG.V
        data. As noted in ..\data\README.md, the date of the most recent datapoint is 2020-12-24.
        """
        stock_price_data = StockPriceDataset.from_csv("PNG.V", PNG_V_CSV_PATH)
        self.assertEqual(stock_price_data.latest_date, date(2020, 12, 24))

    def test_more_recent_than_method_empty_dataset(self) -> None:
        """
        Basic test of the `StockPriceDataset.more_recent_than` method when the StockPriceDataset object is empty.
        """
        stock_price_data = StockPriceDataset("symbol")
        self.assertFalse(bool(stock_price_data.more_recent_than(date(2019, 12, 24))))

    def test_more_recent_than_method_png_v_dataset(self) -> None:
        """
        Basic test of the `StockPriceDataset.more_recent_than` method for StockPriceDataset object populated with PNG.V
        data. As noted in ..\data\README.md, the date of the most recent datapoint is 2020-12-24 and the date of the
        oldest datapoint is 2017-01-03. Test case ensures that trying to get data more recent than 2019-12-24 returns
        only datapoints with dates between 2019-12-24 and 2020-12-24, inclusive.
        """
        date_glb = date(2019, 12, 24)
        stock_price_data = StockPriceDataset.from_csv("PNG.V", PNG_V_CSV_PATH).more_recent_than(date_glb)
        for datapoint_date in stock_price_data["Date"]:
            self.assertTrue(datapoint_date >= date_glb)

    def test_less_recent_than_method_png_v_dataset(self) -> None:
        """
        Basic test of the `StockPriceDataset.more_recent_than` method for StockPriceDataset object populated with PNG.V
        data. As noted in ..\data\README.md, the date of the most recent datapoint is 2020-12-24 and the date of the
        oldest datapoint is 2017-01-03. Test case ensures that trying to get data older than 2018-01-03 returns only
        datapoints with dates between 2017-01-03 and 2018-01-03, inclusive.
        """
        date_lub = date(2018, 1, 3)
        stock_price_data = StockPriceDataset.from_csv("PNG.V", PNG_V_CSV_PATH).less_recent_than(date_lub)
        for datapoint_date in stock_price_data["Date"]:
            self.assertTrue(datapoint_date <= date_lub)

    def test_on_date_method_empty_dataset(self) -> None:
        """
        Basic test of the `StockPriceDataset.on_date` method when the StockPriceDataset object is empty.
        """
        the_date = date(2019, 12, 24)
        stock_price_data = StockPriceDataset("symbol")
        self.assertIsNone(stock_price_data.on_date(the_date))

    def test_on_date_method_png_v_dataset(self) -> None:
        """
        Basic test of the `StockPriceDataset.on_date` method for StockPriceDataset object populated with PNG.V data. As
        noted ..\data\README.md, the date of the most recent datapoint is 2020-12-24 and the date of the oldest
        datapoint is 2017-01-03. Test case ensures that the datapoint on 2020-12-24 is found.
        """
        the_date = date(2019, 12, 24)
        stock_price_datapoint = StockPriceDataset.from_csv("PNG.V", PNG_V_CSV_PATH).on_date(the_date)
        self.assertEqual(stock_price_datapoint["Date"], the_date)


if __name__ == "__main__":
    unittest.main()
