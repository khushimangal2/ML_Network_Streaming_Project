import subprocess
import csv
import os
import re
import time
from datetime import datetime


PING_HOST = "google.com"
PING_COUNT = 10
OUTPUT_FILE = "data/phase8_live_network_data.csv"


def collect_ping_metrics():

    result = subprocess.run(
        ["ping", "-c", str(PING_COUNT), PING_HOST],
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

    if times:

        min_latency = min(times)
        avg_latency = sum(times) / len(times)
        max_latency = max(times)

        latency_range = max_latency - min_latency

        if len(times) > 1:

            differences = [
                abs(times[i] - times[i - 1])
                for i in range(1, len(times))
            ]

            jitter = sum(differences) / len(differences)

        else:
            jitter = 0.0

    else:

        min_latency = 0.0
        avg_latency = 0.0
        max_latency = 0.0
        latency_range = 0.0
        jitter = 0.0

    metrics = {
        "timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "packet_loss_percent": round(
            packet_loss_percent, 3
        ),
        "min_latency_ms": round(
            min_latency, 3
        ),
        "avg_latency_ms": round(
            avg_latency, 3
        ),
        "max_latency_ms": round(
            max_latency, 3
        ),
        "jitter_ms": round(
            jitter, 3
        ),
        "latency_range_ms": round(
            latency_range, 3
        )
    }

    return metrics


def save_metrics(metrics):

    project_directory = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    file_path = os.path.join(
        project_directory,
        OUTPUT_FILE
    )

    os.makedirs(
        os.path.dirname(file_path),
        exist_ok=True
    )

    file_exists = os.path.isfile(file_path)

    fieldnames = [
        "timestamp",
        "packet_loss_percent",
        "min_latency_ms",
        "avg_latency_ms",
        "max_latency_ms",
        "jitter_ms",
        "latency_range_ms"
    ]

    with open(
        file_path,
        "a",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        if not file_exists or os.path.getsize(file_path) == 0:
            writer.writeheader()

        writer.writerow(metrics)


def main():

    number_of_samples = 10
    interval_seconds = 5

    print("=" * 60)
    print("PHASE 8 ADVANCED NETWORK COLLECTOR")
    print("=" * 60)

    print(f"Host: {PING_HOST}")
    print(f"Ping packets per sample: {PING_COUNT}")
    print(f"Samples: {number_of_samples}")
    print(f"Interval: {interval_seconds} seconds")
    print(f"Output: {OUTPUT_FILE}")

    for sample in range(1, number_of_samples + 1):

        print(
            f"\nCollecting sample "
            f"{sample}/{number_of_samples}..."
        )

        metrics = collect_ping_metrics()

        print(metrics)

        save_metrics(metrics)

        if sample < number_of_samples:
            time.sleep(interval_seconds)

    print("\n" + "=" * 60)
    print("COLLECTION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
