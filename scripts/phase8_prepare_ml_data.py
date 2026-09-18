import pandas as pd

INPUT_FILE = "data/phase8_engineered_features.csv"
OUTPUT_FILE = "data/phase8_ml_dataset.csv"

df = pd.read_csv(INPUT_FILE)

# Target to predict
TARGET = "condition"

# Features based on observed network behavior
FEATURES = [
    "measured_packet_loss_percent",
    "min_latency_ms",
    "avg_latency_ms",
    "max_latency_ms",
    "measured_jitter_ms",
    "latency_range_ms",
    "latency_variability_ms",
    "latency_ratio",
    "loss_difference_percent",
    "loss_ratio",
    "jitter_latency_ratio"
]

ml_df = df[FEATURES + [TARGET]].copy()

# Remove any unexpected missing values
ml_df = ml_df.dropna()

ml_df.to_csv(OUTPUT_FILE, index=False)

print("=" * 60)
print("PHASE 8 ML DATASET CREATED")
print("=" * 60)

print(f"Rows: {len(ml_df)}")
print(f"Features: {len(FEATURES)}")
print(f"Target: {TARGET}")

print("\nFeatures:")
for feature in FEATURES:
    print(f" - {feature}")

print("\nTarget distribution:")
print(ml_df[TARGET].value_counts().sort_index().to_string())

print(f"\nSaved to: {OUTPUT_FILE}")
