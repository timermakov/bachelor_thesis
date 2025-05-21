from django.urls import path

from .views import (
    PositionListCreateView, PositionDetailView,
    MarketDataProviderListView, MarketDataProviderConnectView, MarketDataProviderDisconnectView,
    MarketDataPriceView, MarketDataStatsView, MarketDataServerTimeView, MarketDataSymbolsView,
    PortfolioBalanceView, SandboxBalanceView, PortfolioPositionsView, MarketDataFigiView,
    MarketDataProviderAccountsView, TransactionHistoryView,
    run_backtest_view, get_backtest_result_view,
    sandbox_order_view
)
from .analysis import get_available_tickers, get_ticker_data, generate_analysis, get_available_timeframes

urlpatterns = [
    path('positions/', PositionListCreateView.as_view()),
    path('positions/<int:pk>/', PositionDetailView.as_view()),

    path('market-data/providers/', MarketDataProviderListView.as_view()),
    path('market-data/providers/<str:provider_name>/connect/', MarketDataProviderConnectView.as_view()),
    path('market-data/providers/<str:provider_name>/disconnect/', MarketDataProviderDisconnectView.as_view()),
    path('market-data/providers/<str:provider_name>/accounts/', MarketDataProviderAccountsView.as_view()),
    path('market-data/price/', MarketDataPriceView.as_view()),
    path('market-data/stats/', MarketDataStatsView.as_view()),
    path('market-data/time/', MarketDataServerTimeView.as_view()),
    path('market-data/symbols/', MarketDataSymbolsView.as_view()),
    path('market-data/figi/', MarketDataFigiView.as_view()),
    
    path('portfolio/balance/', PortfolioBalanceView.as_view()),
    path('portfolio/positions/', PortfolioPositionsView.as_view()),
    path('portfolio/sandbox/balance/', SandboxBalanceView.as_view()),
    path('portfolio/transaction-history/', TransactionHistoryView.as_view()),
    
    path('analysis/tickers/', get_available_tickers),
    path('analysis/timeframes/', get_available_timeframes),
    path('analysis/ticker-data/', get_ticker_data),
    path('analysis/generate/', generate_analysis),

    path('backtest/', run_backtest_view),
    path('backtest/<str:task_id>/', get_backtest_result_view),

    path('sandbox/order/', sandbox_order_view),
]
