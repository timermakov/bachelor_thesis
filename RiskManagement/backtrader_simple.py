import os
import math
import logging
import backtrader as bt
from datetime import datetime, time
import pandas as pd
from typing import Dict, Any, Union
import numpy as np

from tinkoff_data import TinkoffDataClient
from config_utils import ConfigFileOperator
from plot_utils import save_plot_and_output


logger = logging.getLogger(__name__)

CONFIG_FILE = "config_ru.json"
CSV_PATH = "csv_data/"
RESULTS_PATH = "results_bt_simple/"

config_operator = ConfigFileOperator(
    config_path=CONFIG_FILE,
    csv_path=CSV_PATH,
    results_path=RESULTS_PATH
)


class ForecastTakeProfit:
    @staticmethod
    def get_take_profit_price(position_type, entry_price):
        if position_type == "long":
            return entry_price * 1.05  # +5%
        else:
            return entry_price * 0.95  # -5%


class LongShortDynamicStopStrategy(bt.Strategy):
    """
    - Longs: max 2% loss, dynamic stop moves up as market rises
    - Shorts: max 1% loss, dynamic stop moves down as market falls
    """
    params = (
        ("position_type", "long"),
        ("risk_percent_long", 0.02),
        ("risk_percent_short", 0.01),
        ("atr_multiplier", 1.5),
        ("atr_period", 14),
    )

    def __init__(self):
        self.order = None
        self.entry_price = None
        self.stop_price = None
        self.take_profit_price = None
        self.in_trade = False
        self.completed_trades = []

        self.atr = bt.ind.ATR(self.data, period=self.p.atr_period)

    def log(self, txt):
        dt = self.datas[0].datetime.datetime(0).strftime('%Y-%m-%d %H:%M:%S')
        logger.info(f"{dt} - {txt}")

    def next(self):
        if self.order:
            return

        pos = self.getposition()

        if not pos.size and not self.in_trade:
            self.open_new_trade()
        else:
            if self.in_trade:
                self.update_stop_loss()

    def calc_size_for_risk(self):
        capital = self.broker.getvalue()
        # 70% of capital
        usable_capital = capital * 0.7
        
        if self.params.position_type == "long":
            risk_percent = self.params.risk_percent_long
        else:
            risk_percent = self.params.risk_percent_short

        risk_alloc = usable_capital * risk_percent
        approximate_stop_dist = self.atr[0] * self.p.atr_multiplier
        if approximate_stop_dist <= 0:
            self.log("Stop distance <= 0, size=0.")
            return 0

        current_price = self.data.close[0]
        max_affordable = int(usable_capital / current_price / 1.5)
        
        size = risk_alloc / approximate_stop_dist
        size = max(int(size), 1)
        
        size = min(size, max_affordable)
        
        if self.data.volume[0] > 0:
            max_volume_percent = 0.05
            max_size = max(int(self.data.volume[0] * max_volume_percent), 1)
            size = min(size, max_size)
            
        self.log(f"Calculated position size: {size} (max affordable: {max_affordable})")
        return size

    def open_new_trade(self):
        size = self.calc_size_for_risk()
        if size <= 0:
            return

        current_price = self.data.close[0]

        if self.params.position_type == "long":
            stop_offset = self.atr[0] * self.p.atr_multiplier
            self.stop_price = current_price - stop_offset
            self.take_profit_price = ForecastTakeProfit.get_take_profit_price("long", current_price)
            
            self.entry_price = current_price
            self.entry_bar = len(self.data)
            
            stop_pct = (self.stop_price/current_price - 1) * 100
            tp_pct = (self.take_profit_price/current_price - 1) * 100
            
            self.log(f"LONG Entry. Price={current_price:.2f}, "
                    f"Stop={self.stop_price:.2f} ({stop_pct:.2f}%), "
                    f"TP={self.take_profit_price:.2f} ({tp_pct:.2f}%), "
                    f"Size={size}")
            
            self.order = self.buy(size=size)
            self.in_trade = True
            
        else: 
            stop_offset = self.atr[0] * self.p.atr_multiplier
            self.stop_price = current_price + stop_offset
            self.take_profit_price = ForecastTakeProfit.get_take_profit_price("short", current_price)
            
            self.entry_price = current_price
            self.entry_bar = len(self.data)
            
            stop_pct = (self.stop_price/current_price - 1) * 100
            tp_pct = (self.take_profit_price/current_price - 1) * 100
            
            self.log(f"SHORT Entry. Price={current_price:.2f}, "
                    f"Stop={self.stop_price:.2f} ({stop_pct:.2f}%), "
                    f"TP={self.take_profit_price:.2f} ({tp_pct:.2f}%), "
                    f"Size={size}")
            
            self.order = self.sell(size=size)
            self.in_trade = True

    def update_stop_loss(self):
        current_price = self.data.close[0]
        pos = self.getposition()

        if not pos.size:
            self.in_trade = False
            return

        if self.params.position_type == "long":
            # For long positions, track highest price to calculate trailing stop
            if not hasattr(self, 'highest_price') or current_price > self.highest_price:
                self.highest_price = current_price
            
            atr_stop = self.highest_price - (self.atr[0] * self.p.atr_multiplier)
            
            if atr_stop > self.stop_price:
                old_stop = self.stop_price
                self.stop_price = atr_stop
                self.log(f"LONG Stop raised from {old_stop:.2f} to {self.stop_price:.2f} (ATR={self.atr[0]:.2f})")
            
            if current_price <= self.stop_price:
                pnl_pct = ((current_price/self.entry_price)-1)*100
                
                self.log(f"LONG Stop Hit at {current_price:.2f}. Stop={self.stop_price:.2f}, Entry={self.entry_price:.2f}, "
                         f"P&L={pnl_pct:.2f}%")
                self.close_position()
                return
            
            if current_price >= self.take_profit_price:
                pnl_pct = ((current_price/self.entry_price)-1)*100
                
                self.log(f"LONG Take Profit Hit at {current_price:.2f}. TP={self.take_profit_price:.2f}, Entry={self.entry_price:.2f}, "
                         f"P&L={pnl_pct:.2f}%")
                self.close_position()
                return

        else:
            if not hasattr(self, 'lowest_price') or current_price < self.lowest_price:
                self.lowest_price = current_price
            
            atr_stop = self.lowest_price + (self.atr[0] * self.p.atr_multiplier)
            
            if atr_stop < self.stop_price:
                old_stop = self.stop_price
                self.stop_price = atr_stop
                self.log(f"SHORT Stop lowered from {old_stop:.2f} to {self.stop_price:.2f} (ATR={self.atr[0]:.2f})")
            
            if current_price >= self.stop_price:
                pnl_pct = ((self.entry_price/current_price)-1)*100
                
                self.log(f"SHORT Stop Hit at {current_price:.2f}. Stop={self.stop_price:.2f}, Entry={self.entry_price:.2f}, "
                         f"P&L={pnl_pct:.2f}%")
                self.close_position()
                return
            
            if current_price <= self.take_profit_price:
                pnl_pct = ((self.entry_price/current_price)-1)*100
                
                self.log(f"SHORT Take Profit Hit at {current_price:.2f}. TP={self.take_profit_price:.2f}, Entry={self.entry_price:.2f}, "
                         f"P&L={pnl_pct:.2f}%")
                self.close_position()
                return

    def close_position(self):
        self.close()
        
        exit_price = self.data.close[0]
        if hasattr(self, 'entry_price') and self.entry_price is not None:
            if self.params.position_type == "long":
                pnl_pct = ((exit_price/self.entry_price)-1)*100
            else: 
                pnl_pct = ((self.entry_price/exit_price)-1)*100
            
            self.log(f"Position closed at {exit_price:.2f}, PnL: {pnl_pct:.2f}%")
        
        self.order = None
        self.in_trade = False
        
        if hasattr(self, 'highest_price'):
            delattr(self, 'highest_price')
        if hasattr(self, 'lowest_price'):
            delattr(self, 'lowest_price')


    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.log(f"ORDER COMPLETED: Price={order.executed.price:.2f}, Size={order.executed.size}")
        elif order.status in [order.Canceled]:
            self.log("ORDER CANCELED")
            self.order = None
        elif order.status in [order.Margin]:
            self.log("ORDER MARGIN ISSUE - Not enough cash/margin available")
            self.order = None
        elif order.status in [order.Rejected]:
            self.log("ORDER REJECTED - Check for invalid parameters or after-hours trading")
            self.order = None
        elif order.status in [order.Submitted, order.Accepted]:
            return
            
        if not order.alive():
            self.order = None

    def notify_trade(self, trade):
        if trade.isclosed:
            pnl = trade.pnl
            pnlcomm = trade.pnlcomm  # PnL with commission
            entry_price = trade.price if hasattr(trade, 'price') else self.entry_price if hasattr(self, 'entry_price') else None
            exit_price = trade.data.close[0] 
            
            formatted_entry = f"{entry_price:.2f}" if entry_price is not None else "0.00"
            self.log(f"TRADE CLOSED: Entry={formatted_entry}, Exit={exit_price:.2f}, " +
                    f"Gross PnL={pnl:.2f}, Net PnL={pnlcomm:.2f}, Size={trade.size}")
            
            self.completed_trades.append({
                "datetime": self.data.datetime.datetime(0).strftime('%Y-%m-%d %H:%M:%S'),
                "entry_price": entry_price,
                "exit_price": exit_price,
                "stop_price": self.stop_price if hasattr(self, 'stop_price') else None,
                "take_profit_price": self.take_profit_price if hasattr(self, 'take_profit_price') else None,
                "pnl": pnl,
                "pnlcomm": pnlcomm,
                "size": trade.size,
                "type": self.params.position_type,
                "buy_or_sell": "buy" if self.params.position_type == "long" else "sell",
                "duration": trade.barlen if hasattr(trade, 'barlen') else 0 
            })
            
            self.entry_price = None
            self.stop_price = None
            self.take_profit_price = None


