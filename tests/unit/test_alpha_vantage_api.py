import pytest
from unittest.mock import call, patch
from src.bronze.alpha_vantage_api import AlphaVantageAPIFetcher
from fake_response_api import *
from utils.api_utils import session

class TestAlphaVantageFetcher:
    """Unit tests for the AlphaVantageAPIFetcher class."""

    def test_get_api_key_success(self, monkeypatch):
        """Test successful retrieval of API key from env ironment variables."""
        monkeypatch.setenv("API_ALPHA_VANTAGE_KEY", "testkey")
        key = AlphaVantageAPIFetcher._get_api_key(name_key="API_ALPHA_VANTAGE_KEY")
        assert key == "testkey"

    def test_get_api_key_missing(self, monkeypatch):
        """Test ValueError is raised when API key is missing from environment."""
        monkeypatch.delenv("API_ALPHA_VANTAGE_KEY", raising=False)
        with pytest.raises(ValueError, match="API Key missing"):
            AlphaVantageAPIFetcher._get_api_key(name_key="API_ALPHA_VANTAGE_KEY")

    def test_setup_params(self, monkeypatch):
        """Test parameters are correctly constructed with environment API key."""
        monkeypatch.setenv("API_ALPHA_VANTAGE_KEY", "testkey")
        params = AlphaVantageAPIFetcher._setup_params("TEST")
        assert params == {
            "function": "HISTORICAL_OPTIONS",
            "symbol": "TEST",
            "apikey": "testkey",
            "outputsize": "full"
        }

    @pytest.mark.parametrize("test_case", [
        ("success", fake_requests_get_success, {"data": "some_data"}),
        ("api_error", fake_requests_get_api_error, None),
        ("rate_limit", fake_requests_get_rate_limit, None),
        ("http_error", fake_requests_get_http_error, None),
        ("network_error", fake_requests_get_exception, None),
        ("invalid_json", fake_requests_get_invalid_json, None),
    ])
    def test_fetch_data_scenarios(self, monkeypatch, test_case):
        """Parameterized test for various API response scenarios."""
        scenario, mock_func, expected_data = test_case
        monkeypatch.setenv("API_ALPHA_VANTAGE_KEY", "testkey")
        monkeypatch.setattr(session, "get", mock_func)
        
        data = AlphaVantageAPIFetcher.fetch_data("TEST")
        
        assert data == expected_data

    def test_fetch_data_request_validation(self, mocker, monkeypatch):
        """Test API request is made with correct parameters and headers."""
        monkeypatch.setenv("API_ALPHA_VANTAGE_KEY", "testkey")
        mock_get = mocker.patch.object(session, "get", return_value=FakeResponse({"data": "test"}))
        
        AlphaVantageAPIFetcher.fetch_data("TEST")
        
        expected_params = AlphaVantageAPIFetcher._setup_params("TEST")
        mock_get.assert_called_once_with(
            AlphaVantageAPIFetcher.BASE_URL,
            params=expected_params,
            timeout=AlphaVantageAPIFetcher.DEFAULT_TIMEOUT
        )

    def test_fetch_batch_data_success(self, monkeypatch):
        """Test batch processing of multiple symbols with successful responses."""
        monkeypatch.setenv("API_ALPHA_VANTAGE_KEY", "testkey")
        monkeypatch.setattr(session, "get", fake_request_batch_data)
        
        result = AlphaVantageAPIFetcher.fetch_batch_data(["AAPL", "GOOG"])
        
        assert set(result.keys()) == {"AAPL", "GOOG"}
        assert all(v == {"data": "some_data"} for v in result.values())

    def test_fetch_batch_data_partial_failure(self, monkeypatch, mocker):
        """Test batch processing with mixed success and failure responses."""
        monkeypatch.setenv("API_ALPHA_VANTAGE_KEY", "testkey")
        mocker.patch.object(
            AlphaVantageAPIFetcher,
            "fetch_data",
            side_effect=lambda x: {"data": "ok"} if x == "AAPL" else None
        )
        
        result = AlphaVantageAPIFetcher.fetch_batch_data(["AAPL", "INVALID"])
        assert result == {"AAPL": {"data": "ok"}, "INVALID": None}

    def test_validate_response_edge_cases(self):
        """Test response validation with various edge cases."""
        validator = AlphaVantageAPIFetcher._validate_response
        
        assert validator(None, "TEST") is None
        
        assert validator({"data": []}, "TEST") is None
        
        assert validator({"Error Message": "Invalid symbol"}, "TEST") is None

        assert validator({"Note": "Limit reached"}, "TEST") is None
        
        valid_data = {"data": [1, 2, 3]}
        assert validator(valid_data, "TEST") == valid_data

    def test_unexpected_response_structure(self, monkeypatch):
        """Test handling of responses with unexpected structure."""
        monkeypatch.setenv("API_ALPHA_VANTAGE_KEY", "testkey")
        monkeypatch.setattr(
            session,
            "get",
            lambda *a, **k: FakeResponse(json_data={"unexpected": "format"})
        )
        
        data = AlphaVantageAPIFetcher.fetch_data("TEST")
        assert data is None

    def test_session_persistence(self, mocker, monkeypatch):
        """Test that the class uses the shared requests session instance."""
        monkeypatch.setenv("API_ALPHA_VANTAGE_KEY", "testkey")
        mock_response = mocker.Mock()
        mock_response.json.return_value = {"data": "test"}
        
        mock_session = mocker.Mock()
        mock_session.get.return_value = mock_response
        
        monkeypatch.setattr("utils.api_utils.session", mock_session)
        
        AlphaVantageAPIFetcher.fetch_data("TEST")
        
        mock_session.get.assert_called_once()