def map_quality(prediction):
    prediction_text = str(prediction).lower()

    if prediction_text == "good":
        return "high"
    elif prediction_text == "moderate":
        return "medium"
    else:
        return "low"


tests = {
    "Good": "high",
    "Moderate": "medium",
    "Poor": "low",
}

for prediction, expected in tests.items():
    actual = map_quality(prediction)
    status = "PASS" if actual == expected else "FAIL"
    print(f"{status}: {prediction} -> {actual}")
