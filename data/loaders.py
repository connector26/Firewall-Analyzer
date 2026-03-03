import pandas as pd
import os
from abc import ABC, abstractmethod
from typing import Dict, Any
from utils.logger import logger

import kagglehub  # New import


class DataLoader(ABC):
    @abstractmethod
    def load_data(self, source: str) -> pd.DataFrame:
        pass

    @abstractmethod
    def validate_schema(self, data: pd.DataFrame) -> bool:
        pass

    @abstractmethod
    def get_data_info(self) -> Dict[str, Any]:
        pass


class CSVDataLoader(DataLoader):
    def load_data(self, source: str) -> pd.DataFrame:
        logger.info(f"Loading data from CSV file: {source}")
        return pd.read_csv(source)

    def validate_schema(self, data: pd.DataFrame) -> bool:
        expected_columns = [
            "timestamp",
            "source_ip",
            "destination_ip",
            "source_port",
            "destination_port",
            "protocol",
            "action",
            "bytes_sent",
            "bytes_received",
            "duration",
            "flags",
        ]
        return all(col in data.columns for col in expected_columns)

    def get_data_info(self) -> Dict[str, Any]:
        return {"supported_formats": ["csv"]}


class KaggleDataLoader(DataLoader):
    def __init__(self, dataset: str = "tunguz/internet-firewall-data-set"):
        self.dataset = dataset
        logger.info(f"Initializing KaggleDataLoader for dataset: {self.dataset}")

    def load_data(self, source: str = None) -> pd.DataFrame:
        """
        Download dataset using kagglehub and load first CSV file.
        """
        logger.info(f"Downloading dataset {self.dataset} via kagglehub...")
        path = kagglehub.dataset_download(self.dataset)
        logger.info(f"Dataset downloaded to: {path}")

        # Find first CSV file
        csv_files = [
            os.path.join(path, f) for f in os.listdir(path) if f.endswith(".csv")
        ]
        if not csv_files:
            raise FileNotFoundError("No CSV file found in dataset directory.")
        logger.info(f"Loading CSV data from: {csv_files[0]}")
        return pd.read_csv(csv_files[0])

    def validate_schema(self, data: pd.DataFrame) -> bool:
        expected_columns = [
            "timestamp",
            "source_ip",
            "destination_ip",
            "source_port",
            "destination_port",
            "protocol",
            "action",
            "bytes_sent",
            "bytes_received",
            "duration",
            "flags",
        ]
        valid = all(col in data.columns for col in expected_columns)
        if not valid:
            logger.warning("Schema validation failed: Missing expected columns.")
        return valid

    def get_data_info(self) -> Dict[str, Any]:
        return {"dataset": self.dataset}
