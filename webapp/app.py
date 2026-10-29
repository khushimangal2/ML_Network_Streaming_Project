
from flask import Flask, render_template_string, send_from_directory, jsonify
import os
import subprocess
import joblib
import pandas as pd
import psutil

app = Flask(__name__)

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEO_DIR = os.path.join(PROJECT_DIR, "videos", "qualities")
MODEL_PATH = os.path.join(PROJECT_DIR, "models", "network_condition_model_v2.pkl")

model = joblib.load(MODEL_PATH)


def get_latency(host="8.8.8.8", count=5):
    try:
        result = subprocess.run(
            ["ping", "-c", str(count), host],
            capture_output=True,
            text=True,
            timeout=20
        )

        latency_values = []

        for line in result.stdout.splitlines():
            if "time=" in line:
                latency = line.split("time=")[1].split()[0]
                latency_values.append(float(latency))

        return latency_values if latency_values else None

    except Exception:
        return None


def collect_network_metrics():
    latency_values = get_latency()

    if not latency_values:
        return None

    min_latency = min(latency_values)
    avg_latency = sum(latency_values) / len(latency_values)
    max_latency = max(latency_values)

    if len(latency_values) > 1:
        jitter = sum(
            abs(latency_values[i] - latency_values[i - 1])
            for i in range(1, len(latency_values))
        ) / (len(latency_values) - 1)
    else:
        jitter = 0.0

    result = subprocess.run(
        ["ping", "-c", "10", "8.8.8.8"],
        capture_output=True,
        text=True,
        timeout=30
    )

    packet_loss = 0.0

    for line in result.stdout.splitlines():
        if "packet loss" in line:
            try:
                packet_loss = float(line.split("%")[0].split()[-1])
            except (ValueError, IndexError):
                pass

    return {
        "packet_loss_percent": packet_loss,
        "min_latency_ms": min_latency,
        "avg_latency_ms": avg_latency,
        "max_latency_ms": max_latency,
        "jitter_ms": jitter
    }


def predict_network():
    try:
        metrics = collect_network_metrics()
    except Exception:
        metrics = None

    if metrics is None:
        return {
            "prediction": "Unknown",
            "quality": "medium",
            "metrics": {}
        }

    input_data = pd.DataFrame([{
        "measured_packet_loss_percent": metrics["packet_loss_percent"],
        "min_latency_ms": metrics["min_latency_ms"],
        "avg_latency_ms": metrics["avg_latency_ms"],
        "max_latency_ms": metrics["max_latency_ms"],
        "measured_jitter_ms": metrics["jitter_ms"]
    }])

    prediction = model.predict(input_data)[0]
    prediction_text = str(prediction).lower()

    if prediction_text == "high":
        quality = "high"
    elif prediction_text == "medium":
        quality = "medium"
    else:
        quality = "low"

    return {
        "prediction": str(prediction),
        "quality": quality,
        "metrics": metrics
    }


def collect_system_metrics():
    cpu_percent = psutil.cpu_percent(interval=0.2)
    memory = psutil.virtual_memory()

    return {
        "cpu_percent": round(cpu_percent, 2),
        "ram_percent": round(memory.percent, 2),
        "ram_used_gb": round(memory.used / (1024 ** 3), 2),
        "ram_available_gb": round(memory.available / (1024 ** 3), 2),
        "ram_total_gb": round(memory.total / (1024 ** 3), 2)
    }


HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>ML Adaptive Video Streaming</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            background-color: #f4f4f4;
            margin: 40px;
        }

        .container {
            background: white;
            padding: 25px;
            border-radius: 10px;
            max-width: 900px;
            margin: auto;
        }

        video {
            width: 55%;
            max-height: 600px;
            margin-top: 20px;
        }

        #status {
            font-size: 22px;
            font-weight: bold;
            margin: 20px;
        }

        .metrics {
            margin: 20px auto;
            text-align: left;
            display: inline-block;
            background: #eeeeee;
            padding: 15px;
            border-radius: 8px;
            min-width: 280px;
            max-width: 100%;
            overflow-wrap: anywhere;
        }

        .section-title {
            font-size: 18px;
            font-weight: bold;
        }
    </style>
