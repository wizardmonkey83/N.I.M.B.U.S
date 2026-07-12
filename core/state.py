from dataclasses import dataclass
import websockets

@dataclass
class TradingState:
    # risk settings
    min_edge_frac: float
    max_bet_frac_of_portfolio: float
    min_frac_of_values_in_temp_range: float
    min_frac_of_values_over_under_temp: float
    kelly_fraction_haircut_frac: float

    # position, portfolio metadata
    total_mkt_pos_usd: float
    total_portfolio_usd: float

@dataclass
class DataState:
    # temperature metadata
    # TODO will be swapped for dict[list]
    tmax_noaa_values: list[float]
    tmin_noaa_values: list[float]

    # trading metadata
    daily_tickers: dict

    # connection
    kalshi_websocket: websockets.ClientConnection

@dataclass
class ConfigState:
    # general
    test_mode: bool
    kalshi_base_url: str
    kalshi_get_markets_url: str

    # credentials
    api_key_id: str
    private_key: str
    pk_file_path: str

    # place orders
    place_order_endpoint: str

    # check orders
    get_order_endpoint: str

    # portofolio metadata urls
    portfolio_balance_url_requests: str
    portfolio_balance_url_endpoint: str

    # trading metadata
    # TODO setup for one location in order to test, will be swapped to dict later on. 
    kalshi_series_ticker: str
    kalshi_channels: list[str]
