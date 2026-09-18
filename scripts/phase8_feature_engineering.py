import pandas as pd
import numpy as np

INPUT_FILE = "data/phase7_network_dataset.csv"
OUTPUT_FILE = "data/phase8_engineered_features.csv"

df = pd.read_csv(INPUT_FILE)

# ---------------------------------------------------------
# 1. Basic latency features
# ---------------------------------------------------------

df["latency_range_ms"] = (
    df["max_latency_ms"] - df["min_latency_ms"]
)

df["latency_variability_ms"] = (
    df["max_latency_ms"] - df["avg_latency_ms"]
)

df["latency_ratio"] = (
    df["avg_latency_ms"] / df["min_latency_ms"].replace(0, np.nan)
)

# ---------------------------------------------------------
# 2. Packet-loss features
# ---------------------------------------------------------

df["loss_difference_percent"] = (
    df["measured_packet_loss_percent"]
    - df["configured_packet_loss_percent"]
)

df["loss_ratio"] = (
    df["measured_packet_loss_percent"]
    / df["configured_packet_loss_percent"].replace(0, np.nan)
)

df["loss_ratio"] = df["loss_ratio"].replace([np.inf, -np.inf], np.nan)

# ---------------------------------------------------------
# 3. Jitter-to-latency relationship
# ---------------------------------------------------------

df["jitter_latency_ratio"] = (
    df["measured_jitter_ms"]
    / df["avg_latency_ms"].replace(0, np.nan)
)

# ---------------------------------------------------------
# 4. Network stability score
# ---------------------------------------------------------
# Higher score = more stable network.
# This is a derived research feature, not a ground-truth label.

latency_penalty = (
    df["avg_latency_ms"] / df["avg_latency_ms"].max()
)

jitter_penalty = (
    df["measured_jitter_ms"] / df["measured_jitter_ms"].max()
)

loss_penalty = (
    df["measured_packet_loss_percent"]
    / max(df["measured_packet_loss_percent"].max(), 1)
)

df["network_stability_score"] = (
    1
    - (
        0.5 * latency_penalty
        + 0.3 * jitter_penalty
        + 0.2 * loss_penalty
    )
)

# ---------------------------------------------------------
# 5. Network quality score
# ---------------------------------------------------------
# Higher score = better measured network quality.

df["network_quality_score"] = (
    100
    * (
        0.5 * (1 - latency_penalty)
        + 0.3 * (1 - jitter_penalty)
        + 0.2 * (1 - loss_penalty)
    )
)

# ---------------------------------------------------------
# 6. Handle infinite and missing values
# ---------------------------------------------------------

df = df.replace([np.inf, -np.inf], np.nan)

numeric_columns = df.select_dtypes(include=[np.number]).columns

df[numeric_columns] = df[numeric_columns].fillna(
    df[numeric_columns].median()
)

# ---------------------------------------------------------
# 7. Save engineered dataset
# ---------------------------------------------------------

df.to_csv(OUTPUT_FILE, index=False)

print("=" * 60)
print("PHASE 8 FEATURE ENGINEERING COMPLETE")
print("=" * 60)

print(f"Input rows: {len(pd.read_csv(INPUT_FILE))}")
print(f"Output rows: {len(df)}")
print(f"Input columns: {len(pd.read_csv(INPUT_FILE).columns)}")
print(f"Output columns: {len(df.columns)}")

print("\nNew features:")
new_features = [
    "latency_range_ms",
    "latency_variability_ms",
    "latency_ratio",
    "loss_difference_percent",
    "loss_ratio",
    "jitter_latency_ratio",
    "network_stability_score",
    "network_quality_score",
]

for feature in new_features:
    print(f" - {feature}")

print("\nMissing values:")
print(df.isnull().sum().sum())

print(f"\nSaved to: {OUTPUT_FILE}")
