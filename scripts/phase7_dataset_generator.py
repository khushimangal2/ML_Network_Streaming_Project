import csv
import os
import re
import subprocess
import time
import requests

INTERFACE = "enp0s3"
PING_HOST = "google.com"

OUTPUT_FILE = os.path.expanduser(
    "~/ML_Network_Streaming_Project/data/phase7_test_throughput.csv"
)

CONTROLLER_URL = "http://127.0.0.1:5002"

PING_COUNT = 100
STABILIZATION_SECONDS = 5


def run_command(command):
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("Command failed:")
        print(command)
        print(result.stderr)
        raise RuntimeError("Command failed")

    return result.stdout


def clear_qdisc():
    subprocess.run(
        f"sudo tc qdisc del dev {INTERFACE} root",
        shell=True,
        capture_output=True,
        text=True
    )


def apply_network_condition():
    clear_qdisc()

    run_command(
        f"sudo tc qdisc add dev {INTERFACE} root handle 1: "
        f"tbf rate 5mbit burst 32kbit latency 400ms"
    )

    run_command(
        f"sudo tc qdisc add dev {INTERFACE} parent 1:1 handle 10: "
        f"netem delay 100ms 10ms loss 2%"
    )


def measure_ping():

    output = run_command(
        f"ping -c {PING_COUNT} {PING_HOST}"
    )

    packet_loss = None
    min_latency = None
    avg_latency = None
    max_latency = None

    match = re.search(
        r"([\d.]+)% packet loss",
        output
    )

    if match:
        packet_loss = float(match.group(1))

    match = re.search(
        r"=\s*([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)\s*ms",
        output
    )

    if match:
        min_latency = float(match.group(1))
        avg_latency = float(match.group(2))
        max_latency = float(match.group(3))

    latencies = []

    for line in output.splitlines():

        match = re.search(
            r"time[=<]([\d.]+)\s*ms",
            line
        )

        if match:
            latencies.append(float(match.group(1)))

    measured_jitter = None

    if len(latencies) >= 2:

        differences = []

        for i in range(1, len(latencies)):
            differences.append(
                abs(latencies[i] - latencies[i - 1])
            )

        measured_jitter = (
            sum(differences) / len(differences)
        )

    return (
        packet_loss,
        min_latency,
        avg_latency,
        max_latency,
        measured_jitter
    )


def request_throughput():

    experiment_id = 1

    response = requests.get(
        f"{CONTROLLER_URL}/request_measurement"
        f"?experiment_id={experiment_id}",
        timeout=10
    )

    response.raise_for_status()

    print("Throughput measurement requested.")

    while True:

        response = requests.get(
            f"{CONTROLLER_URL}/get_result",
            timeout=10
        )

        response.raise_for_status()

        result = response.json()

        if result.get("status") == "complete":

            print(
                f"Throughput: "
                f"{result.get('throughput_mbps')} Mbps"
            )

            print(
                f"Download time: "
                f"{result.get('download_time_seconds')} seconds"
            )

            return (
                result.get("throughput_mbps"),
                result.get("download_time_seconds")
            )

        time.sleep(2)


def main():

    print("=" * 60)
    print("PHASE 7 ONE-EXPERIMENT PIPELINE TEST")
    print("=" * 60)

    print("Condition: Moderate")
    print("Bandwidth: 5 Mbps")
    print("Delay: 100 ms")
    print("Jitter: 10 ms")
    print("Packet loss: 2%")
    print("=" * 60)

    try:

        print("\nApplying network condition...")

        apply_network_condition()

        print(
            f"Waiting {STABILIZATION_SECONDS} seconds..."
        )

        time.sleep(STABILIZATION_SECONDS)

        print("\nMeasuring latency/jitter/loss...")

        (
            packet_loss,
            min_latency,
            avg_latency,
            max_latency,
            measured_jitter
        ) = measure_ping()

        print(
            f"Packet loss: {packet_loss}%"
        )

        print(
            f"Min latency: {min_latency} ms"
        )

        print(
            f"Average latency: {avg_latency} ms"
        )

        print(
            f"Max latency: {max_latency} ms"
        )

        print(
            f"Measured jitter: {measured_jitter} ms"
        )

        print("\nRequesting actual throughput...")

        throughput, download_time = request_throughput()

        row = {
            "experiment_id": 1,
            "repetition": 1,
            "condition": "Moderate",
            "configured_bandwidth_mbps": 5,
            "configured_delay_ms": 100,
            "configured_jitter_ms": 10,
            "configured_packet_loss_percent": 2,
            "measured_throughput_mbps": throughput,
            "download_time_seconds": download_time,
            "measured_packet_loss_percent": packet_loss,
            "min_latency_ms": min_latency,
            "avg_latency_ms": avg_latency,
            "max_latency_ms": max_latency,
            "measured_jitter_ms": measured_jitter
        }

        with open(
            OUTPUT_FILE,
            "w",
            newline=""
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=row.keys()
            )

            writer.writeheader()
            writer.writerow(row)

        print("\nExperiment successfully saved.")
        print(OUTPUT_FILE)

    finally:

        clear_qdisc()

        print("\nNetwork restored to normal.")
        print("One-experiment test finished.")


if __name__ == "__main__":
    main()
