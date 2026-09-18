import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, confusion_matrix

INPUT_FILE = "data/phase8_ml_dataset.csv"

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

labels = [
    "Excellent",
    "Good",
    "Moderate",
    "Poor",
    "Very Poor"
]

print("=" * 70)
print("PHASE 8 — MODEL DIAGNOSTICS")
print("=" * 70)

for name, model in models.items():

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print("\n" + "=" * 70)
    print(name)
    print("=" * 70)

    print("\nConfusion Matrix:")
    matrix = confusion_matrix(
        y_test,
        y_pred,
        labels=labels
    )

    print(pd.DataFrame(
        matrix,
        index=[f"Actual {x}" for x in labels],
        columns=[f"Predicted {x}" for x in labels]
    ).to_string())

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            y_pred,
            labels=labels,
            zero_division=0
        )
    )

print("\n" + "=" * 70)
print("DIAGNOSTICS COMPLETE")
print("=" * 70)
