import os
import pandas as pd
import numpy as np
import logging
import backtrader as bt
import backtrader.feeds as btfeeds
import talib
from datetime import datetime, time
from typing import Dict, Any, Union, List

from tinkoff_data import TinkoffDataClient
from config_utils import ConfigFileOperator
from plot_utils import save_plot_and_output

logger = logging.getLogger(__name__)

CONFIG_FILE = "config_ru.json"
CSV_PATH = "csv_data/"
RESULTS_PATH = "results_bt_complex/"

config_operator = ConfigFileOperator(
    config_path=CONFIG_FILE,
    csv_path=CSV_PATH,
    results_path=RESULTS_PATH
)

COMMISSION = 0.0005


def daily_minmax_stop(datafeed, position_type="long"):
    if position_type == "long":
        return datafeed.low[0]
    else:
        return datafeed.high[0]


def volatility_stop(datafeed, atr, multiplier=1.5, position_type="long"):
    if position_type == "long":
        return datafeed.close[0] - atr[0] * multiplier
    else:
        return datafeed.close[0] + atr[0] * multiplier


def period_minmax_stop(datafeed, period=5, position_type="long"):
    """
    Calculate stop loss based on min/max values over a specified period.
    
    Parameters:
    datafeed: Backtrader data feed
    period: Number of bars to look back
    position_type: "long" or "short" position
    
    Returns:
    float: Stop loss price
    """
    available_bars = len(datafeed)
    effective_period = min(period, available_bars-1)
    
    if effective_period <= 0:
        return datafeed.close[0] * (0.95 if position_type == "long" else 1.05)
    
    if position_type == "long":
        low_values: List[float] = [datafeed.low[-i] for i in range(effective_period)]
        if low_values:
            return talib.MIN(np.array(low_values), timeperiod=effective_period)[-1]
        return datafeed.close[0] * 0.95  # Fallback
    else:
        high_values: List[float] = [datafeed.high[-i] for i in range(effective_period)]
        if high_values:
            return talib.MAX(np.array(high_values), timeperiod=effective_period)[-1]
        return datafeed.close[0] * 1.05  # Fallback


def ma_50_18_stop(datafeed, ma_medium, ma_fast, safety_margin=0.005, position_type="long"):
    close = datafeed.close[0]
    short_val = ma_fast[0]
    long_val = ma_medium[0]

    dist_short = abs(close - short_val)
    dist_long = abs(close - long_val)

    if position_type == "long":
        if dist_short < dist_long:
            return short_val * (1.0 - safety_margin)
        else:
            return long_val * (1.0 - safety_margin)
    else:
        if dist_short < dist_long:
            return short_val * (1.0 + safety_margin)
        else:
            return long_val * (1.0 + safety_margin)


def takeprofit_ma_distance(datafeed, ma_medium, ma_fast, position_type="long"):
    close = datafeed.close[0]
    short_val = ma_fast[0]
    long_val = ma_medium[0]
    
    distance_factor = 1.5  # take profits more aggressive

    if position_type == "long":
        distance_to_ma = max(abs(close - short_val), abs(close - long_val))
        return close + (distance_to_ma * distance_factor)
    else:
        distance_to_ma = max(abs(close - short_val), abs(close - long_val))
        return close - (distance_to_ma * distance_factor)


def period_minmax_takeprofit(datafeed, period=5, position_type="long"):
    """
    Calculate take profit based on min/max values over a specified period.
    
    Parameters:
    datafeed: Backtrader data feed
    period: Number of bars to look back (5=weekly, 20=monthly, 60=quarterly)
    position_type: "long" or "short" position
    
    Returns:
    float: Take profit price
    """
    available_bars = len(datafeed)
    effective_period = min(period, available_bars-1)
    
    if effective_period <= 0:
        return datafeed.close[0] * (1.05 if position_type == "long" else 0.95)
    
    close = datafeed.close[0]
    tp_factor = 1.25
    
    if position_type == "long":
        high_values: List[float] = [datafeed.high[-i] for i in range(effective_period)]
        if high_values:
            max_high = talib.MAX(np.array(high_values), timeperiod=effective_period)[-1]
            range_value = max_high - close
            return close + (range_value * tp_factor)
        return datafeed.close[0] * 1.05  # Fallback
    else:
        low_values: List[float] = [datafeed.low[-i] for i in range(effective_period)]
        if low_values:
            min_low = talib.MIN(np.array(low_values), timeperiod=effective_period)[-1]
            range_value = close - min_low
            return close - (range_value * tp_factor)
        return datafeed.close[0] * 0.95  # Fallback

def percentage_takeprofit(datafeed, percent=5.0, position_type="long"):
    """
    Calculate take profit based on simple percentage.
    
    Parameters:
    datafeed: Backtrader data feed
    percent: Percentage for take profit
    position_type: "long" or "short" position
    
    Returns:
    float: Take profit price
    """
    close = datafeed.close[0]
    
    if position_type == "long":
        return close * (1.0 + (percent / 100.0))
    else:
        return close * (1.0 - (percent / 100.0))


