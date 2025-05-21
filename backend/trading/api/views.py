from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
import logging
import threading
import uuid
import json
import sys
import importlib
import importlib.util
import os
from pathlib import Path
from django.conf import settings
from django.http import JsonResponse

from .serializers import PositionSerializer
from ..models import Position
from ..market_data import market_data_manager


logger = logging.getLogger(__name__)

RISKMANAGEMENT_PATH = Path('/usr/src/RiskManagement')
BACKTEST_RESULTS = {}

def run_backtest_async(task_id, params):
    logger.info(f"RiskManagement path: {RISKMANAGEMENT_PATH}")
    
    if not os.path.exists(RISKMANAGEMENT_PATH):
        logger.error(f"Directory does not exist: {RISKMANAGEMENT_PATH}")
        BACKTEST_RESULTS[task_id] = {"error": f"Import error: Directory not found: {RISKMANAGEMENT_PATH}"}
        return
        
    bt_file_path = RISKMANAGEMENT_PATH / "backtrader_complex.py"
    if not os.path.exists(bt_file_path):
        logger.error(f"File does not exist: {bt_file_path}")
        BACKTEST_RESULTS[task_id] = {"error": f"Import error: File not found: {bt_file_path}"}
        return

    sys.path.insert(0, str(RISKMANAGEMENT_PATH))
    try:
        try:
            import backtrader_complex
        except ModuleNotFoundError:
            spec = importlib.util.spec_from_file_location(
                "backtrader_complex",
                str(RISKMANAGEMENT_PATH / "backtrader_complex.py")
            )
            backtrader_complex = importlib.util.module_from_spec(spec)
            sys.modules["backtrader_complex"] = backtrader_complex
            spec.loader.exec_module(backtrader_complex)
        importlib.reload(backtrader_complex)
    except Exception as import_exc:
        logger.exception("Failed to import backtrader_complex in run_backtest_async")
        BACKTEST_RESULTS[task_id] = {"error": f"Import error: {import_exc}"}
        return

    config_path = RISKMANAGEMENT_PATH / 'config_web_ru.json'
    config = {
        "TICKERS": [
            {
                "TICKER": params["ticker"],
                "EXCHANGE": "MOEX",
                "START_DATE": params["start_date"],
                "END_DATE": params["end_date"],
                "INTERVAL": "1d",
                "CAPITAL": params["capital"],
                "RISK_PERCENT": params["risk_percent"],
                "PROFIT_TO_RISK": 3,
                "ATR_MULTIPLIER": 1.5,
                "ATR_WINDOW": 14,
                "STOP_LOSS_METHOD": params["stop_loss_method"],
                "TAKE_PROFIT_METHOD": params["take_profit_method"],
                "POSITION": "long"
            }
        ],
        "STOP_LOSS_METHODS": [params["stop_loss_method"]],
        "TAKE_PROFIT_METHODS": [params["take_profit_method"]]
    }
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    # Run backtest
    try:
        backtrader_complex.CONFIG_FILE = str(config_path)
        backtrader_complex.RESULTS_PATH = str(RISKMANAGEMENT_PATH / 'results_bt_complex')

        result_df, trades = backtrader_complex.backtest(
            backtrader_complex.TinkoffDataClient().load_market_data(
                ticker=params["ticker"],
                exchange="MOEX",
                interval="1d",
                start_date=params["start_date"],
                end_date=params["end_date"],
                csv_file_name=None
            ),
            config["TICKERS"][0]
        )

        summary = {}
        if not result_df.empty:
            summary = {
                "initial_balance": config["TICKERS"][0]["CAPITAL"],
                "final_balance": float(result_df["Balance"].iloc[-1]),
                "profit_loss": float(result_df["Balance"].iloc[-1]) - config["TICKERS"][0]["CAPITAL"],
                "profit_percent": (float(result_df["Balance"].iloc[-1]) - config["TICKERS"][0]["CAPITAL"]) / config["TICKERS"][0]["CAPITAL"] * 100,
                "trade_count": int(result_df["Entry"].count()),
                "win_rate": float(result_df[result_df["Profit/Loss"] > 0].shape[0]) / result_df["Entry"].count() * 100 if result_df["Entry"].count() > 0 else 0
            }
        
        balance_curve_df = result_df[["Date", "Balance"]].copy()
        if hasattr(balance_curve_df["Date"].dtype, 'tz') and balance_curve_df["Date"].dtype.tz is not None:
            balance_curve_df["Date"] = balance_curve_df["Date"].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        BACKTEST_RESULTS[task_id] = {
            "summary": summary,
            "trades": trades,
            "balance_curve": balance_curve_df.to_dict(orient="records")
        }
    except Exception as e:
        import traceback
        logger.exception("Error running backtest in run_backtest_async")
        BACKTEST_RESULTS[task_id] = {"error": str(e), "trace": traceback.format_exc()}

