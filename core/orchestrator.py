import json
from core.state import TradingState

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
    
    buy_order_url_path = config.get("settings", {}).get("trading", {}).get("buy_order_url_path")

    trading_state = TradingState(
        min_edge_pct=min_edge_pct, 
        max_bet_pct_of_portfolio=max_bet_pct_of_portfolio, 
        min_pct_of_values_in_temp_range=min_pct_of_values_in_temp_range, 
        min_pct_of_values_over_under_temp=min_pct_of_values_over_under_temp,
        buy_order_url_path=buy_order_url_path
    )
    
    return
