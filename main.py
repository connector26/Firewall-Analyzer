from analysis.eda_engine import EDAEngine
from data.loaders import CSVDataLoader
from data.validator import DataValidator
from models.anomaly_detector import AnomalyDetector
from models.model_builder import ModelBuilder
from processing.feature_engineer import FeatureEngineer
from processing.preprocessor import DataPreprocessor

if __name__ == "__main__":
    loader = CSVDataLoader()
    df = loader.load_data("./data/internet_firewall_data.csv")

    # Preprocessing
    preprocessor = DataPreprocessor()
    df = preprocessor.preprocess(df)

    # Feature Engineering
    engineer = FeatureEngineer()
    df = engineer.engineer_features(df)

    # Validation
    validator = DataValidator()
    if validator.validate_all(df):
        print("Data passed all validation checks.")
    else:
        print("Data failed validation.")

    # EDA
    eda = EDAEngine(df)
    print(eda.describe_data())
    eda.plot_protocol_distribution()
    eda.plot_action_distribution()
    eda.plot_traffic_over_time()
    anomalies = eda.identify_anomalies()
    print("Anomalies detected:")
    print(anomalies.head())

    # Machine Learning (supervised) - only if target column exists
    target_column = "action_allow"
    if target_column in df.columns:
        model_builder = ModelBuilder(df, target_column=target_column)
        model = model_builder.train_model("RandomForest")
        model_builder.evaluate_model(model)

        # Optional: Hyperparameter tuning
        param_grid = {"n_estimators": [50, 100, 200], "max_depth": [None, 10, 20]}
        best_model = model_builder.tune_hyperparameters("RandomForest", param_grid)
        model_builder.evaluate_model(best_model)
    else:
        print(f"Supervised model training skipped: target column '{target_column}' not found.")

    # Anomaly Detection
    detector = AnomalyDetector(df)
    iforest_model = detector.train_isolation_forest(contamination=0.05)
    ocsvm_model = detector.train_one_class_svm(nu=0.05)

    # Get anomalies
    anomalies_iforest = detector.get_anomalies(method="iforest")
    anomalies_ocsvm = detector.get_anomalies(method="ocsvm")

    print("IsolationForest anomalies (first 5 rows):")
    print(anomalies_iforest.head())

    print("OneClassSVM anomalies (first 5 rows):")
    print(anomalies_ocsvm.head())