def choose_stop_loss(method, datafeed, atr, ma_medium, ma_slow, position_type="long"):
    if method == "daily_minmax":
        return daily_minmax_stop(datafeed, position_type)
    elif method == "volatility_stop":
        return volatility_stop(datafeed, atr, multiplier=1.5, position_type=position_type)
    elif method == "weekly_minmax":
        return period_minmax_stop(datafeed, period=5, position_type=position_type)
    elif method == "monthly_minmax":
        return period_minmax_stop(datafeed, period=20, position_type=position_type)
    elif method == "quarterly_minmax":
        return period_minmax_stop(datafeed, period=60, position_type=position_type)
    elif method == "MA_50_18":
        return ma_50_18_stop(datafeed, ma_medium, ma_slow, position_type=position_type)
    else:
        # Default
        return daily_minmax_stop(datafeed, position_type)


def choose_take_profit(method, datafeed, ma_medium, ma_slow, position_type="long", atr=None):
    if method == "ma_distance":
        return takeprofit_ma_distance(datafeed, ma_medium, ma_slow, position_type=position_type)
    elif method == "weekly_minmax":
        return period_minmax_takeprofit(datafeed, period=5, position_type=position_type)
    elif method == "monthly_minmax":
        return period_minmax_takeprofit(datafeed, period=20, position_type=position_type)
    elif method == "quarterly_minmax":
        return period_minmax_takeprofit(datafeed, period=60, position_type=position_type)
    elif method == "prev_bar_5_percent":
        return percentage_takeprofit(datafeed, percent=5.0, position_type=position_type)
    else:
        # Default
        return takeprofit_ma_distance(datafeed, ma_medium, ma_slow, position_type=position_type)


def validate_data(data):
    if data.close[0] <= 0 or data.volume[0] <= 0:
        return False
    return True


