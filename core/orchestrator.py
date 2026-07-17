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
    
def load_states(config: dict):
    # test mode
    test_mode = config["settings"]["test_mode"]

    # trading
    min_edge_pct = config["settings"]["trading"]["min_edge_pct"]
    max_bet_pct_of_portfolio = config["settings"]["trading"]["max_bet_pct_of_portfolio"]
    min_pct_of_values_in_temp_range = config["settings"]["trading"]["min_pct_of_values_in_temp_range"]
    min_pct_of_values_over_under_temp = config["settings"]["trading"]["min_pct_of_values_over_under_temp"]

    # requests urls
    kalshi_base_url = config["settings"]["urls"]["requests"]["kalshi_base_url"]
    kalshi_get_markets_url = config["settings"]["urls"]["requests"]["kalshi_get_markets_url"]
    portfolio_balance_url_requests = config["settings"]["urls"]["requests"]["kalshi_portfolio_balance_url"]

    # endpoints
    place_order_endpoint = config["settings"]["urls"]["endpoints"]["place_order_endpoint"]
    get_order_endpoint = config["settings"]["urls"]["endpoints"]["get_order_endpoint"]
    portfolio_balance_url_endpoint = config["settings"]["urls"]["endpoints"]["kalshi_portfolio_balance_endpoint"]
    get_positions_endpoint = config["settings"]["urls"]["endpoints"]["get_positions_endpoint"]
    
    # other
    kalshi_channels = config["settings"]["other"]["kalshi_channels"]

    # TODO hardcoded for now. needs to handle multiple locations
    kalshi_series_ticker = config["settling_locations"]["new_york_city"]["series_ticker"]

    api_key_id = config("API_KEY_ID")
    pk_file_path = config("PK_FILE_PATH")

    trading_state = TradingState(
        # risk settings
        min_edge_pct=min_edge_pct, 
        max_bet_pct_of_portfolio=max_bet_pct_of_portfolio, 
        min_pct_of_values_in_temp_range=min_pct_of_values_in_temp_range, 
        min_pct_of_values_over_under_temp=min_pct_of_values_over_under_temp,
    )

    config_state = ConfigState(
        # general
        test_mode=test_mode,
        kalshi_base_url=kalshi_base_url,

        # place orders
        place_order_endpoint=place_order_endpoint,

        # get orders
        get_order_endpoint=get_order_endpoint,

        # credentials
        api_key_id=api_key_id,
        pk_file_path=pk_file_path,

        # portofolio metadata
        portfolio_balance_url_requests=portfolio_balance_url_requests,
        portfolio_balance_url_endpoint=portfolio_balance_url_endpoint,

        # trading metadata
        kalshi_get_markets_url=kalshi_get_markets_url,
        kalshi_series_ticker=kalshi_series_ticker,
        kalshi_channels=kalshi_channels
    )

def load_noaa_url_lat_lon():
    # TODO all hardcoded for now
    noaa_url = config["settling_locations"]["new_york_city"]["grib_filter_url"]
    latitude = config["settling_locations"]["new_york_city"]["coordinates"]["latitude"]
    longitude = config["settling_locations"]["new_york_city"]["coordinates"]["longitude"]

    return noaa_url, str(latitude), str(longitude)