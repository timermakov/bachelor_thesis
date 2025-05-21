import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Параметры
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


def create_combined_plot(df, plots_dir):
    plots_dir = os.path.join(plots_dir, "_Comparison")
    os.makedirs(plots_dir, exist_ok=True)

    sns.set(style="whitegrid")

    # Final Balance
    plt.figure(figsize=(16, 10))
    sns.barplot(x="Ticker", y="Final_Balance", hue="Stop_Loss_Method", data=df)
    plt.title("Финальный баланс по всем акциям")
    plt.ylabel("Final Balance")
    plt.xlabel("Ticker")
    plt.legend(title="Stop Loss Method", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "All_Tickers_Final_Balance_Barplot.png"))
    plt.close()

    # Trades
    plt.figure(figsize=(16, 10))
    sns.barplot(x="Ticker", y="Trades", hue="Stop_Loss_Method", data=df)
    plt.title("Количество сделок по всем акциям")
    plt.ylabel("Trades")
    plt.xlabel("Ticker")
    plt.legend(title="Stop Loss Method", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "All_Tickers_Trades_Barplot.png"))
    plt.close()

    # Win Rate
    plt.figure(figsize=(16, 10))
    sns.barplot(x="Ticker", y="Win_Rate (%)", hue="Stop_Loss_Method", data=df)
    plt.title("Процент выигрышных сделок (%) по всем акциям")
    plt.ylabel("Win Rate (%)")
    plt.xlabel("Ticker")
    plt.legend(title="Stop Loss Method", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "All_Tickers_Win_Rate_Barplot.png"))
    plt.close()

    print(f"Графики сохранены в папке '{plots_dir}'.")


create_combined_plot(data, PLOTS_DIR)
