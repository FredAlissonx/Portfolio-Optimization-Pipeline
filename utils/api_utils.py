import requests
import os
from typing import Dict, Optional
from dotenv import load_dotenv
from utils.logging_setup import LoggingSetup

load_dotenv()
log_br = LoggingSetup.get_bronze_logger()

class APIUtils:
    BASE_URL = ""
    DEFAULT_TIMEOUT: int = 10
    
    @classmethod
    def _get_api_key(cls, name_key) -> str:
        _API_KEY = os.getenv(name_key)
        if _API_KEY is None:
            log_br.error(f"{name_key} API key is missing. Please check your environment variables.")
            raise ValueError("API Key missing.")
        return _API_KEY
    
    
    @classmethod
    def _fetch_data(cls, params: Dict[str, any]) -> Optional[Dict]:
        """
        Fetch historical options data for the given symbol.

        Returns:
            A dictionary with API data if successful; otherwise, None.
        """
        try:
            log_br.info(f"Fetching data from {cls.BASE_URL}.")
            response = requests.get(cls.BASE_URL, params=params, timeout=cls.DEFAULT_TIMEOUT)
            response.raise_for_status()

            data = response.json()
            log_br.info("Successfully Data Fetch.")
            
            return data
        except (requests.exceptions.RequestException, ValueError) as e:
            log_br.error(f"Request failed: {e}")
            return None 