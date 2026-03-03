import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from utils.logger import logger


class EDAEngine:
    """
    Provides exploratory data analysis (EDA) functionality.
    """

    def __init__(self, data: pd.DataFrame):
        self.data = data
        sns.set(style="whitegrid")

    def describe_data(self):
        logger.info("Generating descriptive statistics...")
        description = self.data.describe(include="all")
        logger.debug(f"Descriptive statistics:\n{description}")
        return description

    def plot_protocol_distribution(self):
        logger.info("Plotting protocol distribution...")
        protocol_cols = [
            col for col in self.data.columns if col.startswith("protocol_")
        ]
        if protocol_cols:
            protocol_counts = self.data[protocol_cols].sum()
            protocol_counts.plot(
                kind="bar", title="Protocol Distribution", figsize=(8, 6)
            )
            plt.ylabel("Count")
            plt.show()
        else:
            logger.warning("No protocol columns found for plotting.")

    def plot_action_distribution(self):
        logger.info("Plotting action distribution...")
        action_cols = [col for col in self.data.columns if col.startswith("action_")]
        if action_cols:
            action_counts = self.data[action_cols].sum()
            action_counts.plot(kind="bar", title="Action Distribution", figsize=(8, 6))
            plt.ylabel("Count")
            plt.show()
        else:
            logger.warning("No action columns found for plotting.")

    def plot_traffic_over_time(self, time_unit="h"):
        logger.info(f"Plotting network traffic over time (resampled by {time_unit})...")
        if "timestamp" not in self.data.columns:
            logger.error("Timestamp column missing. Cannot plot traffic over time.")
            return

        traffic = (
            self.data.set_index("timestamp")
            .resample(time_unit.lower())["total_bytes"]
            .sum()
        )

        traffic.plot(figsize=(12, 6), title="Network Traffic Over Time")
        plt.ylabel("Total Bytes")
        plt.xlabel("Time")
        plt.show()

    def identify_anomalies(self, threshold=0.95):
        logger.info(f"Identifying anomalies with threshold: {threshold}")
        total_bytes = self.data["total_bytes"]
        high_traffic_threshold = total_bytes.quantile(threshold)
        anomalies = self.data[total_bytes > high_traffic_threshold]
        logger.debug(f"Anomalies detected:\n{anomalies}")
        return anomalies
