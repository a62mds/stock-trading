"""
Tools for plotting stock price data.
"""
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import finplot as fplt
import pandas as pd

from src.indicators import MACDDataset


RED: str = "#ff0000"
GREEN: str = "#00ff00"
BLUE: str = "#0000ff"


def plot_stock_price_data(stock_price_dataset: "StockPriceDataset", start: date=date(1970, 1, 1), end: date=datetime.today().date()) -> None:
    """
    Plot the stock price data along with the MACD using the `finplot` backend.
    """

    macd_dataset: MACDDataset = MACDDataset(stock_price_dataset.more_recent_than(start).less_recent_than(end))
    macd_dataset.compute()

    candles = macd_dataset[["Date", "Open", "Close", "High", "Low"]]
    macd_dataset.dataframe['Date'] = pd.to_datetime(macd_dataset['Date']).astype('int64') # use finplot's internal representation, which is ns

    ax, ax2 = fplt.create_plot(macd_dataset.symbol, rows=2)

    fplt.candlestick_ochl(candles, ax=ax)
    hover_label = fplt.add_legend('', ax=ax)
    fplt.plot(macd_dataset[MACDDataset.FAST_EWMA], ax=ax, color=RED)
    fplt.plot(macd_dataset[MACDDataset.SLOW_EWMA], ax=ax, color=BLUE)

    fplt.volume_ocv(macd_dataset[["Date", "Open", "Close", MACDDataset.MACD_HISTOGRAM]], ax=ax2, colorfunc=fplt.strength_colorfilter)
    fplt.plot(macd_dataset[MACDDataset.MACD_LINE], ax=ax2, color=RED, legend="MACD")
    fplt.plot(macd_dataset[MACDDataset.MACD_SIGNAL], ax=ax2, color=BLUE, legend="Signal")

    #######################################################
    ## update crosshair and legend when moving the mouse ##

    def update_legend_text(x, y):
        row = macd_dataset.dataframe.loc[macd_dataset.dataframe.Date==x]
        # format html with the candle and set legend
        fmt = '<span style="color:#%s">%%.2f</span>' % ('0b0' if (row.Open<row.Close).all() else 'a00')
        rawtxt = '<span style="font-size:13px">%%s</span> &nbsp; O%s C%s H%s L%s' % (fmt, fmt, fmt, fmt)
        hover_label.setText(rawtxt % (macd_dataset.symbol, row.Open, row.Close, row.High, row.Low))

    def update_crosshair_text(x, y, xtext, ytext):
        ytext = '%s (Close%+.2f)' % (ytext, (y - macd_dataset.dataframe.iloc[x].Close))
        return xtext, ytext

    fplt.set_time_inspector(update_legend_text, ax=ax, when='hover')
    fplt.add_crosshair_info(update_crosshair_text, ax=ax)

    fplt.show()