from rest_framework.decorators import api_view, permission_classes

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def run_backtest_view(request):
    params = request.data
    task_id = str(uuid.uuid4())
    thread = threading.Thread(target=run_backtest_async, args=(task_id, params))
    thread.start()
    return Response({"task_id": task_id})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_backtest_result_view(request, task_id):
    result = BACKTEST_RESULTS.get(task_id)
    if result is None:
        return Response({"status": "pending"})
    return Response(result)

class PositionListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = PositionSerializer

    def get_queryset(self):
        return Position.objects.filter(author=self.request.user).order_by('id')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PositionDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = PositionSerializer
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        return Position.objects.filter(author=self.request.user)

    def check_object_permissions(self, request, obj):
        if obj.author != request.user:
            self.permission_denied(request)

class MarketDataProviderListView(APIView):
    """List all market data providers"""
    permission_classes = [IsAuthenticated, ]
    
    def get(self, request):
        providers = market_data_manager.get_available_providers()
        return Response(providers)


class MarketDataProviderAccountsView(APIView):
    """Get available sandbox accounts for a provider"""
    permission_classes = [IsAuthenticated, ]
    
    def get(self, request, provider_name):
        provider = market_data_manager.get_provider(provider_name)
        
        if not provider:
            return Response({"error": f"Provider {provider_name} not found"}, status=404)
        
        if not hasattr(provider, 'get_sandbox_accounts'):
            return Response({"error": f"Provider {provider_name} does not support sandbox accounts"}, status=400)
        
        try:
            accounts = provider.get_sandbox_accounts()
            return Response(accounts)
        except Exception as e:
            logger.exception(f"Failed to get sandbox accounts for {provider_name}")
            return Response({"error": str(e)}, status=400)


class MarketDataProviderConnectView(APIView):
    """Connect to a market data provider"""
    permission_classes = [IsAuthenticated, ]
    
    def post(self, request, provider_name):
        provider = market_data_manager.get_provider(provider_name)
        
        if not provider:
            return Response({"error": f"Provider {provider_name} not found"}, status=404)
        
        account_name = None
        if request.data and 'account_name' in request.data:
            account_name = request.data['account_name']
        
        if hasattr(provider, 'connect') and callable(provider.connect):
            success = False
            try:
                import inspect
                sig = inspect.signature(provider.connect)
                if 'account_name' in sig.parameters:
                    success = provider.connect(account_name=account_name)
                else:
                    success = provider.connect()
            except Exception as e:
                logger.exception(f"Error connecting to {provider_name}")
                return Response({"error": str(e)}, status=400)
        else:
            return Response({"error": f"Provider {provider_name} does not support connect method"}, status=400)
        
        if success:
            market_data_manager.set_active_provider(provider_name)
            return Response({
                "status": "connected", 
                "provider": provider_name,
                "account_name": account_name
            })
        else:
            return Response({"error": f"Failed to connect to {provider_name}"}, status=400)


class MarketDataProviderDisconnectView(APIView):
    """Disconnect from a market data provider"""
    permission_classes = [IsAuthenticated, ]
    
    def post(self, request, provider_name):
        provider = market_data_manager.get_provider(provider_name)
        
        if not provider:
            return Response({"error": f"Provider {provider_name} not found"}, status=404)
        
        success = provider.disconnect()
        
        if success:
            return Response({"status": "disconnected", "provider": provider_name})
        else:
            return Response({"error": f"Failed to disconnect from {provider_name}"}, status=400)


