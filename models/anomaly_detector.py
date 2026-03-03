from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from utils.logger import logger


class AnomalyDetector:
    """
    Handles unsupervised anomaly detection using IsolationForest and OneClassSVM.
    """

    def __init__(self, data, features=None):
        self.data = data
        self.features = (
            features
            or data.select_dtypes(include=["float64", "int64"]).columns.tolist()
        )
        logger.info(f"Selected features for anomaly detection: {self.features}")
        self.scaler = StandardScaler()
        self.data_scaled = self._scale_data()

    def _scale_data(self):
        logger.info("Scaling data for anomaly detection...")
        return self.scaler.fit_transform(self.data[self.features])

    def train_isolation_forest(self, contamination=0.05):
        logger.info("Training IsolationForest...")
        model = IsolationForest(contamination=contamination, random_state=42)
        model.fit(self.data_scaled)
        self.data["anomaly_iforest"] = model.predict(self.data_scaled)
        self.data["anomaly_iforest"] = self.data["anomaly_iforest"].apply(
            lambda x: 1 if x == -1 else 0
        )
        logger.info("IsolationForest training complete.")
        return model

    def train_one_class_svm(self, nu=0.05, kernel="rbf", gamma="scale"):
        logger.info("Training OneClassSVM...")
        model = OneClassSVM(nu=nu, kernel=kernel, gamma=gamma)
        model.fit(self.data_scaled)
        self.data["anomaly_ocsvm"] = model.predict(self.data_scaled)
        self.data["anomaly_ocsvm"] = self.data["anomaly_ocsvm"].apply(
            lambda x: 1 if x == -1 else 0
        )
        logger.info("OneClassSVM training complete.")
        return model

    def get_anomalies(self, method="iforest"):
        """
        Retrieve rows flagged as anomalies by the selected method.
        """
        column = f"anomaly_{method}"
        if column not in self.data.columns:
            logger.warning(f"No anomalies found for method '{method}'.")
            return None
        anomalies = self.data[self.data[column] == 1]
        logger.info(f"Found {len(anomalies)} anomalies using {method}.")
        return anomalies
