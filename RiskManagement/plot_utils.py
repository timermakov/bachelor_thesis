import os
import json
import matplotlib.pyplot as plt
from datetime import datetime
import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def plot_results(data, results, ticker):
    """
    Visualizes backtest results
    
    Parameters:
    data (DataFrame): The price data with risk management levels
    results (DataFrame): Portfolio results over time
    ticker (str): The stock ticker symbol
    """
    plt.figure(figsize=(14, 7))
    plt.plot(data.index, data["close"], label="Close", alpha=0.6)
    entries = results.dropna(subset=["Entry"])
    plt.scatter(entries["Date"], entries["Entry"], label="Entry", marker="o", c="green")
    plt.scatter(entries["Date"], entries["Stop_Loss"], label="Stop Loss", marker="x", c="red")
    plt.scatter(entries["Date"], entries["Take_Profit"], label="Take Profit", marker="^", c="blue")

    plt.title(f"Цена с уровнями риска - {ticker}")
    plt.xlabel("Дата")
    plt.ylabel("Цена")
    plt.legend()
    plt.grid(True)
    plt.show()

    plt.figure(figsize=(14, 7))
    plt.plot(results["Date"], results["Balance"], label="Balance", c="green", alpha=0.8)
    plt.title(f"Баланс счёта за период - {ticker}")
    plt.xlabel("Дата")
    plt.ylabel("Баланс")
    plt.grid(True)
    plt.legend()
    plt.show()


