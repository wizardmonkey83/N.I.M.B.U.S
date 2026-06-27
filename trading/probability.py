


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


def calculate_temp_edge(tmax: list, tmin: list, kalshi_temp_ranges: list[list]):
    
    results = {}
    for temp_range in kalshi_temp_ranges:
        if len(temp_range) != 2:
            pass

        min_kalshi_temp, max_kalshi_temp = temp_range[0], temp_range[1]
        tmax_values_in_range_pct = temp_values_against_base_temp(min_kalshi_temp=min_kalshi_temp, max_kalshi_temp=max_kalshi_temp, temp_values=tmax)
        tmin_values_in_range_pct = temp_values_against_base_temp(min_kalshi_temp=min_kalshi_temp, max_kalshi_temp=max_kalshi_temp, temp_values=tmin)

        total_pct= tmax_values_in_range_pct + tmin_values_in_range_pct
        summary = {
            "min_kalshi_temp": min_kalshi_temp,
            "max_kalshi_temp": max_kalshi_temp,
            "tmax_values_in_range_pct": tmax_values_in_range_pct,
            "tmin_values_in_range_pct": tmin_values_in_range_pct
        }
        results[total_pct] = summary

    max_pct = max(results)
    ideal_min_kalshi_temp = results[max_pct][min_kalshi_temp]
    ideal_max_kalshi_temp = results[max_pct][max_kalshi_temp]
    
    return ideal_min_kalshi_temp, ideal_max_kalshi_temp
 


    




def calculate_edge(curr_price: float):






