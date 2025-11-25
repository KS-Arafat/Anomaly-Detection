import sys
import pandas as pd
import requests
import json
import time
import random

API_URL = "http://localhost:5000/login"
Dataset_PATH = "./dataset/TON_IoT.csv"


def send_row_to_api(row_dict):
    """Send row and return the API response."""
    response = requests.post(
        API_URL,
        data=json.dumps(row_dict),
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        return response.json()  
    else:
        print("Error:", response.text)
        return {"prediction": None}


def simulate_normal_traffic(df, min_delay=0.5, max_delay=2.0):
    predictions = []
    true_labels = []

    for i in range(len(df)):
        row_series = df.iloc[i]
        row_dict = row_series.to_dict()

        print(f"\nSending row {i+1}/{len(df)} ...")

        response = send_row_to_api(row_dict)
        pred = response.get("prediction")  
        true = row_series["label"]  

        predictions.append(pred)
        true_labels.append(true)

        print(f"\tModel predicted: {pred} | True label: {true}")

        delay = random.uniform(min_delay, max_delay)
        print(f"\tPausing for {delay:.2f} seconds...\n")
        time.sleep(delay)

    return predictions, true_labels


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <number>")
        sys.exit(1)

    try:
        req_n = int(sys.argv[1])
        print(f"Using {req_n} fuzzing samples.")
    except ValueError:
        print("Please provide a valid integer")
        sys.exit(1)

    df = pd.read_csv(Dataset_PATH)

    df_sample = df.sample(n=req_n, random_state=420)

    preds, trues = simulate_normal_traffic(df_sample)

   
    results_df = pd.DataFrame({
        "true_label": trues,
        "prediction": preds
    })

   
    clean_df = results_df.dropna()

    accuracy = (clean_df["true_label"] == clean_df["prediction"]).mean() * 100

    print("\nFUZZING SUMMARY")
    print(clean_df)
    print(f"\n🎯 Prediction Accuracy: {accuracy:.2f}%")

    clean_df.to_csv("fuzzing_results.csv", index=False)
    print("Saved results to fuzzing_results.csv")
