import pandas as pd

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ============================================================
# PHASE 9 - FUTURE LATENCY MODEL COMPARISON
# ============================================================

INPUT_FILE = "data/phase8_future_prediction_features.csv"
OUTPUT_FILE = "results/phase9_model_comparison.csv"


# ------------------------------------------------------------
# 1. Load dataset
# ------------------------------------------------------------

df = pd.read_csv(INPUT_FILE)


# ------------------------------------------------------------
# 2. Features selected from Phase 8
# ------------------------------------------------------------
# Phase 8 showed that Current + Previous features performed
# better than Current-only and Current + Previous + Rolling.

feature_columns = [
    "packet_loss_percent",
    "min_latency_ms",
    "avg_latency_ms",
    "max_latency_ms",
    "jitter_ms",
    "latency_range_ms",
    "previous_latency_ms",
    "previous_jitter_ms",
    "previous_packet_loss_percent"
]

target_column = "future_latency_ms"


X = df[feature_columns]
y = df[target_column]


# ------------------------------------------------------------
# 3. Time-ordered train/test split
# ------------------------------------------------------------
# IMPORTANT:
# We do NOT shuffle the data because we are predicting the future.

split_index = int(len(df) * 0.8)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]


# ------------------------------------------------------------
# 4. Evaluation function
# ------------------------------------------------------------

def evaluate_model(name, predictions):

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = mean_squared_error(
        y_test,
        predictions
    ) ** 0.5

    r2 = r2_score(
        y_test,
        predictions
    )

    return {
        "model": name,
        "mae_ms": mae,
        "rmse_ms": rmse,
        "r2": r2
    }


# ------------------------------------------------------------
# 5. Results list
# ------------------------------------------------------------

results = []


# ------------------------------------------------------------
# 6. Persistence baseline
# ------------------------------------------------------------
# Simple idea:
# Assume the next latency will be equal to the current latency.

persistence_predictions = X_test["avg_latency_ms"].values

results.append(
    evaluate_model(
        "Persistence Baseline",
        persistence_predictions
    )
)


# ------------------------------------------------------------
# 7. Linear Regression
# ------------------------------------------------------------

linear_model = LinearRegression()

linear_model.fit(
    X_train,
    y_train
)

linear_predictions = linear_model.predict(
    X_test
)

results.append(
    evaluate_model(
        "Linear Regression",
        linear_predictions
    )
)


# ------------------------------------------------------------
# 8. Random Forest
# ------------------------------------------------------------

rf_model = RandomForestRegressor(
    n_estimators=200,
    random_state=42
)

rf_model.fit(
    X_train,
    y_train
)

rf_predictions = rf_model.predict(
    X_test
)

results.append(
    evaluate_model(
        "Random Forest",
        rf_predictions
    )
)


# ------------------------------------------------------------
# 9. Gradient Boosting
# ------------------------------------------------------------

gb_model = GradientBoostingRegressor(
    n_estimators=100,
    learning_rate=0.05,
    max_depth=2,
    random_state=42
)

gb_model.fit(
    X_train,
    y_train
)

gb_predictions = gb_model.predict(
    X_test
)

results.append(
    evaluate_model(
        "Gradient Boosting",
        gb_predictions
    )
)


# ------------------------------------------------------------
# 10. Create results DataFrame
# ------------------------------------------------------------

results_df = pd.DataFrame(results)


# Round values for easier reading
results_df["mae_ms"] = results_df["mae_ms"].round(3)
results_df["rmse_ms"] = results_df["rmse_ms"].round(3)
results_df["r2"] = results_df["r2"].round(3)


# ------------------------------------------------------------
# 11. Save results
# ------------------------------------------------------------

results_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ------------------------------------------------------------
# 12. Display experiment information
# ------------------------------------------------------------

print("=" * 65)
print("PHASE 9 - FUTURE LATENCY MODEL COMPARISON")
print("=" * 65)

print("Dataset:", INPUT_FILE)
print("Total samples:", len(df))
print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))
print("Features used:", len(feature_columns))

print("\nFeature set:")
for feature in feature_columns:
    print(" -", feature)


# ------------------------------------------------------------
# 13. Display results
# ------------------------------------------------------------

print("\nModel Results")
print("-" * 65)

print(
    results_df.to_string(
        index=False
    )
)


# ------------------------------------------------------------
# 14. Show actual vs predicted values
# ------------------------------------------------------------

print("\nActual vs Predicted - First 10 Test Samples")
print("-" * 65)

comparison = pd.DataFrame({
    "Actual": y_test.iloc[:10].values,
    "Persistence": persistence_predictions[:10],
    "Linear": linear_predictions[:10],
    "Random_Forest": rf_predictions[:10],
    "Gradient_Boosting": gb_predictions[:10]
})

print(
    comparison.round(2).to_string(
        index=False
    )
)


print("\nResults saved to:")
print(OUTPUT_FILE)

print("\n" + "=" * 65)
print("PHASE 9 EXPERIMENT COMPLETE")
print("=" * 65)
