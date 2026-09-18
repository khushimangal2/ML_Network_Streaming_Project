import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


INPUT_FILE = "data/phase8_future_prediction_features.csv"


df = pd.read_csv(INPUT_FILE)


feature_columns = [
    "packet_loss_percent",
    "min_latency_ms",
    "avg_latency_ms",
    "max_latency_ms",
    "jitter_ms",
    "latency_range_ms",
    "previous_latency_ms",
    "previous_jitter_ms",
    "previous_packet_loss_percent",
    "latency_change_ms",
    "jitter_change_ms",
    "packet_loss_change_percent",
    "rolling_avg_latency_ms",
    "rolling_avg_jitter_ms",
    "rolling_avg_packet_loss_percent",
    "rolling_latency_std_ms",
    "rolling_jitter_std_ms",
    "absolute_latency_change_ms",
    "absolute_jitter_change_ms",
    "absolute_packet_loss_change_percent"
]

target_column = "future_latency_ms"


X = df[feature_columns]
y = df[target_column]


# Time-ordered split
split_index = int(len(df) * 0.8)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]


print("=" * 60)
print("PHASE 8 FUTURE LATENCY PREDICTION")
print("=" * 60)

print("Total samples:", len(df))
print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))
print("Features:", len(feature_columns))


# Linear Regression
linear_model = LinearRegression()
linear_model.fit(X_train, y_train)

linear_predictions = linear_model.predict(X_test)

linear_mae = mean_absolute_error(
    y_test,
    linear_predictions
)

linear_rmse = mean_squared_error(
    y_test,
    linear_predictions
) ** 0.5

linear_r2 = r2_score(
    y_test,
    linear_predictions
)


# Random Forest
rf_model = RandomForestRegressor(
    n_estimators=200,
    random_state=42
)

rf_model.fit(X_train, y_train)

rf_predictions = rf_model.predict(X_test)

rf_mae = mean_absolute_error(
    y_test,
    rf_predictions
)

rf_rmse = mean_squared_error(
    y_test,
    rf_predictions
) ** 0.5

rf_r2 = r2_score(
    y_test,
    rf_predictions
)


print("\nLinear Regression")
print("-----------------")
print("MAE :", round(linear_mae, 3), "ms")
print("RMSE:", round(linear_rmse, 3), "ms")
print("R2  :", round(linear_r2, 3))


print("\nRandom Forest")
print("-------------")
print("MAE :", round(rf_mae, 3), "ms")
print("RMSE:", round(rf_rmse, 3), "ms")
print("R2  :", round(rf_r2, 3))


print("\nActual vs predicted examples:")
print("--------------------------------")

for actual, prediction in zip(
    y_test.iloc[:10],
    rf_predictions[:10]
):

    print(
        f"Actual: {actual:.2f} ms | "
        f"Predicted: {prediction:.2f} ms"
    )


print("\n" + "=" * 60)
print("PREDICTION TEST COMPLETE")
print("=" * 60)
