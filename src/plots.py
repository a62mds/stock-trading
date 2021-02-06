"""
Tools for plotting stock price data.
"""
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import finplot as fplt
import pandas as pd

from src.indicators import macd


RED: str = "#ff0000"
GREEN: str = "#00ff00"
BLUE: str = "#0000ff"


def plot_stock_price_data(stock_price_data: "StockPriceDataset", start: date=date(1970, 1, 1), end: date=datetime.today().date()) -> None:
    """
    Plot the stock price data along with the MACD using the `finplot` backend.
    """

    stock_price_data = stock_price_data.more_recent_than(start).less_recent_than(end)

    candles = stock_price_data[["Date", "Open", "Close", "High", "Low"]]
    macd_dataframe: "pd.DataFrame" = macd(stock_price_data)
    macd_dataframe['Date'] = pd.to_datetime(macd_dataframe['Date']).astype('int64') # use finplot's internal representation, which is ns
    macd_dataframe["Open"] = stock_price_data["Open"]
    macd_dataframe["High"] = stock_price_data["High"]
    macd_dataframe["Close"] = stock_price_data["Close"]
    macd_dataframe["Low"] = stock_price_data["Low"]

    ax, ax2 = fplt.create_plot(stock_price_data.symbol, rows=2)

    fplt.candlestick_ochl(candles, ax=ax)
    hover_label = fplt.add_legend('', ax=ax)
    fplt.plot(macd_dataframe["Fast EWMA"], ax=ax, color=RED)
    fplt.plot(macd_dataframe["Slow EWMA"], ax=ax, color=BLUE)

    fplt.volume_ocv(macd_dataframe[["Date", "Open", "Close", "MACD Histogram"]], ax=ax2, colorfunc=fplt.strength_colorfilter)
    fplt.plot(macd_dataframe["MACD Line"], ax=ax2, color=RED, legend="MACD")
    fplt.plot(macd_dataframe["MACD Signal"], ax=ax2, color=BLUE, legend="Signal")

    #######################################################
    ## update crosshair and legend when moving the mouse ##

    def update_legend_text(x, y):
        row = macd_dataframe.loc[macd_dataframe.Date==x]
        # format html with the candle and set legend
        fmt = '<span style="color:#%s">%%.2f</span>' % ('0b0' if (row.Open<row.Close).all() else 'a00')
        rawtxt = '<span style="font-size:13px">%%s</span> &nbsp; O%s C%s H%s L%s' % (fmt, fmt, fmt, fmt)
        hover_label.setText(rawtxt % (stock_price_data.symbol, row.Open, row.Close, row.High, row.Low))

    def update_crosshair_text(x, y, xtext, ytext):
        ytext = '%s (Close%+.2f)' % (ytext, (y - macd_dataframe.iloc[x].Close))
        return xtext, ytext

    fplt.set_time_inspector(update_legend_text, ax=ax, when='hover')
    fplt.add_crosshair_info(update_crosshair_text, ax=ax)

    fplt.show()
