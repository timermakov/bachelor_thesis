import json
import os
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request

from tinkoff.invest import CandleInterval, Client
from tinkoff.invest.schemas import HistoricCandle
from tinkoff.invest.caching.market_data_cache.cache import MarketDataCache
from tinkoff.invest.caching.market_data_cache.cache_settings import MarketDataCacheSettings
from tinkoff.invest.utils import now

logger = logging.getLogger(__name__)

MARKET_DATA_CACHE_DIR = os.path.join(settings.BASE_DIR, "market_data_cache")
os.makedirs(MARKET_DATA_CACHE_DIR, exist_ok=True)

CONFIG_DIR = os.path.join(settings.BASE_DIR, "config")
os.makedirs(CONFIG_DIR, exist_ok=True)

CONFIG_FILE = os.path.join(CONFIG_DIR, "analysis_config.json")
DEFAULT_CONFIG = {
    "TICKERS": [
        {
            "TICKER": "SBER",
            "FIGI": "BBG004730N88",
            "EXCHANGE": "MOEX",
            "START_DATE": "2023-01-01"
        },
        {
            "TICKER": "GAZP",
            "FIGI": "BBG004730RP0",
            "EXCHANGE": "MOEX",
            "START_DATE": "2023-01-01"
        },
        {
            "TICKER": "AFLT",
            "FIGI": "BBG004S683W7",
            "EXCHANGE": "MOEX",
            "START_DATE": "2023-01-01"
        },
        {
            "TICKER": "NLMK",
            "FIGI": "BBG004S681B4",
            "EXCHANGE": "MOEX",
            "START_DATE": "2023-01-01"
        },
        {
            "TICKER": "OZON", 
            "FIGI": "BBG00Y91R9T3",
            "EXCHANGE": "MOEX",
            "START_DATE": "2023-01-01"
        }
    ],
    "STOP_LOSS_METHODS": ["daily_minmax", "volatility_stop", "weekly_minmax", "monthly_minmax", "MA_50_18"],
    "TAKE_PROFIT_METHODS": ["ma_distance", "weekly_minmax", "monthly_minmax", "prev_bar_5_percent"]
}

TIMEFRAME_MAPPING = {
    "1min": CandleInterval.CANDLE_INTERVAL_1_MIN,
    "5min": CandleInterval.CANDLE_INTERVAL_5_MIN,
    "15min": CandleInterval.CANDLE_INTERVAL_15_MIN,
    "30min": CandleInterval.CANDLE_INTERVAL_30_MIN,
    "1hour": CandleInterval.CANDLE_INTERVAL_HOUR,
    "1day": CandleInterval.CANDLE_INTERVAL_DAY,
    "1week": CandleInterval.CANDLE_INTERVAL_WEEK,
    "1month": CandleInterval.CANDLE_INTERVAL_MONTH
}

DEFAULT_TIMEFRAME = "1day"

if not os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        logger.info(f"Created default config file at {CONFIG_FILE}")
    except Exception as e:
        logger.exception(f"Failed to create default config file")


