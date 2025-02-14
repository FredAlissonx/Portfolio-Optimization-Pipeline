import os
import requests
from dotenv import load_dotenv
from typing import Optional, Dict
from utils.logging_setup import LoggingSetup

load_dotenv()
log_br = LoggingSetup.get_bronze_logger()

class AlphaVantageAPI:
    BASE_URL: str = "https://www.alphavantage.co/query"
    DEFAULT_TIMEOUT: int = 10
    _API_KEY: Optional[str] = None
    
    @classmethod
    def _get_api_key(cls) -> str:
        """
        Retrieve and cache the API key from environment variables.
        Raises:
            ValueError: If the API key is missing.
        """
        if cls._API_KEY is None:
            cls._API_KEY = os.getenv("API_ALPHA_VANTAGE_KEY")
            if not cls._API_KEY:
                log_br.error("API key is missing. Please check your environment variables.")
                raise ValueError("API key missing.")
        return cls._API_KEY

    @classmethod
    def _setup_params(cls, symbol: str) -> dict:
        """
        Prepare the parameters required for the API request.
        """
        return {
            "function": "HISTORICAL_OPTIONS",
            "symbol": symbol,
            "apikey": cls._get_api_key(),
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

        try:
            log_br.info(f"Fetching data for symbol: {symbol}")
            response = requests.get(cls.BASE_URL, params=params, timeout=cls.DEFAULT_TIMEOUT)
            response.raise_for_status()

            data = response.json()
            if "Error Message" in data:
                log_br.error(f"Error fetching data for {symbol}: {data['Error Message']}")
                return None
            elif "Note" in data:
                log_br.warning(f"Rate limit hit: {data['Note']}")
                return None

            return data
        except requests.exceptions.RequestException as e:
            log_br.error(f"Request failed: {e}")
            return None

