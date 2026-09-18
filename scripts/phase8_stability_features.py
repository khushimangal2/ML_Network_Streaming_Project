import pandas as pd
import numpy as np

INPUT_FILE = "data/phase8_engineered_features.csv"
OUTPUT_FILE = "data/phase8_stability_features.csv"

df = pd.read_csv(INPUT_FILE)

# Identify each unique controlled network configuration
group_columns = [
    "condition",
    "configured_bandwidth_mbps",
    "configured_delay_ms",
    "configured_jitter_ms",
    "configured_packet_loss_percent"
]

# Calculate stability statistics across the 5 repetitions
grouped = df.groupby(group_columns)

stability = grouped.agg(
    mean_latency_ms=("avg_latency_ms", "mean"),
    std_latency_ms=("avg_latency_ms", "std"),
    mean_jitter_ms=("measured_jitter_ms", "mean"),
    std_jitter_ms=("measured_jitter_ms", "std"),
    mean_packet_loss_percent=("measured_packet_loss_percent", "mean"),
    std_packet_loss_percent=("measured_packet_loss_percent", "std"),
    mean_latency_range_ms=("latency_range_ms", "mean"),
    std_latency_range_ms=("latency_range_ms", "std")
).reset_index()

# Standard deviation can be NaN for a group with only one observation.
stability = stability.fillna(0)

# Coefficient of variation
stability["latency_cv"] = (
    stability["std_latency_ms"]
    / stability["mean_latency_ms"].replace(0, np.nan)
)

stability["jitter_cv"] = (
    stability["std_jitter_ms"]
    / stability["mean_jitter_ms"].replace(0, np.nan)
)

stability["packet_loss_cv"] = (
    stability["std_packet_loss_percent"]
    / stability["mean_packet_loss_percent"].replace(0, np.nan)
)

stability = stability.replace([np.inf, -np.inf], np.nan)
stability = stability.fillna(0)

# Overall volatility indicator
stability["network_volatility_score"] = (
    stability["latency_cv"]
    + stability["jitter_cv"]
    + stability["packet_loss_cv"]
)

# Lower volatility = more stable
stability["network_stability_score_v2"] = (
    1 / (1 + stability["network_volatility_score"])
)

# Save
stability.to_csv(OUTPUT_FILE, index=False)

print("=" * 60)
print("PHASE 8 STABILITY FEATURE ENGINEERING COMPLETE")
print("=" * 60)

print(f"Original rows: {len(df)}")
print(f"Unique configurations: {len(stability)}")
print(f"Output columns: {len(stability.columns)}")

print("\nNew stability features:")
features = [
    "mean_latency_ms",
    "std_latency_ms",
    "mean_jitter_ms",
    "std_jitter_ms",
    "mean_packet_loss_percent",
    "std_packet_loss_percent",
    "mean_latency_range_ms",
    "std_latency_range_ms",
    "latency_cv",
    "jitter_cv",
    "packet_loss_cv",
    "network_volatility_score",
    "network_stability_score_v2"
]

for feature in features:
    print(f" - {feature}")

print(f"\nSaved to: {OUTPUT_FILE}")
