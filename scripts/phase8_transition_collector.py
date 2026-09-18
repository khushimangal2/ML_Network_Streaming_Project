import subprocess
import csv
import os
import re
import time
from datetime import datetime


INTERFACE = "enp0s3"
PING_HOST = "google.com"

PING_COUNT = 10
SAMPLES_PER_STATE = 10
WAIT_BETWEEN_SAMPLES = 3

OUTPUT_FILE = "data/phase8_transition_network_data.csv"


STATES = [
    {
        "name": "Good",
        "bandwidth": "20mbit",
        "delay": "30ms",
        "jitter": "5ms",
        "loss": "0%"
    },
    {
        "name": "Moderate",
        "bandwidth": "5mbit",
        "delay": "100ms",
        "jitter": "10ms",
        "loss": "2%"
    },
    {
        "name": "Poor",
        "bandwidth": "2mbit",
        "delay": "200ms",
        "jitter": "20ms",
        "loss": "5%"
    },
    {
        "name": "Moderate",
        "bandwidth": "5mbit",
        "delay": "100ms",
        "jitter": "10ms",
        "loss": "2%"
    },
    {
        "name": "Good",
        "bandwidth": "20mbit",
        "delay": "30ms",
        "jitter": "5ms",
        "loss": "0%"
    }
]


def clear_network():

    subprocess.run(
        [
            "sudo",
            "tc",
            "qdisc",
            "del",
            "dev",
            INTERFACE,
            "root"
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


def apply_network_state(state):

    clear_network()

    command = [
        "sudo",
        "tc",
        "qdisc",
        "add",
        "dev",
        INTERFACE,
        "root",
        "handle",
        "1:",
        "tbf",
        "rate",
        state["bandwidth"],
        "burst",
        "32kbit",
        "latency",
        "400ms"
    ]

    subprocess.run(
        command,
        check=True
    )

    command = [
        "sudo",
        "tc",
        "qdisc",
        "add",
        "dev",
        INTERFACE,
        "parent",
        "1:1",
        "handle",
        "10:",
        "netem",
        "delay",
        state["delay"],
        state["jitter"],
        "loss",
        state["loss"]
    ]

    subprocess.run(
        command,
        check=True
    )


def collect_ping_metrics():

    result = subprocess.run(
        [
            "ping",
            "-c",
            str(PING_COUNT),
            PING_HOST
        ],
        capture_output=True,
        text=True
    )

    output = result.stdout

    packet_loss_match = re.search(
        r"(\d+(?:\.\d+)?)% packet loss",
        output
    )

    if packet_loss_match:
        packet_loss = float(
            packet_loss_match.group(1)
        )
    else:
        packet_loss = 100.0

    times = re.findall(
        r"time[=<]([\d.]+)",
        output
    )

    times = [
        float(value)
        for value in times
    ]

    if times:

        min_latency = min(times)
        avg_latency = (
            sum(times) / len(times)
        )
        max_latency = max(times)

        latency_range = (
            max_latency -
            min_latency
        )

        if len(times) > 1:

            differences = [
                abs(
                    times[i] -
                    times[i - 1]
                )
                for i in range(1, len(times))
            ]

            jitter = (
                sum(differences) /
                len(differences)
            )

        else:
            jitter = 0.0

    else:

        min_latency = 0.0
        avg_latency = 0.0
        max_latency = 0.0
        latency_range = 0.0
        jitter = 0.0

    return {
        "packet_loss_percent":
            round(packet_loss, 3),

        "min_latency_ms":
            round(min_latency, 3),

        "avg_latency_ms":
            round(avg_latency, 3),

        "max_latency_ms":
            round(max_latency, 3),

        "jitter_ms":
            round(jitter, 3),

        "latency_range_ms":
            round(latency_range, 3)
    }


def main():

    project_directory = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    output_path = os.path.join(
        project_directory,
        OUTPUT_FILE
    )

    os.makedirs(
        os.path.dirname(output_path),
        exist_ok=True
    )

    fieldnames = [
        "sample_number",
        "timestamp",
        "state",
        "configured_bandwidth_mbps",
        "configured_delay_ms",
        "configured_jitter_ms",
        "configured_packet_loss_percent",
        "measured_packet_loss_percent",
        "min_latency_ms",
        "avg_latency_ms",
        "max_latency_ms",
        "measured_jitter_ms",
        "latency_range_ms"
    ]

    sample_number = 0

    print("=" * 60)
    print("PHASE 8 CONTROLLED NETWORK TRANSITION EXPERIMENT")
    print("=" * 60)

    with open(
        output_path,
        "w",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        try:

            for state in STATES:

                print("\n" + "=" * 60)
                print(
                    f"STATE: {state['name']}"
                )
                print(
                    f"Bandwidth: {state['bandwidth']}"
                )
                print(
                    f"Delay: {state['delay']}"
                )
                print(
                    f"Jitter: {state['jitter']}"
                )
                print(
                    f"Loss: {state['loss']}"
                )
                print("=" * 60)

                apply_network_state(state)

                print(
                    "Network state applied. "
                    "Stabilizing..."
                )

                time.sleep(5)

                for local_sample in range(
                    1,
                    SAMPLES_PER_STATE + 1
                ):

                    sample_number += 1

                    metrics = (
                        collect_ping_metrics()
                    )

                    row = {
                        "sample_number":
                            sample_number,

                        "timestamp":
                            datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),

                        "state":
                            state["name"],

                        "configured_bandwidth_mbps":
                            float(
                                state["bandwidth"]
                                .replace(
                                    "mbit",
                                    ""
                                )
                            ),

                        "configured_delay_ms":
                            float(
                                state["delay"]
                                .replace(
                                    "ms",
                                    ""
                                )
                            ),

                        "configured_jitter_ms":
                            float(
                                state["jitter"]
                                .replace(
                                    "ms",
                                    ""
                                )
                            ),

                        "configured_packet_loss_percent":
                            float(
                                state["loss"]
                                .replace(
                                    "%",
                                    ""
                                )
                            ),

                        "measured_packet_loss_percent":
                            metrics[
                                "packet_loss_percent"
                            ],

                        "min_latency_ms":
                            metrics[
                                "min_latency_ms"
                            ],

                        "avg_latency_ms":
                            metrics[
                                "avg_latency_ms"
                            ],

                        "max_latency_ms":
                            metrics[
                                "max_latency_ms"
                            ],

                        "measured_jitter_ms":
                            metrics[
                                "jitter_ms"
                            ],

                        "latency_range_ms":
                            metrics[
                                "latency_range_ms"
                            ]
                    }

                    writer.writerow(row)
                    file.flush()

                    print(
                        f"{sample_number:02d} | "
                        f"{state['name']:9s} | "
                        f"Latency: "
                        f"{metrics['avg_latency_ms']:.2f} ms | "
                        f"Jitter: "
                        f"{metrics['jitter_ms']:.2f} ms | "
                        f"Loss: "
                        f"{metrics['packet_loss_percent']:.1f}%"
                    )

                    time.sleep(
                        WAIT_BETWEEN_SAMPLES
                    )

        finally:

            print(
                "\nRestoring normal network..."
            )

            clear_network()

            print(
                "Network shaping cleared."
            )

    print("\n" + "=" * 60)
    print("TRANSITION EXPERIMENT COMPLETE")
    print("=" * 60)

    print(
        f"Total samples collected: "
        f"{sample_number}"
    )

    print(
        f"Saved to: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()
