import pandas as pd


INPUT_FILE = "data/phase8_sequential_network_data.csv"
OUTPUT_FILE = "data/phase8_future_prediction_features.csv"


df = pd.read_csv(INPUT_FILE)

df["timestamp"] = pd.to_datetime(df["timestamp"])

df = df.sort_values("timestamp").reset_index(drop=True)


# Previous observations
df["previous_latency_ms"] = df["avg_latency_ms"].shift(1)
df["previous_jitter_ms"] = df["jitter_ms"].shift(1)
df["previous_packet_loss_percent"] = df["packet_loss_percent"].shift(1)


# Changes from the previous observation
df["latency_change_ms"] = (
    df["avg_latency_ms"] -
    df["previous_latency_ms"]
)

df["jitter_change_ms"] = (
    df["jitter_ms"] -
    df["previous_jitter_ms"]
)

df["packet_loss_change_percent"] = (
    df["packet_loss_percent"] -
    df["previous_packet_loss_percent"]
)


# Rolling recent history
df["rolling_avg_latency_ms"] = (
    df["avg_latency_ms"]
    .rolling(window=5, min_periods=1)
    .mean()
)

df["rolling_avg_jitter_ms"] = (
    df["jitter_ms"]
    .rolling(window=5, min_periods=1)
    .mean()
)

df["rolling_avg_packet_loss_percent"] = (
    df["packet_loss_percent"]
    .rolling(window=5, min_periods=1)
    .mean()
)


# Rolling variability
df["rolling_latency_std_ms"] = (
    df["avg_latency_ms"]
    .rolling(window=5, min_periods=2)
    .std()
)

df["rolling_jitter_std_ms"] = (
    df["jitter_ms"]
    .rolling(window=5, min_periods=2)
    .std()
)


# Absolute changes
df["absolute_latency_change_ms"] = (
    df["latency_change_ms"].abs()
)

df["absolute_jitter_change_ms"] = (
    df["jitter_change_ms"].abs()
)

df["absolute_packet_loss_change_percent"] = (
    df["packet_loss_change_percent"].abs()
)


# Future targets
df["future_latency_ms"] = (
    df["avg_latency_ms"].shift(-1)
)

df["future_jitter_ms"] = (
    df["jitter_ms"].shift(-1)
)

df["future_packet_loss_percent"] = (
    df["packet_loss_percent"].shift(-1)
)


# Future changes
df["future_latency_change_ms"] = (
    df["future_latency_ms"] -
    df["avg_latency_ms"]
)

df["future_jitter_change_ms"] = (
    df["future_jitter_ms"] -
    df["jitter_ms"]
)

df["future_packet_loss_change_percent"] = (
    df["future_packet_loss_percent"] -
    df["packet_loss_percent"]
)


# Remove rows where previous/future information is unavailable
df = df.dropna().reset_index(drop=True)


df.to_csv(
    OUTPUT_FILE,
    index=False
)


print("=" * 60)
print("PHASE 8 FUTURE-PREDICTION FEATURE ENGINEERING")
print("=" * 60)

print("Input rows: 200")
print("Output rows:", len(df))
print("Output columns:", len(df.columns))

print("\nSaved to:")
print(OUTPUT_FILE)

print("\nMissing values:")
print(df.isnull().sum().sum())

print("\nColumns:")
for i, column in enumerate(df.columns, start=1):
    print(f"{i}. {column}")
