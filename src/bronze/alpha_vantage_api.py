from dotenv import load_dotenv
from typing import Optional, Dict, List
from utils.logging_setup import LoggingSetup
from utils.api_utils import APIUtils
import pandas as pd

load_dotenv()
log_br = LoggingSetup.get_bronze_logger()

class AlphaVantageAPIFetcher(APIUtils):
    BASE_URL: str = "https://www.alphavantage.co/query"
    DEFAULT_TIMEOUT: int = 10
    
    @classmethod
    def _setup_params(cls, symbol: str) -> dict:
        """
        Prepare the parameters required for the API request.
        """
        return {
            "function": "HISTORICAL_OPTIONS",
            "symbol": symbol,
            "apikey": cls._get_api_key(name_key="API_ALPHA_VANTAGE_KEY"),
            "outputsize": "full"
        }

    @classmethod
    def fetch_data(cls, symbol: str) -> Optional[Dict]:
        """
        Fetch historical options data for the given symbol.

        Returns:
            A dictionary with API data if successful; otherwise, None.
        """
        params = cls._setup_params(symbol)
        data = cls._fetch_data(params=params)
        if "Error Message" in data:
            log_br.error(f"Error fetching data for {symbol}: {data['Error Message']}")
            return None
        elif "Note" in data:
            log_br.warning(f"Rate limit hit: {data['Note']}")
            return None
        return data
        
    @classmethod
    def fetch_batch_data(cls, symbols: List[str]):
        results: dict = {}
        for symbol in symbols:
            log_br.info(f"Fetching data for symbol: {symbol}")
            data = cls.fetch_data(symbol)
            results[symbol] = data
            
        return results