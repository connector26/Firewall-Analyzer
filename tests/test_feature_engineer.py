import pytest
import pandas as pd
from processing.feature_engineer import FeatureEngineer


@pytest.fixture
def preprocessed_dataframe():
    """
    Return a sample DataFrame after preprocessing for feature engineering.
    """
    return pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                ["2025-07-21 10:15:00", "2025-07-22 23:45:00", "2025-07-23 08:30:00"]
            ),
            "source_ip": ["192.168.1.1", "192.168.1.2", "192.168.1.1"],
            "destination_ip": ["10.0.0.1", "10.0.0.2", "10.0.0.3"],
            "source_port": [443, 8080, 22],
            "destination_port": [80, 443, 53],
            "protocol": ["TCP", "UDP", "TCP"],
            "action": ["ALLOW", "DENY", "ALLOW"],
            "bytes_sent": [500, 1500, 2500],
            "bytes_received": [300, 700, 1200],
            "duration": [60, 120, 30],
        }
    )


def test_engineer_features_adds_temporal_features(preprocessed_dataframe):
    engineer = FeatureEngineer()
    df = engineer.engineer_features(preprocessed_dataframe.copy())
    assert "hour" in df.columns
    assert "day_of_week" in df.columns
    assert "is_weekend" in df.columns


def test_engineer_features_adds_network_behavior_features(preprocessed_dataframe):
    engineer = FeatureEngineer()
    df = engineer.engineer_features(preprocessed_dataframe.copy())
    assert "total_bytes" in df.columns
    assert "connection_count" in df.columns
    # Check values
    assert df.loc[0, "total_bytes"] == 800  # 500 + 300
    assert df["connection_count"].max() >= 1


def test_engineer_features_encodes_categorical_features(preprocessed_dataframe):
    engineer = FeatureEngineer()
    df = engineer.engineer_features(preprocessed_dataframe.copy())
    # Check one-hot columns for protocol and action
    protocol_columns = [col for col in df.columns if col.startswith("protocol_")]
    action_columns = [col for col in df.columns if col.startswith("action_")]
    assert len(protocol_columns) > 0
    assert len(action_columns) > 0


def test_engineer_features_pipeline_output_shape(preprocessed_dataframe):
    engineer = FeatureEngineer()
    df = engineer.engineer_features(preprocessed_dataframe.copy())
    assert df.shape[0] == preprocessed_dataframe.shape[0]  # No rows lost
