import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any, Optional, Union
import uuid

from tinkoff.invest import Client, HistoricCandle, Quotation, SecurityTradingStatus, MoneyValue, InstrumentIdType, GetOperationsByCursorRequest
from tinkoff.invest.constants import INVEST_GRPC_API, INVEST_GRPC_API_SANDBOX
from tinkoff.invest.sandbox.client import SandboxClient

from tinkoff.invest.services import InstrumentsService
from tinkoff.invest.utils import quotation_to_decimal, decimal_to_quotation
from .base_provider import BaseMarketDataProvider

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    level=logging.DEBUG,
    filename="tinkoff_provider.log",
    filemode="a"
)
logger = logging.getLogger("TinkoffProvider")

def quotation_to_decimal(quotation: Optional[Quotation]) -> Optional[Decimal]:
    """Convert Quotation to Decimal"""
    if quotation is None:
        return None
    return Decimal(quotation.units) + Decimal(quotation.nano) / Decimal(1_000_000_000)


class TinkoffMarketDataProvider(BaseMarketDataProvider):
    """Tinkoff market data provider implementation"""
    
    def __init__(self, token: str, sandbox: bool = True):
        logger.debug(f"Initializing TinkoffMarketDataProvider (sandbox={sandbox})")
        self.token = token
        self.sandbox = sandbox
        self.account_id = None
        self._connected = False
    
    def _get_client(self):
        """Get a fresh client instance"""
        if self.sandbox:
            return SandboxClient(self.token)
        else:
            return Client(self.token)
    
    def get_sandbox_accounts(self) -> List[Dict[str, Any]]:
        """Get available sandbox accounts"""
        logger.info("Getting available sandbox accounts")
        
        if not self.sandbox:
            logger.warning("Cannot get sandbox accounts when not in sandbox mode")
            return []
        
        try:
            with self._get_client() as client:
                accounts_response = client.sandbox.get_sandbox_accounts()
                accounts = []
                
                for account in accounts_response.accounts:
                    accounts.append({
                        "id": account.id,
                        "name": account.name,
                        "type": str(account.type),
                        "status": str(account.status),
                        "opened_date": account.opened_date.isoformat() if hasattr(account, "opened_date") else None,
                        "access_level": str(account.access_level) if hasattr(account, "access_level") else None
                    })
                
                logger.info(f"Retrieved {len(accounts)} sandbox accounts")
                return accounts
        except Exception:
            logger.exception("Failed to get sandbox accounts")
            return []
    
    def connect(self, account_name: Optional[str] = None) -> bool:
        """Connect to Tinkoff API with specified account or create new one"""
        logger.info(f"Connecting to Tinkoff API (sandbox={self.sandbox}, account_name={account_name})")
        try:
            if self.sandbox:
                with SandboxClient(self.token) as client:
                    try:
                        existing_accounts = client.sandbox.get_sandbox_accounts()
                        logger.info(f"Found {len(existing_accounts.accounts)} existing sandbox accounts")
                        
                        if account_name:
                            for account in existing_accounts.accounts:
                                if account.name == account_name:
                                    logger.info(f"Using existing sandbox account with name '{account_name}' and ID: {account.id}")
                                    self.account_id = account.id
                                    self._connected = True
                                    return True
                            
                            logger.info(f"No existing account with name '{account_name}', creating new one")
                            response = client.sandbox.open_sandbox_account(name=account_name)
                            logger.info(f"Sandbox account created with name '{account_name}' and ID: {response.account_id}")
                            self.account_id = response.account_id
                        else:
                            if existing_accounts.accounts:
                                self.account_id = existing_accounts.accounts[0].id
                                logger.info(f"Using first available sandbox account ID: {self.account_id}")
                            else:
                                response = client.sandbox.open_sandbox_account(name="Default")
                                logger.info(f"Default sandbox account created with ID: {response.account_id}")
                                self.account_id = response.account_id
                    except Exception:
                        logger.exception("Error checking existing sandbox accounts")
                        
                        account_name = account_name or "Default"
                        response = client.sandbox.open_sandbox_account(name=account_name)
                        logger.info(f"Fallback sandbox account created with name '{account_name}' and ID: {response.account_id}")
                        self.account_id = response.account_id
                    
                    try:
                        get_accounts_response = client.sandbox.get_sandbox_accounts()
                        logger.info(f"Found {len(get_accounts_response.accounts)} accounts")
                        for idx, account in enumerate(get_accounts_response.accounts):
                            logger.debug(f"Account {idx+1}: ID={account.id}, Name={account.name}")
                    except Exception:
                        logger.exception("Error verifying sandbox accounts")
            else:
                with Client(self.token) as client:
                    logger.warning("Working with real account is not implemented yet")
                    accounts_response = client.users.get_accounts()
                    logger.info(f"Found {len(accounts_response.accounts)} real accounts")
            
            self._connected = True
            logger.info("Successfully connected to Tinkoff API")
            return True
        except Exception:
            logger.exception("Failed to connect to Tinkoff API")
            self._connected = False
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from Tinkoff API without closing accounts"""
        logger.info("Disconnecting from Tinkoff API")
        try:
            self._connected = False
            self.account_id = None
            logger.info("Successfully disconnected from Tinkoff API (accounts preserved)")
            return True
        except Exception:
            logger.exception("Failed to disconnect from Tinkoff API")
            return False
    
    def is_connected(self) -> bool:
        """Check if connected to Tinkoff API"""
        #logger.debug(f"Connection status check: {self._connected}")
        return self._connected and self.account_id is not None
    
    def get_price(self, symbol: str) -> Dict[str, Any]:
        """Get current price for a symbol (figi)"""
        #logger.info(f"Getting price for symbol: {symbol}")
        if not self.is_connected():
            logger.error("Not connected to Tinkoff API")
            raise Exception("Not connected to Tinkoff API")
        
        try:
            with self._get_client() as client:
                response = client.market_data.get_last_prices(figi=[symbol])
                
                if not response.last_prices:
                    logger.warning(f"No price data available for symbol: {symbol}")
                    raise Exception(f"No price data for {symbol}")
                
                price_data = response.last_prices[0]
                price_value = quotation_to_decimal(price_data.price)
                time_value = price_data.time.timestamp()
                
                #logger.info(f"Retrieved price for {symbol}: {price_value}")
                #logger.debug(f"Price timestamp: {datetime.fromtimestamp(time_value)}")
                
                return {
                    "symbol": symbol,
                    "price": price_value,
                    "time": time_value
                }
        except Exception as e:
            logger.error(f"Failed to get price for {symbol}: {str(e)}", exc_info=True)
            raise
    
    def get_daily_stats(self, symbol: str) -> Dict[str, Any]:
        """Get 24h statistics for a symbol (figi)"""
        logger.info(f"Getting 24h statistics for symbol: {symbol}")
        if not self.is_connected():
            logger.error("Not connected to Tinkoff API")
            raise Exception("Not connected to Tinkoff API")
        
        try:
            with self._get_client() as client:
                from_ = datetime.now() - timedelta(days=1)
                to = datetime.now()
                
                from tinkoff.invest.utils import now
                from tinkoff.invest.schemas import CandleInterval
                
                logger.debug(f"Requesting candles for FIGI {symbol} from {from_} to {to}")
                response = client.market_data.get_candles(
                    figi=symbol,
                    from_=from_,
                    to=to,
                    interval=CandleInterval.CANDLE_INTERVAL_1_HOUR
                )
                
                candles = response.candles
                
                if not candles:
                    logger.warning(f"No candle data available for symbol: {symbol}")
                    raise Exception(f"No candle data for {symbol}")
                
                logger.debug(f"Retrieved {len(candles)} candles for {symbol}")
                
                open_price = quotation_to_decimal(candles[0].open)
                close_price = quotation_to_decimal(candles[-1].close)
                
                high_prices = [quotation_to_decimal(c.high) for c in candles]
                low_prices = [quotation_to_decimal(c.low) for c in candles]
                
                volume = sum(c.volume for c in candles)
                
                price_change = close_price - open_price
                price_change_percent = ((close_price - open_price) / open_price) * 100 if open_price else 0
                
                logger.info(f"Statistics for {symbol}: Open={open_price}, Close={close_price}, Change={price_change_percent:.2f}%")
                
                return {
                    "symbol": symbol,
                    "openPrice": open_price,
                    "closePrice": close_price,
                    "highPrice": max(high_prices),
                    "lowPrice": min(low_prices),
                    "volume": volume,
                    "priceChange": price_change,
                    "priceChangePercent": price_change_percent
                }
        except Exception as e:
            logger.error(f"Failed to get daily stats for {symbol}: {str(e)}", exc_info=True)
            raise
    
    def get_time(self) -> Dict[str, Any]:
        """Get time"""
        logger.info("Getting time")
        
        try:
            current_time = datetime.now()
            timestamp_ms = current_time.timestamp() * 1000
            
            logger.debug(f"Server time: {current_time} ({timestamp_ms} ms)")
            
            return {
                "serverTime": timestamp_ms  # in milliseconds
            }
        except Exception as e:
            logger.error(f"Failed to get time: {str(e)}", exc_info=True)
            raise
    
    def get_symbols(self) -> List[Dict[str, Any]]:
        """Get available symbols from Tinkoff API"""
        logger.info("Getting available symbols")
        if not self.is_connected():
            logger.error("Not connected to Tinkoff API")
            raise Exception("Not connected to Tinkoff API")
        
        try:
            with self._get_client() as client:
                logger.debug("Requesting shares list")
                shares = client.instruments.shares()
                
                logger.info(f"Retrieved {len(shares.instruments)} shares")
                
                result = []
                for instrument in shares.instruments:
                    result.append({
                        "symbol": instrument.figi,
                        "ticker": instrument.ticker,
                        "name": instrument.name,
                        "currency": instrument.currency,
                        "status": "TRADING" if instrument.api_trade_available_flag else "BREAK"
                    })
                
                logger.debug(f"Processed {len(result)} symbols")
                return result
        except Exception as e:
            logger.error(f"Failed to get symbols: {str(e)}", exc_info=True)
            raise

    def get_figi_by_ticker(self, ticker: str, class_code: str) -> Dict[str, Any]:
        """Get FIGI and additional info by ticker name"""
        logger.info(f"Getting FIGI and info for ticker: {ticker}")
        if not self.is_connected():
            logger.error("Not connected to Tinkoff API")
            raise Exception("Not connected to Tinkoff API")
        
        try:
            with self._get_client() as client:
                instruments: InstrumentsService = client.instruments
                tickers = []
                
                logger.debug(f"Searching for ticker {ticker} in shares")
                method_instruments = instruments.shares().instruments
                logger.debug(f"Found {len(method_instruments)} instruments in shares")
	
                for item in method_instruments:
                    tickers.append({
                        "name": item.name,
                        "ticker": item.ticker,
                        "class_code": item.class_code,
                        "figi": item.figi,
                        "uid": item.uid,
                        "type": "shares",
						"min_price_increment": quotation_to_decimal(item.min_price_increment),
						"scale": 9 - len(str(item.min_price_increment.nano)) + 1,
						"lot": item.lot,
						"trading_status": str(SecurityTradingStatus(item.trading_status).name),
						"api_trade_available_flag": item.api_trade_available_flag,
						"currency": item.currency,
						"exchange": item.exchange,
						"buy_available_flag": item.buy_available_flag,
						"sell_available_flag": item.sell_available_flag,
						"short_enabled_flag": item.short_enabled_flag,
						"klong": quotation_to_decimal(item.klong),
						"kshort": quotation_to_decimal(item.kshort),
					})
            
                logger.debug(f"Collected information for {len(tickers)} total instruments")
                
                ticker_info = next((t for t in tickers if t["ticker"] == ticker), None)
                
                if not ticker_info:
                    logger.warning(f"No instrument found with ticker: {ticker}")
                    raise Exception(f"No instrument found with ticker: {ticker}")
                
                logger.info(f"Found instrument for ticker {ticker}: FIGI={ticker_info['figi']}, Type={ticker_info['type']}")
                return ticker_info
        except Exception as e:
            logger.error(f"Failed to get FIGI for ticker {ticker}: {str(e)}", exc_info=True)
            raise

    def get_ticker_by_figi(self, figi: str) -> Dict[str, Any]:
        """Get ticker by FIGI"""
        logger.info(f"Getting ticker for FIGI: {figi}")
        if not self.is_connected():
            logger.error("Not connected to Tinkoff API")
            raise Exception("Not connected to Tinkoff API")
        
        try:
            with self._get_client() as client:
                instrument_response = client.instruments.get_instrument_by(
                        id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI,
                        id=figi
                )
                instrument = instrument_response.instrument
                   
                if not instrument:
                    logger.warning(f"No instrument found with figi: {figi}")
                    raise Exception(f"No instrument found with figi: {figi}")
                
                logger.info(f"Found instrument for figi {figi}: {instrument.ticker}")
                return instrument.ticker
        except Exception as e:
            logger.error(f"Failed to get ticker for FIGI {figi}: {str(e)}", exc_info=True)
            raise

    def get_name_by_figi(self, figi: str) -> Dict[str, Any]:
        """Get name by FIGI"""
        logger.info(f"Getting name for FIGI: {figi}")
        if not self.is_connected():
            logger.error("Not connected to Tinkoff API")
            raise Exception("Not connected to Tinkoff API")
        
        try:
            with self._get_client() as client:
                instrument_response = client.instruments.get_instrument_by(
                        id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI,
                        id=figi
                )
                instrument = instrument_response.instrument
                   
                if not instrument:
                    logger.warning(f"No instrument found with figi: {figi}")
                    raise Exception(f"No instrument found with figi: {figi}")
                
                logger.info(f"Found instrument for figi {figi}: {instrument.ticker}")
                return instrument.name
        except Exception as e:
            logger.error(f"Failed to get name for FIGI {figi}: {str(e)}", exc_info=True)
            raise

    def set_sandbox_balance(self, money: float, currency: str = "rub") -> bool:
        """Set balance for sandbox account"""
        if not self.is_connected() or not self.sandbox:
            logger.error("Not connected to Tinkoff API or not in sandbox mode")
            raise Exception("Not connected to Tinkoff API or not in sandbox mode")
        
        try:
            logger.info(f"Setting sandbox balance: {money} {currency}")
            
            with SandboxClient(self.token) as client:
                logger.debug(f"Created fresh sandbox client for balance setting")
                
                money_decimal = Decimal(money)
                money_quotation = decimal_to_quotation(money_decimal)
                logger.debug(f"Converted {money} to quotation: {money_quotation}")
                
                logger.debug(f"Adding balance to account {self.account_id}")
                response = client.sandbox.sandbox_pay_in(
                    account_id=self.account_id,
                    amount=MoneyValue(
                        units=money_quotation.units,
                        nano=money_quotation.nano,
                        currency=currency
                    )
                )
                logger.info(f"Successfully set sandbox balance to {money} {currency}")
                
                return True
        except Exception as e:
            logger.error(f"Failed to set sandbox balance: {str(e)}", exc_info=True)
            raise
    
    def get_portfolio(self) -> Dict[str, Any]:
        """Get portfolio data for the current account"""
        logger.info(f"Getting portfolio for account: {self.account_id}")
        if not self.is_connected():
            logger.error("Not connected to Tinkoff API")
            raise Exception("Not connected to Tinkoff API")
        
        try:
            with self._get_client() as client:
                logger.debug(f"Requesting portfolio data for account {self.account_id}")
                
                response = client.operations.get_portfolio(account_id=self.account_id)
                
                logger.debug("Processing portfolio summary data")
                result = {
                    "total_amount_portfolio": self._process_money_value(response.total_amount_portfolio),
                    "total_amount_shares": self._process_money_value(response.total_amount_shares),
                    "total_amount_bonds": self._process_money_value(response.total_amount_bonds),
                    "total_amount_etf": self._process_money_value(response.total_amount_etf),
                    "total_amount_currencies": self._process_money_value(response.total_amount_currencies),
                    "total_amount_futures": self._process_money_value(response.total_amount_futures),
                    "expected_yield": {
                        "value": quotation_to_decimal(response.expected_yield)
                    },
                    "positions": []
                }
                
                logger.debug(f"Processing {len(response.positions)} portfolio positions")
                for position in response.positions:
                    figi = position.figi
                    logger.debug(f"Processing position: {figi}")
                    
                    instrument_response = client.instruments.get_instrument_by(
                        id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI,
                        id=figi
                    )
                    instrument = instrument_response.instrument
                    
                    pos_data = {
                        "figi": figi,
                        "ticker": instrument.ticker,
                        "name": instrument.name,
                        "instrument_type": self._get_instrument_type_name(instrument.instrument_type),
                        "quantity": quotation_to_decimal(position.quantity),
                        "average_position_price": self._process_money_value(position.average_position_price),
                        "current_price": self._process_money_value(position.current_price),
                        "expected_yield": quotation_to_decimal(position.expected_yield),
                        "value": None
                    }
                    
                    if pos_data["quantity"] and pos_data["current_price"]:
                        value = pos_data["quantity"] * pos_data["current_price"]["value"]
                        currency = pos_data["current_price"]["currency"]
                        pos_data["value"] = {
                            "value": value,
                            "currency": currency
                        }
                        logger.debug(f"Position value: {value} {currency}")
                    elif pos_data["quantity"]:
                        if pos_data.get("average_position_price") and pos_data["average_position_price"].get("value"):
                            avg_price = pos_data["average_position_price"]["value"]
                            currency = pos_data["average_position_price"]["currency"]
                            pos_data["value"] = {
                                "value": pos_data["quantity"] * avg_price,
                                "currency": currency
                            }
                    
                    result["positions"].append(pos_data)
                
                total_value = result["total_amount_portfolio"]["value"] if result["total_amount_portfolio"] else 0
                total_currency = result["total_amount_portfolio"]["currency"] if result["total_amount_portfolio"] else "unknown"
                logger.info(f"Retrieved portfolio with total value: {total_value} {total_currency}, positions: {len(result['positions'])}")
                
                return result
        except Exception as e:
            logger.exception(f"Failed to get portfolio: {str(e)}")
            raise
    
    def _process_money_value(self, money_value) -> Dict[str, Any]:
        """Helper method to process MoneyValue objects from the API"""
        if money_value is None:
            return None
        
        return {
            "value": quotation_to_decimal(Quotation(units=money_value.units, nano=money_value.nano)),
            "currency": money_value.currency
        }

    def _get_instrument_type_name(self, instrument_type: str) -> str:
        """Convert instrument type to a readable name"""
        type_map = {
            "share": "Stock",
            "currency": "Currency",
            "bond": "Bond",
            "etf": "ETF",
            "futures": "Futures",
            "option": "Option",
        }
        return type_map.get(instrument_type.lower(), instrument_type)

    def _get_operation_type_description(self, operation_type) -> str:
        """Map operation type to human-readable description"""
        if not operation_type:
            return "Unknown"
            
        operation_types = {
            "OPERATION_TYPE_UNSPECIFIED": "Тип операции не определён",
            "OPERATION_TYPE_INPUT": "Пополнение счета",
            "OPERATION_TYPE_OUTPUT": "Вывод средств",
            "OPERATION_TYPE_BUY": "Покупка ЦБ",
            "OPERATION_TYPE_SELL": "Продажа ЦБ",
            "OPERATION_TYPE_EXCHANGE_BUY": "Покупка валюты",
            "OPERATION_TYPE_EXCHANGE_SELL": "Продажа валюты",
            "OPERATION_TYPE_MARGIN_FEE": "Удержание комиссии за непокрытую позицию",
            "OPERATION_TYPE_BOND_TAX": "Удержание налога по купонам",
            "OPERATION_TYPE_TAX": "Удержание налога",
            "OPERATION_TYPE_COUPON": "Выплата купонов",
            "OPERATION_TYPE_DIVIDEND": "Выплата дивидендов",
            "OPERATION_TYPE_SECURITY_FEE": "Удержание комиссии за обязательное хранение ЦБ",
            "OPERATION_TYPE_BROKER_FEE": "Удержание комиссии за операцию",
            "OPERATION_TYPE_BOND_REPAYMENT_FULL": "Погашение облигаций",
            "OPERATION_TYPE_BOND_REPAYMENT": "Частичное погашение облигаций",
            "OPERATION_TYPE_TAX_CORRECTION": "Корректировка налога",
            "OPERATION_TYPE_SERVICE_FEE": "Удержание комиссии за обслуживание брокерского счёта",
            "OPERATION_TYPE_BENEFIT_TAX": "Удержание налога за материальную выгоду",
            "OPERATION_TYPE_MARGIN_FEE_CORRECTION": "Корректировка комиссии за непокрытую позицию",
            "OPERATION_TYPE_DELIVERY_BUY": "Покупка в рамках экспирации фьючерса",
            "OPERATION_TYPE_DELIVERY_SELL": "Продажа в рамках экспирации фьючерса",
            "OPERATION_TYPE_TRACK_MFEE": "Комиссия за управление по счёту автоследования",
            "OPERATION_TYPE_TRACK_PFEE": "Комиссия за результат по счёту автоследования",
            "OPERATION_TYPE_TAX_PROGRESSIVE": "Удержание налога по ставке 15%",
            "OPERATION_TYPE_BOND_TAX_PROGRESSIVE": "Удержание налога по купонам по ставке 15%",
            "OPERATION_TYPE_DIVIDEND_TAX_PROGRESSIVE": "Удержание налога по дивидендам по ставке 15%",
            "OPERATION_TYPE_BENEFIT_TAX_PROGRESSIVE": "Удержание налога за материальную выгоду по ставке 15%",
            "OPERATION_TYPE_TAX_CORRECTION_PROGRESSIVE": "Корректировка налога по ставке 15%",
            "OPERATION_TYPE_TAX_REPO_PROGRESSIVE": "Удержание налога за возмещение по сделкам РЕПО по ставке 15%",
            "OPERATION_TYPE_TAX_REPO": "Удержание налога за возмещение по сделкам РЕПО",
            "OPERATION_TYPE_TAX_REPO_HOLD": "Удержание налога по сделкам РЕПО",
            "OPERATION_TYPE_TAX_REPO_REFUND": "Возврат налога по сделкам РЕПО",
            "OPERATION_TYPE_TAX_REPO_HOLD_PROGRESSIVE": "Удержание налога по сделкам РЕПО по ставке 15%",
            "OPERATION_TYPE_TAX_REPO_REFUND_PROGRESSIVE": "Возврат налога по сделкам РЕПО по ставке 15%",
            "OPERATION_TYPE_DIV_EXT": "Выплата дивидендов на карту",
            "OPERATION_TYPE_TAX_CORRECTION_COUPON": "Корректировка налога по купонам",
            "OPERATION_TYPE_CASH_FEE": "Комиссия за валютный остаток",
            "OPERATION_TYPE_OUT_FEE": "Комиссия за вывод валюты с брокерского счета",
            "OPERATION_TYPE_OUT_STAMP_DUTY": "Гербовый сбор",
            "OPERATION_TYPE_OUTPUT_SWIFT": "SWIFT-перевод (вывод)",
            "OPERATION_TYPE_INPUT_SWIFT": "SWIFT-перевод (ввод)",
            "OPERATION_TYPE_OUTPUT_ACQUIRING": "Перевод на карту",
            "OPERATION_TYPE_INPUT_ACQUIRING": "Перевод с карты",
            "OPERATION_TYPE_OUTPUT_PENALTY": "Комиссия за вывод средств",
            "OPERATION_TYPE_ADVICE_FEE": "Списание оплаты за сервис Советов",
            "OPERATION_TYPE_TRANS_IIS_BS": "Перевод ценных бумаг с ИИС на брокерский счет",
            "OPERATION_TYPE_TRANS_BS_BS": "Перевод ценных бумаг с одного брокерского счета на другой",
            "OPERATION_TYPE_OUT_MULTI": "Вывод денежных средств со счета",
            "OPERATION_TYPE_INP_MULTI": "Пополнение денежных средств со счета",
            "OPERATION_TYPE_OVER_PLACEMENT": "Размещение биржевого овернайта",
            "OPERATION_TYPE_OVER_COM": "Списание комиссии",
            "OPERATION_TYPE_OVER_INCOME": "Доход от оверанайта",
            "OPERATION_TYPE_OPTION_EXPIRATION": "Экспирация опциона",
            "OPERATION_TYPE_FUTURE_EXPIRATION": "Экспирация фьючерса",
        }
        
        if isinstance(operation_type, str) and "." in operation_type:
            operation_type = operation_type.split(".")[-1]
        
        return operation_types.get(str(operation_type), f"Неизвестная операция ({operation_type})")

    def get_operations_by_cursor(self, instrument_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch operations by cursor for a given instrument"""
        logger.info(f"Fetching operations for instrument: {instrument_id}")
        if not self.is_connected():
            logger.error("Not connected to Tinkoff API")
            raise Exception("Not connected to Tinkoff API")

        all_operations = []
        cursor = ""
        try:
            with self._get_client() as client:
                while True:
                    request = GetOperationsByCursorRequest(
                        account_id=self.account_id,
                        instrument_id=instrument_id,
                        cursor=cursor,
                        limit=limit
                    )
                    response = client.operations.get_operations_by_cursor(request)
                    
                    if hasattr(response, 'items'):
                        all_operations.extend(response.items)
                    
                    if not response.has_next:
                        break
                    cursor = response.next_cursor
                    
            logger.info(f"Fetched {len(all_operations)} operations")
            
            result = []
            for op in all_operations:
                operation_dict = {
                    "id": op.id,
                    "date": op.date.isoformat(),
                    "type": op.type,
                    "operationTypeDescription": op.description,
                    "name": self.get_name_by_figi(op.figi),
                    "ticker": self.get_ticker_by_figi(op.figi),
                    "figi": op.figi,
                    "quantity": str(op.quantity),
                    "state": str(op.state),
                    "price": {
                        "currency": op.price.currency,
                        "units": op.price.units,
                        "nano": op.price.nano
                    },
                    "payment": {
                        "currency": op.payment.currency,
                        "units": op.payment.units,
                        "nano": op.payment.nano
                    }
                }
                result.append(operation_dict)
                
            logger.debug(f"Processed {len(result)} operations into dictionaries")
            return result
        except Exception as e:
            logger.error(f"Failed to fetch operations: {str(e)}", exc_info=True)
            raise

    def post_sandbox_order(self, account_id: str, figi: str, direction: str, quantity: int = 1, order_type: str = "market"):
        """Place a sandbox order (buy/sell) using Tinkoff Invest API"""
        from tinkoff.invest.schemas import OrderDirection, OrderType
        from tinkoff.invest.utils import now
        if direction == 'buy':
            order_direction = OrderDirection.ORDER_DIRECTION_BUY
        elif direction == 'sell':
            order_direction = OrderDirection.ORDER_DIRECTION_SELL
        else:
            logger.warning(f"Invalid direction: {direction}")
            raise ValueError(f'Invalid direction: {direction}')

        if order_type == 'market':
            order_type_enum = OrderType.ORDER_TYPE_MARKET
        elif order_type == 'limit':
            order_type_enum = OrderType.ORDER_TYPE_LIMIT
        else:
            logger.warning(f"Invalid order_type: {order_type}")
            raise ValueError(f'Invalid order_type: {order_type}')

        order_id = str(uuid.uuid4())

        try:
            with self._get_client() as client:
                result = client.sandbox.post_sandbox_order(
                    account_id=account_id,
                    figi=figi,
                    quantity=quantity,
                    order_id=order_id,
                    direction=order_direction,
                    order_type=order_type_enum
                )
                logger.info(f"Sandbox order placed: {result}")
                return {
                    'order_id': result.order_id,
                    'execution_report_status': str(result.execution_report_status),
                    'message': getattr(result, 'message', None)
                }
        except Exception:
            logger.exception("Failed to place sandbox order")
            raise