def load_config() -> Dict[str, Any]:
    """Load config from file or return default config"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        else:
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            with open(CONFIG_FILE, "w") as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
            logger.info(f"Created default config file at {CONFIG_FILE}")
            return DEFAULT_CONFIG
    except Exception as e:
        logger.exception(f"Error loading config file")
        return DEFAULT_CONFIG


def get_tinkoff_token() -> str:
    """Get Tinkoff API token from environment or settings"""
    token = os.environ.get("TINKOFF_TOKEN")
    if not token:
        token = getattr(settings, "TINKOFF_INVEST_TOKEN", "")
    
    if not token:
        logger.error("Tinkoff Invest token is not set. Set TINKOFF_TOKEN environment variable or TINKOFF_INVEST_TOKEN in settings.")
    
    return token


def get_ticker_figi(ticker: str) -> Optional[str]:
    """Get FIGI for ticker from config"""
    config = load_config()
    for ticker_config in config["TICKERS"]:
        if ticker_config["TICKER"] == ticker:
            return ticker_config.get("FIGI")
    return None


def get_candle_interval(timeframe: str) -> CandleInterval:
    """Convert timeframe string to CandleInterval"""
    return TIMEFRAME_MAPPING.get(timeframe, CandleInterval.CANDLE_INTERVAL_DAY)


def get_tinkoff_market_data(
    figi: str, 
    from_date: datetime, 
    to_date: datetime = None, 
    interval: CandleInterval = CandleInterval.CANDLE_INTERVAL_DAY
) -> List[HistoricCandle]:
    """Get market data from Tinkoff API with caching"""
    if to_date is None:
        to_date = now()
    
    if from_date.tzinfo is None:
        from_date = from_date.replace(tzinfo=timezone.utc)
    
    if to_date.tzinfo is None:
        to_date = to_date.replace(tzinfo=timezone.utc)
        
    token = get_tinkoff_token()
    if not token:
        logger.error("Cannot fetch market data: Tinkoff token is not set")
        return []
        
    try:
        with Client(token) as client:
            cache_settings = MarketDataCacheSettings(base_cache_dir=Path(MARKET_DATA_CACHE_DIR))
            market_data_cache = MarketDataCache(settings=cache_settings, services=client)
            
            candles = list(market_data_cache.get_all_candles(
                figi=figi,
                from_=from_date,
                to=to_date,
                interval=interval
            ))
            
            return candles
    except Exception as e:
        logger.exception(f"Error getting market data for {figi}")
        return []


def candles_to_dataframe_format(candles: List[HistoricCandle]) -> List[Dict[str, Any]]:
    """Convert candles to a format suitable for frontend charting"""
    result = []
    
    for candle in candles:
        open_price = candle.open.units + candle.open.nano / 1_000_000_000
        high_price = candle.high.units + candle.high.nano / 1_000_000_000
        low_price = candle.low.units + candle.low.nano / 1_000_000_000
        close_price = candle.close.units + candle.close.nano / 1_000_000_000
        
        result.append({
            'datetime': candle.time.isoformat(),
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': candle.volume,
            'is_complete': candle.is_complete
        })
    
    return result


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_available_tickers(request: Request) -> Response:
    """Get list of available tickers from config"""
    try:
        config = load_config()
        tickers = [ticker_config["TICKER"] for ticker_config in config["TICKERS"]]
        return Response({"tickers": tickers})
    except Exception as e:
        logger.exception("Error retrieving available tickers")
        return Response({"tickers": [], "error": "Failed to load tickers"}, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_available_timeframes(request: Request) -> Response:
    """Get list of available timeframes"""
    timeframes = list(TIMEFRAME_MAPPING.keys())
    return Response({"timeframes": timeframes})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_ticker_data(request: Request) -> Response:
    """Get ticker data for technical analysis"""
    ticker = request.query_params.get('ticker')
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    timeframe = request.query_params.get('timeframe', DEFAULT_TIMEFRAME)
    
    if not ticker:
        return Response({"error": "Ticker parameter is required"}, status=400)
    
    figi = get_ticker_figi(ticker)
    if not figi:
        return Response({"error": f"FIGI not found for ticker {ticker}"}, status=404)
    
    try:
        if start_date:
            start_datetime = datetime.fromisoformat(start_date)
        else:
            start_datetime = now() - timedelta(days=730)
            
        if end_date:
            end_datetime = datetime.fromisoformat(end_date)
        else:
            end_datetime = now()
            
        if start_datetime.tzinfo is None:
            start_datetime = start_datetime.replace(tzinfo=timezone.utc)
        
        if end_datetime.tzinfo is None:
            end_datetime = end_datetime.replace(tzinfo=timezone.utc)
            
    except ValueError:
        return Response({"error": "Invalid date format. Use YYYY-MM-DD format."}, status=400)
    
    try:
        interval = get_candle_interval(timeframe)
        
        candles = get_tinkoff_market_data(
            figi=figi,
            from_date=start_datetime,
            to_date=end_datetime,
            interval=interval
        )
        
        if not candles:
            return Response({"error": f"No data found for {ticker}"}, status=404)
            
        data = candles_to_dataframe_format(candles)
        return Response({"data": data})
    
    except Exception as e:
        logger.exception(f"Error getting data for {ticker}")
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_analysis(request: Request) -> Response:
    """Generate technical analysis data"""
    ticker = request.data.get('ticker')
    start_date = request.data.get('start_date')
    end_date = request.data.get('end_date')
    timeframe = request.data.get('timeframe', DEFAULT_TIMEFRAME)
    indicators = request.data.get('indicators', {})
    
    if not ticker:
        return Response({"error": "Ticker parameter is required"}, status=400)
    
    figi = get_ticker_figi(ticker)
    if not figi:
        return Response({"error": f"FIGI not found for ticker {ticker}"}, status=404)
    
    
    try:
        if start_date:
            start_datetime = datetime.fromisoformat(start_date)
        else:
            start_datetime = now() - timedelta(days=730)
            
        if end_date:
            end_datetime = datetime.fromisoformat(end_date)
        else:
            end_datetime = now()

        if start_datetime.tzinfo is None:
            start_datetime = start_datetime.replace(tzinfo=timezone.utc)
        
        if end_datetime.tzinfo is None:
            end_datetime = end_datetime.replace(tzinfo=timezone.utc)
            
    except ValueError:
        return Response({"error": "Invalid date format. Use YYYY-MM-DD format."}, status=400)
    
    try:
        interval = get_candle_interval(timeframe)
        
        candles = get_tinkoff_market_data(
            figi=figi,
            from_date=start_datetime,
            to_date=end_datetime,
            interval=interval
        )
        
        if not candles:
            return Response({"error": f"No data found for {ticker}"}, status=404)
        
        data = candles_to_dataframe_format(candles)
        
        result = {
            "ticker": ticker,
            "timeframe": timeframe,
            "data": data,
            "analysis": {}
        }
        
        # Trend Indicators
        
        # SMA
        if indicators.get('sma', {}).get('enabled'):
            periods = indicators['sma'].get('periods', 20)
            sma_values = calculate_sma(data, periods)
            result["analysis"]["sma"] = {
                "periods": periods,
                "values": sma_values
            }
            
        # EMA
        if indicators.get('ema', {}).get('enabled'):
            periods = indicators['ema'].get('periods', 20)
            ema_values = calculate_ema(data, periods)
            result["analysis"]["ema"] = {
                "periods": periods,
                "values": ema_values
            }
        
        # Bollinger Bands
        if indicators.get('bollinger', {}).get('enabled'):
            periods = indicators['bollinger'].get('periods', 20)
            std_dev = indicators['bollinger'].get('std_dev', 2)
            
            bollinger_values = calculate_bollinger_bands(data, periods, std_dev)
            result["analysis"]["bollinger"] = {
                "periods": periods,
                "std_dev": std_dev,
                "middle": bollinger_values["middle"],
                "upper": bollinger_values["upper"],
                "lower": bollinger_values["lower"]
            }
            
        # Oscillators
            
        # MACD
        if indicators.get('macd', {}).get('enabled'):
            fast_period = indicators['macd'].get('fast_period', 12)
            slow_period = indicators['macd'].get('slow_period', 26)
            signal_period = indicators['macd'].get('signal_period', 9)
            
            macd_values = calculate_macd(data, fast_period, slow_period, signal_period)
            result["analysis"]["macd"] = {
                "fast_period": fast_period,
                "slow_period": slow_period,
                "signal_period": signal_period,
                "macd": macd_values["macd"],
                "signal": macd_values["signal"],
                "histogram": macd_values["histogram"]
            }
        
        # RSI
        if indicators.get('rsi', {}).get('enabled'):
            periods = indicators['rsi'].get('periods', 14)
            
            rsi_values = calculate_rsi(data, periods)
            result["analysis"]["rsi"] = {
                "periods": periods,
                "values": rsi_values,
                "upper_bound": indicators['rsi'].get('upper', 70),
                "lower_bound": indicators['rsi'].get('lower', 30)
            }
            
        # Stochastic Oscillator
        if indicators.get('stochastic', {}).get('enabled'):
            k_period = indicators['stochastic'].get('k_period', 14)
            d_period = indicators['stochastic'].get('d_period', 3)
            
            stochastic_values = calculate_stochastic(data, k_period, d_period)
            result["analysis"]["stochastic"] = {
                "kPeriod": k_period,
                "dPeriod": d_period,
                "kLine": stochastic_values["k_line"],
                "dLine": stochastic_values["d_line"],
                "upperBound": indicators['stochastic'].get('upper', 80),
                "lowerBound": indicators['stochastic'].get('lower', 20)
            }
            logger.info(f"Calculated Stochastic with k_period={k_period}, d_period={d_period}")
            
        # Williams %R
        if indicators.get('williams_r', {}).get('enabled'):
            periods = indicators['williams_r'].get('periods', 14)
            
            williams_r_values = calculate_williams_r(data, periods)
            result["analysis"]["williams_r"] = {
                "periods": periods,
                "values": williams_r_values,
                "upper_bound": indicators['williams_r'].get('upper', -20),
                "lower_bound": indicators['williams_r'].get('lower', -80)
            }
            logger.info(f"Calculated Williams %R with periods={periods}")
            
        # Volume Indicators
            
        # OBV
        if indicators.get('obv', {}).get('enabled'):
            obv_values = calculate_obv(data)
            result["analysis"]["obv"] = {
                "values": obv_values
            }
            
        # VWAP
        if indicators.get('vwap', {}).get('enabled'):
            vwap_values = calculate_vwap(data)
            result["analysis"]["vwap"] = {
                "values": vwap_values
            }
        
        return Response(result)
    
    except Exception as e:
        logger.exception(f"Error generating analysis for {ticker}")
        return Response({"error": str(e)}, status=500)


def calculate_sma(data: List[Dict[str, Any]], periods: int) -> List[List[Any]]:
    """Calculate Simple Moving Average"""
    if len(data) < periods:
        return []
    
    sma_values = []
    for i in range(len(data)):
        if i < periods - 1:
            sma_values.append([data[i]["datetime"], None])
            continue
        
        sum_close = sum(data[j]["close"] for j in range(i - periods + 1, i + 1))
        sma = sum_close / periods
        sma_values.append([data[i]["datetime"], sma])
    
    return sma_values


def calculate_ema(data: List[Dict[str, Any]], periods: int) -> List[List[Any]]:
    """Calculate Exponential Moving Average"""
    if len(data) < periods:
        return []
    
    ema_values = []
    for i in range(periods-1):
        ema_values.append([data[i]["datetime"], None])
    
    initial_sma = sum(data[i]["close"] for i in range(periods)) / periods
    ema_values.append([data[periods-1]["datetime"], initial_sma])
    
    multiplier = 2 / (periods + 1)
    
    current_ema = initial_sma
    for i in range(periods, len(data)):
        current_ema = (data[i]["close"] - current_ema) * multiplier + current_ema
        ema_values.append([data[i]["datetime"], current_ema])
    
    return ema_values


def calculate_macd(data: List[Dict[str, Any]], fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Dict[str, List[List[Any]]]:
    """Calculate MACD (Moving Average Convergence Divergence)"""
    if len(data) < slow_period + signal_period:
        return {"macd": [], "signal": [], "histogram": []}
    
    fast_ema = calculate_ema(data, fast_period)
    slow_ema = calculate_ema(data, slow_period)
    
    macd_line = []
    
    for i in range(len(data)):
        if i < slow_period - 1:
            macd_line.append([data[i]["datetime"], None])
            continue
        
        fast_value = fast_ema[i][1]
        slow_value = slow_ema[i][1]
        
        if fast_value is None or slow_value is None:
            macd_line.append([data[i]["datetime"], None])
        else:
            macd_line.append([data[i]["datetime"], fast_value - slow_value])
    
    signal_data = []
    for i in range(len(data)):
        if macd_line[i][1] is not None:
            signal_data.append({"datetime": data[i]["datetime"], "close": macd_line[i][1]})
    
    # signal line (EMA of MACD)
    signal_line_full = calculate_ema(signal_data, signal_period) if signal_data else []
    
    signal_line = []
    signal_idx = 0
    
    for i in range(len(data)):
        if i < slow_period + signal_period - 2:
            signal_line.append([data[i]["datetime"], None])
        else:
            if signal_idx < len(signal_line_full):
                signal_line.append([data[i]["datetime"], signal_line_full[signal_idx][1]])
                signal_idx += 1
            else:
                signal_line.append([data[i]["datetime"], None])
    
    # histogram (MACD - Signal)
    histogram = []
    
    for i in range(len(data)):
        macd_value = macd_line[i][1]
        signal_value = signal_line[i][1]
        
        if macd_value is None or signal_value is None:
            histogram.append([data[i]["datetime"], None])
        else:
            histogram.append([data[i]["datetime"], macd_value - signal_value])
    
    return {
        "macd": macd_line,
        "signal": signal_line,
        "histogram": histogram
    }


def calculate_stochastic(data: List[Dict[str, Any]], k_period: int = 14, d_period: int = 3) -> Dict[str, List[List[Any]]]:
    """Calculate Stochastic Oscillator
    
    Momentum indicator comparing a particular closing price
    to a range of prices over a certain period of time. 
    %K - the fast oscillator
    %D - the slow oscillator, a moving average of %K.
    Values > 80 - overbought conditions, < 20 - oversold conditions.
    
    Args:
        data: List of price data dictionaries with datetime, open, high, low, close
        k_period: Number of periods for %K calculation
        d_period: Number of periods for %D calculation
        
    Returns:
        Dictionary with 'k_line' and 'd_line' keys, each containing list of [datetime, value] pairs
    """
    if len(data) < k_period:
        logger.warning(f"Not enough data points for Stochastic Oscillator calculation. Need at least {k_period}, got {len(data)}")
        return {"k_line": [], "d_line": []}
    
    try:
        k_line = []
        
        # %K
        for i in range(len(data)):
            if i < k_period - 1:
                k_line.append([data[i]["datetime"], None])
                continue
            
            highest_high = max(data[j]["high"] for j in range(i - k_period + 1, i + 1))
            lowest_low = min(data[j]["low"] for j in range(i - k_period + 1, i + 1))
            
            if highest_high == lowest_low:
                k_value = 50
                logger.debug(f"Stochastic: highest_high equals lowest_low at index {i}, using k_value=50")
            else:
                k_value = 100 * (data[i]["close"] - lowest_low) / (highest_high - lowest_low)
            
            k_line.append([data[i]["datetime"], k_value])
        
        # %D (SMA of %K)
        d_line = []
        
        for i in range(len(data)):
            if i < k_period + d_period - 2:
                d_line.append([data[i]["datetime"], None])
                continue
            
            sum_k = sum(k_line[j][1] for j in range(i - d_period + 1, i + 1) if k_line[j][1] is not None)
            valid_count = sum(1 for j in range(i - d_period + 1, i + 1) if k_line[j][1] is not None)
            
            if valid_count > 0:
                d_value = sum_k / valid_count
            else:
                d_value = None
                logger.debug(f"Stochastic: No valid %K values found for %D at index {i}")
                
            d_line.append([data[i]["datetime"], d_value])
        
        logger.info(f"Stochastic Oscillator calculated successfully: {len(k_line)} K points, {len(d_line)} D points")
        return {
            "k_line": k_line,
            "d_line": d_line
        }
    except Exception as e:
        logger.exception(f"Error calculating Stochastic Oscillator")
        return {"k_line": [], "d_line": []}


def calculate_williams_r(data: List[Dict[str, Any]], periods: int = 14) -> List[List[Any]]:
    """Calculate Williams %R
    
    Momentum indicator measuring overbought/oversold levels, scaled from 0 to -100. 
    Values between -80 and -100 - oversold conditions
    values between 0 and -20 - overbought conditions
    
    Args:
        data: List of price data dictionaries with datetime, open, high, low, close
        periods: Number of periods to use in calculation
        
    Returns:
        List of [datetime, value] pairs where value is between 0 and -100
    """
    if len(data) < periods:
        logger.warning(f"Not enough data points for Williams %R calculation. Need at least {periods}, got {len(data)}")
        return []
    
    try:
        williams_r_values = []
        
        for i in range(len(data)):
            if i < periods - 1:
                williams_r_values.append([data[i]["datetime"], None])
                continue
            
            highest_high = max(data[j]["high"] for j in range(i - periods + 1, i + 1))
            lowest_low = min(data[j]["low"] for j in range(i - periods + 1, i + 1))
            
            if highest_high == lowest_low:
                williams_r = -50
                logger.debug(f"Williams %R: highest_high equals lowest_low at index {i}, using williams_r=-50")
            else:
                williams_r = -100 * (highest_high - data[i]["close"]) / (highest_high - lowest_low)
            
            williams_r_values.append([data[i]["datetime"], williams_r])
        
        logger.info(f"Williams %R calculated successfully: {len(williams_r_values)} points")
        return williams_r_values
    except Exception as e:
        logger.exception(f"Error calculating Williams %R")
        return []


def calculate_obv(data: List[Dict[str, Any]]) -> List[List[Any]]:
    """Calculate On-Balance Volume"""
    if not data:
        return []
    
    obv_values = []
    current_obv = 0
    
    obv_values.append([data[0]["datetime"], current_obv])
    
    for i in range(1, len(data)):
        if data[i]["close"] > data[i-1]["close"]:
            current_obv += data[i]["volume"]
        elif data[i]["close"] < data[i-1]["close"]:
            current_obv -= data[i]["volume"]

        obv_values.append([data[i]["datetime"], current_obv])
    
    return obv_values


def calculate_vwap(data: List[Dict[str, Any]]) -> List[List[Any]]:
    """Calculate Volume Weighted Average Price"""
    if not data:
        return []
    
    vwap_values = []

    cumulative_pv = 0
    cumulative_volume = 0
    
    for i, candle in enumerate(data):
        typical_price = (candle["high"] + candle["low"] + candle["close"]) / 3
        cumulative_pv += typical_price * candle["volume"]
        cumulative_volume += candle["volume"]
        
        if cumulative_volume == 0:
            vwap_values.append([candle["datetime"], None])
        else:
            vwap_values.append([candle["datetime"], cumulative_pv / cumulative_volume])
    
    return vwap_values


def calculate_bollinger_bands(data: List[Dict[str, Any]], periods: int, std_dev: float) -> Dict[str, List[List[Any]]]:
    """Calculate Bollinger Bands"""
    if len(data) < periods:
        return {"middle": [], "upper": [], "lower": []}
    
    middle_band = []
    upper_band = []
    lower_band = []
    
    for i in range(len(data)):
        if i < periods - 1:
            middle_band.append([data[i]["datetime"], None])
            upper_band.append([data[i]["datetime"], None])
            lower_band.append([data[i]["datetime"], None])
            continue
        
        # SMA
        prices = [data[j]["close"] for j in range(i - periods + 1, i + 1)]
        sma = sum(prices) / periods
        
        # standard deviation
        variance = sum((price - sma) ** 2 for price in prices) / periods
        std = variance ** 0.5
        
        middle_band.append([data[i]["datetime"], sma])
        upper_band.append([data[i]["datetime"], sma + (std * std_dev)])
        lower_band.append([data[i]["datetime"], sma - (std * std_dev)])
    
    return {
        "middle": middle_band,
        "upper": upper_band,
        "lower": lower_band
    }


def calculate_rsi(data: List[Dict[str, Any]], periods: int) -> List[List[Any]]:
    """Calculate Relative Strength Index"""
    if len(data) < periods + 1:
        return []
    
    rsi_values = []
    
    gains = []
    losses = []
    
    for i in range(periods):
        rsi_values.append([data[i]["datetime"], None])
    
    # initial average gain and loss
    for i in range(1, periods + 1):
        change = data[i]["close"] - data[i-1]["close"]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    
    avg_gain = sum(gains) / periods
    avg_loss = sum(losses) / periods
    
    if avg_loss == 0:
        rs = 100
    else:
        rs = avg_gain / avg_loss
    
    rsi = 100 - (100 / (1 + rs))
    rsi_values.append([data[periods]["datetime"], rsi])

    for i in range(periods + 1, len(data)):
        change = data[i]["close"] - data[i-1]["close"]
        
        if change > 0:
            current_gain = change
            current_loss = 0
        else:
            current_gain = 0
            current_loss = abs(change)
        
        avg_gain = ((avg_gain * (periods - 1)) + current_gain) / periods
        avg_loss = ((avg_loss * (periods - 1)) + current_loss) / periods
        
        if avg_loss == 0:
            rs = 100
        else:
            rs = avg_gain / avg_loss
        
        rsi = 100 - (100 / (1 + rs))
        rsi_values.append([data[i]["datetime"], rsi])
    
    return rsi_values