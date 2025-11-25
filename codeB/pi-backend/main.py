from datetime import datetime
import warnings
from flask import Flask, jsonify, request, render_template
import random
import pandas as pd
import logging
import os
from preprocessor import load_ids_model, preprocess_rows


os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/iot_server.log",
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
)

warnings.filterwarnings("ignore", message="X does not have valid feature names")

model, scaler, feature_names, label_col = load_ids_model("./model/randomforest_model")

app = Flask(__name__)


def generate_sensor_data():
    data = {
        "city": "Dhaka",
        "country": "Bangladesh",
        "date": datetime.now().strftime("%A %d %B %Y"),
        "temperature": round(random.uniform(28.0, 26.0), 1),
        "weather": "Sunny",
        "temp_min": 17,
        "temp_max": 28,
    }
    return data


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/sensor", methods=["GET"])
def sensor():
    data = generate_sensor_data()
    return jsonify(data)


@app.route("/login", methods=["POST"])
def attack_point():
    try:
        data = request.get_json()

        df = pd.DataFrame([data])

        X_scaled = preprocess_rows(df, feature_names, scaler)

        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(X_scaled)[0, 1]
            pred = 1 if proba >= 0.5 else 0
        else:
            pred = model.predict(X_scaled)[0]
            proba = None

        access = "Access Denied" if pred == 1 else "Access Granted"

        # Build response
        response = {
            "prediction": int(pred),
            "access": access,
        }

        if proba is not None:
            response["attack_probability"] = round(float(proba),2)

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    print("Dummy IoT server running on port 5000...")
    app.run(host="0.0.0.0", port=5000)
