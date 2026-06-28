from core.state import TradingState

def get_pct(numerator, denominator):
    return numerator / denominator if denominator != 0 else 0

def temp_values_against_base_temp(min_kalshi_temp: int, max_kalshi_temp: int, temp_values: list[float]):
    total_values = len(temp_values)
    values_in_range = 0
    for temp in temp_values:
        rnd_temp = round(temp)
        if rnd_temp >= min_kalshi_temp and rnd_temp <= max_kalshi_temp:
            values_in_range += 1

    values_in_range_pct = get_pct(numerator=values_in_range, denominator=total_values)
    return values_in_range_pct

# high=False should be configured depending on the market. high=True for highest temp, high=False for lowest temp
def calculate_edge(min_kalshi_temp: int, max_kalshi_temp: int, best_ask: int, high=False):
    if high:
        temp_values = TradingState.tmax_noaa_values
    else:
        temp_values = TradingState.tmin_noaa_values

    min_edge_pct = TradingState.min_edge_pct

    calculated_odds = temp_values_against_base_temp(min_kalshi_temp=min_kalshi_temp, max_kalshi_temp=max_kalshi_temp, temp_values=temp_values)
    # multiplied by 100 in order to format pct/100 instead of a decimal
    trading_edge = abs((calculated_odds * 100) - best_ask)

    if trading_edge >= min_edge_pct:
        return True
    return False

    
    





