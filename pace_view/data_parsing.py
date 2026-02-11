from sport_activities_features.tcx_manipulation import TCXFile
from sport_activities_features import WeatherIdentification


class DataParser:
    def __init__(self, weather_api_key=None, time_delta=1):
        self.api_key = weather_api_key
        self.time_delta = time_delta
        self.tcx_loader = TCXFile()

    def _get_val(self, item, keys):
        for k in keys:
            if isinstance(item, dict):
                if k in item:
                    return item[k]
            else:
                if hasattr(item, k):
                    return getattr(item, k)
        return 0.0

    def parse_file(self, filepath, is_training=False):
        """
        Parse a TCX file and fetch weather data (if enabled).
        Returns a tuple: (activity_dict, weather_data_list) or None if invalid.
        """
        try:
            raw = self.tcx_loader.read_one_file(filepath)
            act = self.tcx_loader.extract_activity_data(raw, numpy_array=True)
            if "Biking" not in act.get("activity_type", ""):
                return None
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return None

        weather_data = []
        if self.api_key and not is_training:
            try:
                wid = WeatherIdentification(act["positions"], act["timestamps"], self.api_key)
                w_list = wid.get_weather(time_delta=self.time_delta)
                weather_data = wid.get_average_weather_data(act["timestamps"], w_list)
            except Exception as e:
                print(f"Weather API Error: {e}. Using Neutral weather.")
                weather_data = [{"temp": 20, "wspd": 0, "wdir": 0, "hum": 20}] * len(act["timestamps"])
        else:
            weather_data = [{"temp": 20, "wspd": 0, "wdir": 0, "hum": 20}] * len(act["timestamps"])

        return act, weather_data
