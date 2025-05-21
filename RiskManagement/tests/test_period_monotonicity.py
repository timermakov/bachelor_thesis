import logging
import numpy as np
import pytest
import backtrader as bt
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backtrader_complex import period_minmax_stop, period_minmax_takeprofit
from config_utils import ConfigFileOperator
from tinkoff_data import TinkoffDataClient

logger = logging.getLogger(__name__)

@pytest.mark.parametrize("ticker_cfg", [
    {
        "TICKER": "SBER",
        "EXCHANGE": "TQBR",
        "START_DATE": "2023-01-01",
        "END_DATE": "2023-12-31",
        "INTERVAL": "1d"
    },
])
def test_period_minmax_monotonicity(ticker_cfg):
    """
    Test that period_minmax_stop and period_minmax_takeprofit are monotonic with period length.
    For a long position:
      - stop loss (min) should not increase as period increases
      - take profit (max) should not decrease as period increases
    """
    tinkoff_client = TinkoffDataClient()
    config_operator = ConfigFileOperator(
        config_path="RiskManagement/config_ru.json",
        csv_path="RiskManagement/csv_data/"
    )
    ticker = ticker_cfg["TICKER"]
    exchange = ticker_cfg["EXCHANGE"]
    start_date = ticker_cfg["START_DATE"]
    end_date = ticker_cfg["END_DATE"]
    interval = ticker_cfg["INTERVAL"]

    csv_file = config_operator.get_csv_file_path(ticker, start_date, end_date, interval)
    df = tinkoff_client.load_market_data(
        ticker=ticker,
        exchange=exchange,
        interval=interval,
        start_date=start_date,
        end_date=end_date,
        csv_file_name=csv_file
    )

    assert len(df) >= 60, f"Not enough data for {ticker} to test all period calculations"

    cerebro = bt.Cerebro()
    data_feed = bt.feeds.PandasData(dataname=df, timeframe=bt.TimeFrame.Days, compression=1)
    cerebro.adddata(data_feed)

    class TestStrategy(bt.Strategy):
        def __init__(self):
            self.checked = False

        def next(self):
            if len(self.data) > 60 and not self.checked:
                # different periods
                weekly_sl = period_minmax_stop(self.data, period=5, position_type="long")
                monthly_sl = period_minmax_stop(self.data, period=20, position_type="long")
                quarterly_sl = period_minmax_stop(self.data, period=60, position_type="long")

                weekly_tp = period_minmax_takeprofit(self.data, period=5, position_type="long")
                monthly_tp = period_minmax_takeprofit(self.data, period=20, position_type="long")
                quarterly_tp = period_minmax_takeprofit(self.data, period=60, position_type="long")

                # monotonicity
                assert weekly_sl >= monthly_sl >= quarterly_sl, (
                    f"Stop loss not monotonic: weekly={weekly_sl}, monthly={monthly_sl}, quarterly={quarterly_sl}"
                )
                assert weekly_tp <= monthly_tp <= quarterly_tp, (
                    f"Take profit not monotonic: weekly={weekly_tp}, monthly={monthly_tp}, quarterly={quarterly_tp}"
                )

                # value range
                close = self.data.close[0]
                assert weekly_sl <= close and monthly_sl <= close and quarterly_sl <= close, "Stop loss above close"
                assert weekly_tp >= close and monthly_tp >= close and quarterly_tp >= close, "Take profit below close"

                logger.info(f"Monotonicity and value range checks passed for {ticker}")
                self.checked = True
                self.stop()

    cerebro.addstrategy(TestStrategy)
    cerebro.run() 