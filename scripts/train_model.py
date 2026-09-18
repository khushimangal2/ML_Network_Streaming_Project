import os
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib


# -----------------------------
# Load prepared dataset
# -----------------------------
data_path = "data/prepared_network_data.csv"

df = pd.read_csv(data_path)

print("\nDataset loaded successfully!")
print(df.head())


# -----------------------------
# Define input features
# -----------------------------
features = [
    "packet_loss_percent",
    "min_latency_ms",
    "avg_latency_ms",
    "max_latency_ms",
    "jitter_ms"
]

X = df[features]


# -----------------------------
# Define target variable
# -----------------------------
y = df["network_condition"]


# -----------------------------
# Split dataset
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y
)

print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# -----------------------------
# Create Random Forest model
# -----------------------------
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)


# -----------------------------
# Train model
# -----------------------------
model.fit(X_train, y_train)

print("\nModel training completed successfully!")


# -----------------------------
# Make predictions
# -----------------------------
predictions = model.predict(X_test)


# -----------------------------
# Evaluate model
# -----------------------------
accuracy = accuracy_score(y_test, predictions)

print("\nModel Accuracy:", round(accuracy * 100, 2), "%")

print("\nClassification Report:")
print(classification_report(y_test, predictions))


# -----------------------------
# Display actual vs predicted
# -----------------------------
results = pd.DataFrame({
    "Actual": y_test.values,
    "Predicted": predictions
})

print("\nPrediction Results:")
print(results)


# -----------------------------
# Create models directory
# -----------------------------
os.makedirs("models", exist_ok=True)


# -----------------------------
# Save trained model
# -----------------------------
model_path = "models/network_condition_model.pkl"

joblib.dump(model, model_path)

print("\nTrained model saved successfully!")
print("Saved to:", model_path)
