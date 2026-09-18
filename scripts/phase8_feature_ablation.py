import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


INPUT_FILE = "data/phase8_future_prediction_features.csv"


df = pd.read_csv(INPUT_FILE)


current_features = [
    "packet_loss_percent",
    "min_latency_ms",
    "avg_latency_ms",
    "max_latency_ms",
    "jitter_ms",
    "latency_range_ms"
]


previous_features = [
    "previous_latency_ms",
    "previous_jitter_ms",
    "previous_packet_loss_percent",
    "latency_change_ms",
    "jitter_change_ms",
    "packet_loss_change_percent"
]


rolling_features = [
    "rolling_avg_latency_ms",
    "rolling_avg_jitter_ms",
    "rolling_avg_packet_loss_percent",
    "rolling_latency_std_ms",
    "rolling_jitter_std_ms"
]


target = "future_latency_ms"


feature_groups = {
    "Current only": current_features,

    "Current + previous": (
        current_features +
        previous_features
    ),

    "Current + previous + rolling": (
        current_features +
        previous_features +
        rolling_features
    )
}


split_index = int(len(df) * 0.8)


print("=" * 60)
print("PHASE 8 FEATURE ABLATION EXPERIMENT")
print("=" * 60)

print("Total samples:", len(df))
print("Training samples:", split_index)
print("Testing samples:", len(df) - split_index)


results = []


for name, features in feature_groups.items():

    X = df[features]
    y = df[target]

    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]

    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]

    model = LinearRegression()

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(X_test)

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

    results.append({
        "feature_group": name,
        "feature_count": len(features),
        "mae_ms": mae,
        "rmse_ms": rmse,
        "r2": r2
    })

    print("\n" + name)
    print("-" * len(name))
    print("Features:", len(features))
    print("MAE :", round(mae, 3), "ms")
    print("RMSE:", round(rmse, 3), "ms")
    print("R2  :", round(r2, 3))


results_df = pd.DataFrame(results)

results_df.to_csv(
    "results/phase8_feature_ablation.csv",
    index=False
)


print("\n" + "=" * 60)
print("ABLATION EXPERIMENT COMPLETE")
print("=" * 60)

print(
    "Saved to: "
    "results/phase8_feature_ablation.csv"
)
