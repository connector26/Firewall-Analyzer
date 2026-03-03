import pytest
import pandas as pd
from analysis.eda_engine import EDAEngine
import matplotlib.pyplot as plt


@pytest.fixture
def feature_engineered_dataframe():
    """
    Return a sample DataFrame similar to post-feature-engineering output.
    """
    return pd.DataFrame(
        {
            "timestamp": pd.date_range(
                start="2025-07-21 00:00:00", periods=6, freq="h"
            ),
            "total_bytes": [100, 200, 5000, 300, 400, 6000],
            "protocol_tcp": [1, 0, 1, 0, 1, 1],
            "protocol_udp": [0, 1, 0, 1, 0, 0],
            "action_allow": [1, 0, 1, 1, 0, 1],
            "action_deny": [0, 1, 0, 0, 1, 0],
        }
    )


def test_describe_data_returns_dataframe(feature_engineered_dataframe):
    eda = EDAEngine(feature_engineered_dataframe)
    description = eda.describe_data()
    assert isinstance(description, pd.DataFrame)
    assert "total_bytes" in description.columns


def test_identify_anomalies_returns_correct_rows(feature_engineered_dataframe):
    eda = EDAEngine(feature_engineered_dataframe)
    threshold = 0.8
    anomalies = eda.identify_anomalies(threshold=threshold)
    expected_count = (
        feature_engineered_dataframe["total_bytes"]
        > feature_engineered_dataframe["total_bytes"].quantile(threshold)
    ).sum()
    assert anomalies.shape[0] == expected_count


def test_plot_protocol_distribution(monkeypatch, feature_engineered_dataframe):
    eda = EDAEngine(feature_engineered_dataframe)

    # Prevent plt.show() from opening a window
    monkeypatch.setattr(plt, "show", lambda: None)

    # Should not raise errors
    eda.plot_protocol_distribution()


def test_plot_action_distribution(monkeypatch, feature_engineered_dataframe):
    eda = EDAEngine(feature_engineered_dataframe)
    monkeypatch.setattr(plt, "show", lambda: None)
    eda.plot_action_distribution()


def test_plot_traffic_over_time(monkeypatch, feature_engineered_dataframe):
    eda = EDAEngine(feature_engineered_dataframe)
    monkeypatch.setattr(plt, "show", lambda: None)
    eda.plot_traffic_over_time(time_unit="H")
