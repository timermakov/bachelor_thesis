import logging
import numpy as np
import pytest
import backtrader as bt
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backtrader_complex import (
    daily_minmax_stop, volatility_stop, period_minmax_stop, ma_50_18_stop,
    takeprofit_ma_distance, period_minmax_takeprofit
)
from config_utils import ConfigFileOperator
from tinkoff_data import TinkoffDataClient

logger = logging.getLogger(__name__)

SL_METHODS = [
    ("daily_minmax_stop", lambda data: daily_minmax_stop(data, position_type="long")),
    ("volatility_stop", lambda data: volatility_stop(data, atr=np.ones(len(data)), multiplier=1.5, position_type="long")),
    ("period_minmax_stop_5", lambda data: period_minmax_stop(data, period=5, position_type="long")),
    ("period_minmax_stop_20", lambda data: period_minmax_stop(data, period=20, position_type="long")),
    ("period_minmax_stop_60", lambda data: period_minmax_stop(data, period=60, position_type="long")),
    ("ma_50_18_stop", lambda data: ma_50_18_stop(data, ma_medium=np.ones(len(data)), ma_fast=np.ones(len(data)), position_type="long")),
]

TP_METHODS = [
    ("takeprofit_ma_distance", lambda data: takeprofit_ma_distance(data, ma_medium=np.ones(len(data)), ma_fast=np.ones(len(data)), position_type="long")),
    ("period_minmax_takeprofit_5", lambda data: period_minmax_takeprofit(data, period=5, position_type="long")),
    ("period_minmax_takeprofit_20", lambda data: period_minmax_takeprofit(data, period=20, position_type="long")),
    ("period_minmax_takeprofit_60", lambda data: period_minmax_takeprofit(data, period=60, position_type="long")),
]

@pytest.mark.parametrize("ticker_cfg", [
    {
        "TICKER": "SBER",
        "EXCHANGE": "TQBR",
        "START_DATE": "2023-01-01",
        "END_DATE": "2023-12-31",
        "INTERVAL": "1d"
    },
])
def test_all_stoploss_takeprofit_not_nan(ticker_cfg):
    """
    Test that all stop loss and take profit methods do not return NaN, zero, or obviously wrong values.
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
                close = self.data.close[0]
                for name, sl_func in SL_METHODS:
                    sl = sl_func(self.data)
                    assert not np.isnan(sl), f"{name}: Stop loss is NaN"
                    assert sl != 0, f"{name}: Stop loss is zero"
                    assert sl != close, f"{name}: Stop loss equals close price"
                for name, tp_func in TP_METHODS:
                    tp = tp_func(self.data)
                    assert not np.isnan(tp), f"{name}: Take profit is NaN"
                    assert tp != 0, f"{name}: Take profit is zero"
                    assert tp != close, f"{name}: Take profit equals close price"
                logger.info(f"NaN/zero checks passed for all SL/TP methods for {ticker}")
                self.checked = True
                self.stop()

    cerebro.addstrategy(TestStrategy)
    cerebro.run()

@pytest.mark.parametrize("ticker_cfg", [
    {
        "TICKER": "SBER",
        "EXCHANGE": "TQBR",
        "START_DATE": "2023-01-01",
        "END_DATE": "2023-12-31",
        "INTERVAL": "1d"
    },
])
def test_all_stoploss_takeprofit_value_ranges(ticker_cfg):
    """
    Test that all stop loss is always <= close and take profit is always >= close for all methods (long positions).
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
                close = self.data.close[0]
                for name, sl_func in SL_METHODS:
                    sl = sl_func(self.data)
                    assert sl <= close, f"{name}: Stop loss ({sl}) above close ({close})"
                for name, tp_func in TP_METHODS:
                    tp = tp_func(self.data)
                    assert tp >= close, f"{name}: Take profit ({tp}) below close ({close})"
                logger.info(f"Value range checks passed for all SL/TP methods for {ticker}")
                self.checked = True
                self.stop()

    cerebro.addstrategy(TestStrategy)
    cerebro.run() 