import pytest
import pandas as pd
import numpy as np
from models.anomaly_detector import AnomalyDetector


@pytest.fixture
def anomaly_detection_data():
    """
    Create a dummy dataset with some obvious outliers for testing.
    """
    normal_data = pd.DataFrame(
        {
            "feature1": np.random.normal(0, 1, 100),
            "feature2": np.random.normal(0, 1, 100),
        }
    )
    outliers = pd.DataFrame({"feature1": [10, 15, -12], "feature2": [10, -15, 12]})
    return pd.concat([normal_data, outliers], ignore_index=True)


def test_scale_data(anomaly_detection_data):
    detector = AnomalyDetector(anomaly_detection_data)
    assert detector.data_scaled.shape == (103, 2)
    assert np.allclose(detector.data_scaled.mean(), 0, atol=1)  # Mean ~0 after scaling


def test_train_isolation_forest_adds_column(anomaly_detection_data):
    detector = AnomalyDetector(anomaly_detection_data)
    model = detector.train_isolation_forest(contamination=0.05)
    assert "anomaly_iforest" in detector.data.columns
    assert detector.data["anomaly_iforest"].isin([0, 1]).all()


def test_train_one_class_svm_adds_column(anomaly_detection_data):
    detector = AnomalyDetector(anomaly_detection_data)
    model = detector.train_one_class_svm(nu=0.05)
    assert "anomaly_ocsvm" in detector.data.columns
    assert detector.data["anomaly_ocsvm"].isin([0, 1]).all()


def test_get_anomalies_returns_dataframe(anomaly_detection_data):
    detector = AnomalyDetector(anomaly_detection_data)
    detector.train_isolation_forest(contamination=0.05)
    anomalies = detector.get_anomalies(method="iforest")
    assert anomalies is not None
    assert isinstance(anomalies, pd.DataFrame)
    assert "anomaly_iforest" in anomalies.columns
    assert anomalies["anomaly_iforest"].eq(1).all()
