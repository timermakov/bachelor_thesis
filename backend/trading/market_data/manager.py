import os
from typing import Dict, Optional, List, Any
from dotenv import load_dotenv

from .base_provider import BaseMarketDataProvider
from .tinkoff_provider import TinkoffMarketDataProvider

load_dotenv()


class MarketDataManager:
    """Manager for market data providers"""
    
    def __init__(self):
        self.providers: Dict[str, BaseMarketDataProvider] = {}
        self.active_provider: Optional[str] = None
    
    def register_provider(self, name: str, provider: BaseMarketDataProvider) -> None:
        """Register a provider"""
        self.providers[name] = provider
    
    def get_provider(self, name: str) -> Optional[BaseMarketDataProvider]:
        """Get a provider by name"""
        return self.providers.get(name)
    
    def set_active_provider(self, name: str) -> bool:
        """Set the active provider"""
        if name not in self.providers:
            return False
        
        self.active_provider = name
        return True
    
    def get_active_provider(self) -> Optional[BaseMarketDataProvider]:
        """Get the active provider"""
        if not self.active_provider:
            return None
        
        return self.providers.get(self.active_provider)
    
    def get_active_provider_name(self) -> Optional[str]:
        """Get the active provider name"""
        return self.active_provider
    
    def get_available_providers(self) -> List[Dict[str, Any]]:
        """Get a list of available providers with connection status"""
        result = []
        
        for name, provider in self.providers.items():
            result.append({
                "name": name,
                "connected": provider.is_connected(),
                "isActive": name == self.active_provider
            })
        
        return result
    
    @staticmethod
    def create_default() -> 'MarketDataManager':
        """Create a manager with default providers"""
        manager = MarketDataManager()
        
        tinkoff_token = os.environ.get('TINKOFF_TOKEN', '')
        tinkoff_sandbox = os.environ.get('TINKOFF_SANDBOX', 'false').strip().lower() == 'true'
        
        print("DEBUG: TINKOFF_SANDBOX raw value:", os.environ.get('TINKOFF_SANDBOX'))
        print("DEBUG: TINKOFF_SANDBOX as bool:", tinkoff_sandbox)
        
        if tinkoff_token:
            print(f"Registering Tinkoff provider (sandbox: {tinkoff_sandbox})")
            tinkoff_provider = TinkoffMarketDataProvider(tinkoff_token, sandbox=tinkoff_sandbox)
            manager.register_provider('tinkoff', tinkoff_provider)
            manager.set_active_provider('tinkoff')
        else:
            print("No Tinkoff token found. Tinkoff provider not registered.")
        
        return manager 