def save_plot_and_output(data, results, ticker, config, strategies_results_path="strategies_results/", completed_trades=None):
    """
    Saves charts and information to files.
    
    Parameters:
    data (DataFrame): The price data with risk management levels
    results (DataFrame): Portfolio results over time
    ticker (str): The stock ticker symbol
    config (dict): Configuration used for the backtest
    strategies_results_path (str): Path to save strategy-specific results
    completed_trades (list): List of completed trades with details
    """
    os.makedirs(strategies_results_path, exist_ok=True)
    sl = config.get('STOP_LOSS_METHOD', 'SL')
    tp = config.get('TAKE_PROFIT_METHOD', 'TP')
    strategy_name = f"{ticker},_SL_{sl},_TP_{tp}"
    
    plot_price_file = f"{strategy_name},_Price_Risk_Levels.jpg"
    plot_balance_file = f"{strategy_name},_Balance.jpg"
    output_file = f"{strategy_name},_Results.md"
    
    strategy_path = os.path.join(strategies_results_path, strategy_name)
    os.makedirs(strategy_path, exist_ok=True)
    
    plot_price_path = os.path.join(strategy_path, plot_price_file)
    plot_balance_path = os.path.join(strategy_path, plot_balance_file)
    output_path = os.path.join(strategy_path, output_file)
    
    plt.figure(figsize=(14, 7))
    plt.plot(data.index, data["close"], label="Close Price", alpha=0.6)
    entries = results.dropna(subset=["Entry"])
    plt.scatter(entries["Date"], entries["Entry"], label="Entry", marker="o", c="green")
    plt.scatter(entries["Date"], entries["Stop_Loss"], label="Stop Loss", marker="x", c="red")
    plt.scatter(entries["Date"], entries["Take_Profit"], label="Take Profit", marker="^", c="blue")
    
    plt.title(f"Цена с уровнями риска, акция: {ticker}, SL: {sl}, TP: {tp}")
    plt.xlabel("Дата")
    plt.ylabel("Цена")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(plot_price_path, format="jpg", dpi=300)
    plt.close()
    
    plt.figure(figsize=(14, 7))
    plt.plot(results["Date"], results["Balance"], label="Balance", c="green", alpha=0.8)
    plt.title(f"Баланс счёта за период, акция: {ticker}, SL: {sl}, TP: {tp}")
    plt.xlabel("Дата")
    plt.ylabel("Баланс")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(plot_balance_path, format="jpg", dpi=300)
    plt.close()
    
    # Отчёт (в формате Markdown)
    with open(output_path, "w") as f:
		
        f.write(f"# Результаты торговой стратегии для {ticker}\n\n")
        f.write(f"**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
        f.write(f"**Стратегия:** {strategy_name}\n\n")

        f.write("## Конфигурация\n\n")
        f.write("```json\n")
        json.dump(config, f, indent=4)
        f.write("\n```\n\n")
        
        f.write("## Метрики эффективности\n\n")
        initial_balance = config.get("CAPITAL", 0)
        final_balance = results["Balance"].iloc[-1] if not results.empty else initial_balance
        profit_loss = final_balance - initial_balance
        profit_percent = (profit_loss / initial_balance) * 100 if initial_balance > 0 else 0

        profit_losses = results["Profit/Loss"].dropna()
        non_zero_trades = profit_losses[profit_losses != 0]
        
        win_trades = non_zero_trades[non_zero_trades > 0].shape[0]
        loss_trades = non_zero_trades[non_zero_trades < 0].shape[0]
        trade_count = win_trades + loss_trades
        win_rate = (win_trades / trade_count) * 100 if trade_count > 0 else 0
        
        f.write(f"- **Начальный баланс:** {initial_balance:.2f}\n")
        f.write(f"- **Конечный баланс:** {final_balance:.2f}\n")
        f.write(f"- **Прибыль/Убыток:** {profit_loss:.2f} ({profit_percent:.2f}% за период тестирования)\n")
        f.write(f"- **Количество сделок:** {trade_count}\n")
        f.write(f"- **Процент выигрышных сделок:** {win_rate:.2f}% ({win_trades} выигрышных, {loss_trades} убыточных)\n")
        
        if trade_count > 0:
            if not non_zero_trades.empty:
                avg_profit = non_zero_trades[non_zero_trades > 0].mean() if win_trades > 0 else 0
                avg_loss = non_zero_trades[non_zero_trades < 0].mean() if loss_trades > 0 else 0
                max_profit = non_zero_trades.max() if not non_zero_trades.empty else 0
                max_loss = non_zero_trades.min() if not non_zero_trades.empty else 0
                profit_factor = abs(non_zero_trades[non_zero_trades > 0].sum() / non_zero_trades[non_zero_trades < 0].sum()) if loss_trades > 0 and non_zero_trades[non_zero_trades < 0].sum() != 0 else 0
                
                f.write(f"- **Средняя прибыль:** {avg_profit:.2f}\n")
                f.write(f"- **Средний убыток:** {avg_loss:.2f}\n")
                f.write(f"- **Максимальная прибыль:** {max_profit:.2f}\n")
                f.write(f"- **Максимальный убыток:** {max_loss:.2f}\n")
                f.write(f"- **Коэффициент прибыли:** {profit_factor:.2f}\n")
                
                balance_series = results["Balance"].dropna()
                if not balance_series.empty:
                    max_balance = balance_series.cummax()
                    drawdown = (balance_series - max_balance) / max_balance * 100
                    max_drawdown = drawdown.min()
                    f.write(f"- **Максимальная просадка:** {max_drawdown:.2f}%\n")
    
	
        f.write("\n## Графики\n\n")
        f.write(f"### График цены с уровнями риска\n\n")
        f.write(f"![График цены с уровнями риска]({plot_price_file})\n\n")
        f.write(f"### График баланса счёта\n\n")
        f.write(f"![График баланса счёта]({plot_balance_file})\n\n")
        

        f.write("## Завершённые сделки\n\n")
        if completed_trades and len(completed_trades) > 0:
            trades_df = pd.DataFrame(completed_trades)
            if "datetime" in trades_df.columns:
                f.write(f"**Всего сделок:** {len(trades_df)}\n\n")
                f.write("| Сделка № | Дата | Тип | Покупка / продажа | Количество акций | Цена | Stop Loss в момент сделки | Take Profit в момент сделки | Прибыль / убыток | Прибыль / убыток с учётом комиссии |\n")
                f.write("|:--------:|:----:|:---:|:-----------------:|:----------------:|:----:|:-------------------------:|:---------------------------:|:----------------:|:----------------------------------:|\n")
                
                for i, trade in trades_df.iterrows():
                    date_str = trade.get("datetime", "N/A")
                    trade_type = trade.get("type", "N/A")
                    buy_or_sell = trade.get("buy_or_sell", "N/A")
                    size = trade.get("size", "N/A")
                    price = trade.get("price", 0)
                    stop = trade.get("stop_price", 0)
                    tp = trade.get("take_profit_price", 0)
                    pnl = trade.get("pnl", 0)
                    pnlcomm = trade.get("pnlcomm", 0)
                    
                    try:
                        price = float(price) if price != "N/A" else 0
                        stop = float(stop) if stop != "N/A" else 0
                        tp = float(tp) if tp != "N/A" else 0
                        pnl = float(pnl)
                        pnlcomm = float(pnlcomm)
                        
                        f.write(f"| {i+1} | {date_str} | {trade_type} | {buy_or_sell} | {size} | {price:.2f} | {stop:.2f} | {tp:.2f} | {pnl:.2f} | {pnlcomm:.2f} |\n")
                    except (ValueError, TypeError):
                        f.write(f"| {i+1} | {date_str} | {trade_type} | {buy_or_sell} | {size} | {price} | {stop} | {tp} | {pnl} | {pnlcomm} |\n")
            else:
                f.write("*Нет информации о сделках*\n\n")
                f.write("```\n")
                f.write(str(trades_df))
                f.write("\n```\n")
        else:
            f.write("*Нет завершённых сделок*\n")
    
    logger.info(f"Saved plots to: {plot_price_path} and {plot_balance_path}")
    logger.info(f"Saved results to: {output_path}")
    