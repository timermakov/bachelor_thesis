import os
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union
import pytz

from tinkoff.invest import (
    CandleInterval, 
    Client, 
    HistoricCandle, 
    RequestError
)
from tinkoff.invest.utils import now

logger = logging.getLogger(__name__)

INTERVAL_MAPPING = {
    "1m": CandleInterval.CANDLE_INTERVAL_1_MIN,
    "5m": CandleInterval.CANDLE_INTERVAL_5_MIN,
    "15m": CandleInterval.CANDLE_INTERVAL_15_MIN,
    "1h": CandleInterval.CANDLE_INTERVAL_HOUR,
    "1d": CandleInterval.CANDLE_INTERVAL_DAY,
    "4h": CandleInterval.CANDLE_INTERVAL_4_HOUR,
    "1w": CandleInterval.CANDLE_INTERVAL_WEEK,
    "1M": CandleInterval.CANDLE_INTERVAL_MONTH
}

class TinkoffDataClient:
    """Client for fetching historical data from Tinkoff Invest API"""
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize the Tinkoff data client
        
        Args:
            token: Tinkoff API token. If None, will try to get from TINKOFF_TOKEN environment variable
        """
        self.token = token or os.environ.get("TINKOFF_TOKEN")
        if not self.token:
            raise ValueError("Tinkoff API token not provided and TINKOFF_TOKEN environment variable not set")
    
    def _convert_candle_to_dict(self, candle: HistoricCandle) -> Dict:
        """Convert Tinkoff candle to dictionary format compatible with our system"""
        return {
            "open": candle.open.units + candle.open.nano / 1e9,
            "high": candle.high.units + candle.high.nano / 1e9,
            "low": candle.low.units + candle.low.nano / 1e9,
            "close": candle.close.units + candle.close.nano / 1e9,
            "volume": candle.volume,
            "datetime": candle.time
        }
    
    def get_figi_by_ticker(self, ticker: str, class_code: str) -> str:
        """
        Get FIGI (Financial Instrument Global Identifier) by ticker symbol
        
        Args:
            ticker: Stock ticker symbol
            class_code: Class code
        Returns:
            FIGI identifier
        """
        with Client(self.token) as client:
            instruments = client.instruments.find_instrument(query=ticker)
            for instrument in instruments.instruments:
                if instrument.ticker == ticker and instrument.class_code == class_code:
                    return instrument.figi
            
            raise ValueError(f"Ticker {ticker} not found in Tinkoff API")
    
    def get_historical_data(
        self, 
        ticker: str, 
        interval: str, 
        from_date: Union[str, datetime], 
        to_date: Optional[Union[str, datetime]] = None
    ) -> pd.DataFrame:
        """
        Get all candles for a given ticker and time range
        
        Args:
            ticker: Stock ticker symbol or FIGI
            interval: Time interval (1m, 5m, 15m, 1h, 1d, 1w, 1M)
            from_date: Start date (string in YYYY-MM-DD format or datetime)
            to_date: End date (string in YYYY-MM-DD format or datetime), defaults to today
            
        Returns:
            DataFrame with historical data
        """
        if isinstance(from_date, str):
            try:
                from_date = datetime.strptime(from_date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                from_date = datetime.strptime(from_date, "%Y-%m-%d")
        
        if from_date.tzinfo is None:
            from_date = pytz.UTC.localize(from_date)
        
        if to_date is None:
            to_date = now()
        elif isinstance(to_date, str):
            try:
                to_date = datetime.strptime(to_date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                to_date = datetime.strptime(to_date, "%Y-%m-%d")
            if to_date.tzinfo is None:
                to_date = pytz.UTC.localize(to_date)
        elif to_date.tzinfo is None:
            to_date = pytz.UTC.localize(to_date)
        
        figi = ticker if ticker.startswith("BBG") else self.get_figi_by_ticker(ticker, 'TQBR') # Shares
        
        if interval not in INTERVAL_MAPPING:
            raise ValueError(f"Invalid interval: {interval}. Must be one of {list(INTERVAL_MAPPING.keys())}")
        candle_interval = INTERVAL_MAPPING[interval]
        
        all_candles = []
        current_from = from_date
        
        with Client(self.token) as client:
            while current_from < to_date:
                current_to = min(current_from + timedelta(days=365), to_date)
                
                try:
                    logger.info(f"Fetching data for {ticker} from {current_from} to {current_to}")
                    candles = list(client.get_all_candles(
                        figi=figi,
                        from_=current_from,
                        to=current_to,
                        interval=candle_interval
                    ))
                    
                    batch_candles = [self._convert_candle_to_dict(candle) for candle in candles]
                    all_candles.extend(batch_candles)
                    
                except RequestError:
                    logger.exception(f"Error fetching data for {ticker}")
                    raise
                
                current_from = current_to
        
        if not all_candles:
            logger.warning(f"No data found for {ticker} from {from_date} to {to_date}")
            return pd.DataFrame()
        
        df = pd.DataFrame(all_candles)
        
        df.set_index('datetime', inplace=True)
        
        return df 
    
    def load_market_data(
        self, 
        ticker: str, 
        exchange: str, 
        interval: str, 
        start_date: Union[str, datetime], 
        end_date: Union[str, datetime],
        csv_file_name: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Loads data from CSV file if it exists, otherwise downloads data from Tinkoff API and saves to CSV.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'SBER')
            exchange: Exchange (for compatibility, ignored)
            interval: Time interval (e.g., '1d')
            start_date: Start date (e.g., '2022-01-01')
            end_date: End date (e.g., '2022-12-31')
            csv_file_name: Path to the CSV file to load data from or save data to. If None, data will be
                          fetched from the API but not saved.
            
        Returns:
            DataFrame with historical data
        """
        try:
            if csv_file_name is None:
                logger.info(f"Скачивание данных с Tinkoff API для {ticker}...")
                data = self.get_historical_data(
                    ticker=ticker,
                    interval=interval,
                    from_date=start_date,
                    to_date=end_date
                )
                if data.empty:
                    raise ValueError(f"Не удалось получить данные для {ticker}")
                
                if start_date:
                    data = data[data.index >= start_date]
                if end_date:
                    data = data[data.index <= end_date]
                
                return data
            
            if os.path.exists(csv_file_name):
                logger.info(f"Загрузка данных из CSV-файла: {csv_file_name}")
                data = pd.read_csv(csv_file_name, parse_dates=['datetime'], index_col='datetime')
            else:
                logger.info(f"Скачивание данных с Tinkoff API для {ticker}...")
                data = self.get_historical_data(
                    ticker=ticker,
                    interval=interval,
                    from_date=start_date,
                    to_date=end_date
                )
                if data.empty:
                    raise ValueError(f"Не удалось получить данные для {ticker}")
                
                if start_date:
                    data = data[data.index >= start_date]
                if end_date:
                    data = data[data.index <= end_date]
                
                data.to_csv(csv_file_name)
                logger.info(f"Данные сохранены в файл: {csv_file_name}")
            return data
        except Exception as e:
            logger.exception(f"Ошибка при загрузке данных для {ticker}")
            raise 
        
    def convert_tinkoff_df_to_bt(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert Tinkoff dataframe to format expected by backtrader."""
        if not all(col in df.columns for col in ['open', 'high', 'low', 'close', 'volume']):
            raise ValueError("Dataframe missing required columns")
        
        df = df.reset_index()
        
        df['datetime'] = df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        df = df[['datetime', 'open', 'high', 'low', 'close', 'volume']]
        
        return df