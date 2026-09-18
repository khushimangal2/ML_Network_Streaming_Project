import subprocess
import csv
import os
import re
import time
from datetime import datetime


PING_HOST = "google.com"
PING_COUNT = 10
NUMBER_OF_SAMPLES = 200
INTERVAL_SECONDS = 5

OUTPUT_FILE = "data/phase8_sequential_network_data.csv"


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
        packet_loss_percent = 100.0

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


def main():

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

    fieldnames = [
        "timestamp",
        "packet_loss_percent",
        "min_latency_ms",
        "avg_latency_ms",
        "max_latency_ms",
        "jitter_ms",
        "latency_range_ms"
    ]

    print("=" * 60)
    print("PHASE 8 SEQUENTIAL NETWORK DATA COLLECTOR")
    print("=" * 60)
    print(f"Host: {PING_HOST}")
    print(f"Ping packets per sample: {PING_COUNT}")
    print(f"Total samples: {NUMBER_OF_SAMPLES}")
    print(f"Interval: {INTERVAL_SECONDS} seconds")
    print(f"Output: {OUTPUT_FILE}")
    print("=" * 60)

    with open(
        file_path,
        "w",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for sample in range(
            1,
            NUMBER_OF_SAMPLES + 1
        ):

            print(
                f"\nCollecting sample "
                f"{sample}/{NUMBER_OF_SAMPLES}..."
            )

            metrics = collect_ping_metrics()

            print(
                f"Latency: {metrics['avg_latency_ms']} ms | "
                f"Jitter: {metrics['jitter_ms']} ms | "
                f"Loss: {metrics['packet_loss_percent']}%"
            )

            writer.writerow(metrics)
            file.flush()

            if sample < NUMBER_OF_SAMPLES:
                time.sleep(INTERVAL_SECONDS)

    print("\n" + "=" * 60)
    print("SEQUENTIAL COLLECTION COMPLETE")
    print("=" * 60)
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
