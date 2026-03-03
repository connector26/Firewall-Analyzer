import pandas as pd
import ipaddress
from datetime import datetime
from utils.logger import logger


class DataValidator:
    """
    Validates firewall log data for schema integrity and data quality.
    """

    REQUIRED_COLUMNS = [
        "timestamp",
        "source_ip",
        "destination_ip",
        "source_port",
        "destination_port",
        # "protocol",
        # "action",
        "bytes_sent",
        "bytes_received",
        "duration",
        # "flags",
    ]

    def validate_schema(self, data: pd.DataFrame) -> bool:
        """
        Check if DataFrame has all required columns.
        Skips protocol and action if one-hot encoded.
        """
        logger.info("Validating data schema...")
        missing_columns = []

        normalized_columns = [c.strip().lower() for c in data.columns]

        for col in self.REQUIRED_COLUMNS:
            if col not in normalized_columns:
                missing_columns.append(col)

        # Protocol and Action special check
        for optional_col in ["protocol", "action"]:
            one_hot_exists = any(f"{optional_col}_" in c for c in normalized_columns)
            if not one_hot_exists and optional_col not in normalized_columns:
                logger.warning(
                    f"Optional column '{optional_col}' is missing and no one-hot columns found."
                )

        if missing_columns:
            logger.error(
                f"Schema validation failed. Missing columns: {missing_columns}"
            )
            return False

        logger.info("Schema validation passed.")
        return True

    def validate_ip_addresses(self, data: pd.DataFrame) -> bool:
        """
        Validate source_ip and destination_ip fields for proper IPv4/IPv6 addresses.
        """
        logger.info("Validating IP address formats...")
        for col in ["source_ip", "destination_ip"]:
            if not self._validate_ip_column(data[col]):
                logger.error(f"Invalid IP address found in column: {col}")
                return False
        logger.info("IP address validation passed.")
        return True

    def validate_ports(self, data: pd.DataFrame) -> bool:
        """
        Check source_port and destination_port are valid port numbers (1-65535).
        """
        logger.info("Validating port numbers...")
        for col in ["source_port", "destination_port"]:
            invalid_ports = data[~data[col].between(1, 65535)]
            if not invalid_ports.empty:
                logger.error(
                    f"Invalid port numbers found in column {col}: {invalid_ports[col].unique().tolist()}"
                )
                return False
        logger.info("Port validation passed.")
        return True

    def validate_timestamps(self, data: pd.DataFrame) -> bool:
        """
        Validate timestamp field for correct datetime format.
        """
        logger.info("Validating timestamps...")
        try:
            pd.to_datetime(data["timestamp"], errors="raise")
            logger.info("Timestamp validation passed.")
            return True
        except Exception as e:
            logger.error(f"Invalid timestamp format: {e}")
            return False

    def validate_all(self, data: pd.DataFrame) -> bool:
        """
        Run all validation checks.
        """
        logger.info("Starting comprehensive data validation...")
        schema_ok = self.validate_schema(data)
        ip_ok = self.validate_ip_addresses(data)
        port_ok = self.validate_ports(data)
        ts_ok = self.validate_timestamps(data)

        all_ok = schema_ok and ip_ok and port_ok and ts_ok
        if all_ok:
            logger.info("All data validation checks passed.")
        else:
            logger.error("Data validation failed.")
        return all_ok

    def _validate_ip_column(self, series: pd.Series) -> bool:
        """
        Helper: Validate if all entries in a column are valid IP addresses.
        """
        for ip in series.dropna().unique():
            try:
                ipaddress.ip_address(ip)
            except ValueError:
                logger.debug(f"Invalid IP detected: {ip}")
                return False
        return True
