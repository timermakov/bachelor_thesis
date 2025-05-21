import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


RESULTS_DIR = "results_bt_complex/"
PLOTS_DIR = "plots_bt_complex/"


os.makedirs(PLOTS_DIR, exist_ok=True)


def load_all_csvs(directory):
    all_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.csv')]
    df_list = []
    for file in all_files:
        try:
            df = pd.read_csv(file)
            required_columns = ["Ticker", "Stop_Loss_Method", "Take_Profit_Method", "Final_Balance", "Trades",
                                "Win_Rate (%)"]
            if all(col in df.columns for col in required_columns):
                df_list.append(df)
            else:
                print(f"Файл {file} пропущен из-за отсутствия необходимых столбцов.")
        except Exception as e:
            print(f"Ошибка при чтении файла {file}: {e}")
    if df_list:
        combined_df = pd.concat(df_list, ignore_index=True)
        return combined_df
    else:
        print("Нет валидных CSV-файлов для чтения.")
        return pd.DataFrame()


data = load_all_csvs(RESULTS_DIR)

if data.empty:
    raise ValueError("Нет данных в CSV-файлах в директории 'results/'.")


def create_plots(df, plots_dir):
    tickers = df['Ticker'].unique()

    for ticker in tickers:
        plots_dir = os.path.join(PLOTS_DIR, ticker)
        os.makedirs(plots_dir, exist_ok=True)  

        ticker_df = df[df['Ticker'] == ticker]

        pivot_balance = ticker_df.pivot_table(values="Final_Balance", index="Stop_Loss_Method",
                                              columns="Take_Profit_Method", aggfunc="mean")
        pivot_trades = ticker_df.pivot_table(values="Trades", index="Stop_Loss_Method", columns="Take_Profit_Method",
                                             aggfunc="mean")
        pivot_win_rate = ticker_df.pivot_table(values="Win_Rate (%)", index="Stop_Loss_Method",
                                               columns="Take_Profit_Method", aggfunc="mean")

        sns.set(style="whitegrid")

        # Final Balance
        plt.figure(figsize=(12, 8))
        sns.heatmap(pivot_balance, annot=True, fmt=".2f", cmap="YlGnBu")
        plt.title(f"Финальный баланс по результатам торговли {ticker}")
        plt.ylabel("Stop Loss Method")
        plt.xlabel("Take Profit Method")
        plt.tight_layout()
        plt.savefig(os.path.join(plots_dir, f"{ticker}_Final_Balance_Heatmap.png"))
        plt.close()

        # Trades
        plt.figure(figsize=(12, 8))
        sns.heatmap(pivot_trades, annot=True, fmt=".0f", cmap="YlOrRd")
        plt.title(f"Количество сделок для {ticker}")
        plt.ylabel("Stop Loss Method")
        plt.xlabel("Take Profit Method")
        plt.tight_layout()
        plt.savefig(os.path.join(plots_dir, f"{ticker}_Trades_Heatmap.png"))
        plt.close()

        # Win Rate (%)
        plt.figure(figsize=(12, 8))
        sns.heatmap(pivot_win_rate, annot=True, fmt=".2f", cmap="coolwarm")
        plt.title(f"Процент выигрышных сделок (%) для {ticker}")
        plt.ylabel("Stop Loss Method")
        plt.xlabel("Take Profit Method")
        plt.tight_layout()
        plt.savefig(os.path.join(plots_dir, f"{ticker}_Win_Rate_Heatmap.png"))
        plt.close()

        # Барплоты
        # Final Balance
        plt.figure(figsize=(14, 7))
        sns.barplot(x="Stop_Loss_Method", y="Final_Balance", hue="Take_Profit_Method", data=ticker_df)
        plt.title(f"Финальный баланс по результатам торговли {ticker} по методам Stop Loss и Take Profit")
        plt.ylabel("Final Balance")
        plt.xlabel("Stop Loss Method")
        plt.legend(title="Take Profit Method", bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(os.path.join(plots_dir, f"{ticker}_Final_Balance_Barplot.png"))
        plt.close()

        # Trades
        plt.figure(figsize=(14, 7))
        sns.barplot(x="Stop_Loss_Method", y="Trades", hue="Take_Profit_Method", data=ticker_df)
        plt.title(f"Количество сделок по результатам торговли {ticker} по методам Stop Loss и Take Profit")
        plt.ylabel("Trades")
        plt.xlabel("Stop Loss Method")
        plt.legend(title="Take Profit Method", bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(os.path.join(plots_dir, f"{ticker}_Trades_Barplot.png"))
        plt.close()

        # Win Rate (%)
        plt.figure(figsize=(14, 7))
        sns.barplot(x="Stop_Loss_Method", y="Win_Rate (%)", hue="Take_Profit_Method", data=ticker_df)
        plt.title(f"Win Rate (%) по результатам торговли {ticker} по методам Stop Loss и Take Profit")
        plt.ylabel("Win Rate (%)")
        plt.xlabel("Stop Loss Method")
        plt.legend(title="Take Profit Method", bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(os.path.join(plots_dir, f"{ticker}_Win_Rate_Barplot.png"))
        plt.close()

        print(f"Графики для акции {ticker} сохранены в директории '{plots_dir}'.")


create_plots(data, PLOTS_DIR)
