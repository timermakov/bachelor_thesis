# Результаты торговой стратегии для AFLT

**Дата:** 2025-05-17 12:23:04  
**Стратегия:** AFLT,_SL_MA_50_18,_TP_weekly_minmax

## Конфигурация

```json
{
    "TICKER": "AFLT",
    "EXCHANGE": "MOEX",
    "START_DATE": "2023-01-01",
    "END_DATE": "2024-12-31",
    "INTERVAL": "1d",
    "CAPITAL": 1000000,
    "RISK_PERCENT": 0.02,
    "PROFIT_TO_RISK": 3,
    "ATR_MULTIPLIER": 1.5,
    "ATR_WINDOW": 14,
    "STOP_LOSS_METHOD": "MA_50_18",
    "TAKE_PROFIT_METHOD": "weekly_minmax",
    "POSITION": "long"
}
```

## Метрики эффективности

- **Начальный баланс:** 1000000.00
- **Конечный баланс:** 1091263.59
- **Прибыль/Убыток:** 91263.59 (9.13% за период тестирования)
- **Количество сделок:** 40
- **Процент выигрышных сделок:** 57.50% (23 выигрышных, 17 убыточных)
- **Средняя прибыль:** 14423.87
- **Средний убыток:** -14146.20
- **Максимальная прибыль:** 32602.15
- **Максимальный убыток:** -30653.76
- **Коэффициент прибыли:** 1.38
- **Максимальная просадка:** -4.16%

## Графики

### График цены с уровнями риска

![График цены с уровнями риска](AFLT,_SL_MA_50_18,_TP_weekly_minmax,_Price_Risk_Levels.jpg)

### График баланса счёта

![График баланса счёта](AFLT,_SL_MA_50_18,_TP_weekly_minmax,_Balance.jpg)

## Завершённые сделки

**Всего сделок:** 81

