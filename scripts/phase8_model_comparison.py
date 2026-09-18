import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

INPUT_FILE = "data/phase8_ml_dataset.csv"
RESULT_FILE = "results/phase8_model_comparison.csv"

# ---------------------------------------------------------
# 1. Load dataset
# ---------------------------------------------------------

df = pd.read_csv(INPUT_FILE)

X = df.drop(columns=["condition"])
y = df["condition"]

# ---------------------------------------------------------
# 2. Train/test split
# ---------------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# ---------------------------------------------------------
# 3. Define models
# ---------------------------------------------------------

models = {

    "Logistic Regression": Pipeline([
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(
            max_iter=2000,
            random_state=42
        ))
    ]),

    "Decision Tree": DecisionTreeClassifier(
        max_depth=5,
        random_state=42
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        random_state=42
    ),

    "Gradient Boosting": GradientBoostingClassifier(
        n_estimators=100,
        max_depth=3,
        learning_rate=0.05,
        random_state=42
    )
}

# ---------------------------------------------------------
# 4. Cross-validation setup
# ---------------------------------------------------------

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

results = []

print("=" * 70)
print("PHASE 8 — MULTI-MODEL COMPARISON")
print("=" * 70)

print(f"\nTotal samples: {len(df)}")
print(f"Training samples: {len(X_train)}")
print(f"Testing samples: {len(X_test)}")
print(f"Features: {X.shape[1]}")

# ---------------------------------------------------------
# 5. Train and evaluate models
# ---------------------------------------------------------

for name, model in models.items():

    print("\n" + "-" * 70)
    print(f"MODEL: {name}")
    print("-" * 70)

    # Cross-validation accuracy
    cv_scores = cross_val_score(
        model,
        X_train,
        y_train,
        cv=cv,
        scoring="accuracy"
    )

    # Train on training data
    model.fit(X_train, y_train)

    # Test prediction
    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)

    precision = precision_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0
    )

    recall = recall_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0
    )

    cv_mean = cv_scores.mean()
    cv_std = cv_scores.std()

    print(f"Cross-validation accuracy: {cv_mean:.4f} ± {cv_std:.4f}")
    print(f"Test accuracy:             {accuracy:.4f}")
    print(f"Weighted precision:        {precision:.4f}")
    print(f"Weighted recall:           {recall:.4f}")
    print(f"Weighted F1-score:         {f1:.4f}")

    results.append({
        "model": name,
        "cv_accuracy_mean": cv_mean,
        "cv_accuracy_std": cv_std,
        "test_accuracy": accuracy,
        "weighted_precision": precision,
        "weighted_recall": recall,
        "weighted_f1": f1
    })

# ---------------------------------------------------------
# 6. Save comparison results
# ---------------------------------------------------------

results_df = pd.DataFrame(results)

results_df = results_df.sort_values(
    by="weighted_f1",
    ascending=False
)

results_df.to_csv(
    RESULT_FILE,
    index=False
)

print("\n" + "=" * 70)
print("MODEL COMPARISON COMPLETE")
print("=" * 70)

print("\nFinal ranking:")
print(results_df.round(4).to_string(index=False))

print(f"\nSaved to: {RESULT_FILE}")
