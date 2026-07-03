import datetime
import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from core.orchestrator import load_config, load_states, load_noaa_url_lat_lon
from extraction.get_grib import get_noaa_forecast
from connection.kalshi import connect
from extraction.get_trade_info import get_account_balance
from core.state import TradingState, ConfigState
from connection.credentials import create_signature, load_private_key_from_file, generate_timestamp

print("Loading config...")
config = load_config()
print("Config loaded!")

test_mode = config.get("settings", {}).get("test_mode")

pk_file_path = ConfigState.pk_file_path
ConfigState.private_key = load_private_key_from_file(file_path=pk_file_path)

print("Loading initial trading state...")
load_states(config=config)
print("Initial trading state loaded!")

print("Retrieving account balance...")
get_account_balance(timestamp=generate_timestamp())
print("Retrieved account balance!")


noaa_url, latitude, longitude = load_noaa_url_lat_lon()
# load weather metrics on boot so that trading logic has data
get_noaa_forecast(noaa_url=noaa_url, latitude=latitude, longitude=longitude)

scheduler = AsyncIOScheduler()
scheduler.add_job(get_noaa_forecast, "cron", hour="*/6", minute=0, kwargs={"noaa_url": noaa_url, "latitude": latitude, "longitude": longitude})

async def main():
    # needs to start within the main event loop for time sync purposes
    scheduler.start()
    timestamp = generate_timestamp()
    if test_mode:
        ws_url = config.get("settings", {}).get("test_urls", {}).get("websockets", {}).get("kalshi_ws_url")
        print("Test mode toggled ON")
    else:
        ws_url = config.get("settings", {}).get("urls", {}).get("websockets", {}).get("kalshi_ws_url")
        print("Test mode toggled OFF")

    ws_url_endpoint = config.get("settings", {}).get("urls", {}).get("endpoints", {}).get("kalshi_trade_endpoint")

    generated_signature = create_signature(private_key=ConfigState.private_key, method="GET", path=ws_url_endpoint, timestamp=timestamp)
    await connect(ws_url=ws_url, api_key_id=ConfigState.api_key_id, generated_signature=generated_signature, timestamp=timestamp)


asyncio.run(main())