class CSVData(bt.feeds.GenericCSVData):
    params = (
        ("dtformat", "%Y-%m-%d %H:%M:%S"),
        ("tmformat", ""),
        ("datetime", 0),
        ("open", 1),
        ("high", 2),
        ("low", 3),
        ("close", 4),
        ("volume", 5),
        ("openinterest", -1),
    )


def run_strategy(config):
    """
    Run the backtrader strategy with the provided configuration
    
    Args:
        config: Configuration dictionary from load_config
    """
    tinkoff_client = TinkoffDataClient()

    for ticker_config in config["TICKERS"]:
        cerebro = bt.Cerebro()
        cerebro.broker.setcash(ticker_config["CAPITAL"])
        
        cerebro.broker.setcommission(commission=0.0005)  # 0.05% commission
        cerebro.broker.set_slippage_perc(0.001)  # 0.1% slip
        
        ticker = ticker_config["TICKER"]
        exchange = ticker_config["EXCHANGE"]
        start_date = ticker_config["START_DATE"]
        end_date = ticker_config["END_DATE"]
        interval = ticker_config["INTERVAL"]

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
            
            bt_df = tinkoff_client.convert_tinkoff_df_to_bt(df)
            bt_df.to_csv(csv_file, index=False)
            
            data_feed = CSVData(
                dataname=csv_file,
                fromdate=ConfigFileOperator.try_parse_datetime(start_date),
                todate=ConfigFileOperator.try_parse_datetime(end_date),
                timeframe=bt.TimeFrame.Minutes if interval in ['1m', '5m', '15m', '1h', '4h'] else
                          bt.TimeFrame.Days if interval in ['1d'] else
                          bt.TimeFrame.Weeks if interval in ['1w'] else
                          bt.TimeFrame.Months,
                compression=1 if interval in ['1m', '1d', '1w', '1M'] else
                           5 if interval == '5m' else
                           15 if interval == '15m' else
                           60 if interval == '1h' else
                           240,
            )
            cerebro.adddata(data_feed, name=ticker)
            
            # market session hours
            if interval in ['1m', '5m', '15m', '1h', '4h']:
                data_feed.sessionstart = time(9, 50)
                data_feed.sessionend = time(18, 39)
            
            position_type = ticker_config.get("POSITION", "long")
            
            cerebro.addstrategy(
                LongShortDynamicStopStrategy,
                position_type=position_type,
                risk_percent_long=0.04,
                risk_percent_short=0.02
            )
            
            logger.info(f"=== Running strategy for Ticker: {ticker} ===")
            start_value = cerebro.broker.getvalue()
            logger.info(f"Start portfolio value: {start_value:.2f}")
            results = cerebro.run()
            end_value = cerebro.broker.getvalue()
            logger.info(f"End portfolio value: {end_value:.2f}")
            
            strat_instance = results[0]
            
            df = pd.DataFrame(strat_instance.completed_trades)
            logger.info("\n--- Completed Trades ---")
            if not df.empty:
                logger.info(f"\n{df}")
                total_trades = len(df)
                total_pnl = df["pnl"].sum()
                avg_pnl = df["pnl"].mean()
                max_win = df["pnl"].max()
                max_loss = df["pnl"].min()
                wins = len(df[df["pnl"] > 0])
                
                logger.info("\n--- Summary Stats ---")
                logger.info(f"Total Trades: {total_trades}")
                logger.info(f"Win Rate: {wins / total_trades:.2%}")
                logger.info(f"Total PnL: {total_pnl:.2f}")
                logger.info(f"Total PnL (%): {total_pnl / start_value * 100 :.2f}%")
                logger.info(f"Avg PnL: {avg_pnl:.2f}")
                logger.info(f"Max Win: {max_win:.2f}")
                logger.info(f"Max Loss: {max_loss:.2f}")
            else:
                logger.info("No trades completed.")
            
            # Realtime plot
            cerebro.plot()
            
            try:
                bt_data = pd.DataFrame()
                bt_data['datetime'] = data_feed.lines.datetime.array
                bt_data['close'] = data_feed.lines.close.array
                bt_data['open'] = data_feed.lines.open.array
                bt_data['high'] = data_feed.lines.high.array
                bt_data['low'] = data_feed.lines.low.array
                bt_data['datetime'] = bt_data['datetime'].apply(lambda x: bt.num2date(x) if x != 0 else None)
                bt_data = bt_data.dropna(subset=['datetime'])
                bt_data = bt_data.set_index('datetime')
                
                results_df = pd.DataFrame()
                
                if not df.empty:
                    all_dates = bt_data.index.tolist()
                    results_df = pd.DataFrame(index=all_dates)
                    results_df.index.name = 'Date'
                    results_df = results_df.reset_index()
                    
                    results_df['Balance'] = start_value
                    
                    results_df['Entry'] = None
                    results_df['Stop_Loss'] = None
                    results_df['Take_Profit'] = None
                    results_df['Profit/Loss'] = 0
                    
                    cumulative_pnl = 0
                    for i, trade in df.iterrows():
                        trade_date = datetime.strptime(trade['datetime'], '%Y-%m-%d %H:%M:%S')
                        trade_date_idx = None
                        
                        date_diffs = [(j, abs((date - trade_date).total_seconds())) 
                                     for j, date in enumerate(results_df['Date'])]
                        date_diffs.sort(key=lambda x: x[1])
                        if date_diffs:
                            trade_date_idx = date_diffs[0][0]
                            
                        if trade_date_idx is not None:
                            results_df.loc[trade_date_idx, 'Entry'] = trade.get('entry_price')
                            results_df.loc[trade_date_idx, 'Stop_Loss'] = trade.get('stop_price')
                            results_df.loc[trade_date_idx, 'Take_Profit'] = trade.get('take_profit_price')
                            results_df.loc[trade_date_idx, 'Profit/Loss'] = trade.get('pnl', 0)
                            
                            cumulative_pnl += trade.get('pnl', 0)
                            
                            results_df.loc[trade_date_idx:, 'Balance'] = start_value + cumulative_pnl
                else:
                    # No trades
                    results_df['Date'] = bt_data.index.tolist()
                    results_df['Balance'] = start_value
                    results_df['Entry'] = None
                    results_df['Stop_Loss'] = None
                    results_df['Take_Profit'] = None
                    results_df['Profit/Loss'] = 0
                
                enhanced_config = ticker_config.copy()
                enhanced_config['STOP_LOSS_METHOD'] = 'Dynamic'
                enhanced_config['TAKE_PROFIT_METHOD'] = 'Forecast'
                enhanced_config['CAPITAL'] = start_value
                
                save_plot_and_output(
                    data=bt_data,
                    results=results_df,
                    ticker=ticker,
                    config=enhanced_config,
                    strategies_results_path=RESULTS_PATH,
                    completed_trades=df.to_dict('records') if not df.empty else []
                )
                logger.info("Successfully saved results to files")
            except Exception as e:
                logger.exception(f"Error saving results: {str(e)}")
            
        except Exception as e:
            logger.exception(f"Error processing ticker {ticker}: {str(e)}")


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("backtrader_simple.log"),
            logging.StreamHandler()
        ]
    )
    
    try:
        config = config_operator.load_config()
        if not config_operator.validate_config():
            logger.error("Invalid configuration. Exiting.")
            return
        
        run_strategy(config)
    except FileNotFoundError:
        logger.error(f"Config file '{CONFIG_FILE}' not found.")
        return
    except Exception as e:
        logger.exception("Error running strategy")


if __name__ == "__main__":
    main()
