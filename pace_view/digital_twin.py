from sklearn.ensemble import RandomForestRegressor


class DigitalTwinModel:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, max_depth=15, n_jobs=-1)
        self.is_trained = False
        # wind_speed_mps and wind_dir are implicitly included via virtual_power
        self.features = ["virtual_power", "speed_mps", "dist", "temp", "ele", "hum"]

    def train(self, df_history):
        """
        Trains the Digital Twin model to predict heart rate from physics and environment.
        """
        numeric_cols = df_history.select_dtypes(include=["number"]).columns
        if "hr" not in numeric_cols:
            raise KeyError("Missing numeric 'hr'")

        if "hum" not in df_history.columns:
            df_history["hum"] = 50.0

        df_clean = df_history.dropna(subset=self.features + ["hr"])

        df_resampled = df_clean.iloc[::30]  # Downsample to every 30th second

        X = df_resampled[self.features]
        y = df_resampled["hr"]

        self.model.fit(X, y)
        self.is_trained = True
        return self.model.score(X, y)

    def predict(self, df_new):
        """
        Predicts heart rate for the provided dataframe.
        """
        if not self.is_trained:
            raise Exception("Model not trained.")
        X = df_new[self.features].fillna(0)
        return self.model.predict(X)

    def predict_drift(self, df_new):
        """
        Calculates the physiological drift (Actual HR - Predicted HR).
        """
        if not self.is_trained:
            raise Exception("Model not trained.")

        df_new = df_new.copy()
        df_new["hr_predicted"] = self.predict(df_new)

        # Positive drift (+10) = heart is beating faster than expected (e.g., heat, fatigue)
        # Negative drift (-10) = heart is beating slower (e.g., fresh, cold)
        df_new["drift"] = df_new["hr"] - df_new["hr_predicted"]

        return df_new
