import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

INPUT_FILE = "data/phase8_ml_dataset.csv"
OUTPUT_FILE = "results/phase8_feature_importance.csv"

df = pd.read_csv(INPUT_FILE)

X = df.drop(columns=["condition"])
y = df["condition"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=8,
    random_state=42
)

model.fit(X_train, y_train)

importance = pd.DataFrame({
    "feature": X.columns,
    "importance": model.feature_importances_
})

importance = importance.sort_values(
    by="importance",
    ascending=False
).reset_index(drop=True)

importance.to_csv(
    OUTPUT_FILE,
    index=False
)

print("=" * 70)
print("PHASE 8 — FEATURE IMPORTANCE")
print("=" * 70)

print("\nFeature ranking:")
print(importance.round(4).to_string(index=False))

print(f"\nSaved to: {OUTPUT_FILE}")
