import pandas as pd
import pytest

from pace_view.data_parsing import DataParser
from pace_view.data_cleaning import DataCleaner
from pace_view.physics import PhysicsEngine

import os

#data parsing test on a single tcx file
def test_data_parsing_with_tcx_file():
    tcx_path = "data/1.tcx"

    parser = DataParser(weather_api_key=None)

    result = parser.parse_file(tcx_path, is_training=True)
    assert result is not None

    activity, weather = result

    assert "Biking" in activity.get("activity_type", "")
    assert len(activity["timestamps"]) > 0
    assert len(weather) == len(activity["timestamps"])    


#data parsing test on a single tcx file with weather api enabled
def test_data_parsing_with_tcx_file_with_weather():
    tcx_path = "data/1.tcx"

    weather_api_key = os.getenv('weather_api_key')

    parser = DataParser(weather_api_key=weather_api_key)

    result = parser.parse_file(tcx_path, is_training=True)
    assert result is not None

    activity, weather = result

    assert "Biking" in activity.get("activity_type", "")
    assert len(activity["timestamps"]) > 0
    assert len(weather) == len(activity["timestamps"])
    assert weather[0]['temp'] >= -20
    assert weather[0]['hum'] >= 0


#data cleaning test on a single tcx file
def test_data_cleaning_after_parsing():
    tcx_path = "data/1.tcx"
    parser = DataParser(weather_api_key=None)
    cleaner = DataCleaner(parser)

    parsed = parser.parse_file(tcx_path, is_training=True)
    assert parsed is not None

    act, weather = parsed
    df = cleaner.to_dataframe(act, weather)

    assert df is not None
    assert len(df) > 0
    assert "speed_mps" in df.columns
    assert pd.api.types.is_numeric_dtype(df["speed_mps"])


#test the mining on five files
#this test only runs if niaarm is installed
def test_mining_with_five_tcx_files(monkeypatch):
    pytest.importorskip("niaarm")
    pytest.importorskip("niapy")

    from pace_view.mining import PatternMiner

    weather_api_key = os.getenv('weather_api_key')

    parser = DataParser(weather_api_key=weather_api_key)
    cleaner = DataCleaner(parser)
    physics = PhysicsEngine()

    LIMIT = 100
    files = []
    for i in range(1, 200):
        path = f"data/{i}.tcx"
        parsed = parser.parse_file(path, is_training=True)
        if parsed is None:
            continue
        files.append(path)
        if len(files) == LIMIT:
            break

    assert len(files) == LIMIT

    dfs = []
    for path in files:
        parsed = parser.parse_file(path, is_training=True)
        assert parsed is not None
        activity, weather = parsed
        df = cleaner.to_dataframe(activity, weather)
        df = physics.calculate_virtual_power(df)
        dfs.append(df)

    full_history_df = pd.concat(dfs, ignore_index=True)
    assert "headwind_mps" in full_history_df.columns
    assert "grad" in full_history_df.columns

    # monkeypatch mining so it is fast and deterministic
    # class DummyDataset:
    #     def __init__(self, path):
    #         self.path = path

    # def fake_get_rules(dataset, algo, metrics, max_iters, logging):
    #     return (["IF Wind=Headwind AND Terrain=Climb THEN Struggling"], 0.01)

    expected_rule = ["IF Wind=Headwind AND Terrain=Climb THEN Struggling"]

    # monkeypatch.setattr("pace_view.mining.Dataset", DummyDataset)
    # monkeypatch.setattr("pace_view.mining.get_rules", fake_get_rules)

    miner = PatternMiner()
    report = miner.discover_rules(full_history_df)

    print(report)

    assert isinstance(report, dict)
    assert "Top_Rules" in report