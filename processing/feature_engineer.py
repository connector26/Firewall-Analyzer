import pandas as pd
from utils.logger import logger


class FeatureEngineer:
    """
    Generates features for machine learning models from firewall logs.
    """

    def engineer_features(self, data: pd.DataFrame) -> pd.DataFrame:
        logger.info("Starting feature engineering pipeline...")
        data = self._extract_temporal_features(data)
        data = self._compute_network_behavior_features(data)
        data = self._encode_categorical_features(data)
        logger.info("Feature engineering pipeline complete.")
        return data

    def _extract_temporal_features(self, data: pd.DataFrame) -> pd.DataFrame:
        logger.info("Extracting temporal features from timestamp...")
        if "timestamp" in data.columns:
            data["hour"] = data["timestamp"].dt.hour
            data["day_of_week"] = data["timestamp"].dt.dayofweek  # Monday=0
            data["is_weekend"] = data["day_of_week"].apply(lambda x: 1 if x >= 5 else 0)
        return data

    def _compute_network_behavior_features(self, data: pd.DataFrame) -> pd.DataFrame:
        logger.info("Computing network behavior features...")
        # Total bytes transferred
        data["total_bytes"] = data["bytes_sent"] + data["bytes_received"]

        # Connection frequency per source_ip
        if "source_ip" in data.columns:
            conn_freq = data.groupby("source_ip").size().rename("connection_count")
            data = data.merge(
                conn_freq, left_on="source_ip", right_index=True, how="left"
            )

        return data

    def _encode_categorical_features(self, data: pd.DataFrame) -> pd.DataFrame:
        logger.info("Encoding categorical features (protocol, action)...")
        categorical_cols = ["protocol", "action"]

        for col in categorical_cols:
            if col in data.columns:
                dummies = pd.get_dummies(data[col], prefix=col, drop_first=False)
                data = pd.concat([data, dummies], axis=1)
                data = data.drop(columns=[col])

        return data
