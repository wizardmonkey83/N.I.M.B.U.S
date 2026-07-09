import asyncio
import requests_async
import requests

from core.state import ConfigState, TradingState, DataState
from connection.credentials import package_header, create_signature

def get_account_balance(timestamp: str):
    api_key_id = ConfigState.api_key_id
    generated_signature = create_signature(private_key=ConfigState.private_key, method="GET", path=ConfigState.portfolio_balance_url_endpoint, timestamp=timestamp)
    headers = package_header(api_key_id=api_key_id, generated_signature=generated_signature, timestamp=timestamp)

    request_url = ConfigState.portfolio_balance_url_requests
    response = requests.get(url=request_url, headers=headers)

    if response.status_code != 200:
        print("Error getting account balance!")
        print(f"Details: {response.text}")
    else: 
        # double check kalshi's docs, they looked a bit funky on the formatting for "balance_dollars"
        balance_dollars = response.json().get("balance_dollars")
        TradingState.total_portfolio_usd = float(balance_dollars)

async def get_daily_tickers():
    base_url = ConfigState.kalshi_get_markets_url
    series_ticker = ConfigState.kalshi_series_ticker
    request_url = f"{base_url}?series_ticker={series_ticker}"

    updated_tickers = False
    for i in range(4):
        try:
            response = await requests_async.get(url=request_url)
            if response.status_code == 200:
                data = response.json()
                markets = data.get("markets")

                if not markets:
                    raise Exception("Unable to get 'markets' from response json body.")
                
                daily_tickers = []
                for mkt in markets:
                    daily_tickers.append({
                        "ticker": mkt["ticker"],
                        "name": mkt["subtitle"]
                    })

                DataState.daily_tickers = daily_tickers
                updated_tickers = True
                break

            
        except Exception as e:
            print(f"Error getting daily tickers. Error: {e}. Trying again...")
            await asyncio.sleep(i * 2)

    if not updated_tickers:
        pass
        # TODO if unable to get daily tickers. program sleeps for a day and user is notified of failure.

    if hasattr(DataState, 'kalshi_websocket') and DataState.kalshi_websocket:
        print("Forcefully closing old WebSocket connection to trigger a fresh daily reset...")
        try:
            await DataState.kalshi_websocket.close()
        except Exception as e:
            # TODO handle this
            print(f"Error while closing active socket: {e}")
    else:
        print("No active WebSocket connection found to reset. Loop will connect with new tickers on its next boot.")