"""
Tools for plotting stock price data.
"""
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import finplot as fplt
import pandas as pd

from src.indicators import MACD
from src.stock_price_data import StockPriceDataset


RED: str = "#ff0000"
GREEN: str = "#00ff00"
BLUE: str = "#0000ff"


def plot_stock_price_data(stock_price_dataset: StockPriceDataset, start: date=date(1970, 1, 1), end: date=datetime.today().date()) -> None:
    """
    Plot the stock price data along with the MACD using the `finplot` backend.
    """

    macd: MACD = MACD()
    stock_price_dataset = macd(stock_price_dataset)
    if stock_price_dataset is None:
        raise ValueError("Dataset is invalid")
    stock_price_dataset = stock_price_dataset.more_recent_than(start).less_recent_than(end)

    candles = stock_price_dataset[["Date", "Open", "Close", "High", "Low"]]
    stock_price_dataset.dataframe['Date'] = pd.to_datetime(stock_price_dataset['Date']).astype('int64') # use finplot's internal representation, which is ns

    ax, ax2, ax3 = fplt.create_plot(stock_price_dataset.symbol, rows=3)
    hover_label = fplt.add_legend('', ax=ax)

    fplt.candlestick_ochl(candles, ax=ax)
    fplt.plot(stock_price_dataset[MACD.FAST_EWMA], ax=ax, color=RED, legend=f"EWMA [{macd.fast_ewma_span}]")
    fplt.plot(stock_price_dataset[MACD.SLOW_EWMA], ax=ax, color=BLUE, legend=f"EWMA [{macd.slow_ewma_span}]")

    fplt.volume_ocv(stock_price_dataset[["Date", "Open", "Close", "Volume"]], ax=ax2)
    fplt.add_legend("Volume", ax=ax2)

    fplt.volume_ocv(stock_price_dataset[["Date", "Open", "Close", MACD.MACD_HISTOGRAM]], ax=ax3, colorfunc=fplt.strength_colorfilter)
    fplt.plot(stock_price_dataset[MACD.MACD_LINE], ax=ax3, color=RED, legend="MACD")
    fplt.plot(stock_price_dataset[MACD.MACD_SIGNAL], ax=ax3, color=BLUE, legend="Signal")

    #######################################################
    ## update crosshair and legend when moving the mouse ##

    def update_legend_text(x, y):
        row = stock_price_dataset.dataframe.loc[stock_price_dataset.dataframe.Date==x]
        # format html with the candle and set legend
        fmt = '<span style="color:#%s">%%.2f</span>' % ('0b0' if (row.Open<row.Close).all() else 'a00')
        rawtxt = '<span style="font-size:13px">%%s</span> &nbsp; O%s C%s H%s L%s' % (fmt, fmt, fmt, fmt)
        hover_label.setText(rawtxt % (stock_price_dataset.symbol, row.Open, row.Close, row.High, row.Low))

    def update_crosshair_text(x, y, xtext, ytext):
        ytext = '%s (Close%+.2f)' % (ytext, (y - stock_price_dataset.dataframe.iloc[x].Close))
        return xtext, ytext

    fplt.set_time_inspector(update_legend_text, ax=ax, when='hover')
    fplt.add_crosshair_info(update_crosshair_text, ax=ax)

    fplt.show()
