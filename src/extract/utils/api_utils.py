import requests
import os
from dotenv import load_dotenv
import logging
from typing import Optional, Dict

class APIUtils:
    @classmethod
    def __setup_params(cls, symbol: str) -> dict:
        """
        Prepare the parameters required for making a request to the API.

        This method loads the API key from environment variables and constructs 
        the request parameters for fetching historical options data for a given symbol.

        Args:
            symbol (str): The stock or asset symbol to fetch historical options data for.

        Returns:
            dict: A dictionary containing the API parameters.
        
        Raises:
            ValueError: If the API key is missing from environment variables.
        """
        load_dotenv()
        API_KEY = os.getenv("API_KEY")
        
        if not API_KEY:
            logging.error("API key is missing. Please check your environment variables.")
            raise ValueError("API missing.")
        
        return {
            "function": "HISTORICAL_OPTIONS",
            "symbol": symbol,
            "apikey": API_KEY,
            "outputsize": "full"
        }
    
    @classmethod
    def make_requests(cls, symbol: str) -> Optional[Dict]:
        """
        Make a request to the Alpha Vantage API to fetch historical options data for a symbol.

        This method constructs the request parameters using the `__setup_params` method, sends 
        a GET request to the API, and processes the response to check for any errors. If the 
        request is successful and no errors are encountered, the data is returned. Otherwise, 
        appropriate error messages are logged, and `None` is returned.

        Args:
            symbol (str): The symbol for which historical options data is requested.

        Returns:
            Optional[Dict]: The response data from the API in dictionary format if successful,
                             or `None` if there is an error or rate limit issue.

        Raises:
            requests.exceptions.RequestException: If the request to the API fails.
        """
        BASE_URL: str = "https://www.alphavantage.co/query"
        params = cls.__setup_params(symbol)
        
        try:
            logging.info(f"Fetching data for symbol: {symbol}")
            response = requests.get(BASE_URL, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for errors in API response
            if "Error Message" in data:
                logging.error(f"Error fetching data for {symbol}: {data['Error Message']}")
                return None
            elif "Note" in data:
                logging.warning(f"Rate limit hit: {data['Note']}")
                return None
            
            return data
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
            return None
