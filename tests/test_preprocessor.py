import pytest
import pandas as pd
import numpy as np
from processing.preprocessor import DataPreprocessor


@pytest.fixture
def raw_dataframe():
    """
    Return a sample raw DataFrame with issues for testing.
    """
    return pd.DataFrame(
        {
            "timestamp": ["2025-07-21 10:00:00", "invalid-date", np.nan],
            "source_ip": ["192.168.1.1", None, "10.0.0.1"],
            "destination_ip": [None, "10.0.0.2", "10.0.0.3"],
            "source_port": [443, 0, 70000],
            "destination_port": [80, -1, 65536],
            "protocol": ["TCP", None, "UDP"],
            "action": ["ALLOW", None, "DENY"],
            "bytes_sent": [1000, None, 5000],
            "bytes_received": [500, np.nan, 2000],
            "duration": [60, -10, None],
            "flags": ["SYN", None, "ACK"],
        }
    )


def test_clean_data_removes_duplicates(raw_dataframe):
    df = pd.concat([raw_dataframe, raw_dataframe])  # Duplicate rows
    preprocessor = DataPreprocessor()
    cleaned_df = preprocessor._clean_data(df)
    assert cleaned_df.shape[0] == raw_dataframe.shape[0], "Duplicates should be removed"


def test_normalize_features_scales_numeric(raw_dataframe):
    preprocessor = DataPreprocessor()
    normalized_df = preprocessor._normalize_features(raw_dataframe.copy())
    for col in ["bytes_sent", "bytes_received", "duration"]:
        assert normalized_df[col].min() >= 0
        assert normalized_df[col].max() <= 1


def test_handle_missing_values_fills_nulls(raw_dataframe):
    preprocessor = DataPreprocessor()
    filled_df = preprocessor._handle_missing_values(raw_dataframe.copy())

    # Check numeric NaNs filled with 0
    numeric_cols = ["bytes_sent", "bytes_received", "duration"]
    assert filled_df[numeric_cols].isnull().sum().sum() == 0

    # Check categorical NaNs filled with "UNKNOWN"
    categorical_cols = ["protocol", "action", "flags"]
    assert (filled_df[categorical_cols] == "UNKNOWN").any().any()


def test_parse_timestamps_handles_invalid(raw_dataframe):
    preprocessor = DataPreprocessor()
    parsed_df = preprocessor._parse_timestamps(raw_dataframe.copy())
    assert parsed_df["timestamp"].isnull().sum() == 0, "All timestamps should be filled"
    assert pd.api.types.is_datetime64_any_dtype(parsed_df["timestamp"]), (
        "Timestamps should be datetime"
    )


def test_full_preprocess_pipeline(raw_dataframe):
    preprocessor = DataPreprocessor()
    processed_df = preprocessor.preprocess(raw_dataframe.copy())

    # Final assertions
    assert processed_df.isnull().sum().sum() == 0, "No missing values should remain"
    assert pd.api.types.is_datetime64_any_dtype(processed_df["timestamp"])
    assert processed_df.shape[0] == raw_dataframe.shape[0], (
        "Row count should not change"
    )
