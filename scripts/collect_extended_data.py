import subprocess
import csv
import os
import re
import time
from datetime import datetime


def collect_network_metrics():
    result = subprocess.run(
        ["ping", "-c", "10", "google.com"],
        capture_output=True,
        text=True
    )

    output = result.stdout

    packet_loss_match = re.search(
        r"(\d+(?:\.\d+)?)% packet loss",
        output
    )

    if packet_loss_match:
        packet_loss_percent = float(packet_loss_match.group(1))
    else:
        packet_loss_percent = 0.0

    times = re.findall(
        r"time[=<]([\d.]+)",
        output
    )

    times = [float(value) for value in times]

    if len(times) > 0:
        min_latency_ms = min(times)
        avg_latency_ms = sum(times) / len(times)
        max_latency_ms = max(times)

        if len(times) > 1:
            differences = []

            for i in range(1, len(times)):
                difference = abs(times[i] - times[i - 1])
                differences.append(difference)

            jitter_ms = sum(differences) / len(differences)
        else:
            jitter_ms = 0.0

    else:
        min_latency_ms = 0.0
        avg_latency_ms = 0.0
        max_latency_ms = 0.0
        jitter_ms = 0.0

    metrics = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "packet_loss_percent": packet_loss_percent,
        "min_latency_ms": round(min_latency_ms, 3),
        "avg_latency_ms": round(avg_latency_ms, 3),
        "max_latency_ms": round(max_latency_ms, 3),
        "jitter_ms": round(jitter_ms, 3)
    }

    return metrics


def save_network_data(metrics):
    script_directory = os.path.dirname(
        os.path.abspath(__file__)
    )

    project_directory = os.path.dirname(
        script_directory
    )

    data_directory = os.path.join(
        project_directory,
        "data"
    )

    os.makedirs(
        data_directory,
        exist_ok=True
    )

    file_path = os.path.join(
        data_directory,
        "extended_network_data.csv"
    )

    file_exists = os.path.isfile(file_path)

    with open(
        file_path,
        "a",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "timestamp",
                "packet_loss_percent",
                "min_latency_ms",
                "avg_latency_ms",
                "max_latency_ms",
                "jitter_ms"
            ]
        )

        if not file_exists or os.path.getsize(file_path) == 0:
            writer.writeheader()

        writer.writerow(metrics)

    print("\nNetwork metrics collected successfully!")
    print("Saved to:", file_path)


def main():
    number_of_samples = 5

    for sample_number in range(1, number_of_samples + 1):

        print("\nCollecting sample", sample_number)

        metrics = collect_network_metrics()

        print("Collected Network Metrics:")
        print(metrics)

        save_network_data(metrics)

        if sample_number < number_of_samples:
            print("Waiting 10 seconds...")
            time.sleep(10)

    print("\nAll network samples collected successfully!")


if __name__ == "__main__":
    main()
