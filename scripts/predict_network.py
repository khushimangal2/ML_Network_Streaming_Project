import os
import subprocess
import time
import joblib
import pandas as pd


# ---------------------------------
# Load trained ML model
# ---------------------------------
model_path = "models/network_condition_model.pkl"

if not os.path.exists(model_path):
    print("Error: Trained model not found!")
    print("Expected location:", model_path)
    exit()

model = joblib.load(model_path)

print("Trained ML model loaded successfully!")


# ---------------------------------
# Function to measure ping latency
# ---------------------------------
def get_latency(host="8.8.8.8", count=5):
    try:
        result = subprocess.run(
            ["ping", "-c", str(count), host],
            capture_output=True,
            text=True
        )

        output = result.stdout

        latency_values = []

        for line in output.splitlines():
            if "time=" in line:
                latency = line.split("time=")[1].split()[0]
                latency_values.append(float(latency))

        if len(latency_values) == 0:
            return None

        return latency_values

    except Exception as e:
        print("Error collecting latency:", e)
        return None


# ---------------------------------
# Calculate network metrics
# ---------------------------------
def collect_network_metrics():
    latency_values = get_latency()

    if latency_values is None:
        print("Could not collect network latency.")
        return None

    min_latency = min(latency_values)
    avg_latency = sum(latency_values) / len(latency_values)
    max_latency = max(latency_values)

    jitter = sum(
        abs(latency_values[i] - latency_values[i - 1])
        for i in range(1, len(latency_values))
    ) / (len(latency_values) - 1)

    # Packet loss calculation
    result = subprocess.run(
        ["ping", "-c", "10", "8.8.8.8"],
        capture_output=True,
        text=True
    )

    output = result.stdout

    packet_loss = 0.0

    for line in output.splitlines():
        if "packet loss" in line:
            packet_loss = float(
                line.split("%")[0].split()[-1]
            )

    return {
        "packet_loss_percent": packet_loss,
        "min_latency_ms": min_latency,
        "avg_latency_ms": avg_latency,
        "max_latency_ms": max_latency,
        "jitter_ms": jitter
    }


# ---------------------------------
# Collect live network metrics
# ---------------------------------
print("\nCollecting live network metrics...")

metrics = collect_network_metrics()

if metrics is None:
    exit()

print("\nCollected Network Metrics:")

for key, value in metrics.items():
    print(f"{key}: {round(value, 3)}")


# ---------------------------------
# Convert metrics to DataFrame
# ---------------------------------
input_data = pd.DataFrame(
    [metrics],
    columns=[
        "packet_loss_percent",
        "min_latency_ms",
        "avg_latency_ms",
        "max_latency_ms",
        "jitter_ms"
    ]
)


# ---------------------------------
# Predict network condition
# ---------------------------------
prediction = model.predict(input_data)[0]

print("\n" + "=" * 40)
print("PREDICTED NETWORK CONDITION:", prediction)
print("=" * 40)


# ---------------------------------
# Streaming recommendation
# ---------------------------------
if prediction == "Good":
    print("\nRecommended Video Quality: 1080p")
else:
    print("\nRecommended Video Quality: 480p or 720p")