| Сделка № | Дата | Тип | Покупка / продажа | Количество акций | Цена | Stop Loss в момент сделки | Take Profit в момент сделки | Прибыль / убыток | Прибыль / убыток с учётом комиссии |
|:--------:|:----:|:---:|:-----------------:|:----------------:|:----:|:-------------------------:|:---------------------------:|:----------------:|:----------------------------------:|
| 1 | 2023-03-17 00:00:00 | LONG | BUY | 19045 | 28.29 | 27.88 | 29.00 | 0.00 | -269.39 |
| 2 | 2023-03-21 00:00:00 | LONG | SELL | -19045 | 29.86 | 27.88 | 29.00 | 29900.65 | 29346.92 |
| 3 | 2023-03-28 00:00:00 | LONG | BUY | 13295 | 33.25 | 28.61 | 33.46 | 0.00 | -221.03 |
| 4 | 2023-04-03 00:00:00 | LONG | SELL | -13295 | 31.50 | 32.09 | 33.46 | -23266.25 | -23696.68 |
| 5 | 2023-04-11 00:00:00 | LONG | BUY | 10701 | 34.96 | 30.63 | 35.47 | 0.00 | -187.05 |
| 6 | 2023-04-18 00:00:00 | LONG | SELL | -10701 | 36.28 | 33.96 | 35.47 | 14125.32 | 13744.15 |
| 7 | 2023-04-20 00:00:00 | LONG | BUY | 9989 | 37.71 | 32.88 | 38.01 | 0.00 | -188.34 |
| 8 | 2023-04-21 00:00:00 | LONG | SELL | -9989 | 39.20 | 32.88 | 38.01 | 14883.61 | 14499.48 |
| 9 | 2023-04-27 00:00:00 | LONG | BUY | 8662 | 39.07 | 34.83 | 40.18 | 0.00 | -169.21 |
| 10 | 2023-05-02 00:00:00 | LONG | SELL | -8662 | 40.47 | 39.25 | 40.18 | 12126.80 | 11782.31 |
| 11 | 2023-05-11 00:00:00 | LONG | BUY | 7384 | 38.49 | 37.14 | 40.38 | 0.00 | -142.11 |
| 12 | 2023-05-30 00:00:00 | LONG | SELL | -7384 | 39.78 | 39.35 | 40.38 | 9525.36 | 9236.39 |
| 13 | 2023-06-05 00:00:00 | LONG | BUY | 9505 | 40.07 | 38.72 | 41.36 | 0.00 | -190.43 |
| 14 | 2023-06-16 00:00:00 | LONG | SELL | -9505 | 43.50 | 40.36 | 41.36 | 32602.15 | 32204.98 |
| 15 | 2023-06-28 00:00:00 | LONG | BUY | 9829 | 42.51 | 40.81 | 44.12 | 0.00 | -208.92 |
| 16 | 2023-07-05 00:00:00 | LONG | SELL | -9829 | 41.40 | 42.15 | 44.12 | -10910.19 | -11322.57 |
| 17 | 2023-07-11 00:00:00 | LONG | BUY | 8952 | 42.12 | 41.81 | 42.42 | 0.00 | -188.53 |
| 18 | 2023-07-18 00:00:00 | LONG | SELL | -8952 | 42.70 | 41.81 | 42.42 | 5192.16 | 4812.51 |
| 19 | 2023-07-19 00:00:00 | LONG | BUY | 11455 | 44.48 | 42.00 | 44.46 | 0.00 | -254.76 |
| 20 | 2023-07-26 00:00:00 | LONG | SELL | -11455 | 44.94 | 43.53 | 44.46 | 5269.30 | 4757.15 |
| 21 | 2023-08-01 00:00:00 | LONG | BUY | 12663 | 45.82 | 42.99 | 45.94 | 0.00 | -290.11 |
| 22 | 2023-08-17 00:00:00 | LONG | SELL | -12663 | 43.89 | 44.92 | 45.94 | -24439.59 | -25007.59 |
| 23 | 2023-08-29 00:00:00 | LONG | BUY | 9106 | 44.80 | 43.15 | 45.55 | 0.00 | -203.97 |
| 24 | 2023-09-08 00:00:00 | LONG | SELL | -9106 | 42.59 | 43.49 | 45.55 | -20124.26 | -20522.15 |
| 25 | 2024-01-09 00:00:00 | LONG | BUY | 11333 | 37.60 | 37.14 | 37.81 | 0.00 | -213.06 |
| 26 | 2024-01-15 00:00:00 | LONG | SELL | -11333 | 38.05 | 37.14 | 37.81 | 5099.85 | 4671.18 |
| 27 | 2024-01-30 00:00:00 | LONG | BUY | 15194 | 38.32 | 37.11 | 38.62 | 0.00 | -291.12 |
| 28 | 2024-01-31 00:00:00 | LONG | SELL | -15194 | 39.42 | 37.11 | 38.62 | 16713.40 | 16122.81 |
| 29 | 2024-02-05 00:00:00 | LONG | BUY | 14534 | 39.81 | 37.85 | 40.22 | 0.00 | -289.30 |
| 30 | 2024-02-07 00:00:00 | LONG | SELL | -14534 | 40.50 | 39.11 | 40.22 | 10028.46 | 9444.85 |
| 31 | 2024-02-13 00:00:00 | LONG | BUY | 13808 | 39.96 | 38.46 | 41.09 | 0.00 | -275.88 |
| 32 | 2024-02-21 00:00:00 | LONG | SELL | -13808 | 37.74 | 38.81 | 41.09 | -30653.76 | -31190.20 |
| 33 | 2024-03-01 00:00:00 | LONG | BUY | 10282 | 38.56 | 37.13 | 39.37 | 0.00 | -198.24 |
| 34 | 2024-03-05 00:00:00 | LONG | SELL | -10282 | 39.95 | 38.28 | 39.37 | 14291.98 | 13888.36 |
| 35 | 2024-03-11 00:00:00 | LONG | BUY | 13094 | 39.67 | 38.65 | 41.14 | 0.00 | -259.72 |
| 36 | 2024-03-15 00:00:00 | LONG | SELL | -13094 | 40.12 | 40.26 | 41.14 | 5892.30 | 5369.91 |
| 37 | 2024-03-21 00:00:00 | LONG | BUY | 12097 | 40.79 | 39.03 | 42.09 | 0.00 | -246.72 |
| 38 | 2024-03-25 00:00:00 | LONG | SELL | -12097 | 39.90 | 40.16 | 42.09 | -10766.33 | -11254.38 |
| 39 | 2024-03-26 00:00:00 | LONG | BUY | 11725 | 40.50 | 39.39 | 41.65 | 0.00 | -237.43 |
| 40 | 2024-03-28 00:00:00 | LONG | SELL | -11725 | 41.94 | 39.77 | 41.65 | 16884.00 | 16400.70 |
| 41 | 2024-03-29 00:00:00 | LONG | BUY | 11413 | 42.96 | 39.97 | 43.53 | 0.00 | -245.15 |
| 42 | 2024-04-01 00:00:00 | LONG | SELL | -11413 | 45.78 | 39.97 | 43.53 | 32184.66 | 31678.27 |
| 43 | 2024-04-04 00:00:00 | LONG | BUY | 7803 | 50.01 | 41.74 | 51.98 | 0.00 | -195.11 |
| 44 | 2024-04-16 00:00:00 | LONG | SELL | -7803 | 49.86 | 49.99 | 51.98 | -1170.45 | -1560.09 |
| 45 | 2024-04-27 00:00:00 | LONG | BUY | 8223 | 52.18 | 49.31 | 52.40 | 0.00 | -214.54 |
| 46 | 2024-05-03 00:00:00 | LONG | SELL | -8223 | 50.60 | 50.92 | 52.40 | -12992.34 | -13414.92 |
| 47 | 2024-05-14 00:00:00 | LONG | BUY | 9408 | 52.20 | 50.11 | 52.52 | 0.00 | -245.55 |
| 48 | 2024-05-15 00:00:00 | LONG | SELL | -9408 | 54.29 | 50.11 | 52.52 | 19662.72 | 19161.79 |
| 49 | 2024-05-20 00:00:00 | LONG | BUY | 7430 | 58.00 | 51.33 | 58.68 | 0.00 | -215.47 |
| 50 | 2024-05-22 00:00:00 | LONG | SELL | -7430 | 59.35 | 57.01 | 58.68 | 10030.50 | 9594.54 |
| 51 | 2024-05-29 00:00:00 | LONG | BUY | 6265 | 56.00 | 53.78 | 61.78 | 0.00 | -175.42 |
| 52 | 2024-06-03 00:00:00 | LONG | SELL | -6265 | 55.00 | 55.27 | 61.78 | -6265.00 | -6612.71 |
| 53 | 2024-06-05 00:00:00 | LONG | BUY | 5375 | 57.00 | 54.85 | 58.11 | 0.00 | -153.19 |
| 54 | 2024-06-10 00:00:00 | LONG | SELL | -5375 | 58.81 | 55.57 | 58.11 | 9728.75 | 9417.51 |
| 55 | 2024-06-14 00:00:00 | LONG | BUY | 4991 | 59.87 | 56.80 | 59.97 | 0.00 | -149.41 |
| 56 | 2024-06-17 00:00:00 | LONG | SELL | -4991 | 62.89 | 56.80 | 59.97 | 15072.82 | 14766.47 |
| 57 | 2024-06-21 00:00:00 | LONG | BUY | 4789 | 64.69 | 57.98 | 64.90 | 0.00 | -154.90 |
| 58 | 2024-06-26 00:00:00 | LONG | SELL | -4789 | 62.65 | 62.69 | 64.90 | -9769.56 | -10074.48 |
| 59 | 2024-06-27 00:00:00 | LONG | BUY | 5276 | 64.35 | 59.17 | 65.07 | 0.00 | -169.76 |
| 60 | 2024-07-02 00:00:00 | LONG | SELL | -5276 | 61.14 | 61.81 | 65.07 | -16935.96 | -17267.00 |
| 61 | 2024-07-23 00:00:00 | LONG | BUY | 4370 | 58.22 | 57.86 | 58.35 | 0.00 | -127.21 |
| 62 | 2024-07-24 00:00:00 | LONG | SELL | -4370 | 57.12 | 57.86 | 58.35 | -4807.00 | -5059.02 |
| 63 | 2024-09-18 00:00:00 | LONG | BUY | 5582 | 51.70 | 51.10 | 52.05 | 0.00 | -144.29 |
| 64 | 2024-09-20 00:00:00 | LONG | SELL | -5582 | 52.31 | 51.10 | 52.05 | 3405.02 | 3114.73 |
| 65 | 2024-09-24 00:00:00 | LONG | BUY | 5968 | 55.20 | 50.95 | 55.17 | 0.00 | -164.72 |
| 66 | 2024-09-27 00:00:00 | LONG | SELL | -5968 | 53.21 | 53.26 | 55.17 | -11876.32 | -12199.82 |
| 67 | 2024-10-04 00:00:00 | LONG | BUY | 6361 | 53.20 | 51.20 | 57.47 | 0.00 | -169.20 |
| 68 | 2024-10-16 00:00:00 | LONG | SELL | -6361 | 57.55 | 55.30 | 57.47 | 27670.35 | 27318.11 |
| 69 | 2024-10-30 00:00:00 | LONG | BUY | 6826 | 56.35 | 55.00 | 59.24 | 0.00 | -192.32 |
| 70 | 2024-10-31 00:00:00 | LONG | SELL | -6826 | 53.34 | 55.00 | 59.24 | -20546.26 | -20920.63 |
| 71 | 2024-11-05 00:00:00 | LONG | BUY | 5453 | 56.03 | 55.29 | 57.91 | 0.00 | -152.77 |
| 72 | 2024-11-08 00:00:00 | LONG | SELL | -5453 | 59.30 | 55.79 | 57.91 | 17831.31 | 17516.86 |
| 73 | 2024-11-11 00:00:00 | LONG | BUY | 4902 | 61.25 | 56.10 | 60.93 | 0.00 | -150.12 |
| 74 | 2024-11-12 00:00:00 | LONG | SELL | -4902 | 61.99 | 56.10 | 60.93 | 3627.48 | 3325.42 |
| 75 | 2024-11-18 00:00:00 | LONG | BUY | 6363 | 62.05 | 57.41 | 67.69 | 0.00 | -197.41 |
| 76 | 2024-11-20 00:00:00 | LONG | SELL | -6363 | 60.14 | 60.84 | 67.69 | -12153.33 | -12542.08 |
| 77 | 2024-11-22 00:00:00 | LONG | BUY | 5536 | 59.60 | 57.95 | 66.28 | 0.00 | -164.97 |
| 78 | 2024-11-26 00:00:00 | LONG | SELL | -5536 | 57.33 | 57.95 | 66.28 | -12566.72 | -12890.38 |
| 79 | 2024-12-24 00:00:00 | LONG | BUY | 4426 | 56.10 | 54.95 | 56.56 | 0.00 | -124.15 |
| 80 | 2024-12-25 00:00:00 | LONG | SELL | -4426 | 53.56 | 54.95 | 56.56 | -11242.04 | -11484.72 |
| 81 | 2024-12-30 00:00:00 | LONG | BUY | 5335 | 59.04 | 54.78 | 58.50 | 0.00 | -157.49 |