# ----------------------------------------------------------------------
# 2) BACKTRADER STRATEGY
# ----------------------------------------------------------------------
class MultiStopTakeStrategy(bt.Strategy):
    params = (
        ("stop_loss_method", "weekly_minmax"),
        ("take_profit_method", "weekly_minmax"),
        ("position_type", "long"),
        ("risk_percent", 0.02),
        ("risk_percent_long", 0.02),
        ("risk_percent_short", 0.01),
        ("profit_to_risk", 2.0),
        ("atr_multiplier", 1.2),
        ("atr_period", 14),
        ("partial_exit", True),
        ("partial_exit_threshold", 0.3),  # Take partial profits earlier
        ("ma_fast", 8),                   # Fast MA for more signals
        ("ma_medium", 20),
        ("ma_slow", 60),
        ("rsi_period", 7),
        ("min_trade_bars", 3),            # Minimum bars between trades
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        
        self.in_trade = False
        self.entry_price = None
        self.stop_price = None
        self.take_profit_price = None
        
        self.atr = bt.ind.ATR(self.data, period=self.p.atr_period)
        self.rsi = bt.ind.RSI(self.data.close, period=self.p.rsi_period)
 
        self.ema_fast = bt.ind.EMA(self.data.close, period=self.p.ma_fast)
        self.ema_medium = bt.ind.EMA(self.data.close, period=self.p.ma_medium)
        self.ema_slow = bt.ind.EMA(self.data.close, period=self.p.ma_slow)
        
        close_array = np.array([self.data.close[i] for i in range(-50, 1)])
        
        self.ma_fast_values = talib.SMA(close_array, timeperiod=self.p.ma_fast)
        self.ma_medium_values = talib.SMA(close_array, timeperiod=self.p.ma_medium)
        self.ma_slow_values = talib.SMA(close_array, timeperiod=self.p.ma_slow)
        
        self.ma_fast = bt.ind.SMA(self.data.close, period=self.p.ma_fast)
        self.ma_medium = bt.ind.SMA(self.data.close, period=self.p.ma_medium)
        self.ma_slow = bt.ind.SMA(self.data.close, period=self.p.ma_slow)
        self.crossover_fast = bt.ind.CrossOver(self.ma_fast, self.ma_medium)
        self.crossover_medium = bt.ind.CrossOver(self.ma_medium, self.ma_slow)

        self.completed_trades = []

        self.order = None
        self.last_trade_size = None
        self.last_executed_price = None
	
        # Trend state indicators
        self.in_uptrend = False
        self.in_downtrend = False
        
        # Trade management variables 
        self.profit_target_hit = False
        self.partial_exit_done = False

    def log(self, txt):
        dt = self.data.datetime.datetime(0).strftime('%Y-%m-%d %H:%M:%S')
        logger.info(f"{dt} - {txt}")

    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])

        if self.order:
            return

        pos = self.getposition()

        if not pos.size:
            self.open_new_trade()
        else:
            self.update_stop_loss()

    def open_new_trade(self):
        """
        Opens a new trade with simplified entry logic.
        """
        # 1) if re-entry condition is met
        if not self.check_reentry_condition():
            return
        
        # if have position, do nothing
        if self.position.size != 0:
            return
            
        self.last_trade_bar = len(self.data)

        # 2) position size with adaptive risk
        size = self.calc_adaptive_size()
        if size <= 0:
            return

        # 3) stop-loss and take-profit
        stop_price = choose_stop_loss(
            self.p.stop_loss_method,
            self.data,
            self.atr,
            self.ma_medium,
            self.ma_slow,
            position_type=self.p.position_type
        )
        
        entry_price = self.data.close[0]
        
        self.entry_price = entry_price
        self.stop_price = stop_price
        
        if self.p.position_type == "long":
            if stop_price >= entry_price:
                self.stop_price = entry_price - (self.atr[0] * self.p.atr_multiplier)
        else:
            if stop_price <= entry_price:
                self.stop_price = entry_price + (self.atr[0] * self.p.atr_multiplier)
        
        base_tp_price = choose_take_profit(
            self.p.take_profit_method,
            self.data,
            self.ma_medium,
            self.ma_slow,
            position_type=self.p.position_type,
            atr=self.atr
        )
        
        self.original_tp_method = self.p.take_profit_method
        
        tp_price = self.calculate_adaptive_take_profit(base_tp_price)
        self.take_profit_price = tp_price

        if self.p.position_type == "long":
            if tp_price <= entry_price:
                self.take_profit_price = entry_price * (1.0 + self.p.profit_to_risk * self.p.risk_percent_long)
                
            tp_percent = ((self.take_profit_price / entry_price) - 1.0) * 100
            self.log(f"BUY CREATE - E:{entry_price:.2f}, SL:{self.stop_price:.2f}, TP:{self.take_profit_price:.2f} ({tp_percent:.2f}%)")
            self.order = self.buy(size=size)
        else:
            if tp_price >= entry_price:
                self.take_profit_price = entry_price * (1.0 - self.p.profit_to_risk * self.p.risk_percent_short)
            
            tp_percent = ((1.0 - self.take_profit_price / entry_price)) * 100
            self.log(f"SHORT CREATE - E:{entry_price:.2f}, SL:{self.stop_price:.2f}, TP:{self.take_profit_price:.2f} ({tp_percent:.2f}%)")
            self.order = self.sell(size=size)

        self.in_trade = True

    def calc_adaptive_size(self):
        """
        Simplified position sizing - more consistent and easy to track.
        """
        capital = self.broker.getvalue() 
        usable_capital = capital * 0.7  # max 70%
        
        risk_percent = self.p.risk_percent
        
        if (self.p.position_type == "long" and self.ma_fast[0] > self.ma_medium[0]) or \
           (self.p.position_type == "short" and self.ma_fast[0] < self.ma_medium[0]):
            risk_percent *= 1.2
        
        stop_dist = self.atr[0] * self.p.atr_multiplier
        
        if stop_dist <= 0 or self.data.close[0] <= 0:
            self.log("Invalid stop distance or price. Cannot calculate position size.")
            return 0
        
        risk_amount = usable_capital * risk_percent
        
        size = int(risk_amount / stop_dist)
        
        size = max(size, 1)
        
        max_affordable = int(usable_capital / self.data.close[0])
        size = min(size, max_affordable)
        
        # 5% of current volume
        if self.data.volume[0] > 0:
            max_volume_size = int(self.data.volume[0] * 0.05)
            size = min(size, max_volume_size)
        
        self.log(f"Position size: {size}, Risk: {risk_percent:.2%}")
        return size
    
    def calculate_adaptive_take_profit(self, base_tp_price):
        """
        Enhanced take profit calculation using the base target from the selected method
        and adjusting it based on market conditions.
        """
        entry_price = self.data.close[0]
        
        atr_val = self.atr[0]
        
        if self.p.position_type == "long":
            base_distance = base_tp_price - entry_price
        else:
            base_distance = entry_price - base_tp_price
            
        max_adjustment = 0.3  
        
        atr_percent = atr_val / entry_price
        
        if atr_percent > 0.02:
            volatility_factor = 1.1
        elif atr_percent < 0.01:
            volatility_factor = 0.9
        else:
            volatility_factor = 1.0
            
        trend_factor = 1.0
        if self.p.position_type == "long":
            if self.ma_fast[0] > self.ma_medium[0] > self.ma_slow[0]:  # Strong uptrend
                trend_factor = 1.15
        else:
            if self.ma_fast[0] < self.ma_medium[0] < self.ma_slow[0]:  # Strong downtrend
                trend_factor = 1.15 
        
        # if overbought/oversold, more conservative
        rsi_factor = 1.0
        if self.p.position_type == "long" and self.rsi[0] > 70:  # Overbought
            rsi_factor = 0.9
        elif self.p.position_type == "short" and self.rsi[0] < 30:  # Oversold
            rsi_factor = 0.9
            
        combined_factor = volatility_factor * trend_factor * rsi_factor

        if combined_factor > (1.0 + max_adjustment):
            combined_factor = 1.0 + max_adjustment
        elif combined_factor < (1.0 - max_adjustment):
            combined_factor = 1.0 - max_adjustment
            
        adjusted_distance = base_distance * combined_factor
        
        if self.p.position_type == "long":
            adjusted_tp = entry_price + adjusted_distance
        else:
            adjusted_tp = entry_price - adjusted_distance
            
        self.log(f"TP adjustment: Base={base_tp_price:.2f}, Adjusted={adjusted_tp:.2f}, " + 
                 f"Method={self.p.take_profit_method}, Factors: Vol={volatility_factor:.2f}, " + 
                 f"Trend={trend_factor:.2f}, RSI={rsi_factor:.2f}")
            
        return adjusted_tp

    def check_reentry_condition(self):
        """
        Simplified entry logic focusing on high-probability setups to increase trade frequency.
        """
        if len(self.data) < 10:
            return False
            
        bars_since_last_trade = len(self.data) - self.last_trade_bar if hasattr(self, 'last_trade_bar') else 999
        if bars_since_last_trade < self.p.min_trade_bars:
            return False
            
        pos_type = self.p.position_type
        close_price = self.data.close[0]
        prev_close = self.data.close[-1]
        
        is_uptrend = self.ma_fast[0] > self.ma_medium[0] > self.ma_slow[0]
        is_downtrend = self.ma_fast[0] < self.ma_medium[0] < self.ma_slow[0]
        
        # 1. SIMPLE MOMENTUM ENTRY CONDITIONS
        
        if pos_type == "long":
            if not is_uptrend and close_price < self.ma_slow[0]:
                return False
                
            # entry signal 1: price closes above fast MA with volume confirmation
            if (close_price > self.ma_fast[0] and prev_close <= self.ma_fast[0] and
                self.data.volume[0] > self.data.volume[-1] * 1.1):
                self.log("LONG ENTRY: Price broke above fast MA with volume")
                return True
                
            # entry signal 2: RSI crosses above 50 in uptrend
            if (self.rsi[0] > 50 and self.rsi[-1] <= 50 and 
                close_price > self.ma_medium[0]):
                self.log("LONG ENTRY: RSI crossed above 50 in uptrend")
                return True
                
            # entry signal 3: Fast MA crosses above medium MA (Golden Cross)
            if self.crossover_fast > 0 and close_price > self.ma_medium[0]:
                self.log("LONG ENTRY: Golden cross (fast MA crossed above medium MA)")
                return True
                
            # entry signal 4: Breakout above previous week's high
            high_1w = max([self.data.high[-i] for i in range(1, 6) if i < len(self.data)])
            if close_price > high_1w and prev_close <= high_1w:
                self.log("LONG ENTRY: Breakout above weekly high")
                return True
        
        else:
            if not is_downtrend and close_price > self.ma_slow[0]:
                return False
                
            if (close_price < self.ma_fast[0] and prev_close >= self.ma_fast[0] and
                self.data.volume[0] > self.data.volume[-1] * 1.1):
                self.log("SHORT ENTRY: Price broke below fast MA with volume")
                return True
                
            if (self.rsi[0] < 50 and self.rsi[-1] >= 50 and 
                close_price < self.ma_medium[0]):
                self.log("SHORT ENTRY: RSI crossed below 50 in downtrend")
                return True
                
            if self.crossover_fast < 0 and close_price < self.ma_medium[0]:
                self.log("SHORT ENTRY: Death cross (fast MA crossed below medium MA)")
                return True
                
            low_1w = min([self.data.low[-i] for i in range(1, 6) if i < len(self.data)])
            if close_price < low_1w and prev_close >= low_1w:
                self.log("SHORT ENTRY: Breakdown below weekly low")
                return True
                
        return False

    def update_trend_state(self):
        """
        Update trend state based on price relative to EMAs, 
        moving average alignment, and recent price action.
        """
        if len(self.data) < 2:
            self.in_uptrend = False
            self.in_downtrend = False
            return
            
        close = self.data.close[0]
        ema_fast = self.ema_fast[0]
        ema_slow = self.ema_slow[0]
        
        if np.isnan(ema_fast) or np.isnan(ema_slow) or np.isnan(self.ma_slow[0]):
            self.in_uptrend = True
            self.in_downtrend = True
            return
        
        price_above_ema_fast = close > ema_fast
        price_above_ema_slow = close > ema_slow
        ema_fast_above_ema_slow = ema_fast > ema_slow
        rising_ma_slow = self.ma_slow[0] > self.ma_slow[-1]
        
        price_below_ema_fast = close < ema_fast
        price_below_ema_slow = close < ema_slow
        ema_fast_below_ema_slow = ema_fast < ema_slow
        falling_ma_slow = self.ma_slow[0] < self.ma_slow[-1]

        self.in_uptrend = price_above_ema_fast and (price_above_ema_slow or rising_ma_slow) and (ema_fast_above_ema_slow or rising_ma_slow)
        self.in_downtrend = price_below_ema_fast and (price_below_ema_slow or falling_ma_slow) and (ema_fast_below_ema_slow or falling_ma_slow)
        
        if not self.in_uptrend and not self.in_downtrend and len(self.data) < 200:
            self.in_uptrend = rising_ma_slow or price_above_ema_fast
            self.in_downtrend = falling_ma_slow or price_below_ema_fast

    def update_stop_loss(self):
        """
        Enhanced stop-loss and take profit management with clear exit rules.
        """
        current_price = self.data.close[0]
        pos = self.getposition()

        if not pos.size:
            self.in_trade = False
            self.partial_exit_done = False
            self.profit_target_hit = False
            return

        if self.p.position_type == "long":
            profit_pct = (current_price - self.entry_price) / self.entry_price
        else:
            profit_pct = (self.entry_price - current_price) / self.entry_price

        if self.p.position_type == "long" and current_price >= self.take_profit_price:
            self.log(f"LONG Take Profit Hit at {current_price:.2f}. Profit: {profit_pct:.2%}")
            self.log(f"Take Profit Method: {self.original_tp_method}, Price: {self.take_profit_price:.2f}")
            self.close_position()
            return
        elif self.p.position_type == "short" and current_price <= self.take_profit_price:
            self.log(f"SHORT Take Profit Hit at {current_price:.2f}. Profit: {profit_pct:.2%}")
            self.log(f"Take Profit Method: {self.original_tp_method}, Price: {self.take_profit_price:.2f}")
            self.close_position()
            return

        if self.p.partial_exit and not self.partial_exit_done and profit_pct >= self.p.partial_exit_threshold:
            partial_size = pos.size // 2  # exit 50% of position
            if partial_size > 0:
                if self.p.position_type == "long":
                    self.log(f"LONG Partial Profit: {profit_pct:.2%}. Closing {partial_size} shares at {current_price:.2f}")
                    self.sell(size=partial_size)
                else:
                    self.log(f"SHORT Partial Profit: {profit_pct:.2%}. Closing {partial_size} shares at {current_price:.2f}")
                    self.buy(size=partial_size)
                self.partial_exit_done = True
                
                buffer = 0.002  # 0.2% buffer above/below entry
                if self.p.position_type == "long":
                    self.stop_price = max(self.entry_price * (1 + buffer), self.stop_price)
                else:
                    self.stop_price = min(self.entry_price * (1 - buffer), self.stop_price)
                
                self.log(f"Moving stop to breakeven+ after partial exit: {self.stop_price:.2f}")

        # trailing stop
        if self.p.position_type == "long":
            trail_percent = self.p.risk_percent_long * (0.7 if self.partial_exit_done else 1.0)
            new_stop_candidate = current_price * (1.0 - trail_percent)
            
            if new_stop_candidate > self.stop_price:
                self.log(f"Raising stop: {self.stop_price:.2f} → {new_stop_candidate:.2f}")
                self.stop_price = new_stop_candidate
                
            if current_price <= self.stop_price:
                self.log(f"LONG Stop Hit at {current_price:.2f}. Profit: {profit_pct:.2%}")
                self.close_position()
                
            elif self.partial_exit_done and profit_pct >= self.p.profit_to_risk * self.p.risk_percent_long:
                self.log(f"LONG Extended Profit Target at {current_price:.2f}. Profit: {profit_pct:.2%}")
                self.close_position()

        else:  
            trail_percent = self.p.risk_percent_short * (0.7 if self.partial_exit_done else 1.0)
            new_stop_candidate = current_price * (1.0 + trail_percent)
            
            if new_stop_candidate < self.stop_price:
                self.log(f"Lowering stop: {self.stop_price:.2f} → {new_stop_candidate:.2f}")
                self.stop_price = new_stop_candidate
                
            if current_price >= self.stop_price:
                self.log(f"SHORT Stop Hit at {current_price:.2f}. Profit: {profit_pct:.2%}")
                self.close_position()
                
            elif self.partial_exit_done and profit_pct >= self.p.profit_to_risk * self.p.risk_percent_short:
                self.log(f"SHORT Extended Profit Target at {current_price:.2f}. Profit: {profit_pct:.2%}")
                self.close_position()

    def close_position(self):
        """Close the current position and reset flags."""
        self.close()
        self.order = None
        self.in_trade = False

    def notify_trade(self, trade):
        if trade.isopen:
            self.order = None
            dt = self.data.datetime.datetime(0).strftime('%Y-%m-%d %H:%M:%S')

            trade_type = "LONG" if self.p.position_type == "long" else "SHORT"
            self.completed_trades.append({
                "datetime": dt,
                "buy_or_sell": "BUY",
                "type": trade_type,
                "status": trade.status,
                "size": self.last_trade_size,
                "price": self.last_executed_price,
                "entry_price": self.data.close[0],
                "stop_price": self.stop_price,
                "take_profit_price": self.take_profit_price,
				"value": trade.value,
                "pnl": trade.pnl,
                "pnlcomm": trade.pnlcomm
            })
            self.log(
                f"TRADE OPENED - Type: {trade_type}, Status: {trade.status}, Size: {self.last_trade_size}, Price: {trade.price:.2f}, "
                f"Value: {trade.value:.2f}, Commission: {trade.commission:.2f}, PnL: {trade.pnl:.2f}, PnLComm: {trade.pnlcomm:.2f}"
            )
        if trade.isclosed:
            self.order = None
            dt = self.data.datetime.datetime(0).strftime('%Y-%m-%d %H:%M:%S')

            trade_type = "LONG" if self.p.position_type == "long" else "SHORT"
            self.completed_trades.append({
                "datetime": dt,
                "buy_or_sell": "SELL",
                "type": trade_type,
                "status": trade.status,
                "size": self.last_trade_size,
                "price": self.last_executed_price,
                "entry_price": self.data.close[0],
                "stop_price": self.stop_price,
                "take_profit_price": self.take_profit_price,
				"value": trade.value,
                "pnl": trade.pnl,
                "pnlcomm": trade.pnlcomm
            })
            self.log(
                f"TRADE CLOSED - Type: {trade_type}, Status: {trade.status}, Size: {self.last_trade_size}, Price: {trade.price:.2f}, "
                f"Value: {trade.value:.2f}, Commission: {trade.commission:.2f}, PnL: {trade.pnl:.2f}, PnLComm: {trade.pnlcomm:.2f}"
            )
            
    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.log(f'ORDER COMPLETED - Price: {order.executed.price:.2f}, Size: {order.executed.size}')
            self.last_trade_size = order.executed.size
            self.last_executed_price = order.executed.price
        elif order.status in [order.Canceled]:
            self.log('ORDER CANCELED')
            self.order = None
        elif order.status in [order.Margin]:
            self.log('ORDER MARGIN ISSUE - Not enough cash/margin available')
            self.order = None
        elif order.status in [order.Rejected]:
            self.log('ORDER REJECTED - Check for invalid parameters or after-hours trading')
            self.order = None
        elif order.status in [order.Submitted, order.Accepted]:
            return
            
        if not order.alive():
            self.order = None


