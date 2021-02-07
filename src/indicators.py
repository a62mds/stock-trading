"""
Tools for computing technical indicators of stock price data.
"""
from pathlib import Path

import pandas as pd

from src.stock_price_data import StockPriceDataset


class IndicatorDataset(StockPriceDataset):
    """
    Base class for a stock price dataset containing technical indicator data computed from the stock price data.
    """

    def __init__(self, stock_price_dataset: StockPriceDataset) -> None:
        """
        Initialize an IndicatorDataset object from an existing StockPriceDataset object.
        """
        super().__init__(stock_price_dataset.symbol, dataframe=stock_price_dataset.dataframe)

    def compute(self) -> None:
        """
        Pure abstract method for computing the 
        """
        raise NotImplementedError(f"Cannot compute technical indicator data for abstract base class {self.__class__.__name__}")


class MACDDataset(IndicatorDataset):
    """
    Indicator dataset containing MACD data.
    """

    FAST_EWMA: str = "Fast EWMA"
    SLOW_EWMA: str = "Slow EWMA"
    MACD_LINE: str = "MACD Line"
    MACD_SIGNAL: str = "MACD Signal"
    MACD_HISTOGRAM: str = "MACD Histogram"

    def __init__(self,
        stock_price_dataset: StockPriceDataset,
        field: str="Close",
        fast_ewma_span: int=12,
        slow_ewma_span: int=26,
        signal_span: int=9
    ) -> None:
        """
        Initialize a MACDDataset object from a StockPriceDataset, specifying the field defining the timeseries data,
        the fast and slow EWMA spans, and the signal span.
        """
        super().__init__(stock_price_dataset)
        if field not in self.dataframe:
            raise KeyError(f"Dataset does not contain field '{field}'")
        self.field: str = field
        if slow_ewma_span <= fast_ewma_span:
            raise ValueError(
                f"Span {fast_ewma_span} of fast EWMA is greater than or equal to span {slow_ewma_span} of slow EWMA"
            )
        self.fast_ewma_span: int = fast_ewma_span
        self.slow_ewma_span: int = slow_ewma_span
        self.signal_span: int = signal_span
        self._computed: bool = False

    def compute(self) -> None:
        """
        Compute the MACD indicator of the timeseries data of the specified field, assuming this hasn't yet been done.
        If it has already been done, do nothing.

        References:

            - https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.ewm.html
            - https://en.wikipedia.org/wiki/MACD
            - https://www.investopedia.com/terms/m/macd.asp
        """
        if not self._computed:
            self.dataframe[self.FAST_EWMA] = self.dataframe[self.field].ewm(span=self.fast_ewma_span).mean()
            self.dataframe[self.SLOW_EWMA] = self.dataframe[self.field].ewm(span=self.slow_ewma_span).mean()
            self.dataframe[self.MACD_LINE] = self.dataframe[self.FAST_EWMA] - self.dataframe[self.SLOW_EWMA]
            self.dataframe[self.MACD_SIGNAL] = self.dataframe[self.MACD_LINE].ewm(span=self.signal_span).mean()
            self.dataframe[self.MACD_HISTOGRAM] = self.dataframe[self.MACD_LINE] - self.dataframe[self.MACD_SIGNAL]
            self._computed = True
