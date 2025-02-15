from typing import Optional, Dict, List
from utils.config import bronze_logger
from utils.api_utils import APIUtils

class AlphaVantageAPIFetcher(APIUtils):
    """
    A class to fetch historical options data from the Alpha Vantage API.

    This class inherits from APIUtils and provides methods to prepare query parameters,
    fetch data for a single symbol, and batch fetch data for multiple symbols.
    """

    BASE_URL: str = "https://www.alphavantage.co/query"
    
    @classmethod
    def _setup_params(cls, symbol: str) -> Dict:
        """
        Prepare the parameters required for the Alpha Vantage API request.

        Constructs a dictionary of parameters needed by the Alpha Vantage API, including the function type,
        symbol, API key, and output size.

        Args:
            symbol (str): The stock symbol for which to fetch data.

        Returns:
            Dict[str, str]: A dictionary of parameters to be sent with the API request.
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
        Fetch historical options data for the given symbol from the Alpha Vantage API.

        This method prepares the request parameters for a given symbol, calls the API using
        the parent class method, and validates the response.

        Args:
            symbol (str): The stock symbol for which to fetch data.

        Returns:
            Optional[Dict]: A dictionary containing the API data if successful; otherwise, None.
        """
        params = cls._setup_params(symbol = symbol)
        data = cls._fetch_data(params = params)
        super()._validate_response(data = data, symbol = symbol)
        
        return data
        
    @classmethod
    def fetch_batch_data(cls, symbols: List[str]) -> Dict:
        """
        Fetch historical options data for multiple symbols from the Alpha Vantage API.

        Iterates over a list of symbols, fetches the data for each symbol, and compiles the results
        into a dictionary mapping each symbol to its respective data.

        Args:
            symbols (List[str]): A list of stock symbols for which to fetch data.

        Returns:
            Dict[str, Optional[Dict]]: A dictionary where keys are symbols and values are the corresponding
            data dictionaries. If data retrieval fails for a symbol, its value will be None.
        """
        results: dict = {}
        for symbol in symbols:
            bronze_logger.info(f"Fetching data for symbol: {symbol}")
            data = cls.fetch_data(symbol)
            results[symbol] = data
            
        return results