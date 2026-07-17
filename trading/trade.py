import uuid
import datetime
import math
import asyncio
import requests_async
from collections import defaultdict


from core.state import TradingState, ConfigState, TestState
from connection.credentials import load_private_key_from_file, create_signature, package_header, generate_timestamp

def get_kelly_fraction(odds_of_event_occuring: float, implied_prob: float):
    """
        Using this formula --> f = ((b(p) - q) / b) * h
        Where: 
            f = fraction of bankroll to wager
            b = net profit per one dollar risked --> 1 - implied odds / implied odds
            p = win probability
            q = loss probability
            h = percent of kelly fraction to use

        Imagine a scenario where a contract is priced at $0.53 and the program determines that contract has a 0.82 chance of occurring.
        Here:
            b = 1 - 0.53 / 0.53 --> 0.88
            p = 0.82
            q = 0.18
            h = 0.50

        So: 
            f = ((0.88(0.82) - 0.18) / 0.88) * 0.5
            f = 0.31
        
        This means for this trade, 31% of bankroll should be wagered. 
    """
    contract_price = implied_prob
    expected_profit = 1 - contract_price

    b = expected_profit / contract_price
    p = odds_of_event_occuring
    q = 1 - odds_of_event_occuring
    h = TradingState.kelly_fraction_haircut_frac

    kelly_fraction = (((b * p) - q) / b) * h
    return round(kelly_fraction, 2)


async def place_order(num_of_contracts: float, curr_contract_price: float, ticker: str, side: str):
    """
        Sample scenario:

        First, arguemnts are parsed:

        num_of_contracts = 92
        curr_contract_price = 0.53
        ticker = FED-23DEC-T3.00
        side = "ask"
        
        Now, onto the core logic:
    
        kalshi_base_url = "https://external-api.kalshi.com"
        place_order_endpoint = "/trade-api/v2/portfolio/events/orders"

        Private key and API key id are loaded.

        for i in range(4):
            Timestamp, generated signature (for request signing), and headers are all created.

            formatted_contract_price = "92.00"
            client_order_id = 3f2b1c9e-8d4a-4a7f-9c2d-6e1b7f0a5d13

            order_data = {
                "ticker": FED-23DEC-T3.00,
                "side": "ask",
                "count": "92.00",
                "price": "0.53",
                "time_in_force": "good_till_canceled",
                "self_trade_prevention_type": "taker_at_cross",
                "client_order_id": 3f2b1c9e-8d4a-4a7f-9c2d-6e1b7f0a5d13
            }


            Now we wait!

            Request success? BREAK

            If not:

            retry_url_path = "https://external-api.kalshi.com/trade-api/v2/portfolio/orders/3f2b1c9e-8d4a-4a7f-9c2d-6e1b7f0a5d13"

            Generated signature and headers are created.

            Request is sent out to see if the order exists.

            If it does: BREAK. If it doesn't: CONTINUE LOOPING
    """

    kalshi_base_url = ConfigState.kalshi_base_url
    place_order_endpoint = ConfigState.place_order_endpoint

    private_key = ConfigState.private_key
    api_key_id = ConfigState.api_key_id

    for i in range(4):
        timestamp = generate_timestamp()
        generated_signature = create_signature(private_key=private_key, method="POST", path=place_order_endpoint, timestamp=timestamp)
        headers = package_header(api_key_id=api_key_id, generated_signature=generated_signature, timestamp=timestamp, content_type="application/json")

        formatted_num_contracts = f"{num_of_contracts}.00"
        client_order_id = str(uuid.uuid4())

        order_data = {
            "ticker": ticker,
            "side": side,
            "count": formatted_num_contracts,
            "price": str(curr_contract_price),
            "time_in_force": "good_till_canceled",
            "self_trade_prevention_type": "taker_at_cross",
            "client_order_id": client_order_id
        }

        try:
            response = await requests_async.post(url=(kalshi_base_url + place_order_endpoint), headers=headers, json=order_data)
            break

        except Exception as e:
            get_order_endpoint = ConfigState.get_order_endpoint

            # TODO check if this url is correct
            retry_url_path = kalshi_base_url + get_order_endpoint + client_order_id

            generated_signature = create_signature(private_key=private_key, method="GET", path=retry_url_path, timestamp=timestamp)
            headers = package_header(api_key_id=api_key_id, generated_signature=generated_signature, timestamp=timestamp)

            # TODO check this url
            response = await requests_async.get(url=retry_url_path, headers=headers)

            if response.status_code == 200:
                break

            print(f"Error while placing order request: {e}")
            await asyncio.sleep(i * 2)

    return response if response else None

