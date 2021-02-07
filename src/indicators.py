"""
Tools for computing technical indicators of stock price data.
"""
from typing import Optional

from src import logger
from src.stock_price_data import StockPriceDataset


class Indicator(object):
    """
    Abstract base class for computing technical indicators.
    """

    def __init__(self, field: str) -> None:
        """
        Initialize an Indicator object with the field of interest.
        """
        self.field = field
        logger.debug(f"{self.__class__.__name__} field = {self.field}")

    def is_valid(self, dataset: StockPriceDataset) -> bool:
        """
        Ensure the dataset is valid. For now, this entails ensuring that the dataset contains the field of interest.
        """
        if self.field not in dataset.dataframe:
            logger.error(f"Dataset does not contain field '{self.field}'")
            return False
        return True

    def __call__(self, dataset: StockPriceDataset) -> StockPriceDataset:
        """
        Pure abstract method. Subclasses should implement this method with the logic specific to the technical
        indicator.
        """
        raise NotImplementedError(
            f"Cannot compute technical indicator data for abstract base class {self.__class__.__name__}"
        )


class MACD(Indicator):
    """
    MACD indicator computation class.
    """

    FAST_EWMA: str = "Fast EWMA"
    SLOW_EWMA: str = "Slow EWMA"
    MACD_LINE: str = "MACD Line"
    MACD_SIGNAL: str = "MACD Signal"
    MACD_HISTOGRAM: str = "MACD Histogram"

    def __init__(self, field: str="Close", fast_ewma_span: int=12, slow_ewma_span: int=26, signal_span: int=9) -> None:
        """
        Initialize a MACD object, specifying the field defining the timeseries data, the fast and slow EWMA spans, and
        the signal span.
        """
        if slow_ewma_span <= fast_ewma_span:
            raise ValueError(
                f"Span {fast_ewma_span} of fast EWMA is greater than or equal to span {slow_ewma_span} of slow EWMA"
            )
        super().__init__(field)
        self.fast_ewma_span: int = fast_ewma_span
        self.slow_ewma_span: int = slow_ewma_span
        self.signal_span: int = signal_span
        logger.debug(f"{self.__class__.__name__} fast_ewma_span = {self.fast_ewma_span}")
        logger.debug(f"{self.__class__.__name__} slow_ewma_span = {self.slow_ewma_span}")
        logger.debug(f"{self.__class__.__name__} signal_span = {self.signal_span}")

    def __call__(self, dataset: StockPriceDataset) -> Optional[StockPriceDataset]:
        """
        Ensure that the dataset is valid and, if it is, compute the MACD indicator of the timeseries data of the
        specified field, save the data as new series in the dataset, and return the updated dataset.

        If the dataset is not valid, return None.

        References:

            - https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.ewm.html
            - https://en.wikipedia.org/wiki/MACD
            - https://www.investopedia.com/terms/m/macd.asp
        """
        if not self.is_valid(dataset):
            return None
        dataset.dataframe[self.FAST_EWMA] = dataset.dataframe[self.field].ewm(span=self.fast_ewma_span).mean()
        dataset.dataframe[self.SLOW_EWMA] = dataset.dataframe[self.field].ewm(span=self.slow_ewma_span).mean()
        dataset.dataframe[self.MACD_LINE] = dataset.dataframe[self.FAST_EWMA] - dataset.dataframe[self.SLOW_EWMA]
        dataset.dataframe[self.MACD_SIGNAL] = dataset.dataframe[self.MACD_LINE].ewm(span=self.signal_span).mean()
        dataset.dataframe[self.MACD_HISTOGRAM] = dataset.dataframe[self.MACD_LINE] - dataset.dataframe[self.MACD_SIGNAL]
        return dataset
