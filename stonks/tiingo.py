import requests
import os

API_KEY = os.getenv("TIINGO_API_KEY")
SEARCH_URL = "https://api.tiingo.com/tiingo/daily"
IEX_URL = "https://api.tiingo.com/iex"


# custom exception for Tiingo error or failures
class TiingoError(Exception):
    def __init__(self, message: str, status: int):
        super().__init__(message)
        self.message = message
        self.status = status


def fetch_stock(ticker):
    try:
        # get company data
        company_res = requests.get(
            f"{SEARCH_URL}/{ticker.upper()}?token={API_KEY}", timeout=10
        )
        company_res.raise_for_status()

        # get stock data
        summary_res = requests.get(
            f"{IEX_URL}/{ticker.upper()}?token={API_KEY}", timeout=10
        )
        summary_res.raise_for_status()
    # handle HTTP errors
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code
        if status == 404:
            raise TiingoError(
                "No record has been found, please enter a valid symbol", 404
            )
        elif status == 401:
            raise TiingoError("API authentication failed", 401)
        elif status == 429:
            raise TiingoError("Too many requests, please try again later", 429)
        else:
            raise TiingoError("Could not fetch stock data", status)
    # handle general errors
    except requests.exceptions.RequestException:
        raise TiingoError("Error encountered", 500)

    summary_payload = summary_res.json()
    if not summary_payload or summary_payload[0] is None:
        raise TiingoError("No record has been found, please enter a valid symbol", 404)

    return company_res.json(), summary_payload[0]
