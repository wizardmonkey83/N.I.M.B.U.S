from core.state import TradingState, DataState

def get_pct(numerator, denominator):
    return numerator / denominator if denominator != 0 else 0

def temp_values_against_base_temp(min_kalshi_temp: int, max_kalshi_temp: int, temp_values: list[float]):
    # say the list contains 30 values...
    total_values = len(temp_values)
    # and if 17 of those values fall inside the range --> min_kalshi_temp, max_kalshi_temp...
    values_in_range = 0
    for temp in temp_values:
        # if temp == 82.6 then rnd_temp == 83
        rnd_temp = round(temp)
        # if min_kalshi_temp == 82 and max_kalshi_temp == 84 then rnd_temp fits!
        # which means values_in_range gets 1 added to it
        if rnd_temp >= min_kalshi_temp and rnd_temp <= max_kalshi_temp:
            values_in_range += 1

    # then this would return 17/30 --> 0.567
    values_in_range_frac = get_pct(numerator=values_in_range, denominator=total_values)
    return values_in_range_frac

# high=False should be configured depending on the market. high=True for highest temp, high=False for lowest temp
def calculate_edge(min_kalshi_temp: int, max_kalshi_temp: int, yes_price: float, no_price: float, high=False, buying=True):
    """
        Imagine this example scenario:

        Lets initialize some variables: 

            min_kalshi_temp = 82
            max_kalshi_temp = 84

            best_ask (price to buy contract at a 'YES' position) = 0.53
            best_bid (price to sell contract at a 'NO' position) = 0.45

            high (trading on 'highest temp in NYC today') = True

            min_edge_pct (the minimum difference between calculated_odds and best_ask or best_bid) = 0.10
        
        Now that we have those, lets move onto getting our odds:

            Variables are passed into: temp_values_against_base_temp() and we get returned the calculated odds --> 0.82

        But what do the calculated odds represent?

        The value: 0.82 represents the number of NOAA temp values that fit within the range 82-84.
        In other words, the program determines there's a 82% chance that the weather will fall somewhere between 82-84.

        Is calculated_odds higher than the best_ask?
        Is calculated_odds lower than the best bid?

        If higher, then does the margin exceed min_edge_pct?
        If lower, then does the margin exceed min_edge_pct?

        In our scenario, the calculated_odds exceed the min_edge_pct (0.82 - 0.53 = 0.29 and 0.29 > 0.10) so the trade is worthwhile.

        To close out, we return: True (buy is worthwhile) and the calculated_odds (for math down the line).

        Success!
    """

    if high:
        temp_values = DataState.tmax_noaa_values
    else:
        temp_values = DataState.tmin_noaa_values

    min_edge_pct = TradingState.min_edge_frac

    # returns floating point number --> ex. 0.567
    calculated_odds_of_event_occuring = temp_values_against_base_temp(min_kalshi_temp=min_kalshi_temp, max_kalshi_temp=max_kalshi_temp, temp_values=temp_values)

    # 0.82 - 0.53 = 0.29
    yes_trading_edge = calculated_odds_of_event_occuring - yes_price
    # 0.18 (chance of event not occuring) - 0.45 = -0.27
    no_trading_edge = calculated_odds_of_event_occuring - no_price
    trading_edge = max(yes_trading_edge, no_trading_edge)

    decision = None
    if trading_edge >= min_edge_pct:
        should_trade = True

        if trading_edge == yes_trading_edge:
            trade_type = "buy"
        else:
            trade_type = "sell"
        
        decision = {
            "trade_type": trade_type,
            "odds_of_event_occuring": calculated_odds_of_event_occuring if trade_type == "buy" else 1 - calculated_odds_of_event_occuring
        }

        return should_trade, decision
    
    should_trade = False
    return should_trade, decision