from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from utils.logger import logger


class ModelBuilder:
    """
    Handles training and evaluation of ML models for classification.
    """

    def __init__(self, data, target_column="action_allow"):
        self.data = data
        self.target_column = target_column
        self.models = {
            "RandomForest": RandomForestClassifier(),
            "LogisticRegression": LogisticRegression(max_iter=500),
            "SVC": SVC(),
        }
        self.X_train, self.X_test, self.y_train, self.y_test = self._split_data()

    def _split_data(self):
        logger.info("Splitting data into train and test sets...")
        X = self.data.drop(columns=[self.target_column])
        y = self.data[self.target_column]

        # Drop non-numeric columns (timestamps, IPs, strings) that sklearn can't handle
        non_numeric_cols = X.select_dtypes(exclude=["number", "bool"]).columns.tolist()
        if non_numeric_cols:
            logger.warning(f"Dropping non-numeric columns from features: {non_numeric_cols}")
            X = X.drop(columns=non_numeric_cols)

        # Drop anomaly flag columns if present (injected by AnomalyDetector)
        anomaly_cols = [c for c in X.columns if c.startswith("anomaly_")]
        if anomaly_cols:
            X = X.drop(columns=anomaly_cols)

        logger.info(f"Feature columns used for training ({len(X.columns)}): {X.columns.tolist()}")
        return train_test_split(X, y, test_size=0.2, random_state=42)

    def train_model(self, model_name="RandomForest"):
        logger.info(f"Training {model_name} model...")
        model = self.models.get(model_name)
        if model is None:
            logger.error(f"Model '{model_name}' not found.")
            return None
        model.fit(self.X_train, self.y_train)
        logger.info(f"{model_name} training complete.")
        return model

    def evaluate_model(self, model):
        logger.info("Evaluating model performance...")
        y_pred = model.predict(self.X_test)
        acc = accuracy_score(self.y_test, y_pred)
        logger.info(f"Accuracy: {acc:.4f}")
        logger.info(
            "Classification Report:\n" + classification_report(self.y_test, y_pred, zero_division=0)
        )
        logger.info("Confusion Matrix:\n" + str(confusion_matrix(self.y_test, y_pred)))
        return acc

    def tune_hyperparameters(self, model_name="RandomForest", param_grid=None):
        logger.info(f"Tuning hyperparameters for {model_name}...")
        model = self.models.get(model_name)
        if model is None:
            logger.error(f"Model '{model_name}' not found for tuning.")
            return None
        grid_search = GridSearchCV(model, param_grid, cv=3, scoring="accuracy")
        grid_search.fit(self.X_train, self.y_train)
        logger.info(f"Best parameters: {grid_search.best_params_}")
        logger.info(f"Best score: {grid_search.best_score_:.4f}")
        return grid_search.best_estimator_
