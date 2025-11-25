import joblib
import pandas as pd
import numpy as np


def load_ids_model(path: str):
    saved = joblib.load(path)
    model = saved["model"]
    scaler = saved["scaler"]
    feature_names = saved["feature_names"]
    label_col = saved["label_col"]
    return model, scaler, feature_names, label_col


def preprocess_rows(df: pd.DataFrame, feature_names, scaler):
    for col in ["label", "class", "Label", "Class", "attack", "target"]:
        if col in df.columns:
            df = df.drop(columns=[col])

    df = df.select_dtypes(include=[np.number]).fillna(0)

    for col in feature_names:
        if col not in df.columns:
            df[col] = 0.0

    df = df[feature_names]
    X_scaled = scaler.transform(df.values)
    return X_scaled
