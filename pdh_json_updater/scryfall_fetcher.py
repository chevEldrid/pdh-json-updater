"""Abstractions for data gathering Scryfall API calls"""
import time
import traceback
from typing import List, Optional
from urllib.parse import urlparse

import jsonpickle
import requests


class ScryfallResponse:  # pylint: disable=too-few-public-methods
    """Data class storing the response from a scryfall API call"""

    def __init__(self, data, was_successful=True, error_message=""):
        self.data: List = data
        self.was_successful: bool = was_successful
        self.error_message: str = error_message
        if error_message is not None and error_message != "":
            self.was_successful = False


class ScryfallFetcher:  # pylint: disable=too-few-public-methods
    """API requester abstraction for Scryfall"""

    SCRYFALL_API_HOST = "api.scryfall.com"
    SCRYFALL_USER_AGENT = "pdh-json-updater/0.1.0"
    SCRYFALL_HEADERS = {
        "User-Agent": SCRYFALL_USER_AGENT,
        "Accept": "application/json",
    }
    SLOW_ENDPOINTS = {
        "/cards/search",
        "/cards/named",
        "/cards/random",
        "/cards/collection",
    }
    DEFAULT_API_DELAY_SECONDS = 0.1
    SLOW_API_DELAY_SECONDS = 0.5

    last_api_request_at: Optional[float] = None

    @staticmethod
    def fetch_data(url: str, raise_exceptions: bool) -> ScryfallResponse:
        """Gather data from Scryfall given an endpoint url"""
        data: List = []
        try:
            while True:
                ScryfallFetcher.wait_for_rate_limit(url)
                response = requests.get(
                    url, timeout=60, headers=ScryfallFetcher.SCRYFALL_HEADERS
                )
                jsonpickled_response = None
                if "application/json" in response.headers.get("content-type", ""):
                    jsonpickled_response = jsonpickle.loads(response.text, safe=True)

                if not response.ok or jsonpickled_response is None:
                    error_message: str
                    if (
                        jsonpickled_response is not None
                        and isinstance(jsonpickled_response, dict)
                        and "details" in jsonpickled_response
                    ):
                        error_message = jsonpickled_response["details"]
                    else:
                        error_message = response.text

                    if raise_exceptions:
                        raise ConnectionError(error_message)
                    return ScryfallResponse(
                        data, was_successful=False, error_message=error_message
                    )

                data.extend(jsonpickled_response["data"])
                if jsonpickled_response["has_more"]:
                    url = jsonpickled_response["next_page"]
                else:
                    break

        except Exception:  # pylint: disable=broad-except
            if raise_exceptions:
                raise
            return ScryfallResponse(
                data, was_successful=False, error_message=traceback.format_exc()
            )

        return ScryfallResponse(data)

    @staticmethod
    def wait_for_rate_limit(url: str) -> None:
        """Apply Scryfall's per-endpoint API rate limits."""
        delay_seconds = ScryfallFetcher.get_rate_limit_delay_seconds(url)
        if delay_seconds == 0:
            return

        now = time.monotonic()
        if ScryfallFetcher.last_api_request_at is not None:
            elapsed_seconds = now - ScryfallFetcher.last_api_request_at
            remaining_delay = delay_seconds - elapsed_seconds
            if remaining_delay > 0:
                time.sleep(remaining_delay)
                now = time.monotonic()

        ScryfallFetcher.last_api_request_at = now

    @staticmethod
    def get_rate_limit_delay_seconds(url: str) -> float:
        """Return the delay Scryfall requires before the next request."""
        parsed_url = urlparse(url)
        if parsed_url.hostname != ScryfallFetcher.SCRYFALL_API_HOST:
            return 0

        if parsed_url.path in ScryfallFetcher.SLOW_ENDPOINTS:
            return ScryfallFetcher.SLOW_API_DELAY_SECONDS

        return ScryfallFetcher.DEFAULT_API_DELAY_SECONDS
