
import os
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

DATA_PATH = "data/phase7_network_dataset.csv"
MODEL_PATH = "models/network_condition_model_v2.pkl"

FEATURES = [
    "measured_packet_loss_percent",
    "min_latency_ms",
    "avg_latency_ms",
    "max_latency_ms",
    "measured_jitter_ms"
]

LABEL_MAPPING = {
    "Excellent": "high",
    "Good": "high",
    "Moderate": "medium",
    "Poor": "low",
    "Very Poor": "low"
}


def main():
    df = pd.read_csv(DATA_PATH)

    required_columns = FEATURES + ["condition"]
    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = df[required_columns].dropna().copy()
    df["streaming_quality"] = df["condition"].map(LABEL_MAPPING)
    df = df.dropna(subset=["streaming_quality"])

    X = df[FEATURES]
    y = df["streaming_quality"]

    print("Samples:", len(df))
    print("\nClass distribution:")
    print(y.value_counts())

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=200,
        class_weight="balanced",
        random_state=42
    )

    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    print("\nTest accuracy:",
          round(accuracy_score(y_test, predictions) * 100, 2), "%")

    print("\nClassification report:")
    print(classification_report(
        y_test,
        predictions,
        labels=["high", "medium", "low"],
        zero_division=0
    ))

    print("Confusion matrix (labels: high, medium, low):")
    print(confusion_matrix(
        y_test,
        predictions,
        labels=["high", "medium", "low"]
    ))

    os.makedirs("models", exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print("\nNew model saved to:", MODEL_PATH)
    print("The existing model has not been changed.")


if __name__ == "__main__":
    main()
