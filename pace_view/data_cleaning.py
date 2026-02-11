"""
Cleaning and alignment logic for parsed activity and weather data.
"""

import numpy as np
import pandas as pd


class DataCleaner:
    """
    Builds a clean, aligned dataframe from parsed TCX and weather data.
    """
    def __init__(self, parser):
        self.parser = parser

    def to_dataframe(self, act, weather_data):
        """
        Clean and align parsed activity + weather into a dataframe.
        """
        temps = [self.parser._get_val(w, ["temp", "temperature"]) for w in weather_data]
        hums = [self.parser._get_val(w, ["hum", "humidity"]) for w in weather_data]
        winds = [self.parser._get_val(w, ["wspd", "wind_speed"]) for w in weather_data]
        bearings = [self.parser._get_val(w, ["wdir", "wind_direction"]) for w in weather_data]

        hr_numeric = pd.to_numeric(act["heartrates"], errors="coerce")
        speed_numeric = pd.to_numeric(act["speeds"], errors="coerce")
        min_len = min(len(act["timestamps"]), len(hr_numeric))

        df = pd.DataFrame(
            {
                "time": act["timestamps"][:min_len],
                "lat": [p[0] for p in act["positions"]][:min_len],
                "lon": [p[1] for p in act["positions"]][:min_len],
                "ele": act["altitudes"][:min_len],
                "dist": act["distances"][:min_len],
                "hr": hr_numeric[:min_len],
                "speed_mps": speed_numeric[:min_len] / 3.6,
                "temp": temps[:min_len],
                "wind_speed_mps": np.array(winds[:min_len]) / 3.6,
                "wind_dir": bearings[:min_len],
                "hum": hums[:min_len],
            }
        )

        return df