async def buy_contracts(curr_contract_price: float, ticker: str, odds_of_event_occuring: float, side: str):
    """
        Sample scenario:

        curr_contract_price = 0.54
        ticker = FED-23DEC-T3.00
        odds_of_event_occuring = 0.82

        max_bet_frac_of_portfolio = 0.30
        total_mkt_pos_usd = 100
        total_portfolio_usd = 500

        pos_vs_portfolio = 100/500 = 0.20

        if 0.20 <= 0.30:
            bettable_frac_of_portfolio = 0.30 - 0.20 = 0.10
            kelly_bettable_frac = 0.31

            bet_amount_usd = 0.10 * 500 = 50

            contracts_to_buy = floor(50 / 0.54) = 92

        else:
            nothing
    """

    max_bet_frac_of_portfolio = TradingState.max_bet_frac_of_portfolio
    total_mkt_pos_usd = TradingState.total_mkt_pos_usd
    total_portfolio_usd = TradingState.total_portfolio_usd

    # stores as a frac --> 50/100 = 0.5
    pos_vs_portfolio = total_mkt_pos_usd / total_portfolio_usd
    if pos_vs_portfolio <= max_bet_frac_of_portfolio:
        # stores in this format --> 
        bettable_frac_of_portfolio = max_bet_frac_of_portfolio - pos_vs_portfolio
        kelly_bettable_frac = get_kelly_fraction(odds_of_event_occuring=odds_of_event_occuring, implied_prob=curr_contract_price)

        if kelly_bettable_frac > bettable_frac_of_portfolio:
            bet_amount_usd = bettable_frac_of_portfolio * total_portfolio_usd
        else:
            bet_amount_usd = kelly_bettable_frac * total_portfolio_usd
        
        contracts_to_buy = math.floor(bet_amount_usd / curr_contract_price)

        test_mode = ConfigState.test_mode
        if test_mode:
            live_orders = TestState.live_orders

            string_contracts_to_buy = f"{contracts_to_buy}.00"

            order_data = next((order for order in live_orders if order["ticker"] == ticker), None)
            if not order_data:
                order_data = defaultdict(dict)
                order_data["ticker"] = ticker

            order_data["position_fp"] = string_contracts_to_buy
            order_data["market_exposure_dollars"] = curr_contract_price

            total_traded_dollars = float(order_data.get("total_traded_dollars", "00.00")) + (contracts_to_buy * curr_contract_price)
            # im pretty sure this formatting is fine
            order_data["total_traded_dollars"] = str(total_traded_dollars)

        else:
            response = await place_order(num_of_contracts=contracts_to_buy, curr_contract_price=curr_contract_price, ticker=ticker, side=side)

        if response.status_code == 201 or test_mode:
            print(f"Order placed successfully!")
            print(f"Order details --> Bought {contracts_to_buy} contracts at a price of {curr_contract_price} per contract.")

            # this might be better to just pull from kalshi via async request but could take longer
            TradingState.total_mkt_pos_usd += bet_amount_usd
            
            # TODO save this to the db --> save_order_to_db()
        else:
            print("Error buying contracts!")
            print(f"Error: {response.status_code} - {response.text}")