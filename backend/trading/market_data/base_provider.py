from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class BaseMarketDataProvider(ABC):
    """Base class for market data providers"""
    
    @abstractmethod
    def get_price(self, symbol: str) -> Dict[str, Any]:
        """Get current price for a symbol"""
        pass
    
    @abstractmethod
    def get_daily_stats(self, symbol: str) -> Dict[str, Any]:
        """Get 24h statistics for a symbol"""
        pass
    
    @abstractmethod
    def get_time(self) -> Dict[str, Any]:
        """Get server time"""
        pass
    
    @abstractmethod
    def get_symbols(self) -> List[Dict[str, Any]]:
        """Get available symbols"""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if provider is connected"""
        pass
    
    @abstractmethod
    def connect(self) -> bool:
        """Connect to the provider"""
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """Disconnect from the provider"""
        pass 