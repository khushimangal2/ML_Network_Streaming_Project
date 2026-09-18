import pandas as pd
import os

input_file = "data/extended_network_data.csv"
output_file = "data/prepared_network_data.csv"

df = pd.read_csv(input_file)

def classify_network(row):
    if row["packet_loss_percent"] > 2:
        return "Poor"

    if row["avg_latency_ms"] > 150:
        return "Poor"

    if row["jitter_ms"] > 30:
        return "Poor"

    if row["avg_latency_ms"] > 80:
        return "Moderate"

    if row["jitter_ms"] > 15:
        return "Moderate"

    return "Good"

df["network_condition"] = df.apply(classify_network, axis=1)

features = [
    "packet_loss_percent",
    "min_latency_ms",
    "avg_latency_ms",
    "max_latency_ms",
    "jitter_ms",
    "network_condition"
]

prepared_df = df[features]

os.makedirs("data", exist_ok=True)

prepared_df.to_csv(output_file, index=False)

print("Data preparation completed successfully!")
print("Saved to:", output_file)

print("\nPrepared dataset:")
print(prepared_df)

print("\nNetwork condition distribution:")
print(prepared_df["network_condition"].value_counts())

