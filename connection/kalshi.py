import websockets
import asyncio
import json
import requests

from core.state import ConfigState, TradingState
from trading.probability import calculate_edge
from trading.trade import buy_contracts
from connection.credentials import package_header, create_signature, generate_timestamp

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


async def connect(ws_url: str, api_key_id: str, generated_signature: str, timestamp: str):
    auth_header = package_header(api_key_id=api_key_id, generated_signature=generated_signature, timestamp=timestamp)

    async with websockets.connect(ws_url, additional_headers=auth_header) as websocket:
        print("Connected to Kalshi websocket")

        async for message in websocket:
            print(f"Received: {message}")

async def subscribe_to_markets(self, channels: list, mkt_tickers: list):
    subscription_message = {
        "id": self.message_id,
        "cmd": "subscribe",
        "params": {
            "channels": channels,
            "market_tickers": mkt_tickers
        }
    }
    await self.ws.send(json.dumps(subscription_message))
    self.message_id += 1

async def process_message(message):
    data = json.loads(message)
    if data.get("type") != "orderbook_delta":
        return
    
    elif data.get("type") == "error":
        error_code = data.get("msg", {}).get("code")
        error_msg = data.get("msg", {}).get("msg")
        print(f"Error {error_code}: {error_msg}")
        return

    should_buy, calculated_odds = calculate_edge(data["ticker"], data["best_bid"], data["best_ask"])

    if should_buy:
        asyncio.create_task(buy_contracts(curr_contract_price=data["best_ask"], ticker=data["ticker"], calculated_prob=calculated_odds))
