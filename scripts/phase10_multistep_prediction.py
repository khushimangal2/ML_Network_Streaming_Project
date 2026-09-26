import pandas as pd

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ============================================================
# PHASE 10 - MULTI-STEP FUTURE LATENCY PREDICTION
# ============================================================

INPUT_FILE = "data/phase10_multistep_targets.csv"
OUTPUT_FILE = "results/phase10_multistep_model_comparison.csv"


# ------------------------------------------------------------
# 1. Load dataset
# ------------------------------------------------------------

df = pd.read_csv(INPUT_FILE)


# ------------------------------------------------------------
# 2. Input features
# ------------------------------------------------------------
# These are the current network measurements.
#
# We deliberately do NOT use future columns as input features.
# Otherwise, information from the future would leak into the model.

feature_columns = [
    "packet_loss_percent",
    "min_latency_ms",
    "avg_latency_ms",
    "max_latency_ms",
    "jitter_ms",
    "latency_range_ms"
]

X = df[feature_columns]


# ------------------------------------------------------------
# 3. Time-ordered train/test split
# ------------------------------------------------------------
# 80% oldest observations -> training
# 20% newest observations -> testing
#
# No random shuffling.

split_index = int(len(df) * 0.8)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]


print("=" * 70)
print("PHASE 10 - MULTI-STEP FUTURE LATENCY PREDICTION")
print("=" * 70)

print("Dataset:", INPUT_FILE)
print("Total samples:", len(df))
print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))
print("Features:", len(feature_columns))

print("\nFeature set:")
for feature in feature_columns:
    print(" -", feature)


# ------------------------------------------------------------
# 4. Evaluation function
# ------------------------------------------------------------

def evaluate_model(
    horizon,
    model_name,
    y_test,
    predictions
):

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
        "horizon": horizon,
        "model": model_name,
        "mae_ms": mae,
        "rmse_ms": rmse,
        "r2": r2
    }


# ------------------------------------------------------------
# 5. Store results
# ------------------------------------------------------------

results = []


# ------------------------------------------------------------
# 6. Train models for each future horizon
# ------------------------------------------------------------

for horizon in range(1, 5):

    target_column = f"future_latency_{horizon}"

    y = df[target_column]

    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]


    print("\n" + "=" * 70)
    print(f"FORECAST HORIZON +{horizon}")
    print("=" * 70)

    # --------------------------------------------------------
    # Persistence baseline
    # --------------------------------------------------------
    # Assumption:
    # future latency = current latency

    persistence_predictions = X_test["avg_latency_ms"].values

    persistence_result = evaluate_model(
        horizon,
        "Persistence Baseline",
        y_test,
        persistence_predictions
    )

    results.append(
        persistence_result
    )


    # --------------------------------------------------------
    # Linear Regression
    # --------------------------------------------------------

    linear_model = LinearRegression()

    linear_model.fit(
        X_train,
        y_train
    )

    linear_predictions = linear_model.predict(
        X_test
    )

    linear_result = evaluate_model(
        horizon,
        "Linear Regression",
        y_test,
        linear_predictions
    )

    results.append(
        linear_result
    )


    # --------------------------------------------------------
    # Random Forest
    # --------------------------------------------------------

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

    rf_result = evaluate_model(
        horizon,
        "Random Forest",
        y_test,
        rf_predictions
    )

    results.append(
        rf_result
    )


    # --------------------------------------------------------
    # Gradient Boosting
    # --------------------------------------------------------

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

    gb_result = evaluate_model(
        horizon,
        "Gradient Boosting",
        y_test,
        gb_predictions
    )

    results.append(
        gb_result
    )


# ------------------------------------------------------------
# 7. Create results DataFrame
# ------------------------------------------------------------

results_df = pd.DataFrame(
    results
)


# Round metrics

results_df["mae_ms"] = (
    results_df["mae_ms"].round(3)
)

results_df["rmse_ms"] = (
    results_df["rmse_ms"].round(3)
)

results_df["r2"] = (
    results_df["r2"].round(3)
)


# ------------------------------------------------------------
# 8. Save results
# ------------------------------------------------------------

results_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ------------------------------------------------------------
# 9. Display complete results
# ------------------------------------------------------------

print("\n\n")
print("=" * 70)
print("MULTI-STEP MODEL COMPARISON")
print("=" * 70)

print(
    results_df.to_string(
        index=False
    )
)


# ------------------------------------------------------------
# 10. Display best model by MAE for each horizon
# ------------------------------------------------------------

print("\n")
print("=" * 70)
print("LOWEST MAE BY HORIZON")
print("=" * 70)

for horizon in range(1, 5):

    horizon_results = results_df[
        results_df["horizon"] == horizon
    ]

    best_row = horizon_results.loc[
        horizon_results["mae_ms"].idxmin()
    ]

    print(
        f"+{horizon}: "
        f"{best_row['model']} "
        f"(MAE = {best_row['mae_ms']:.3f} ms)"
    )


# ------------------------------------------------------------
# 11. Save location
# ------------------------------------------------------------

print("\nResults saved to:")
print(OUTPUT_FILE)

print("\n" + "=" * 70)
print("PHASE 10 MODEL EXPERIMENT COMPLETE")
print("=" * 70)
