import xarray
import os

def convert_to_f_from_k(temp: float):
    return (temp - 273.15) * 1.8 + 32

def extract_forecast_from_temp(temp_forecast_path: str, latitude: float, longitude: float):

    try:
        if not os.path.exists(temp_forecast_path):
            raise Exception("temp_forecast_path does not exist.")
        
        dataset = xarray.open_dataset(temp_forecast_path, engine="cfgrib")
        subset = dataset.sel(latitude=latitude, longitude=longitude, method="nearest")

        tmax, tmin = subset["tmax"].values, subset["tmin"].values

        # adjust for fahrenheit
        tmax = convert_to_f_from_k(tmax)
        tmin = convert_to_f_from_k(tmin)

        return tmax, tmin

    except Exception as e:
        print(f"Erorr parsing forecast: {e}")

    finally:
        if dataset:
            dataset.close()
        
        if os.path.exists(temp_forecast_path):
            os.remove(temp_forecast_path)