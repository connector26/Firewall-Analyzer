import pytest
import pandas as pd
from data.loaders import CSVDataLoader, KaggleDataLoader

# Sample test data
TEST_CSV_PATH = "./data/test_sample.csv"


@pytest.fixture
def sample_csv(tmp_path):
    """
    Create a sample CSV file for testing.
    """
    df = pd.DataFrame(
        {
            "timestamp": ["2025-07-21 10:00:00"],
            "source_ip": ["192.168.1.1"],
            "destination_ip": ["10.0.0.1"],
            "source_port": [443],
            "destination_port": [80],
            "protocol": ["TCP"],
            "action": ["ALLOW"],
            "bytes_sent": [1000],
            "bytes_received": [500],
            "duration": [60],
            "flags": ["SYN"],
        }
    )
    test_file = tmp_path / "test_sample.csv"
    df.to_csv(test_file, index=False)
    return str(test_file)


def test_csv_loader_load_data(sample_csv):
    loader = CSVDataLoader()
    df = loader.load_data(sample_csv)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "source_ip" in df.columns


def test_csv_loader_validate_schema(sample_csv):
    loader = CSVDataLoader()
    df = loader.load_data(sample_csv)
    assert loader.validate_schema(df)


def test_csv_loader_get_data_info():
    loader = CSVDataLoader()
    info = loader.get_data_info()
    assert isinstance(info, dict)
    assert "supported_formats" in info


def test_kaggle_loader_get_data_info():
    loader = KaggleDataLoader()
    info = loader.get_data_info()
    assert isinstance(info, dict)
    assert "dataset" in info