class MarketDataPriceView(APIView):
    """Get price for a symbol"""
    permission_classes = [IsAuthenticated, ]
    
    def get(self, request):
        symbol = request.query_params.get('symbol')
        provider_name = request.query_params.get('provider')
        
        if not symbol:
            return Response({"error": "Symbol parameter is required"}, status=400)
        
        provider = None
        if provider_name:
            provider = market_data_manager.get_provider(provider_name)
        else:
            provider = market_data_manager.get_active_provider()
        
        if not provider:
            return Response({"error": "No active provider"}, status=400)
        
        if not provider.is_connected():
            return Response({"error": "Provider not connected"}, status=400)
        
        try:
            price_data = provider.get_price(symbol)
            return Response(price_data)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class MarketDataStatsView(APIView):
    """Get daily stats for a symbol"""
    permission_classes = [IsAuthenticated, ]
    
    def get(self, request):
        symbol = request.query_params.get('symbol')
        provider_name = request.query_params.get('provider')
        
        if not symbol:
            return Response({"error": "Symbol parameter is required"}, status=400)
        
        provider = None
        if provider_name:
            provider = market_data_manager.get_provider(provider_name)
        else:
            provider = market_data_manager.get_active_provider()
        
        if not provider:
            return Response({"error": "No active provider"}, status=400)
        
        if not provider.is_connected():
            return Response({"error": "Provider not connected"}, status=400)
        
        try:
            stats_data = provider.get_daily_stats(symbol)
            return Response(stats_data)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class MarketDataServerTimeView(APIView):
    """Get server time"""
    permission_classes = [IsAuthenticated, ]
    
    def get(self, request):
        provider_name = request.query_params.get('provider')
        
        provider = None
        if provider_name:
            provider = market_data_manager.get_provider(provider_name)
        else:
            provider = market_data_manager.get_active_provider()
        
        if not provider:
            return Response({"error": "No active provider"}, status=400)
        
        if not provider.is_connected():
            return Response({"error": "Provider not connected"}, status=400)
        
        try:
            time_data = provider.get_time()
            return Response(time_data)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class MarketDataSymbolsView(APIView):
    """Get available symbols"""
    permission_classes = [IsAuthenticated, ]
    
    def get(self, request):
        provider_name = request.query_params.get('provider')
        
        provider = None
        if provider_name:
            provider = market_data_manager.get_provider(provider_name)
        else:
            provider = market_data_manager.get_active_provider()
        
        if not provider:
            return Response({"error": "No active provider"}, status=400)
        
        if not provider.is_connected():
            return Response({"error": "Provider not connected"}, status=400)
        
        try:
            symbols_data = provider.get_symbols()
            return Response(symbols_data)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class MarketDataFigiView(APIView):
    """Get FIGI by ticker symbol"""
    permission_classes = [IsAuthenticated, ]
    
    def get(self, request):
        ticker = request.query_params.get('ticker')
        provider_name = request.query_params.get('provider')
        
        if not ticker:
            return Response({"error": "Ticker parameter is required"}, status=400)
        
        provider = None
        if provider_name:
            provider = market_data_manager.get_provider(provider_name)
        else:
            provider = market_data_manager.get_active_provider()
        
        if not provider:
            return Response({"error": "No active provider"}, status=400)
        
        if not provider.is_connected():
            return Response({"error": "Provider not connected"}, status=400)
        
        try:
            figi_data = provider.get_figi_by_ticker(ticker, 'TQBR') # Shares
            return Response(figi_data)
        except Exception as e:
            logger.exception(f"Error getting FIGI for ticker {ticker}")
            return Response({"error": str(e)}, status=400)


class PortfolioBalanceView(APIView):
    """Get portfolio balance"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get current portfolio balance"""
        try:
            provider_name = request.query_params.get('provider', 'tinkoff')
            
            provider = market_data_manager.get_provider(provider_name)
            
            if not provider:
                return Response({"error": f"Provider {provider_name} not found"}, status=404)
            
            if not provider.is_connected():
                connected = provider.connect()
                if not connected:
                    return Response({"error": f"Failed to connect to {provider_name}"}, status=400)
            
            try:
                portfolio_data = provider.get_portfolio()
                
                total_amount_portfolio = portfolio_data.get('total_amount_portfolio', {})
                
                balance = 0
                if total_amount_portfolio and 'value' in total_amount_portfolio:
                    balance = float(total_amount_portfolio['value'])
                
                return Response({
                    'balance': balance,
                    'currency': total_amount_portfolio.get('currency', 'RUB')
                })
                
            except (AttributeError, TypeError) as e:
                logger.error(f"Error getting portfolio: {e}")
                return Response({
                    'balance': 0,
                    'currency': 'RUB'
                })
                
        except Exception as e:
            logger.error(f"Error in PortfolioBalanceView: {e}")
            return Response(
                {'error': str(e)},
                status=400
            )