# ----------------------------------------------------------------------
# 3) MAIN RUN
# ----------------------------------------------------------------------
def run_backtrader_with_config(config):
    """
    Run backtest with specific stop-loss and take-profit methods from config.
    
    Parameters:
    config (dict): Main configuration
    """
    tinkoff_client = TinkoffDataClient()
    
    run_one_variant = config.get("RUN_ONE_VARIANT", False)
    
    if run_one_variant:
        sl_method = config["STOP_LOSS_METHOD"]
        tp_method = config["TAKE_PROFIT_METHOD"]
        logger.info(f"Running one variant with SL: {sl_method}, TP: {tp_method}")
    
    for ticker_cfg in config["TICKERS"]:
        ticker = ticker_cfg["TICKER"]
        exchange = ticker_cfg["EXCHANGE"]
        start_date = ticker_cfg["START_DATE"]
        end_date = ticker_cfg["END_DATE"]
        interval = ticker_cfg["INTERVAL"]
        
        
        csv_file = config_operator.get_csv_file_path(ticker, start_date, end_date, interval)
        
        try:
            df = tinkoff_client.load_market_data(
                ticker=ticker,
                exchange=exchange,
                interval=interval,
                start_date=start_date,
                end_date=end_date,
                csv_file_name=csv_file
            )
            
            logger.info(f"\n=== Running backtest for {ticker} with SL: {sl_method}, TP: {tp_method} ===")
            
            strategy_config = {
                "TICKER": ticker_cfg["TICKER"],
                "EXCHANGE": ticker_cfg["EXCHANGE"],
                "START_DATE": ticker_cfg["START_DATE"],
                "END_DATE": ticker_cfg["END_DATE"],
                "INTERVAL": ticker_cfg["INTERVAL"],
                "CAPITAL": ticker_cfg["CAPITAL"],
                "RISK_PERCENT": ticker_cfg["RISK_PERCENT"],
                "PROFIT_TO_RISK": ticker_cfg["PROFIT_TO_RISK"],
                "ATR_MULTIPLIER": ticker_cfg["ATR_MULTIPLIER"],
                "ATR_WINDOW": ticker_cfg["ATR_WINDOW"],
                "STOP_LOSS_METHOD": sl_method,
                "TAKE_PROFIT_METHOD": tp_method,
                "POSITION": ticker_cfg.get("POSITION", "long")
            }
            
            backtest_results, completed_trades = backtest(df, strategy_config)
            
            save_plot_and_output(df, backtest_results, ticker, strategy_config, STRATEGIES_RESULTS_PATH, 
                                 completed_trades=completed_trades)
            
            # performance metrics
            initial_balance = strategy_config["CAPITAL"]
            final_balance = backtest_results["Balance"].iloc[-1] if not backtest_results.empty else initial_balance
            profit_loss = final_balance - initial_balance
            profit_percent = (profit_loss / initial_balance) * 100 if initial_balance > 0 else 0
            
            trade_count = backtest_results["Entry"].count()
            wins = backtest_results[backtest_results["Profit/Loss"] > 0].shape[0]
            losses = backtest_results[backtest_results["Profit/Loss"] < 0].shape[0]
            win_rate = (wins / trade_count) * 100 if trade_count > 0 else 0
            
            logger.info(f"Initial Balance: {initial_balance:.2f}")
            logger.info(f"Final Balance: {final_balance:.2f}")
            logger.info(f"Profit/Loss: {profit_loss:.2f} ({profit_percent:.2f}%)")
            logger.info(f"Number of Trades: {trade_count}")
            logger.info(f"Win Rate: {win_rate:.2f}% ({wins} wins, {losses} losses)")
            
        except Exception as e:
            logger.exception(f"Error processing ticker {ticker}: {str(e)}")


