import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from utils.logger import logger
import random
import numpy as np


class DataPreprocessor:
    """
    Handles column mapping, cleaning, and placeholder filling.
    """

    COLUMN_MAP = {
        "Source Port": "source_port",
        "Destination Port": "destination_port",
        "Action": "action",
        "Bytes Sent": "bytes_sent",
        "Bytes Received": "bytes_received",
        "Elapsed Time (sec)": "duration",
    }

    MISSING_COLUMNS_DEFAULTS = {
        "timestamp": pd.Timestamp.now(),
        "source_ip": "0.0.0.0",
        "destination_ip": "0.0.0.0",
        "protocol": "TCP",
        "flags": "NONE",
    }

    def preprocess(self, data: pd.DataFrame) -> pd.DataFrame:
        logger.info("Starting preprocessing: mapping columns and filling missing data.")

        # Rename columns
        data = data.rename(columns=self.COLUMN_MAP)

        # Add missing expected columns
        for col, default in self.MISSING_COLUMNS_DEFAULTS.items():
            if col not in data.columns:
                logger.warning(
                    f"Column '{col}' missing. Filling with default: {default}"
                )
                data[col] = default

        # Clean invalid ports
        data = self._fix_invalid_ports(data)
        data = self._clean_data(data)
        data = self._normalize_features(data)
        data = self._handle_missing_values(data)
        data = self._parse_timestamps(data)

        logger.info("Preprocessing complete.")
        return data

    def _fix_invalid_ports(self, data: pd.DataFrame) -> pd.DataFrame:
        for col in ["source_port", "destination_port"]:
            if col in data.columns:
                invalid_ports = (data[col] < 1) | (data[col] > 65535)
                count = invalid_ports.sum()
                if count > 0:
                    logger.warning(
                        f"Found {count} invalid values in '{col}'. Replacing with random valid ports."
                    )
                    data.loc[invalid_ports, col] = [
                        random.randint(1024, 65535) for _ in range(count)
                    ]
        return data

    def _clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        logger.info("Cleaning data: removing duplicates and irrelevant rows.")
        initial_shape = data.shape
        data = data.drop_duplicates()
        logger.debug(f"Removed {initial_shape[0] - data.shape[0]} duplicate rows.")
        return data

    def _normalize_features(self, data: pd.DataFrame) -> pd.DataFrame:
        logger.info("Normalizing numeric features using MinMaxScaler.")
        numeric_cols = ["bytes_sent", "bytes_received", "duration"]
        scaler = MinMaxScaler()

        for col in numeric_cols:
            if col in data.columns:
                logger.debug(f"Normalizing column: {col}")
                data[col] = scaler.fit_transform(data[[col]])

        return data

    def _handle_missing_values(self, data: pd.DataFrame) -> pd.DataFrame:
        logger.info("Handling missing values.")
        # Fill numeric NaNs with 0
        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        data[numeric_cols] = data[numeric_cols].fillna(0)

        # Fill categorical NaNs with "UNKNOWN"
        categorical_cols = data.select_dtypes(include=["object"]).columns.tolist()
        data[categorical_cols] = data[categorical_cols].fillna("UNKNOWN")

        return data

    def _parse_timestamps(self, data: pd.DataFrame) -> pd.DataFrame:
        logger.info("Parsing timestamp column and handling timezone.")
        if "timestamp" in data.columns:
            data["timestamp"] = pd.to_datetime(data["timestamp"], errors="coerce")
            # Fill NaT with current timestamp
            data["timestamp"] = data["timestamp"].fillna(pd.Timestamp.now())
        return data
