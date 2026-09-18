from flask import Flask, jsonify, request
import threading

app = Flask(__name__)

lock = threading.Lock()

measurement_state = {
    "status": "idle",
    "experiment_id": None,
    "throughput_mbps": None,
    "download_time_seconds": None
}


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "message": "Throughput controller is running"
    })


@app.route("/request_measurement", methods=["GET"])
def request_measurement():
    experiment_id = request.args.get("experiment_id")

    if not experiment_id:
        return jsonify({
            "status": "error",
            "message": "experiment_id is required"
        }), 400

    with lock:
        measurement_state["status"] = "requested"
        measurement_state["experiment_id"] = experiment_id
        measurement_state["throughput_mbps"] = None
        measurement_state["download_time_seconds"] = None

    print(f"\nMeasurement requested for experiment {experiment_id}")

    return jsonify({
        "status": "requested",
        "experiment_id": experiment_id
    })


@app.route("/get_measurement_request", methods=["GET"])
def get_measurement_request():
    with lock:
        return jsonify({
            "status": measurement_state["status"],
            "experiment_id": measurement_state["experiment_id"]
        })


@app.route("/submit_measurement", methods=["GET"])
def submit_measurement():
    experiment_id = request.args.get("experiment_id")
    throughput = request.args.get("throughput_mbps")
    download_time = request.args.get("download_time_seconds")

    if not experiment_id or throughput is None or download_time is None:
        return jsonify({
            "status": "error",
            "message": "Missing measurement data"
        }), 400

    with lock:
        if str(measurement_state["experiment_id"]) != str(experiment_id):
            return jsonify({
                "status": "error",
                "message": "Experiment ID does not match current experiment"
            }), 409

        measurement_state["status"] = "complete"
        measurement_state["throughput_mbps"] = float(throughput)
        measurement_state["download_time_seconds"] = float(download_time)

    print(
        f"Experiment {experiment_id} complete | "
        f"Throughput: {float(throughput):.3f} Mbps | "
        f"Download time: {float(download_time):.3f} seconds"
    )

    return jsonify({
        "status": "complete",
        "experiment_id": experiment_id,
        "throughput_mbps": float(throughput),
        "download_time_seconds": float(download_time)
    })


@app.route("/get_result", methods=["GET"])
def get_result():
    with lock:
        return jsonify(measurement_state)


@app.route("/reset", methods=["GET"])
def reset():
    with lock:
        measurement_state["status"] = "idle"
        measurement_state["experiment_id"] = None
        measurement_state["throughput_mbps"] = None
        measurement_state["download_time_seconds"] = None

    print("\nController reset.")

    return jsonify({
        "status": "idle"
    })


if __name__ == "__main__":
    print("Starting synchronized throughput controller...")
    print("Waiting for experiment requests...")

    app.run(
        host="0.0.0.0",
        port=5002,
        threaded=True
    )
