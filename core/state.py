from dataclasses import dataclass

@dataclass
class TradingState:
    min_edge_pct: int
    max_bet_pct_of_portfolio: int
    min_pct_of_values_in_temp_range: int
    min_pct_of_values_over_under_temp: int
    
    buy_order_url_path: str
    buy_order_base_url_path: str
    private_key_path: str

    total_mkt_pos_usd: float
    total_portfolio_usd: float

    tmax_noaa_values: list[float]
    tmin_noaa_values: list[float]

