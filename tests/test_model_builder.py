import pytest
import pandas as pd
from models.model_builder import ModelBuilder
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC


@pytest.fixture
def sample_classification_data():
    """
    Return a small DataFrame for classification testing.
    """
    return pd.DataFrame(
        {
            "feature1": [0.1, 0.2, 0.8, 0.9, 0.4, 0.5, 0.6, 0.7],
            "feature2": [1, 0, 1, 0, 1, 0, 1, 0],
            "action_allow": [1, 0, 1, 0, 1, 0, 1, 0],  # Binary target
        }
    )


def test_split_data_returns_train_test_sets(sample_classification_data):
    builder = ModelBuilder(sample_classification_data, target_column="action_allow")
    assert builder.X_train.shape[0] > 0
    assert builder.X_test.shape[0] > 0
    assert builder.y_train.shape[0] > 0
    assert builder.y_test.shape[0] > 0


def test_train_model_returns_trained_model(sample_classification_data):
    builder = ModelBuilder(sample_classification_data, target_column="action_allow")
    model = builder.train_model("RandomForest")
    assert isinstance(model, RandomForestClassifier)


def test_train_invalid_model_returns_none(sample_classification_data):
    builder = ModelBuilder(sample_classification_data, target_column="action_allow")
    model = builder.train_model("NonExistentModel")
    assert model is None


def test_evaluate_model_returns_accuracy(sample_classification_data):
    builder = ModelBuilder(sample_classification_data, target_column="action_allow")
    model = builder.train_model("LogisticRegression")
    accuracy = builder.evaluate_model(model)
    assert 0.0 <= accuracy <= 1.0


def test_tune_hyperparameters_returns_best_estimator(sample_classification_data):
    builder = ModelBuilder(sample_classification_data, target_column="action_allow")
    param_grid = {"n_estimators": [10, 20]}
    best_model = builder.tune_hyperparameters("RandomForest", param_grid)
    assert isinstance(best_model, RandomForestClassifier)
