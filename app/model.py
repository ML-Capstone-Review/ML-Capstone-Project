"""Rebuild the notebook-selected classifier with its original data workflow."""
from pathlib import Path
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             precision_score, recall_score, roc_auc_score, roc_curve)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from .schema import CATEGORICAL_COLUMNS, ID_COLUMN, NUMERIC_COLUMNS, TARGET, ENGINEERED_COLUMN

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "airline_passenger_satisfaction.csv"
CLASS_NAMES = ["Neutral or Dissatisfied", "Satisfied"]


def load_and_prepare_data():
    """Apply notebook cells B1–B3, retaining their split and learned bounds."""
    data = pd.read_csv(DATA_PATH).drop_duplicates().drop(columns=[ID_COLUMN])
    data["Arrival Delay"] = data["Arrival Delay"].fillna(data["Arrival Delay"].median())
    X = data.drop(columns=[TARGET])
    y = data[TARGET].map({"Neutral or Dissatisfied": 0, "Satisfied": 1})
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    numeric = X_train.select_dtypes(include=["int64", "float64"]).columns.tolist()
    categorical = X_train.select_dtypes(include=["str"]).columns.tolist()
    bounds = {}
    for col in numeric:
        q1, q3 = X_train[col].quantile([0.25, 0.75])
        iqr = q3 - q1
        bounds[col] = (q1 - 1.5 * iqr, q3 + 1.5 * iqr)
    for col, (low, high) in bounds.items():
        X_train[col] = X_train[col].clip(lower=low, upper=high)
        X_test[col] = X_test[col].clip(lower=low, upper=high)
    X_train[ENGINEERED_COLUMN] = X_train["Departure Delay"] + X_train["Arrival Delay"]
    X_test[ENGINEERED_COLUMN] = X_test["Departure Delay"] + X_test["Arrival Delay"]
    numeric.append(ENGINEERED_COLUMN)
    preprocessor = ColumnTransformer(transformers=[
        ("numerical", StandardScaler(), numeric),
        ("categorical", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical),
    ])
    return data, X_train, X_test, y_train, y_test, bounds, numeric, categorical, preprocessor


def train_notebook_model():
    """Fit only the notebook-selected estimator; do not run notebook searches."""
    data, X_train, X_test, y_train, y_test, bounds, numeric, categorical, preprocessor = load_and_prepare_data()
    model = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(
            n_estimators=200, min_samples_split=5, max_depth=None,
            random_state=42, n_jobs=1
        )),
    ])
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]
    false_positive_rate, true_positive_rate, _ = roc_curve(y_test, probabilities)
    metrics = {
        "Accuracy": accuracy_score(y_test, predictions),
        "Precision (weighted)": precision_score(y_test, predictions, average="weighted", zero_division=0),
        "Recall (weighted)": recall_score(y_test, predictions, average="weighted", zero_division=0),
        "Weighted F1-score": f1_score(y_test, predictions, average="weighted", zero_division=0),
        "ROC-AUC": roc_auc_score(y_test, probabilities),
    }
    artifacts = {
        "confusion_matrix": confusion_matrix(y_test, predictions),
        "roc_curve": (false_positive_rate, true_positive_rate),
        "feature_importance": pd.DataFrame({
            "Feature": model.named_steps["preprocessor"].get_feature_names_out(),
            "Importance": model.named_steps["classifier"].feature_importances_,
        }).sort_values("Importance", ascending=False).head(15),
        "test_rows": len(y_test),
        "train_rows": len(y_train),
        "metrics": metrics,
    }
    return model, data, bounds, numeric, categorical, artifacts


def build_input_frame(values, bounds, numeric, categorical):
    """Apply training-set clipping and notebook Total Delay engineering."""
    frame = pd.DataFrame([{key: values[key] for key in numeric if key != ENGINEERED_COLUMN} |
                          {key: values[key] for key in categorical}])
    for col, (low, high) in bounds.items():
        frame[col] = frame[col].clip(lower=low, upper=high)
    frame[ENGINEERED_COLUMN] = frame["Departure Delay"] + frame["Arrival Delay"]
    return frame[numeric + categorical]
