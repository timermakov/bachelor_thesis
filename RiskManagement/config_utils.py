import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Union, List, Optional

logger = logging.getLogger(__name__)

class ConfigFileOperator:
    """
    A class for handling configuration file operations and related utilities.
    Provides methods for loading configs, parsing dates, directory management,
    and generating file paths consistently.
    """
    
    def __init__(self, config_path: str, csv_path: str = "csv_data/", results_path: Optional[str] = None):
        """
        Initialize the ConfigFileOperator.
        
        Args:
            config_path: Path to the configuration file
            csv_path: Base directory for CSV data files
            results_path: Directory for results (if needed)
        """
        self.config_path = config_path
        self.csv_path = csv_path
        self.results_path = results_path
        self.config = None
        
        self.ensure_directory_exists(self.csv_path)
        if self.results_path:
            self.ensure_directory_exists(self.results_path)
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from the JSON file specified during initialization.
        
        Returns:
            Dictionary with configuration values
            
        Raises:
            FileNotFoundError: If the config file doesn't exist
            json.JSONDecodeError: If the config file contains invalid JSON
        """
        try:
            with open(self.config_path, "r") as f:
                self.config = json.load(f)
                return self.config
        except FileNotFoundError:
            logger.exception(f"Config file '{self.config_path}' not found.")
            raise
        except json.JSONDecodeError:
            logger.exception(f"Invalid JSON in config file '{self.config_path}'.")
            raise
    
    @staticmethod
    def try_parse_datetime(date_str: str) -> datetime:
        """
        Try to parse a string as datetime with both formats:
        - '%Y-%m-%d %H:%M:%S' (datetime format)
        - '%Y-%m-%d' (date-only format)
        
        Args:
            date_str: Date string to parse
            
        Returns:
            Parsed datetime object
            
        Raises:
            ValueError: If the date string cannot be parsed with either format
        """
        try:
            return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return datetime.strptime(date_str, "%Y-%m-%d")
    
    @staticmethod
    def ensure_directory_exists(directory_path: str) -> None:
        """
        Ensure that a directory exists, creating it if necessary
        
        Args:
            directory_path: Path to the directory to check/create
        """
        os.makedirs(directory_path, exist_ok=True)
    
    def get_csv_file_path(self, ticker: str, start_date: str, end_date: str, interval: str) -> str:
        """
        Generate a consistent file path for CSV data files
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date string
            end_date: End date string
            interval: Time interval string (e.g., '1d')
            
        Returns:
            Full path to the CSV file
        """
        return os.path.join(self.csv_path, f"{ticker}_{start_date}_{end_date}_{interval}.csv")
    
    def validate_config(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Validate that a configuration dictionary has the required structure and values
        
        Args:
            config: Configuration dictionary to validate. If None, uses the internally stored config.
            
        Returns:
            True if the configuration is valid, False otherwise
        """
        config_to_validate = config if config is not None else self.config
        
        if config_to_validate is None:
            logger.error("No configuration provided and no configuration loaded.")
            return False
        
        if "TICKERS" not in config_to_validate:
            logger.error("Configuration is missing 'TICKERS' section")
            return False
        
        for idx, ticker_config in enumerate(config_to_validate["TICKERS"]):
            required_fields = ["TICKER", "EXCHANGE", "START_DATE", "END_DATE", "INTERVAL", "CAPITAL"]
            for field in required_fields:
                if field not in ticker_config:
                    logger.error(f"Ticker config at index {idx} is missing required field '{field}'")
                    return False
        
        return True
    
    def get_tickers_config(self) -> List[Dict[str, Any]]:
        """
        Get the list of ticker configurations from the loaded config.
        
        Returns:
            List of ticker configuration dictionaries
            
        Raises:
            ValueError: If config hasn't been loaded yet
        """
        if self.config is None:
            raise ValueError("Configuration has not been loaded. Call load_config() first.")
        
        return self.config.get("TICKERS", []) 