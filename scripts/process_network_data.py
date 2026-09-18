import csv
import re
import statistics

input_file = "../data/network_data.csv"
output_file = "../data/processed_network_data.csv"

processed_data = []

with open(input_file, "r") as file:
    reader = csv.DictReader(file)

    for row in reader:
        ping_output = row["ping_output"]

        times = re.findall(r"time=([0-9.]+) ms", ping_output)

        if times:
            latencies = [float(time) for time in times]

            min_latency = min(latencies)
            avg_latency = statistics.mean(latencies)
            max_latency = max(latencies)

            if len(latencies) > 1:
                jitter = statistics.stdev(latencies)
            else:
                jitter = 0

            processed_data.append({
                "timestamp": row["timestamp"],
                "min_latency_ms": min_latency,
                "avg_latency_ms": avg_latency,
                "max_latency_ms": max_latency,
                "jitter_ms": jitter
            })

with open(output_file, "w", newline="") as file:
    fieldnames = [
        "timestamp",
        "min_latency_ms",
        "avg_latency_ms",
        "max_latency_ms",
        "jitter_ms"
    ]

    writer = csv.DictWriter(file, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(processed_data)

print("Network data processed successfully!")
print("Saved to:", output_file)
