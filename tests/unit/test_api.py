import pytest
import requests
from unittest.mock import patch, MagicMock
from utils.api_utils import APIUtils

BASE_URL = "https://www.alphavantage.co/query"
VALID_API_KEY = "valid_api_key"
VALID_SYMBOL = "AAPL"
INVALID_SYMBOL = "INVALID"

class TestAPIUtils:
    @patch("os.getenv")
    def test_setup_params_success(self, mock_getenv):
        """Test parameter setup with a valid API key."""
        mock_getenv.return_value = VALID_API_KEY
        params = APIUtils._APIUtils__setup_params(VALID_SYMBOL)
        expected_params = {
            "function": "HISTORICAL_OPTIONS",
            "symbol": VALID_SYMBOL,
            "apikey": VALID_API_KEY,
            "outputsize": "full"
        }
        assert params == expected_params

    @patch("os.getenv")
    def test_setup_params_missing_api_key(self, mock_getenv):
        """Test parameter setup when the API key is missing."""
        mock_getenv.return_value = None
        with pytest.raises(ValueError, match="API missing."):
            APIUtils._APIUtils__setup_params(VALID_SYMBOL)

    @patch("requests.get")
    @patch("utils.api_utils.APIUtils._APIUtils__setup_params")
    def test_make_requests_success(self, mock_setup_params, mock_get):
        """Test successful API response."""
        mock_setup_params.return_value = {
            "function": "HISTORICAL_OPTIONS",
            "symbol": VALID_SYMBOL,
            "apikey": VALID_API_KEY,
            "outputsize": "full"
        }
        mock_response = self._create_mock_response({"data": "example_data"})
        mock_get.return_value = mock_response

        result = APIUtils.make_requests(VALID_SYMBOL)
        assert result == {"data": "example_data"}
        mock_get.assert_called_once_with(BASE_URL, params=mock_setup_params.return_value)

    @pytest.mark.parametrize(
        "response_data, expected_result, log_level",
        [
            ({"Error Message": "Invalid symbol"}, None, "error"),
            ({"Note": "Rate limit exceeded"}, None, "warning"),
            ({}, {}, None),
        ],
    )
    @patch("requests.get")
    @patch("utils.api_utils.APIUtils._APIUtils__setup_params")
    def test_make_requests_various_responses(self, mock_setup_params, mock_get, response_data, expected_result, log_level, caplog):
        """Test various API responses."""
        mock_setup_params.return_value = {
            "function": "HISTORICAL_OPTIONS",
            "symbol": VALID_SYMBOL,
            "apikey": VALID_API_KEY,
            "outputsize": "full"
        }
        mock_response = self._create_mock_response(response_data)
        mock_get.return_value = mock_response

        result = APIUtils.make_requests(VALID_SYMBOL)
        assert result == expected_result

        if log_level:
            assert any(record.levelname == log_level.upper() for record in caplog.records)

    @patch("requests.get")
    @patch("utils.api_utils.APIUtils._APIUtils__setup_params")
    def test_make_requests_request_exception(self, mock_setup_params, mock_get):
        """Test handling of a network error."""
        mock_setup_params.return_value = {
            "function": "HISTORICAL_OPTIONS",
            "symbol": VALID_SYMBOL,
            "apikey": VALID_API_KEY,
            "outputsize": "full"
        }
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        result = APIUtils.make_requests(VALID_SYMBOL)
        assert result is None

    def _create_mock_response(self, json_data):
        mock_response = MagicMock()
        mock_response.json.return_value = json_data
        mock_response.raise_for_status = MagicMock()
        return mock_response
