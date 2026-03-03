import pytest
import pandas as pd
from data.validator import DataValidator


@pytest.fixture
def valid_dataframe():
    return pd.DataFrame(
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


@pytest.fixture
def invalid_dataframe():
    return pd.DataFrame(
        {
            "timestamp": ["invalid-date"],
            "source_ip": ["999.999.999.999"],
            "destination_ip": ["bad_ip"],
            "source_port": [70000],
            "destination_port": [-1],
            "protocol": ["UNKNOWN"],
            "action": ["DENY"],
            "bytes_sent": [-500],
            "bytes_received": [-300],
            "duration": [-10],
            "flags": ["INVALID"],
        }
    )


def test_validate_schema_pass(valid_dataframe):
    validator = DataValidator()
    assert validator.validate_schema(valid_dataframe)


def test_validate_schema_fail(invalid_dataframe):
    validator = DataValidator()
    # Remove a required column to trigger failure
    df = invalid_dataframe.drop(columns=["bytes_sent"])
    assert not validator.validate_schema(df)


def test_validate_ip_addresses(valid_dataframe):
    validator = DataValidator()
    assert validator.validate_ip_addresses(valid_dataframe)


def test_validate_ports(valid_dataframe):
    validator = DataValidator()
    assert validator.validate_ports(valid_dataframe)


def test_validate_timestamps(valid_dataframe):
    validator = DataValidator()
    assert validator.validate_timestamps(valid_dataframe)


def test_validate_all(valid_dataframe):
    validator = DataValidator()
    assert validator.validate_all(valid_dataframe)
