from dataclasses import dataclass

@dataclass
class TradingState:
    min_edge_frac: float
    max_bet_frac_of_portfolio: float
    min_frac_of_values_in_temp_range: float
    min_frac_of_values_over_under_temp: float
    kelly_fraction_haircut_frac: float

    total_mkt_pos_usd: float
    total_portfolio_usd: float

@dataclass
class DataState:
    tmax_noaa_values: list[float]
    tmin_noaa_values: list[float]

@dataclass
class ConfigState:
    api_key_id: str
    private_key: str

    api_key_id: str
    private_key: str
    
    buy_order_url: str
    buy_order_base_url: str
    pk_file_path: str
    portfolio_balance_url_requests: str
    portfolio_balance_url_endpoint: str