# ----------------------------------------------------------------------
# 4) BACKTEST FUNCTION & STRATEGY VARIATIONS
# ----------------------------------------------------------------------
def backtest(data, config):
    """
    Run backtest for a single strategy configuration and return results.
    
    Parameters:
    data (DataFrame): Market data 
    config (dict): Strategy configuration
    
    Returns:
    DataFrame: Results of the backtest with trades and performance
    """
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(config["CAPITAL"])
    cerebro.broker.setcommission(commission=COMMISSION)
    
    data_feed = bt.feeds.PandasData(
        dataname=data,
        timeframe=bt.TimeFrame.Days,
        compression=1
    )

    cerebro.adddata(data_feed)
    
    cerebro.addstrategy(
        MultiStopTakeStrategy,
        stop_loss_method=config["STOP_LOSS_METHOD"],
        take_profit_method=config["TAKE_PROFIT_METHOD"],
        position_type=config["POSITION"],
        risk_percent=config["RISK_PERCENT"],
        profit_to_risk=config["PROFIT_TO_RISK"],
        atr_multiplier=config["ATR_MULTIPLIER"],
        atr_period=config["ATR_WINDOW"]
    )
    
    cerebro.addanalyzer(bt.analyzers.SharpeRatio)
    cerebro.addanalyzer(bt.analyzers.DrawDown)
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer)
    
    # Run backtest
    start_value = cerebro.broker.getvalue()
    results = cerebro.run()
    end_value = cerebro.broker.getvalue()
    strat = results[0]
    
    trades_df = pd.DataFrame(strat.completed_trades)
    
    balance_values = [start_value]
    current_balance = start_value
    
    results_df = pd.DataFrame({
        "Date": data.index,
        "Close": data["close"],
        "Balance": [start_value] * len(data)
    })
    
    if not trades_df.empty:
        for idx, trade in trades_df.iterrows():
            trade_date = datetime.strptime(trade["datetime"], '%Y-%m-%d %H:%M:%S')
            
            date_series = results_df["Date"]
            if hasattr(date_series.dtype, 'tz') and date_series.dtype.tz is not None:
                date_series = date_series.dt.tz_localize(None)
            
            pd_trade_date = pd.Timestamp(trade_date)
            
            mask = date_series >= pd_trade_date
            if mask.any():
                trade_date_idx = mask.idxmax()
                
                current_balance += trade["pnl"]
                results_df.loc[trade_date_idx:, "Balance"] = current_balance
                
                results_df.loc[trade_date_idx, "Entry"] = trade["entry_price"]
                results_df.loc[trade_date_idx, "Type"] = trade["type"]
                results_df.loc[trade_date_idx, "Stop_Loss"] = trade["stop_price"]  
                results_df.loc[trade_date_idx, "Take_Profit"] = trade["take_profit_price"]
                results_df.loc[trade_date_idx, "Profit/Loss"] = trade["pnl"]

    return results_df, strat.completed_trades

