import uuid
import datetime
import time
import math
import requests
from core.state import TradingState
from connection.credentials import load_private_key_from_file, create_signature

def place_buy_order(contracts_to_buy: float, curr_contract_price: float, ticker: str, method: str):
    private_key_path = TradingState.private_key_path
    buy_order_base_url_path = TradingState.buy_order_base_url_path
    url_path = TradingState.buy_order_url_path
    private_key = load_private_key_from_file(file_path=private_key_path)

    for i in range(4):
        timestamp = str(int(datetime.datetime.now().timestamp() * 1000))
        generated_signature = create_signature(private_key=private_key, timestamp=timestamp, method=method, path=url_path)

        headers = {
            'KALSHI-ACCESS-KEY': api_key_id,
            'KALSHI-ACCESS-SIGNATURE': generated_signature,
            'KALSHI-ACCESS-TIMESTAMP': timestamp,
            'Content-Type': 'application/json'
        }

        client_order_id = str(uuid.uuid4())
        order_data = {
            "ticker": ticker,
            "side": "bid",
            "count": contracts_to_buy,
            "price": curr_contract_price,
            "time_in_force": "good_till_canceled",
            "self_trade_prevention_type": "taker_at_cross",
            "client_order_id": client_order_id
        }

        try:
            response = requests.post(url=(buy_order_base_url_path + url_path), headers=headers, json=order_data)
            break

        except Exception as e:
            response = requests.get(url=(f"{buy_order_base_url_path}{url_path}/{client_order_id}"), headers=headers)
            if response:
                break

            print(f"Error while placing buy order request: {e}")
            time.sleep(i * 2)

    return response

def buy_contracts(curr_contract_price: str, ticker: str):
    max_bet_pct_of_portfolio = TradingState.max_bet_pct_of_portfolio
    total_mkt_pos_usd = TradingState.total_mkt_pos_usd
    total_portfolio_usd = TradingState.total_portfolio_usd
    method = "POST"

    # if there is still room to trade
    pos_vs_portfolio = ((total_mkt_pos_usd / total_portfolio_usd) * 100)
    if pos_vs_portfolio <= max_bet_pct_of_portfolio:
        bettable_pct_of_porfolio = max_bet_pct_of_portfolio - pos_vs_portfolio
        bet_amount_usd = (bettable_pct_of_porfolio / 100) * total_portfolio_usd
        contracts_to_buy = math.floor(bet_amount_usd / curr_contract_price)

        response = place_buy_order(contracts_to_buy=contracts_to_buy, curr_contract_price=curr_contract_price, ticker=ticker, method=method)

        if response.status_code == 201:
            print(f"Order placed successfully!")
            print(f"Order details --> Bought {contracts_to_buy} contracts at a price of {curr_contract_price} per contract.")
        else:
            print("Error buying contracts.")
            print(f"Error: {response.status_code} - {response.text}")

    return