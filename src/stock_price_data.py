"""
Tools for obtaining stock price data.
"""
import csv
from datetime import date, datetime, timedelta
from pathlib import Path

import requests


DATA_DIR: Path = Path(__file__).resolve().parent.parent / "data"


def update(symbol, start: date=date(1970, 1, 1), interval: str="1d") -> None:
    """
    Check 
    """
    end: date = datetime.today().date()
    output_path: Path = DATA_DIR / symbol / f"{symbol}.csv"
    print(f"Checking for existing stock price data for '{symbol}'...")
    update_existing: bool = False
    if output_path.exists():
        print(f"Found {output_path}")
        if start == date(1970, 1, 1):
            print(f"Checking date of most recent stock price data for '{symbol}'")
            with output_path.open(mode="r") as existing_data:
                reader = csv.DictReader(existing_data)
                start = datetime.strptime(list(reader)[-1]["Date"], "%Y-%m-%d").date()
                print(f"Date of most recent data: {start}")
                # No need to retrieve data for the date of most recent existing data
                start = start + timedelta(days=1)
                update_existing = True
    else:
        print(f"No existing data found for '{symbol}'")
        output_path.parent.mkdir(exist_ok=True, parents=True)
    if start >= end:
        print(f"Existing data for '{symbol}' is more recent than {end}")
        return
    print(f"Retrieving stock price data for '{symbol}' from {start} to {end} at an interval of {interval}...")
    stock_data: bytes = _get_stock_price_data(symbol, start, end, interval)
    if update_existing:
        # Remove the header from the retrieved CSV data
        stock_data = b"\n" + b"\n".join(stock_data.split(b"\n")[1:])
    print(f"Saving stock price data for '{symbol}' to {output_path}...")
    with output_path.open(mode="ab") as o:
        o.write(stock_data)
    print(f"Done.")


def _get_stock_price_data(symbol: str, start: date, end: date, interval: str) -> str:
    """
    Download stock data from `url` and return as a CSV-formatted string.
    """
    url: str = _get_yahoo_finance_url(symbol, start, end + timedelta(days=1), interval)
    stock_data: str = requests.get(url).content
    return stock_data


def _get_yahoo_finance_url(symbol: str, start: date, end: date, interval: str) -> str:
    """
    Generate a Yahoo Finance URL for accessing CSV data for the given stock symbol over the specified period and at the
    specified interval.
    """
    if interval not in ["1d", "1wk", "1mo"]:
        raise ValueError(f"Invalid interval: {interval}")
    base_url: str = "https://query1.finance.yahoo.com/v7/finance/download"
    period1: str = f"period1={_date_to_unix_time(start)}"
    period2: str = f"period2={_date_to_unix_time(end)}"
    interval = f"interval={interval}"
    events: str = "events=history"
    include_adjusted: str = "includeAdjustedClose=true"
    return f"{base_url}/{symbol}?{period1}&{period2}&{interval}&{events}&{include_adjusted}"


def _date_to_unix_time(the_date: date) -> str:
    """
    Convert the date to the Unix timestamp of midnight on that day.
    """
    start_epoch: date = date(1970, 1, 1)
    seconds_elapsed = (the_date - start_epoch).total_seconds()
    return f"{seconds_elapsed:.0f}"
