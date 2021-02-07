"""
Driver script for analyzing stock price data.
"""
import argparse
from datetime import date, datetime
from pathlib import Path
import sys
import traceback
from typing import Optional

from src import logger
from src.plots import plot_stock_price_data
from src.stock_price_data import StockPriceDataset, VALID_INTERVALS


__version__ = "0.1.0"


ROOT_DIR: Path = Path(__file__).resolve().parent
DATA_DIR: Path = ROOT_DIR / "data"
LOG_DIR: Path = ROOT_DIR / ".logs"


def main(args: argparse.Namespace) -> int:
    """
    Read data from existing CSV file for ...
    """
    logger.debug(f"{__file__} main function arguments:")
    for arg in vars(args):
        logger.debug(f"  {arg}: {getattr(args, arg)}")
    return_code: int = 0
    try:
        csv_path: Path = DATA_DIR / args.symbol / f"{args.symbol}.csv"
        stock_price_data = StockPriceDataset(args.symbol)
        logger.debug(f"Checking for CSV file '{csv_path}'...")
        if csv_path.is_file():
            logger.debug("Found CSV file")
            logger.info(f"Reading data for symbol '{args.symbol}' from CSV file '{csv_path}'...")
            stock_price_data = StockPriceDataset.from_csv(args.symbol, csv_path)
        if args.update:
            logger.info(f"Downloading updated data for symbol '{args.symbol}'...")
            stock_price_data += StockPriceDataset.from_yahoo_finance(args.symbol, start=stock_price_data.latest_date, interval=args.interval)
            logger.info(f"Writing updated data for symbol '{args.symbol}' to CSV file...")
            stock_price_data.to_csv(csv_path, overwrite=True)
        kwargs: dict = {}
        if args.start:
            kwargs = {**kwargs, "start": datetime.strptime(args.start, "%Y-%m-%d").date()}
        if args.end:
            kwargs = {**kwargs, "end": datetime.strptime(args.end, "%Y-%m-%d").date()}
        logger.info(f"Plotting data for symbol '{args.symbol}'...")
        plot_stock_price_data(stock_price_data, **kwargs)
    except Exception as e:
        logger.error(f"Encountered unhandled {e.__class__.__name__}: {e}")
        for line in traceback.format_exc().rstrip().split("\n"):
            logger.debug(line)
        return_code = -1
    logger.debug(f"{__file__} main function returning {return_code}")
    return return_code


if __name__ == "__main__":

    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('-V', '--version', action='version', version="%(prog)s ("+__version__+")")
    PARSER.add_argument("symbol", type=str, default="PNG.V", help="Stock symbol whose prices are to be analyzed")
    PARSER.add_argument("-s", "--start", type=str, help="GLB for date range", default=None)
    PARSER.add_argument("-e", "--end", type=str, help="LUB for date range", default=None)
    PARSER.add_argument("-i", "--interval", type=str, default="1d", choices=VALID_INTERVALS, help="Interval between successive datapoints")
    PARSER.add_argument("-u", "--update", action="store_true", help="Update existing stock price data first")
    ARGS = PARSER.parse_args()

    LOGGER_SETTINGS = logger.LogSettings(console_level=logger.INFO, root_name=f"Analyze-{ARGS.symbol}")
    logger.setup(LOGGER_SETTINGS)

    RETURN_CODE = main(ARGS)

    logger.debug(f"{__file__} exiting with code {RETURN_CODE}")
    sys.exit(RETURN_CODE)
