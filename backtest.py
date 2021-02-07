"""
Tool for backtesting trading strategies.
"""
import argparse
from pathlib import Path
import sys
import traceback

from src import logger
from src.stock_price_data import StockPriceDataset, VALID_INTERVALS


__version__ = "0.1.0"


ROOT_DIR: Path = Path(__file__).resolve().parent
DATA_DIR: Path = ROOT_DIR / "data"
LOG_DIR: Path = ROOT_DIR / ".logs"


def main(args: argparse.Namespace) -> int:
    """

    """
    logger.debug(f"{__file__} main function arguments:")
    for arg in vars(args):
        logger.debug(f"  {arg}: {getattr(args, arg)}")
    return_code: int = 0
    try:
        pass
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

    LOGGER_SETTINGS = logger.LogSettings(console_level=logger.INFO, root_name=f"Backtest-{ARGS.symbol}")
    logger.setup(LOGGER_SETTINGS)

    RETURN_CODE = main(ARGS)

    logger.debug(f"{__file__} exiting with code {RETURN_CODE}")
    sys.exit(RETURN_CODE)
