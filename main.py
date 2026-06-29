import datetime
import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from core.orchestrator import load_config, load_trading_state, load_noaa_url_lat_lon
from extraction.get_grib import get_noaa_forecast
from connection.kalshi import connect, get_account_balance
from core.state import TradingState, ConfigState
from connection.credentials import create_signature, load_private_key_from_file

print("Loading config...")
config = load_config()
print("Config loaded!")

print("Loading initial trading state...")
load_trading_state(config=config)
print("Initial trading state loaded!")

print("Retrieving account balance...")
get_account_balance()
print("Retrieved account balance!")


noaa_url, latitude, longitude = load_noaa_url_lat_lon()
# load weather metrics on boot so that trading logic has data
get_noaa_forecast(noaa_url=noaa_url, latitude=latitude, longitude=longitude)

scheduler = AsyncIOScheduler()
scheduler.add_job(get_noaa_forecast(), "cron", hour="*/6", minute=0, kwargs={"noaa_url": noaa_url, "latitude": latitude, "longitude": longitude})
# TODO add job that checks currently held contracts against updated odds. should run on the same schedule as get_noaa_forecast
scheduler.start()

async def main():
    pk_file_path = ConfigState.pk_file_path
    ConfigState.private_key = load_private_key_from_file(file_path=pk_file_path)

    curr_datetime = datetime.datetime.now()
    timestamp = curr_datetime.timestamp()
    curr_time_miliseconds = int(timestamp * 1000)
    timestamp_str = str(curr_time_miliseconds)

    ws_url = config.get("settings", {}).get("kalshi_ws_url")
    generated_signature = create_signature(private_key=ConfigState.private_key, timestamp=timestamp, method="GET", path=ws_url)
    await connect(ws_url=ws_url, api_key_id=ConfigState.api_key_id, generated_signature=generated_signature)


asyncio.run(main())

