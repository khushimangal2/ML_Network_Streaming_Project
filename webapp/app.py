from flask import Flask, render_template_string, send_from_directory, jsonify
import os
import subprocess
import joblib
import pandas as pd
from datetime import datetime

app = Flask(__name__)

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VIDEO_DIR = os.path.join(PROJECT_DIR, "videos", "qualities")

MODEL_PATH = os.path.join(
    PROJECT_DIR,
    "models",
    "network_condition_model.pkl"
)

model = joblib.load(MODEL_PATH)


# ---------------------------------
# Get latency values
# ---------------------------------

def get_latency(host="8.8.8.8", count=5):

    try:
        result = subprocess.run(
            ["ping", "-c", str(count), host],
            capture_output=True,
            text=True
        )

        latency_values = []

        for line in result.stdout.splitlines():

            if "time=" in line:

                latency = line.split("time=")[1].split()[0]

                # Remove possible units
                latency = latency.replace("ms", "")

                latency_values.append(float(latency))

        if len(latency_values) == 0:
            return None

        return latency_values

    except Exception:
        return None


# ---------------------------------
# Collect live network metrics
# ---------------------------------

def collect_network_metrics():

    latency_values = get_latency()

    if latency_values is None:
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
        text=True
    )

    packet_loss = 0.0

    for line in result.stdout.splitlines():

        if "packet loss" in line:

            try:
                packet_loss = float(
                    line.split("%")[0].split()[-1]
                )
            except (ValueError, IndexError):
                packet_loss = 0.0

    return {
        "packet_loss_percent": packet_loss,
        "min_latency_ms": min_latency,
        "avg_latency_ms": avg_latency,
        "max_latency_ms": max_latency,
        "jitter_ms": jitter
    }


# ---------------------------------
# Predict network condition
# ---------------------------------

def predict_network():

    metrics = collect_network_metrics()

    if metrics is None:

        return {
            "prediction": "Unknown",
            "quality": "medium",
            "metrics": {},
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }

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

    try:

        prediction = model.predict(input_data)[0]

    except Exception as error:

        return {
            "prediction": "Prediction Error",
            "quality": "medium",
            "metrics": metrics,
            "error": str(error),
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }

    prediction_text = str(prediction).lower()

    if prediction_text == "good":

        quality = "high"

    elif prediction_text == "moderate":

        quality = "medium"

    else:

        quality = "low"

    return {
        "prediction": str(prediction),
        "quality": quality,
        "metrics": metrics,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }


# ---------------------------------
# Web page
# ---------------------------------

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

    margin-top: 20px;

    text-align: left;

    display: inline-block;

    background: #eeeeee;

    padding: 15px;

    border-radius: 8px;

    min-width: 300px;

}

#refreshButton {

    padding: 10px 20px;

    font-size: 16px;

    cursor: pointer;

    border: none;

    border-radius: 6px;

    background-color: #333;

    color: white;

    margin-top: 10px;

}

#refreshButton:disabled {

    opacity: 0.6;

    cursor: not-allowed;

}

#lastUpdate {

    margin-top: 10px;

    color: #555;

    font-size: 14px;

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


<div id="status">

Starting automatic network monitoring...

</div>


<button id="refreshButton" onclick="manualRefresh()">

Refresh Network Prediction

</button>


<div id="lastUpdate">

Last update: Not available

</div>


<div id="metrics" class="metrics">

Collecting network metrics...

</div>


<video id="videoPlayer" controls>

Your browser does not support the video tag.

</video>


</div>


<script>


let currentQuality = "";

let monitoring = false;

let monitoringInterval = null;



// ---------------------------------
// Analyze network
// ---------------------------------

function analyzeNetwork(showLoading = false) {


    const button =

        document.getElementById("refreshButton");


    if (showLoading) {

        button.disabled = true;

        button.innerText = "Checking Network...";

    }


    fetch("/predict")


    .then(response => {

        if (!response.ok) {

            throw new Error("Server returned an error.");

        }

        return response.json();

    })


    .then(data => {


        document.getElementById("status").innerText =

            "Predicted Network: "

            + data.prediction

            + " → Selected Video: "

            + data.quality.toUpperCase()

            + " QUALITY";


        let metricText =

            "<b>Live Network Metrics</b><br><br>";


        if (Object.keys(data.metrics).length === 0) {

            metricText +=

                "Network metrics unavailable.";

        }


        for (const key in data.metrics) {


            metricText +=

                key

                + ": "

                + Number(data.metrics[key]).toFixed(3)

                + "<br>";

        }


        document.getElementById("metrics").innerHTML =

            metricText;


        document.getElementById("lastUpdate").innerText =

            "Last update: "

            + data.timestamp;


        if (data.quality !== currentQuality) {


            switchVideo(data.quality);


            currentQuality = data.quality;

        }


    })


    .catch(error => {


        document.getElementById("status").innerText =

            "Error collecting network data.";


        document.getElementById("metrics").innerHTML =

            "<b>Error:</b> "

            + error.message;


    })


    .finally(() => {


        if (showLoading) {

            button.disabled = false;

            button.innerText =

                "Refresh Network Prediction";

        }

    });

}



// ---------------------------------
// Manual refresh
// ---------------------------------

function manualRefresh() {

    analyzeNetwork(true);

}



// ---------------------------------
// Switch video quality
// ---------------------------------

function switchVideo(quality) {


    const video =

        document.getElementById("videoPlayer");


    const currentTime =

        video.currentTime;


    const wasPlaying =

        !video.paused;


    video.src =

        "/video/"

        + quality

        + ".mp4";


    video.load();


    video.onloadedmetadata = function() {


        try {

            video.currentTime = currentTime;

        }

        catch (error) {

            console.log(

                "Could not restore video position."

            );

        }


        if (wasPlaying) {

            video.play().catch(

                error => console.log(

                    "Video autoplay was blocked."

                )

            );

        }

    };

}



// ---------------------------------
// Automatic monitoring
// ---------------------------------

function startMonitoring() {


    if (monitoring) {

        return;

    }


    monitoring = true;


    analyzeNetwork();


    monitoringInterval = setInterval(

        analyzeNetwork,

        15000

    );

}


window.onload = startMonitoring;


</script>


</body>

</html>

"""


# ---------------------------------
# Flask routes
# ---------------------------------

@app.route("/")
def home():

    return render_template_string(HTML_PAGE)


@app.route("/predict")
def predict():

    return jsonify(predict_network())


@app.route("/video/<filename>")
def video(filename):

    return send_from_directory(

        VIDEO_DIR,

        filename

    )


# ---------------------------------
# Run application
# ---------------------------------

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=False

    )