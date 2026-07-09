import websockets
import asyncio
import json
import uuid

from core.state import ConfigState, TradingState, DataState
from trading.probability import calculate_edge
from trading.trade import buy_contracts
from connection.credentials import package_header, create_signature, generate_timestamp


async def connect(ws_url: str, api_key_id: str, generated_signature: str, timestamp: str):
    while True:
        try:
            auth_header = package_header(api_key_id=api_key_id, generated_signature=generated_signature, timestamp=timestamp)
            print("Connecting to kalshi websocket...")
            async with websockets.connect(ws_url, additional_headers=auth_header) as websocket:
                print("Connected to Kalshi websocket")
                DataState.kalshi_websocket = websocket

                daily_tickers_with_names = DataState.daily_tickers
                mkt_tickers = [item["ticker"] for item in daily_tickers_with_names]

                channels = ConfigState.kalshi_channels

                await subscribe_to_markets(websocket=websocket, channels=channels, mkt_tickers=mkt_tickers)


                async for message in websocket:
                    print(f"Received: {message}")
                    await process_message(message=message)
            
        except Exception as e:
            print("Websocket connection closed!")
            DataState.kalshi_websocket = None
            await asyncio.sleep(5)

        # this should cycle back up and restart the connection

async def subscribe_to_markets(websocket, channels: list[str], mkt_tickers: list[str]):
    message_id = uuid.uuid4()
    
    subscription_message = {
        "id": message_id,
        "cmd": "subscribe",
        "params": {
            "channels": channels,
            "market_tickers": mkt_tickers
        }
    }
    await websocket.ws.send(json.dumps(subscription_message))

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
