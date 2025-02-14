import os
import pytest
import requests
from typing import Dict
from unittest.mock import patch
from src.bronze.alpha_vantage_api import AlphaVantageAPI


class FakeResponse:
    """A fake response object to simulate requests.Response."""
    def __init__(self, json_data: Dict = None, status_code: int = 200, json_callable=None):
        self._json_data = json_data
        self.status_code = status_code
        self._json_callable = json_callable

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError("HTTP error")

    def json(self):
        if self._json_callable:
            return self._json_callable()
        return self._json_data


def fake_requests_get_success(url, params, timeout):
    """Simulate a successful API call returning valid data."""
    return FakeResponse({"data": "some_data"})


def fake_requests_get_api_error(url, params, timeout):
    """Simulate a response with an error message from the API."""
    return FakeResponse({"Error Message": "Invalid symbol"}, status_code=200)


def fake_requests_get_rate_limit(url, params, timeout):
    """Simulate a response where the rate limit has been hit."""
    return FakeResponse({"Note": "Rate limit hit"}, status_code=200)


def fake_requests_get_http_error(url, params, timeout):
    """Simulate an HTTP error (e.g., 404)."""
    return FakeResponse({}, status_code=404)


def fake_requests_get_exception(url, params, timeout):
    """Simulate a network exception during the API call."""
    raise requests.RequestException("Network error")

def fake_json():
    raise ValueError("Invalid JSON")

def fake_requests_get_invalid_json(url, params, timeout):
    """Simulate a response with invalid JSON."""
    return FakeResponse(json_callable=fake_json)

class TestAlphaVantageAPI:
    """Unit tests for the AlphaVantageAPI class."""

    def test_get_api_key_success(self, monkeypatch):
        """
        Test that _get_api_key returns the key from the environment and caches it.
        """
        monkeypatch.setenv("API_ALPHA_VANTAGE_KEY", "testkey")
        key = AlphaVantageAPI._get_api_key()
        assert key == "testkey"
        # Remove the env var to test caching; _API_KEY should still be available.
        monkeypatch.delenv("API_ALPHA_VANTAGE_KEY")
        key_cached = AlphaVantageAPI._get_api_key()
        assert key_cached == "testkey"

    def test_get_api_key_missing(self, monkeypatch):
        """
        Test that _get_api_key raises ValueError when no API key is set.
        """
        monkeypatch.delenv("API_ALPHA_VANTAGE_KEY", raising=False)
        with pytest.raises(ValueError):
            AlphaVantageAPI._get_api_key()

    def test_setup_params(self, monkeypatch):
        """
        Test that _setup_params returns the correct dictionary of parameters.
        """
        monkeypatch.setenv("API_ALPHA_VANTAGE_KEY", "testkey")
        params = AlphaVantageAPI._setup_params("TEST")
        expected = {
            "function": "HISTORICAL_OPTIONS",
            "symbol": "TEST",
            "apikey": "testkey",
            "outputsize": "full"
        }
        assert params == expected

    def test_fetch_data_success(self, monkeypatch):
        """
        Test that fetch_data returns valid data when the API call is successful.
        """
        monkeypatch.setenv("API_ALPHA_VANTAGE_KEY", "testkey")
        monkeypatch.setattr(requests, "get", fake_requests_get_success)
        data = AlphaVantageAPI.fetch_data("TEST")
        assert data == {"data": "some_data"}

    def test_fetch_data_api_error(self, monkeypatch):
        """
        Test that fetch_data returns None when the API returns an error message.
        """
        monkeypatch.setenv("API_ALPHA_VANTAGE_KEY", "testkey")
        monkeypatch.setattr(requests, "get", fake_requests_get_api_error)
        data = AlphaVantageAPI.fetch_data("TEST")
        assert data is None

    def test_fetch_data_rate_limit(self, monkeypatch):
        """
        Test that fetch_data returns None when the API rate limit is hit.
        """
        monkeypatch.setenv("API_ALPHA_VANTAGE_KEY", "testkey")
        monkeypatch.setattr(requests, "get", fake_requests_get_rate_limit)
        data = AlphaVantageAPI.fetch_data("TEST")
        assert data is None

    def test_fetch_data_http_error(self, monkeypatch):
        """
        Test that fetch_data returns None when an HTTP error occurs.
        """
        monkeypatch.setenv("API_ALPHA_VANTAGE_KEY", "testkey")
        monkeypatch.setattr(requests, "get", fake_requests_get_http_error)
        data = AlphaVantageAPI.fetch_data("TEST")
        assert data is None

    def test_fetch_data_exception(self, monkeypatch):
        """
        Test that fetch_data returns None when a network exception occurs.
        """
        monkeypatch.setenv("API_ALPHA_VANTAGE_KEY", "testkey")
        monkeypatch.setattr(requests, "get", fake_requests_get_exception)
        data = AlphaVantageAPI.fetch_data("TEST")
        assert data is None

    def test_fetch_data_invalid_json(self, monkeypatch):
        """
        Test that fetch_data returns None when the API response contains invalid JSON.
        """
        monkeypatch.setenv("API_ALPHA_VANTAGE_KEY", "testkey")
        monkeypatch.setattr(requests, "get", fake_requests_get_invalid_json)
        data = AlphaVantageAPI.fetch_data("TEST")
        assert data is None

    def test_fetch_data_validate_request_args(self, monkeypatch, mocker):
        """
        Test that fetch_data makes the correct API request with the right arguments.
        """
        monkeypatch.setenv("API_ALPHA_VANTAGE_KEY", "testkey")
        mock_get = mocker.patch("requests.get", return_value=FakeResponse({"data": "test"}))
        
        AlphaVantageAPI.fetch_data("TEST")
        
        mock_get.assert_called_once_with(
            AlphaVantageAPI.BASE_URL,
            params=AlphaVantageAPI._setup_params("TEST"),
            timeout=AlphaVantageAPI.DEFAULT_TIMEOUT
        )
