#!/usr/bin/env python

import os
import logging
import pytest
import pandas as pd
from datetime import datetime, timedelta
import pytz
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tinkoff_data import TinkoffDataClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@pytest.mark.parametrize("ticker,interval", [
    ("SBER", "1d"),
])
def test_tinkoff_data_fetch(ticker, interval):
    """
    Test fetching historical data from T-Bank API for a known ticker and interval.
    """
    token = os.environ.get("TINKOFF_TOKEN")
    if not token:
        pytest.skip("TINKOFF_TOKEN environment variable not set")

    client = TinkoffDataClient(token=token)

    end_date = datetime.now(pytz.UTC) - timedelta(days=5)
    start_date = end_date - timedelta(days=90)

    logger.info(f"Fetching data for {ticker} from {start_date.date()} to {end_date.date()}")
    df = client.get_historical_data(ticker=ticker, interval=interval, from_date=start_date, to_date=end_date)
    print(df)
    assert isinstance(df, pd.DataFrame), "Returned object is not a DataFrame"
    assert not df.empty, f"No data found for {ticker}"
    for col in ["open", "high", "low", "close", "volume"]:
        assert col in df.columns, f"Missing column: {col}"

    # date range
    assert df.index.min().date() >= start_date.date(), "Data starts before requested start_date"
    assert df.index.max().date() <= end_date.date(), "Data ends after requested end_date"
    assert len(df) > 10, "Too few rows returned"

    # statistics
    stats = df.describe()
    assert stats.loc["mean", "close"] > 10, "Mean close price too low for SBER"
    assert stats.loc["max", "close"] < 1000, "Max close price too high for SBER"
    assert stats.loc["min", "close"] > 1, "Min close price too low for SBER"
    logger.info(f"Data fetch and stats checks passed for {ticker}")

if __name__ == "__main__":
    test_tinkoff_data_fetch("SBER", "1d")