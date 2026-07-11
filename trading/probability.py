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
# 
def calculate_edge(min_kalshi_temp: int, max_kalshi_temp: int, best_ask: int, high=False):
    if high:
        temp_values = DataState.tmax_noaa_values
    else:
        temp_values = DataState.tmin_noaa_values

    min_edge_pct = TradingState.min_edge_frac

    # returns floating point number --> ex. 0.567
    calculated_odds = temp_values_against_base_temp(min_kalshi_temp=min_kalshi_temp, max_kalshi_temp=max_kalshi_temp, temp_values=temp_values)
    # multiplied by 100 in order to format pct/100 instead of a decimal
    trading_edge = (calculated_odds * 100) - best_ask

    if trading_edge >= min_edge_pct:
        return True, calculated_odds
    return False, None