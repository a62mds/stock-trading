"""
Tools for obtaining stock price data.
"""
from __future__ import annotations
import csv
from datetime import date, datetime, timedelta
from io import StringIO
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import pandas as pd
import requests

from src.conversions import date_to_unix_time


STOCK_PRICE_FIELDS = [
    "Date",
    "Open",
    "High",
    "Close",
    "Low",
    "Volume"
]

VALID_INTERVALS = [
    "1d",
    "1wk",
    "1mo"
]
VALID_INTERVAL_TIMEDELTAS = dict(zip(VALID_INTERVALS, [
    {"days": 1},
    {"weeks": 1},
    {"months": 1}
]))


class StockPriceDataset(object):
    """
    Fairly thin wrapper around a Pandas DataFrame with some additional functionality for dealing specifically with
    stock price data.
    """

    def __init__(self, symbol: str, dataframe: pd.DataFrame=pd.DataFrame(columns=STOCK_PRICE_FIELDS)) -> None:
        """
        Initialize a StockPriceDataset from an existing Pandas DataFrame. The DataFrame must have all fields listed in
        `STOCK_PRICE_FIELDS`, and must have a date format that can be converted using the Pandas to_datetime function.
        """
        missing_fields: List[str] = list()
        for field in STOCK_PRICE_FIELDS:
            if field not in dataframe.columns.to_list():
                missing_fields.append(field)
        if missing_fields:
            raise KeyError(f"Missing fields: {', '.join(missing_fields)}")
        self.symbol = symbol
        self.dataframe: pd.DataFrame = dataframe.sort_values(by=["Date"]).reset_index(drop=True)
        self.dataframe["Date"] = pd.to_datetime(self.dataframe["Date"], unit="ns")
        self._earliest_date: Optional[date] = None
        self._latest_date: Optional[date] = None
        self._len: Optional[int] = None

    def __iadd__(self, other: StockPriceDataset) -> StockPriceDataset:
        """
        Overload of the += operator for StockPriceDataset objects. Useful for updating a StockPriceDataset object using
        data from a second with, presumably, more recent datapoints.
        """
        self.dataframe = self.dataframe.append(other.dataframe).drop_duplicates(subset="Date").reset_index(drop=True)
        return self

    def __bool__(self) -> bool:
        """
        Evaluate the truthiness of a StockPriceDataset object. True if the internal Pandas DataFrame is nonempty, false
        otherwise.
        """
        return len(self) > 0

    def __len__(self) -> int:
        """
        Return the number of datapoints in the internal dataframe.
        """
        if self._len is None:
            self._len = len(self.dataframe.index)
        return self._len

    def __getitem__(self, key: Any) -> Any:
        """
        Pass calls to the `[]` operator to the internal Pandas DataFrame.
        """
        return self.dataframe[key]

    @classmethod
    def from_yahoo_finance(cls, symbol: str, start: date=date(1970, 1, 1), end: date=datetime.today().date(), interval: str="1d") -> StockPriceDataset:
        """
        Download stock data from Yahoo Finance for the given stock symbol over the specified period and at the
        specified interval and return as a StockPriceDataset.

        Start should be the greatest lower-bound on the date range.
        """
        if interval not in VALID_INTERVALS:
            raise ValueError(f"Invalid interval: {interval}")
        start += timedelta(**VALID_INTERVAL_TIMEDELTAS[interval])
        if start >= end:
            return StockPriceDataset(symbol)
        url: str = cls._make_yahoo_finance_url(symbol, start, end, interval)
        stock_price_data_str: str = requests.get(url).text
        stock_price_data: pd.DataFrame = pd.read_csv(StringIO(stock_price_data_str))
        return StockPriceDataset(symbol, dataframe=stock_price_data)

    @staticmethod
    def _make_yahoo_finance_url(symbol: str, start: date, end: date, interval: str) -> str:
        """
        Generate a Yahoo Finance URL for accessing CSV data for the given stock symbol over the specified period and
        at the specified interval.
        """
        if interval not in ["1d", "1wk", "1mo"]:
            raise ValueError(f"Invalid interval: {interval}")
        base_url: str = "https://query1.finance.yahoo.com/v7/finance/download"
        period1: str = f"period1={date_to_unix_time(start)}"
        period2: str = f"period2={date_to_unix_time(end)}"
        interval = f"interval={interval}"
        events: str = "events=history"
        include_adjusted: str = "includeAdjustedClose=true"
        return f"{base_url}/{symbol}?{period1}&{period2}&{interval}&{events}&{include_adjusted}"

    @classmethod
    def from_csv(cls, symbol: str, csv_path: Path) -> StockPriceDataset:
        """
        Basically a wrapper around the Pandas `read_csv` function.
        """
        if not csv_path.exists():
            raise FileNotFoundError(f"Cannot find CSV file '{csv_file}'")
        stock_price_data: pd.DataFrame = pd.read_csv(csv_path)
        return StockPriceDataset(symbol, dataframe=stock_price_data)

    def to_csv(self, csv_path: Path, overwrite: bool=False) -> None:
        """
        Basically a wrapper around the Pandas `DataFrame.to_csv` method.
        """
        csv_path = csv_path.resolve()
        if csv_path.exists():
            if csv_path.is_dir():
                raise FileExistsError(f"Path is a directory: '{csv_path}'")
            if not overwrite:
                raise FileExistsError(f"CSV file already exists: '{csv_path}'")
            csv_path.unlink()
        with csv_path.open(mode="w", newline="") as csv_file:
            self.dataframe.to_csv(csv_file, index=False)

    @property
    def earliest_date(self) -> Optional[date]:
        """
        Get the date of the oldest datapoint as a `datetime.date` object, if the dataframe is nonempty. Otherwise,
        return `None`.
        """
        if self._earliest_date is None and len(self) > 0:
            self._earliest_date = self.dataframe["Date"].iloc[0].date()
        return self._earliest_date

    @property
    def latest_date(self) -> Optional[date]:
        """
        Get the date of the most recent datapoint as a `datetime.date` object, if the dataframe is nonempty. Otherwise,
        Return `None`.
        """
        if self._latest_date is None and len(self) > 0:
            self._latest_date = self.dataframe["Date"].iloc[-1].date()
        return self._latest_date

    def more_recent_than(self, start: date) -> StockPriceDataset:
        """
        Return a StockPriceDataset consisting of all datapoints in self.dataframe timestamped at or after the `start`
        date.
        """
        return self._filter(lambda dataframe: pd.to_datetime(start) <= dataframe["Date"])

    def less_recent_than(self, end: date) -> StockPriceDataset:
        """
        Return a StockPriceDataset consisting of all datapoints in self.dataframe timestamped at or before the `end`
        date.
        """
        return self._filter(lambda dataframe: dataframe["Date"] <= pd.to_datetime(end))

    def on_date(self, the_date: date) -> Optional[Dict[str, Union[str, float, int, ]]]:
        """
        Return a dict of `str`-type keys mapping to either a `str` for the date, a `float` for the open, high, close,
        and low prices on `the_date`, or an `int` for the volume, assuming there is a datapoint with date `the_date`.
        Otherwise, return `None`.
        """
        datapoint: StockPriceDataset = self._filter(lambda dataframe: dataframe["Date"] == pd.to_datetime(the_date))
        return None if not datapoint else {field: datapoint.dataframe.iloc[0][field] for field in STOCK_PRICE_FIELDS}

    def _filter(self, condition: Callable[[pd.DataFrame], "pd.Series[bool]"]) -> StockPriceDataset:
        """
        Return a StockPriceDataset consisting of all datapoints in self.dataframe that satisfy the `condition`, which
        is a function that takes a pd.DataFrame and returns a pd.Series of boolean values with the same length as the
        pd.DataFrame. The _i_th datapoint is kept in or removed from the pd.DataFrame depending on the truth value of
        the _i_th boolean in the pd.Series.
        """
        stock_price_data: pd.DataFrame = self.dataframe.loc[condition]
        return StockPriceDataset(self.symbol, dataframe=stock_price_data)