def run_all_variants(data, main_config, ticker):
    """
    Run backtests for all combinations of stop-loss and take-profit methods for a ticker.
    Saves results to compare_results_{ticker}.csv
    
    Parameters:
    data (DataFrame): Market data
    main_config (dict): Main configuration with strategy options
    ticker (str): Ticker symbol to test
    
    Returns:
    DataFrame: Comparison of all strategy combinations
    """
    sl_methods = main_config["STOP_LOSS_METHODS"]
    tp_methods = main_config["TAKE_PROFIT_METHODS"]

    ticker_config = next((item for item in main_config["TICKERS"] if item["TICKER"] == ticker), None)
    if ticker_config is None:
        logger.warning(f"Configuration for ticker {ticker} not found.")
        return None

    results_list = []
    for slm in sl_methods:
        for tpm in tp_methods:
            local_config = {            
                "TICKER": ticker_config["TICKER"],
                "EXCHANGE": ticker_config["EXCHANGE"],
                "START_DATE": ticker_config["START_DATE"],
                "END_DATE": ticker_config["END_DATE"],
                "INTERVAL": ticker_config["INTERVAL"],
                "CAPITAL": ticker_config["CAPITAL"],
                "RISK_PERCENT": ticker_config["RISK_PERCENT"],
                "PROFIT_TO_RISK": ticker_config["PROFIT_TO_RISK"],
                "ATR_MULTIPLIER": ticker_config["ATR_MULTIPLIER"],
                "ATR_WINDOW": ticker_config["ATR_WINDOW"],
                "STOP_LOSS_METHOD": slm,
                "TAKE_PROFIT_METHOD": tpm,
                "POSITION": ticker_config.get("POSITION", "long")
            }

            # Run backtest
            bt_results, completed_trades = backtest(data, local_config)
            final_balance = bt_results["Balance"].iloc[-1] if not bt_results.empty else local_config["CAPITAL"]
            trade_count = bt_results["Entry"].count()
            
            profit_losses = bt_results["Profit/Loss"].dropna()
            non_zero_trades = profit_losses[profit_losses != 0]
            wins = non_zero_trades[non_zero_trades > 0].shape[0]
            losses = non_zero_trades[non_zero_trades < 0].shape[0]
            win_rate = wins / (wins + losses) if (wins + losses) else 0

            save_plot_and_output(data, bt_results, ticker, local_config, STRATEGIES_RESULTS_PATH,
                                completed_trades=completed_trades)

            results_list.append({
                "Ticker": ticker,
                "Stop_Loss_Method": slm,
                "Take_Profit_Method": tpm,
                "Final_Balance": final_balance,
                "Trades": trade_count,
                "Win_Rate (%)": round(win_rate * 100, 2)
            })

    df_compare = pd.DataFrame(results_list)
    compare_file_name = os.path.join(RESULTS_PATH,
                                   f"compare_results_{ticker}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv")
    df_compare.to_csv(compare_file_name, index=False)
    logger.info(f"Comparative test results for {ticker} saved to {compare_file_name}")
    return df_compare

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("backtrader_complex.log"),
            logging.StreamHandler()
        ]
    )
    
    global RESULTS_PATH, STRATEGIES_RESULTS_PATH
    RESULTS_PATH = "results_bt_complex"
    STRATEGIES_RESULTS_PATH = os.path.join(RESULTS_PATH, "strategies")
    
    os.makedirs(RESULTS_PATH, exist_ok=True)
    os.makedirs(STRATEGIES_RESULTS_PATH, exist_ok=True)
    
    try:
        config = config_operator.load_config()
        if not config_operator.validate_config():
            logger.error("Invalid configuration. Exiting.")
            return
        
        if config["TICKERS"]:
            tinkoff_client = TinkoffDataClient()

        run_variants = config.get("RUN_ALL_VARIANTS", False)
        
        if run_variants:
            tinkoff_client = TinkoffDataClient()
            
            for ticker_cfg in config["TICKERS"]:
                ticker = ticker_cfg["TICKER"]
                exchange = ticker_cfg["EXCHANGE"]
                start_date = ticker_cfg["START_DATE"]
                end_date = ticker_cfg["END_DATE"]
                interval = ticker_cfg["INTERVAL"]
                
                csv_file = config_operator.get_csv_file_path(ticker, start_date, end_date, interval)
                
                try:
                    df = tinkoff_client.load_market_data(
                        ticker=ticker,
                        exchange=exchange,
                        interval=interval,
                        start_date=start_date,
                        end_date=end_date,
                        csv_file_name=csv_file
                    )
                    
                    run_all_variants(df, config, ticker)
                    
                except Exception as e:
                    logger.exception(f"Error processing ticker {ticker}: {str(e)}")
        else:
            run_backtrader_with_config(config)
            
    except FileNotFoundError:
        logger.error(f"Config file '{CONFIG_FILE}' not found.")
        return
    except Exception as e:
        logger.exception("Error running backtrader")


if __name__ == "__main__":
    main()
