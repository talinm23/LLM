import pandas as pd
from typing import Dict, Any, Union
import requests
from requests.exceptions import RequestException
from agents import function_tool
import os
from agents import Agent, Runner
import asyncio

#ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")


def process_data(data):
    print(data)
    inner = data["Time Series (Daily)"]
    df = pd.DataFrame.from_dict(
        {
            key: {
                "open": value["1. open"],
                "high": value["2. high"],
                "low": value["3. low"],
                "close": value["4. close"],
                "volume": value["5. volume"],
            }
            for key, value in inner.items()
        },
        orient="index"
    )

    # Normalizing to a date format but keeping the dates as strings:
    # parse then format back to YYYY-MM-DD
    df.index = pd.to_datetime(df.index).strftime("%Y-%m-%d")
    ohlcv_dict = df.to_dict(orient="index")  # keys are now strings
    result = {"ohlcv": ohlcv_dict}  # This is safe to return via Pydantic / tool
    return result

@function_tool
def get_price_data(symbol: str, interval: str, api_key: str) -> Dict[str, Any]:  # or dict

    """ Retrieves historical or real-time price data for a given symbol from the Alpha Vantage website using a free API key.
    Args:
        symbol: The stock, crypto, or forex ticker symbol (e.g., 'AAPL', 'BTCUSD').
        interval: The interval for the prices
        api_key: The secret key for API authentication.

    Returns:
        A dictionary containing the price data or an error message on failure.
    """
    interval = "TIME_SERIES_DAILY"
    # Construct the URL using a readable f-string
    url = (
        f"https://www.alphavantage.co/query?"
        f"function={interval}&symbol={symbol}"
        f"&apikey={api_key}&extended_hours=false"
    )

    # Make the request and parse the JSON data in a single step
    try:
        with requests.Session() as session:
            response = session.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            result = process_data(data)
            print("Data retrieved successfully!")
            return result

        return process_data(data)
        # 'data' now holds the retrieved stock information as a Python dictionary.



    except RequestException as e:
        # Catch network errors, DNS failures, connection timeouts, and HTTP errors from raise_for_status()
        error_message = f"API Request Failed for {symbol}: {e}"
        print(f"Error: {error_message}")
        return {"error": error_message, "status_code": getattr(e.response, 'status_code', 'N/A')}

    except ValueError:
        # Catch JSONDecodeError (raised as ValueError in older Python/requests versions)
        error_message = f"Failed to decode JSON response for {symbol}. Response text: {response.text[:100]}..."
        print(f"Error: {error_message}")
        return {"error": error_message}

    except Exception as e:
        # Catch any other unexpected errors
        error_message = f"An unexpected error occurred for {symbol}: {e}"
        print(f"Error: {error_message}")
        return {"error": error_message}

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")







'''
@function_tool
def run_quant_agent(prompt: str) -> str:
    """Call the QuantAgent with the given prompt and return its text output."""
    #result = asyncio.run(QuantAgent, input=prompt)

    coro = Runner.run(QuantAgent, input=prompt)
    # Run it to completion synchronously
    result = asyncio.run(coro)

    # depending on the SDK version, adapt how you extract the final text:
    #print(result.keys())
    return result.output_text  # or whatever field contains the final text

@function_tool
def run_coder_agent(prompt: str) -> str:
    """Call the CoderAgent with the given prompt and return its text output."""
    result = asyncio.run(CoderAgent, input=prompt)
    print(result.keys())
    return result.output_text
'''