import requests
import os
import time
import xarray

from datetime import datetime
from tempfile import NamedTemporaryFile

from core.state import DataState

def convert_to_f_from_k(temp: float):
    return (temp - 273.15) * 1.8 + 32

def extract_forecast_from_temp(temp_forecast_path: str, latitude: float, longitude: float):

    dataset = None
    try:
        if not os.path.exists(temp_forecast_path):
            raise Exception("temp_forecast_path does not exist.")
        
        dataset = xarray.open_dataset(temp_forecast_path, engine="cfgrib")

        # rounding since xarray lat/lon is rounded. adding 360 to longitude since noaa uses 0-360 instead of -180-180
        latitude, longitude = round(latitude, 2), round((longitude + 360), 2)
        # interp() grabs a weighted average from the lat/lon around the target lat/lon. sel() also works but just grabs the closest. use "method='nearest" when using sel()
        subset = dataset.interp(latitude=latitude, longitude=longitude)

        tmax, tmin = subset["tmax"].values, subset["tmin"].values

        # adjust for fahrenheit
        tmax = convert_to_f_from_k(float(tmax))
        tmin = convert_to_f_from_k(float(tmin))

        return tmax, tmin

    except Exception as e:
        print(f"Erorr parsing forecast: {e}")

    finally:
        if dataset:
            dataset.close()
        
        if os.path.exists(temp_forecast_path):
            os.remove(temp_forecast_path)


# makes the get call to noaa to get raw temp information
def get_noaa_forecast(url: str, latitude: str, longitude: str):
    # url needs these params --> todays_date, file_cycle, forecast_hour
    # todays_date --> yyyymmdd
    # file_cycle --> 00, 06, 12, 18

    date_obj = datetime.now()
    todays_date = date_obj.strftime("%Y%m%d")

    curr_hour = datetime.now().hour
    if len(curr_hour) == 2:
        forecast_hour = f"0{curr_hour}"
        file_cycle = str(curr_hour)
    elif len(curr_hour) == 1:
        forecast_hour = f"00{curr_hour}"
        file_cycle = f"0{curr_hour}"
    # TODO might need a failsafe in case datetime implodes


    # avoids potential script identification
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
    }

    tmax_values, tmin_values = [], []
    forecast_path = None
    for file in range(31):
        if file == 0:
            member_id = "gec00"
        elif file < 10:
            member_id = f"gep0{file}"
        else:
            member_id = f"gep{file}"

        # to avoid crashing if the get request fails once
        for i in range(4):
            try: 

                with NamedTemporaryFile(suffix=".grib2", delete=False) as temp_forecast:

                    formatted_url = url.format(todays_date=todays_date, forecast_hour=forecast_hour, file_cycle=file_cycle, member_id=member_id)

                    with requests.get(formatted_url, timeout=15, headers=headers, stream=True) as r:
                        r.raise_for_status()
                        # chunk_size can change depending on the systems memory. more = faster download. 
                        for chunk in r.iter_content(chunk_size=8192):
                            temp_forecast.write(chunk)

                    forecast_path = temp_forecast.name

                if forecast_path:
                    break

            except Exception as e:
                print(f"Error getting forecast. File: {file}. Cycle: {i}. Error: {e}")
                print(f"Resposnse content: {r.content}")
                time.sleep(i * 2)

        if forecast_path:
            tmax, tmin = extract_forecast_from_temp(temp_forecast_path=forecast_path, latitude=latitude, longitude=longitude)
            tmax_values.append(tmax)
            tmin_values.append(tmin)

        print(f" Values from file {file} successfully loaded.")
    
    DataState.tmax_noaa_values = tmax_values
    DataState.tmin_noaa_values = tmin_values
    print("TMAX, TMIN values loaded to trading state!")