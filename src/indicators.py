"""
Tools for computing technical indicators of stock price data.
"""
from pathlib import Path

import pandas as pd

from src.stock_price_data import StockPriceDataset


def macd(
    dataset: StockPriceDataset, field: str="Close", fast_ewma_span: int=12, slow_ewma_span: int=26, signal_span: int=9
    ) -> pd.DataFrame:
    """
    Computes the MACD indicator of the timeseries data contained in the `field` column of the `dataset`. Returns a
    `pd.DataFrame` with the following fields:

        - "Date"
        - "Fast EWMA"
        - "Slow EWMA"
        - "MACD Line"
        - "MACD Signal"
        - "MACD Histogram"

    References:

        - https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.ewm.html
        - https://en.wikipedia.org/wiki/MACD
        - https://www.investopedia.com/terms/m/macd.asp
    """
    if slow_ewma_span <= fast_ewma_span:
        raise ValueError(
            f"Span {fast_ewma_span} of fast EWMA is greater than or equal to span {slow_ewma_span} of slow EWMA"
        )
    macd_dataframe = pd.DataFrame()
    macd_dataframe["Date"] = dataset["Date"]
    macd_dataframe["Fast EWMA"] = dataset[field].ewm(span=fast_ewma_span).mean()
    macd_dataframe["Slow EWMA"] = dataset[field].ewm(span=slow_ewma_span).mean()
    macd_dataframe["MACD Line"] = macd_dataframe["Fast EWMA"] - macd_dataframe["Slow EWMA"]
    macd_dataframe["MACD Signal"] = macd_dataframe["MACD Line"].ewm(span=signal_span).mean()
    macd_dataframe["MACD Histogram"] = macd_dataframe["MACD Line"] - macd_dataframe["MACD Signal"]
    return macd_dataframe
