import requests
import os
import time

from datetime import datetime
from tempfile import NamedTemporaryFile

def get_noaa_forecast(url: str, forecast_hour: str):
    # url needs these params --> todays_date, file_cycle, forecast_hour
    # todays_date --> yyyymmdd
    # file_cycle --> 00, 06, 12, 18

    date_obj = datetime.now()
    todays_date = date_obj.strftime("%Y%m%d")

    file_cycle = "18"

    # avoids potential script identification
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
    }

    forecast_path = None
    for i in range(4):
        try: 

            with NamedTemporaryFile(suffix=".grib2", delete=False) as temp_forecast:

                url = url.format(todays_date=todays_date, forecast_hour=forecast_hour, file_cycle=file_cycle)
                print(f"URL: {url}")

                with requests.get(url, timeout=15, headers=headers, stream=True) as r:
                    r.raise_for_status()
                    # chunk_size can change depending on the systems memory. more = faster download. 
                    for chunk in r.iter_content(chunk_size=8192):
                        temp_forecast.write(chunk)
                forecast_path = temp_forecast.name

            if forecast_path:
                break

        except Exception as e:
            print(f"Error getting forecast. Cycle: {i}. Error: {e}")
            print(f"Resposnse content: {r.content}")
            time.sleep(i * 2)
        
    return forecast_path