class PortfolioPositionsView(APIView):
    """Get portfolio positions"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get current portfolio positions"""
        try:
            provider_name = request.query_params.get('provider', 'tinkoff')
            
            provider = market_data_manager.get_provider(provider_name)
            
            if not provider:
                return Response({"error": f"Provider {provider_name} not found"}, status=404)
            
            if not provider.is_connected():
                provider.connect()
            
            try:
                portfolio_data = provider.get_portfolio()
                
                return Response({
                    'positions': portfolio_data.get('positions', []),
                    'total': {
                        'portfolio': portfolio_data.get('total_amount_portfolio', {}),
                        'expected_yield': portfolio_data.get('expected_yield', {})
                    }
                })
                
            except AttributeError:
                return Response({
                    'positions': [],
                    'total': {
                        'portfolio': {'value': 0, 'currency': 'RUB'},
                        'expected_yield': {'value': 0, 'relative': 0}
                    }
                })
                
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=400
            )


class SandboxBalanceView(APIView):
    """Set sandbox account balance"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Set sandbox account balance"""
        try:
            provider_name = request.data.get('provider', 'tinkoff')
            
            try:
                balance = float(request.data.get('balance', 0))
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Invalid balance value. Must be a number.'},
                    status=400
                )
                
            if balance <= 0:
                return Response(
                    {'error': 'Balance must be positive'},
                    status=400
                )
            
            currency = request.data.get('currency', 'rub')
            
            provider = market_data_manager.get_provider(provider_name)
            
            if not provider:
                return Response({"error": f"Provider {provider_name} not found"}, status=404)
            
            if not hasattr(provider, 'sandbox') or not provider.sandbox:
                return Response(
                    {'error': 'This operation is only available in sandbox mode'},
                    status=400
                )
            
            if not provider.is_connected():
                logger.info(f"Provider {provider_name} not connected. Connecting...")
                if not provider.connect():
                    return Response(
                        {'error': 'Failed to connect to provider API'},
                        status=400
                    )
            
            try:
                logger.info(f"Setting sandbox balance: {balance} {currency}")
                
                provider.set_sandbox_balance(balance, currency)
                
                return Response({
                    'message': 'Balance updated successfully',
                    'balance': balance,
                    'currency': currency
                })
            except Exception as e:
                logger.error(f"Error setting sandbox balance: {e}", exc_info=True)
                return Response(
                    {'error': f'Failed to set sandbox balance: {str(e)}'},
                    status=400
                )
        except Exception as e:
            logger.error(f"Unexpected error in SandboxBalanceView: {e}", exc_info=True)
            return Response(
                {'error': str(e)},
                status=400
            )


class TransactionHistoryView(APIView):
    """Fetch transaction history for a given instrument"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        instrument_id = request.query_params.get('instrument_id')
        if not instrument_id:
            return Response({"error": "Instrument ID is required"}, status=400)

        provider_name = request.query_params.get('provider', 'tinkoff')
        provider = market_data_manager.get_provider(provider_name)

        if not provider:
            return Response({"error": f"Provider {provider_name} not found"}, status=404)

        if not provider.is_connected():
            if not provider.connect():
                return Response({"error": f"Failed to connect to {provider_name}"}, status=400)

        try:
            operations = provider.get_operations_by_cursor(instrument_id)
            return Response({"operations": operations})
        except Exception as e:
            logger.exception(f"Error fetching transaction history for instrument {instrument_id}")
            return Response({"error": str(e)}, status=400)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def sandbox_order_view(request):
    """Place a sandbox order (buy/sell) via the active provider"""
    try:
        provider = market_data_manager.get_active_provider()
        if not provider:
            return Response({"error": "No active provider"}, status=400)
        if not provider.is_connected():
            if not provider.connect():
                return Response({"error": "Provider not connected and failed to connect"}, status=400)

        data = request.data
        account_id = data.get("account_id")
        figi = data.get("figi")
        direction = data.get("direction")
        quantity = data.get("quantity", 1)

        if not all([account_id, figi, direction]):
            return Response({"error": "Missing required parameters"}, status=400)

        try:
            result = provider.post_sandbox_order(
                account_id=account_id,
                figi=figi,
                direction=direction,
                quantity=quantity
            )
            return Response({"result": result})
        except Exception as e:
            logger.exception("Failed to place sandbox order")
            return Response({"error": str(e)}, status=400)
    except Exception as e:
        logger.exception("Unexpected error in sandbox_order_view")
        return Response({"error": str(e)}, status=400)
