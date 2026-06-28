import websockets
import asyncio
import datetime
import json
from trading.probability import calculate_edge
from trading.trade import buy_contracts

def package_header(api_key_id: str, generated_signature: str):
    curr_datetime = datetime.datetime.now()
    timestamp = curr_datetime.timestamp()
    curr_time_miliseconds = int(timestamp * 1000)
    timestamp_str = str(curr_time_miliseconds)

    auth_header = {
        "KALSHI-ACCESS-KEY": api_key_id,
        "KALSHI-ACCESS-SIGNATURE": generated_signature,
        "KALSHI-ACCESS-TIMESTAMP": timestamp_str
    }

    return auth_header

async def connect(ws_url: str, api_key_id: str, generated_signature: str):
    auth_header = package_header(api_key_id=api_key_id, generated_signature=generated_signature)

    async with websockets.connect(ws_url, additional_headers=auth_header) as websocket:
        print("Connected to Kalshi websocket")

        async for message in websocket:
            print(f"Received: {message}")

asyncio.run(connect())

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

    calc_edge_task = asyncio.create_task(calculate_edge(data["ticker"], data["best_bid"], data["best_ask"]))
    should_buy = await calc_edge_task

    if should_buy:
        asyncio.create_task(buy_contracts(curr_contract_price=int(data["best_ask"]), ticker=data["ticker"]))
