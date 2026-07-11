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

                daily_tickers_dict = DataState.daily_tickers
                mkt_tickers = [key for key in daily_tickers_dict]

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
    """
        Sample market_ticker message:

        {
            "type": "ticker",
            "sid": 11,
            "msg": {
                "market_ticker": "FED-23DEC-T3.00",
                "market_id": "9b0f6b43-5b68-4f9f-9f02-9a2d1b8ac1a1",
                "price_dollars": "0.480",
                "yes_bid_dollars": "0.450",
                "yes_ask_dollars": "0.530",
                "volume_fp": "33896.00",
                "open_interest_fp": "20422.00",
                "dollar_volume": 16948,
                "dollar_open_interest": 10211,
                "yes_bid_size_fp": "300.00",
                "yes_ask_size_fp": "150.00",
                "last_trade_size_fp": "25.00",
                "ts": 1669149841,
                "ts_ms": 1669149841000,
                "time": "2022-11-22T20:44:01Z"
            }
        }
    """

    data = json.loads(message)
        
    if data.get("type") == "error":
        error_code = data.get("msg", {}).get("code")
        error_msg = data.get("msg", {}).get("msg")
        print(f"Error {error_code}: {error_msg}")
        return
    elif data.get("type") != "ticker":
        return
    
    if not data.get("msg", {}).get("market_ticker") and not data.get("msg", {}).get("yes_ask_dollars") and not data.get("msg", {}).get("yes_bid_dollars"):
        return

    should_buy, calculated_odds = calculate_edge(data["msg"]["market_ticker"], data["msg"]["yes_bid_dollars"], data["msg"]["yes_ask_dollars"])

    if should_buy:
        asyncio.create_task(buy_contracts(curr_contract_price=data["best_ask"], ticker=data["ticker"], calculated_prob=calculated_odds))