</head>

<body>
<div class="container">
    <h1>ML-Based Adaptive Video Streaming System</h1>

    <p>
        Network conditions are monitored automatically and
        video quality changes based on ML prediction.
    </p>

    <div id="status">Starting automatic network monitoring...</div>

    <div id="metrics" class="metrics">
        Collecting network metrics...
    </div>

    <br>

    <div id="systemMetrics" class="metrics">
        <div class="section-title">Live System Metrics</div>
        <p>Collecting CPU and RAM information...</p>
    </div>

    <br>

    <video id="videoPlayer" controls>
        Your browser does not support the video tag.
    </video>
</div>

<script>
let currentQuality = "";
let monitoring = false;

function analyzeNetwork() {
    fetch("/predict")
    .then(response => {
        if (!response.ok) throw new Error("Network request failed");
        return response.json();
    })
    .then(data => {
        document.getElementById("status").innerText =
            "Predicted Network: " + data.prediction +
            " → Selected Video: " + data.quality.toUpperCase() +
            " QUALITY";

        let metricText =
            "<div class='section-title'>Live Network Metrics</div><br>";

        for (const key in data.metrics) {
            metricText += key + ": " +
                Number(data.metrics[key]).toFixed(3) + "<br>";
        }

        document.getElementById("metrics").innerHTML = metricText;

        if (data.quality !== currentQuality) {
            switchVideo(data.quality);
            currentQuality = data.quality;
        }
    })
    .catch(error => {
        document.getElementById("status").innerText =
            "Error collecting network data.";
        console.error(error);
    });
}

function switchVideo(quality) {
    const video = document.getElementById("videoPlayer");
    const currentTime = video.currentTime;
    const wasPlaying = !video.paused;
    const newSource = "/video/" + quality + ".mp4";

    if (video.getAttribute("src") === newSource) {
        return;
    }

    video.onloadedmetadata = null;
    video.onerror = null;

    video.onloadedmetadata = function() {
        video.currentTime = Math.min(
            currentTime,
            Math.max(0, video.duration - 0.1)
        );

        document.getElementById("status").innerText +=
            " — Video loaded: " + quality.toUpperCase();

        if (wasPlaying) {
            video.play().catch(() => {
                console.log("Press play to resume the video.");
            });
        }
    };

    video.onerror = function() {
        console.error("Failed to load video:", newSource);
        document.getElementById("status").innerText +=
            " — Video loading failed";
    };

    video.src = newSource;
    video.load();
}


function updateSystemMetrics() {
    fetch("/system_metrics")
    .then(response => {
        if (!response.ok) throw new Error("System metrics request failed");
        return response.json();
    })
    .then(data => {
        document.getElementById("systemMetrics").innerHTML =
            "<div class='section-title'>Live System Metrics</div>" +
            "<p>CPU Usage: " + data.cpu_percent + "%</p>" +
            "<p>RAM Usage: " + data.ram_percent + "%</p>" +
            "<p>RAM Used: " + data.ram_used_gb + " GB</p>" +
            "<p>RAM Available: " + data.ram_available_gb + " GB</p>" +
            "<p>Total RAM: " + data.ram_total_gb + " GB</p>";
    })
    .catch(error => {
        document.getElementById("systemMetrics").innerHTML =
            "<div class='section-title'>Live System Metrics</div>" +
            "<p>Unable to collect CPU/RAM metrics.</p>";
        console.error(error);
    });
}

function startMonitoring() {
    if (monitoring) return;

    monitoring = true;
    analyzeNetwork();
    updateSystemMetrics();

    setInterval(analyzeNetwork, 15000);
    setInterval(updateSystemMetrics, 5000);
}

window.onload = startMonitoring;
</script>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML_PAGE)


@app.route("/predict")
def predict():
    return jsonify(predict_network())


@app.route("/system_metrics")
def system_metrics():
    return jsonify(collect_system_metrics())


@app.route("/video/<filename>")
def video(filename):
    allowed_videos = {"high.mp4", "medium.mp4", "low.mp4"}

    if filename not in allowed_videos:
        return jsonify({"error": "Video not found"}), 404

    return send_from_directory(VIDEO_DIR, filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

