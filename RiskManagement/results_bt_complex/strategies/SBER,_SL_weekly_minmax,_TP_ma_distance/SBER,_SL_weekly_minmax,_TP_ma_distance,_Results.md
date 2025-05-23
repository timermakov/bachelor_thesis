# Результаты торговой стратегии для SBER

**Дата:** 2025-05-17 12:23:36  
**Стратегия:** SBER,_SL_weekly_minmax,_TP_ma_distance

## Конфигурация

```json
{
    "TICKER": "SBER",
    "EXCHANGE": "MOEX",
    "START_DATE": "2023-01-01",
    "END_DATE": "2024-12-31",
    "INTERVAL": "1d",
    "CAPITAL": 1000000,
    "RISK_PERCENT": 0.02,
    "PROFIT_TO_RISK": 3,
    "ATR_MULTIPLIER": 1.5,
    "ATR_WINDOW": 14,
    "STOP_LOSS_METHOD": "weekly_minmax",
    "TAKE_PROFIT_METHOD": "ma_distance",
    "POSITION": "long"
}
```

## Метрики эффективности

- **Начальный баланс:** 1000000.00
- **Конечный баланс:** 1154468.46
- **Прибыль/Убыток:** 154468.46 (15.45% за период тестирования)
- **Количество сделок:** 25
- **Процент выигрышных сделок:** 40.00% (10 выигрышных, 15 убыточных)
- **Средняя прибыль:** 38093.99
- **Средний убыток:** -15098.10
- **Максимальная прибыль:** 97883.65
- **Максимальный убыток:** -28511.40
- **Коэффициент прибыли:** 1.68
- **Максимальная просадка:** -6.32%

## Графики

### График цены с уровнями риска

![График цены с уровнями риска](SBER,_SL_weekly_minmax,_TP_ma_distance,_Price_Risk_Levels.jpg)

### График баланса счёта

![График баланса счёта](SBER,_SL_weekly_minmax,_TP_ma_distance,_Balance.jpg)

## Завершённые сделки

**Всего сделок:** 51

