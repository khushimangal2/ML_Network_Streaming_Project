import pandas as pd
import numpy as np

INPUT_FILE = "data/phase8_live_network_data.csv"
OUTPUT_FILE = "data/phase8_dynamic_network_features.csv"

df = pd.read_csv(INPUT_FILE)

# Make sure observations are ordered by time
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp").reset_index(drop=True)

# ---------------------------------------------------------
# 1. Changes from previous observation
# ---------------------------------------------------------

df["latency_change_ms"] = (
    df["avg_latency_ms"].diff()
)

df["jitter_change_ms"] = (
    df["jitter_ms"].diff()
)

df["packet_loss_change_percent"] = (
    df["packet_loss_percent"].diff()
)

# ---------------------------------------------------------
# 2. Absolute changes
# ---------------------------------------------------------

df["absolute_latency_change_ms"] = (
    df["latency_change_ms"].abs()
)

df["absolute_jitter_change_ms"] = (
    df["jitter_change_ms"].abs()
)

df["absolute_packet_loss_change_percent"] = (
    df["packet_loss_change_percent"].abs()
)

# ---------------------------------------------------------
# 3. Rolling averages
# ---------------------------------------------------------

window = 3

df["rolling_avg_latency_ms"] = (
    df["avg_latency_ms"]
    .rolling(window=window, min_periods=1)
    .mean()
)

df["rolling_avg_jitter_ms"] = (
    df["jitter_ms"]
    .rolling(window=window, min_periods=1)
    .mean()
)

df["rolling_avg_packet_loss_percent"] = (
    df["packet_loss_percent"]
    .rolling(window=window, min_periods=1)
    .mean()
)

# ---------------------------------------------------------
# 4. Rolling standard deviation
# ---------------------------------------------------------

df["rolling_latency_std_ms"] = (
    df["avg_latency_ms"]
    .rolling(window=window, min_periods=2)
    .std()
)

df["rolling_jitter_std_ms"] = (
    df["jitter_ms"]
    .rolling(window=window, min_periods=2)
    .std()
)

# ---------------------------------------------------------
# 5. Short-term trends
# ---------------------------------------------------------

df["latency_trend"] = (
    df["avg_latency_ms"]
    .diff()
)

df["jitter_trend"] = (
    df["jitter_ms"]
    .diff()
)

df["packet_loss_trend"] = (
    df["packet_loss_percent"]
    .diff()
)

# ---------------------------------------------------------
# 6. Network volatility
# ---------------------------------------------------------

df["network_volatility"] = (
    df["rolling_latency_std_ms"].fillna(0)
    + df["rolling_jitter_std_ms"].fillna(0)
    + df["absolute_latency_change_ms"].fillna(0)
)

# ---------------------------------------------------------
# 7. Fill first-row NaN values
# ---------------------------------------------------------

df = df.replace([np.inf, -np.inf], np.nan)

df = df.fillna(0)

# ---------------------------------------------------------
# 8. Save
# ---------------------------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("=" * 65)
print("PHASE 8 — DYNAMIC FEATURE ENGINEERING COMPLETE")
print("=" * 65)

print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")

print("\nDynamic features added:")

features = [
    "latency_change_ms",
    "jitter_change_ms",
    "packet_loss_change_percent",
    "absolute_latency_change_ms",
    "absolute_jitter_change_ms",
    "absolute_packet_loss_change_percent",
    "rolling_avg_latency_ms",
    "rolling_avg_jitter_ms",
    "rolling_avg_packet_loss_percent",
    "rolling_latency_std_ms",
    "rolling_jitter_std_ms",
    "latency_trend",
    "jitter_trend",
    "packet_loss_trend",
    "network_volatility"
]

for feature in features:
    print(f" - {feature}")

print(f"\nSaved to: {OUTPUT_FILE}")
