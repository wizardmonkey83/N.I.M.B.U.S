from core.orchestrator import load_config
from extraction.get_grib import get_noaa_forecast
from extraction.parse_grib import extract_forecast_from_temp

config = load_config()

noaa_url = config.get("settling_locations").get("new_york_city").get("grib_filter_url")
latitude = config.get("settling_locations").get("new_york_city").get("coordinates").get("latitude")
longitude = config.get("settling_locations").get("new_york_city").get("coordinates").get("longitude")

temp_forecast_path = get_noaa_forecast(url=noaa_url, forecast_hour="06")
extract_forecast_from_temp(temp_forecast_path=temp_forecast_path, latitude=latitude, longitude=longitude)

