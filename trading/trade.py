import uuid
import datetime
import math
import asyncio
import requests_async
from core.state import TradingState, ConfigState
from connection.credentials import load_private_key_from_file, create_signature, package_header, generate_timestamp

def get_kelly_fraction(calculated_prob: float, implied_prob: float):
    """
        Using this formula --> f = ((b(p) - q) / b) * h
        Where: 
            f = fraction of bankroll to wager
            b = net profit per one dollar risked --> programs odds / implied odds
            p = win probability
            q = loss probability
            h = percent of kelly fraction to use

        Imagine a scenario where a contract is priced at 40 cents and the program determines that contract has a 70% chance of occurring.
        Here:
            b = 70/40 --> 1.75
            p = 0.7
            q = 0.3
            h = 0.5

        So: 
            f = ((1.75(0.7) - 0.3) / 1.75) * 0.5
            f = 0.26
        
        This means for this trade, 26% of bankroll should be wagered. 
    """
    contract_price = implied_prob
    expected_profit = 1 - contract_price

    b = expected_profit / contract_price
    p = calculated_prob
    q = 1 - calculated_prob
    h = TradingState.kelly_fraction_haircut_frac

    kelly_fraction = (((b * p) - q) / b) * h
    return round(kelly_fraction, 2)


async def place_buy_order(contracts_to_buy: str, curr_contract_price: str, ticker: str):
    buy_order_base_url_path = ConfigState.buy_order_base_url
    url_path = ConfigState.buy_order_url
    private_key = ConfigState.private_key
    api_key_id = ConfigState.api_key_id

    for i in range(4):
        timestamp = generate_timestamp()
        generated_signature = create_signature(private_key=private_key, method="POST", path=url_path, timestamp=timestamp)
        headers = package_header(api_key_id=api_key_id, generated_signature=generated_signature, timestamp=timestamp, content_type="application/json")

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
            response = await requests_async.post(url=(buy_order_base_url_path + url_path), headers=headers, json=order_data)
            break

        except Exception as e:
            # TODO check if this url is correct
            retry_url_path = f"{buy_order_base_url_path}{url_path}/{client_order_id}"
            generated_signature = create_signature(private_key=private_key, method="GET", path=retry_url_path, timestamp=timestamp)
            headers = package_header(api_key_id=api_key_id, generated_signature=generated_signature, timestamp=timestamp)

            response = await requests_async.get(url=url_path, headers=headers)

            if response.status_code == 200:
                break

            print(f"Error while placing buy order request: {e}")
            await asyncio.sleep(i * 2)

    return response if response else None

async def buy_contracts(curr_contract_price: str, ticker: str, calculated_prob: float):
    max_bet_frac_of_portfolio = TradingState.max_bet_frac_of_portfolio
    total_mkt_pos_usd = TradingState.total_mkt_pos_usd
    total_portfolio_usd = TradingState.total_portfolio_usd

    # stores as a frac --> 50/100 = 0.5
    pos_vs_portfolio = total_mkt_pos_usd / total_portfolio_usd
    if pos_vs_portfolio <= max_bet_frac_of_portfolio:
        # stores in this format --> 
        bettable_frac_of_porfolio = max_bet_frac_of_portfolio - pos_vs_portfolio
        kelly_bettable_frac = get_kelly_fraction(calculated_prob=calculated_prob, implied_prob=float(curr_contract_price))

        if kelly_bettable_frac > bettable_frac_of_porfolio:
            bet_amount_usd = bettable_frac_of_porfolio * total_portfolio_usd
        else:
            bet_amount_usd = kelly_bettable_frac * total_portfolio_usd
        
        contracts_to_buy = math.floor(bet_amount_usd / float(curr_contract_price))
        contracts_to_buy = f"{contracts_to_buy}.00"

        if ConfigState.test_mode:
            


        response = await place_buy_order(contracts_to_buy=contracts_to_buy, curr_contract_price=curr_contract_price, ticker=ticker, method="POST")

        if response.status_code == 201:
            print(f"Order placed successfully!")
            print(f"Order details --> Bought {contracts_to_buy} contracts at a price of {curr_contract_price} per contract.")

            # this might be better to just pull from kalshi via async request but could take longer
            TradingState.total_mkt_pos_usd += curr_contract_price * contracts_to_buy
            
            # TODO save this to the db --> save_order_to_db()
        else:
            print("Error buying contracts!")
            print(f"Error: {response.status_code} - {response.text}")