| Сделка № | Дата | Тип | Покупка / продажа | Количество акций | Цена | Stop Loss в момент сделки | Take Profit в момент сделки | Прибыль / убыток | Прибыль / убыток с учётом комиссии |
|:--------:|:----:|:---:|:-----------------:|:----------------:|:----:|:-------------------------:|:---------------------------:|:----------------:|:----------------------------------:|
| 1 | 2023-03-20 00:00:00 | LONG | BUY | 2395 | 196.02 | 169.26 | 249.50 | 0.00 | -234.73 |
| 2 | 2023-05-04 00:00:00 | LONG | SELL | -2395 | 236.89 | 237.77 | 249.50 | 97883.65 | 97365.24 |
| 3 | 2023-05-19 00:00:00 | LONG | BUY | 1874 | 230.99 | 226.15 | 256.32 | 0.00 | -216.44 |
| 4 | 2023-05-31 00:00:00 | LONG | SELL | -1874 | 244.00 | 246.16 | 256.32 | 24380.74 | 23935.67 |
| 5 | 2023-06-08 00:00:00 | LONG | BUY | 2032 | 241.30 | 232.54 | 259.43 | 0.00 | -245.16 |
| 6 | 2023-06-26 00:00:00 | LONG | SELL | -2032 | 239.60 | 240.28 | 259.43 | -3454.40 | -3942.99 |
| 7 | 2023-07-04 00:00:00 | LONG | BUY | 2280 | 243.40 | 236.80 | 249.83 | 0.00 | -277.48 |
| 8 | 2023-07-21 00:00:00 | LONG | SELL | -2280 | 243.18 | 244.41 | 249.83 | -501.60 | -1056.30 |
| 9 | 2023-07-25 00:00:00 | LONG | BUY | 3191 | 245.48 | 241.70 | 250.29 | 0.00 | -391.66 |
| 10 | 2023-08-01 00:00:00 | LONG | SELL | -3191 | 269.00 | 244.26 | 250.29 | 75052.32 | 74231.47 |
| 11 | 2023-08-02 00:00:00 | LONG | BUY | 2827 | 268.50 | 245.90 | 305.70 | 0.00 | -379.52 |
| 12 | 2023-08-08 00:00:00 | LONG | SELL | -2827 | 261.92 | 263.73 | 305.70 | -18601.66 | -19351.41 |
| 13 | 2023-08-21 00:00:00 | LONG | BUY | 2477 | 262.44 | 254.33 | 282.81 | 0.00 | -325.03 |
| 14 | 2023-09-08 00:00:00 | LONG | SELL | -2477 | 258.08 | 262.04 | 282.81 | -10799.72 | -11444.38 |
| 15 | 2023-09-13 00:00:00 | LONG | BUY | 2700 | 262.40 | 253.10 | 272.16 | 0.00 | -354.24 |
| 16 | 2023-09-20 00:00:00 | LONG | SELL | -2700 | 252.80 | 255.61 | 272.16 | -25920.00 | -26615.52 |
| 17 | 2023-10-02 00:00:00 | LONG | BUY | 2198 | 261.37 | 249.83 | 264.41 | 0.00 | -287.25 |
| 18 | 2023-10-10 00:00:00 | LONG | SELL | -2198 | 264.89 | 257.67 | 264.41 | 7736.96 | 7158.60 |
| 19 | 2023-10-17 00:00:00 | LONG | BUY | 2781 | 268.30 | 257.00 | 282.10 | 0.00 | -373.07 |
| 20 | 2023-11-14 00:00:00 | LONG | SELL | -2781 | 283.70 | 274.59 | 282.10 | 42827.40 | 42059.84 |
| 21 | 2023-11-20 00:00:00 | LONG | BUY | 2939 | 281.96 | 278.51 | 308.48 | 0.00 | -414.34 |
| 22 | 2023-11-29 00:00:00 | LONG | SELL | -2939 | 279.36 | 281.11 | 308.48 | -7641.40 | -8466.26 |
| 23 | 2023-12-06 00:00:00 | LONG | BUY | 2318 | 279.92 | 270.52 | 291.26 | 0.00 | -324.43 |
| 24 | 2023-12-07 00:00:00 | LONG | SELL | -2318 | 267.62 | 270.52 | 291.26 | -28511.40 | -29146.00 |
| 25 | 2024-01-04 00:00:00 | LONG | BUY | 2649 | 274.67 | 268.52 | 285.10 | 0.00 | -363.80 |
| 26 | 2024-02-13 00:00:00 | LONG | SELL | -2649 | 287.52 | 278.72 | 285.10 | 34039.65 | 33295.03 |
| 27 | 2024-02-15 00:00:00 | LONG | BUY | 2852 | 289.30 | 281.25 | 313.24 | 0.00 | -412.54 |
| 28 | 2024-02-21 00:00:00 | LONG | SELL | -2852 | 283.90 | 284.44 | 313.24 | -15400.80 | -16218.18 |
| 29 | 2024-02-26 00:00:00 | LONG | BUY | 2855 | 288.52 | 280.20 | 299.88 | 0.00 | -411.86 |
| 30 | 2024-03-11 00:00:00 | LONG | SELL | -2855 | 301.00 | 293.19 | 299.88 | 35630.40 | 34788.86 |
| 31 | 2024-03-18 00:00:00 | LONG | BUY | 2807 | 299.40 | 295.14 | 323.05 | 0.00 | -420.21 |
| 32 | 2024-03-25 00:00:00 | LONG | SELL | -2807 | 294.00 | 295.14 | 323.05 | -15157.80 | -15990.64 |
| 33 | 2024-03-29 00:00:00 | LONG | BUY | 2763 | 299.38 | 291.05 | 316.10 | 0.00 | -413.59 |
| 34 | 2024-04-24 00:00:00 | LONG | SELL | -2763 | 307.50 | 308.69 | 316.10 | 22435.56 | 21597.16 |
| 35 | 2024-04-27 00:00:00 | LONG | BUY | 2723 | 309.25 | 306.26 | 325.60 | 0.00 | -421.04 |
| 36 | 2024-05-07 00:00:00 | LONG | SELL | -2723 | 306.23 | 306.26 | 325.60 | -8223.46 | -9061.44 |
| 37 | 2024-05-08 00:00:00 | LONG | BUY | 2709 | 308.41 | 304.34 | 317.42 | 0.00 | -417.74 |
| 38 | 2024-05-15 00:00:00 | LONG | SELL | -2709 | 318.20 | 308.55 | 317.42 | 26521.11 | 25672.37 |
| 39 | 2024-05-16 00:00:00 | LONG | BUY | 2668 | 320.00 | 308.08 | 341.05 | 0.00 | -426.88 |
| 40 | 2024-05-31 00:00:00 | LONG | SELL | -2668 | 316.00 | 317.07 | 341.05 | -10672.00 | -11520.42 |
| 41 | 2024-06-10 00:00:00 | LONG | BUY | 2209 | 320.80 | 305.00 | 332.16 | 0.00 | -354.32 |
| 42 | 2024-06-20 00:00:00 | LONG | SELL | -2209 | 310.70 | 312.96 | 332.16 | -22310.90 | -23008.39 |
| 43 | 2024-06-25 00:00:00 | LONG | BUY | 1977 | 317.50 | 306.02 | 322.07 | 0.00 | -313.85 |
| 44 | 2024-06-27 00:00:00 | LONG | SELL | -1977 | 324.80 | 313.40 | 322.07 | 14432.10 | 13797.19 |
| 45 | 2024-06-28 00:00:00 | LONG | BUY | 2492 | 327.87 | 312.60 | 346.04 | 0.00 | -408.53 |
| 46 | 2024-07-10 00:00:00 | LONG | SELL | -2492 | 319.00 | 321.80 | 346.04 | -22104.04 | -22910.04 |
| 47 | 2024-09-24 00:00:00 | LONG | BUY | 2065 | 273.90 | 260.55 | 293.58 | 0.00 | -282.80 |
| 48 | 2024-10-02 00:00:00 | LONG | SELL | -2065 | 266.01 | 267.46 | 293.58 | -16292.85 | -16850.31 |
| 49 | 2024-11-12 00:00:00 | LONG | BUY | 1955 | 259.99 | 238.07 | 276.43 | 0.00 | -254.14 |
| 50 | 2024-11-15 00:00:00 | LONG | SELL | -1955 | 249.31 | 250.65 | 276.43 | -20879.40 | -21377.24 |
| 51 | 2024-12-23 00:00:00 | LONG | BUY | 1561 | 260.00 | 223.72 | 295.83 | 0.00 | -202.93 |
