import pytest
from src.bronze.alpha_vantage_api import AlphaVantageAPI

@pytest.fixture(autouse=True)
def reset_api_key():
    """
    Reset the cached API key before each test so that tests do not interfere with each other.
    """
    AlphaVantageAPI._API_KEY = None