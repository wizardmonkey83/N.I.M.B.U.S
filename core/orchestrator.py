import json
from core.state import TradingState, ConfigState
from decouple import config

def load_config():
    config_path = "config.json"

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            dict_config = json.load(f)

            if not isinstance(dict_config, dict):
                raise TypeError("dict_config must be a dict type!")

            return dict_config
        
    except Exception as e:
        raise Exception(f"Unable to load config as a dict: {e}")
    
def load_trading_state(config: dict):
    min_edge_pct = config.get("settings", {}).get("trading", {}).get("min_edge_pct")
    max_bet_pct_of_portfolio = config.get("settings", {}).get("trading", {}).get("max_bet_pct_of_portfolio")
    min_pct_of_values_in_temp_range = config.get("settings", {}).get("trading", {}).get("min_pct_of_values_in_temp_range")
    min_pct_of_values_over_under_temp = config.get("settings", {}).get("trading", {}).get("min_pct_of_values_over_under_temp")

    buy_order_url_path = config.get("settings", {}).get("urls", {}).get("endpoints", {}).get("buy_order_url_path")
    portfolio_balance_url_requests = config.get("settings", {}).get("urls", {}).get("requests", {}).get("kalshi_portfolio_balance_url")
    portfolio_balance_url_endpoint = config.get("settings", {}).get("urls", {}).get("endpoints", {}).get("kalshi_portfolio_balance_endpoint")
    api_key_id = config("API_KEY_ID")
    pk_file_path = config("PK_FILE_PATH")

    trading_state = TradingState(
        min_edge_pct=min_edge_pct, 
        max_bet_pct_of_portfolio=max_bet_pct_of_portfolio, 
        min_pct_of_values_in_temp_range=min_pct_of_values_in_temp_range, 
        min_pct_of_values_over_under_temp=min_pct_of_values_over_under_temp,
    )

    config_state = ConfigState(
        buy_order_url=buy_order_url_path,
        api_key_id=api_key_id,
        pk_file_path=pk_file_path,
        portfolio_balance_url_requests=portfolio_balance_url_requests,
        portfolio_balance_url_endpoint=portfolio_balance_url_endpoint
    )

def load_noaa_url_lat_lon():
    noaa_url = config.get("settling_locations", {}).get("new_york_city", {}).get("grib_filter_url")
    latitude = config.get("settling_locations", {}).get("new_york_city", {}).get("coordinates", {}).get("latitude")
    longitude = config.get("settling_locations", {}).get("new_york_city", {}).get("coordinates", {}).get("longitude")
    return noaa_url, str(latitude), str(longitude)
