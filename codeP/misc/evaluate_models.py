#!/usr/bin/env python3
"""evaluate_models.py - Evaluate saved AE and OCSVM models on dataset (if labels exist)."""
import argparse, os
import numpy as np, pandas as pd, joblib
from sklearn.metrics import precision_recall_fscore_support

parser = argparse.ArgumentParser()
parser.add_argument('--data', type=str, default='DATA/TON_IoT/ton_iot.csv')
parser.add_argument('--ae_model', type=str, default='RESULTS/models/autoencoder.h5')
parser.add_argument('--ocsvm_model', type=str, default='RESULTS/models/ocsvm_model.joblib')
parser.add_argument('--scaler_ae', type=str, default='RESULTS/models/scaler_ae.joblib')
parser.add_argument('--scaler_ocsvm', type=str, default='RESULTS/models/scaler_ocsvm.joblib')
parser.add_argument('--ae_threshold', type=str, default='RESULTS/ae_threshold.npy')
args = parser.parse_args()

if not os.path.exists(args.data):
    raise FileNotFoundError(args.data)
df = pd.read_csv(args.data)
X = df.select_dtypes(include=['number']).fillna(0)
if X.shape[1]==0:
    raise ValueError('No numeric features')

label_col = None
for c in ['label','Label','attack','isattack']:
    if c in df.columns:
        label_col = c; break

y = None
if label_col:
    y_raw = df[label_col].astype(str).str.lower()
    y = (~y_raw.isin(['normal','0','0.0','false','benign'])).astype(int).values

ae_available = os.path.exists(args.ae_model) and os.path.exists(args.scaler_ae) and os.path.exists(args.ae_threshold)
ocsvm_available = os.path.exists(args.ocsvm_model) and os.path.exists(args.scaler_ocsvm)

if ae_available:
    from tensorflow.keras.models import load_model
    ae = load_model(args.ae_model)
    scaler_ae = joblib.load(args.scaler_ae)
    X_ae = scaler_ae.transform(X)
    recon = ae.predict(X_ae)
    mse = np.mean((X_ae - recon)**2, axis=1)
    thresh = float(np.load(args.ae_threshold))
    y_pred_ae = (mse > thresh).astype(int)
    print(f"AE: threshold={thresh:.6g}, anomalies_detected={y_pred_ae.sum()}")
else:
    print("AE artifacts missing, skipping AE evaluation.")

if ocsvm_available:
    ocsvm = joblib.load(args.ocsvm_model)
    scaler_ocsvm = joblib.load(args.scaler_ocsvm)
    X_o = scaler_ocsvm.transform(X)
    pred = ocsvm.predict(X_o)
    y_pred_ocsvm = np.where(pred==-1, 1, 0)
    print(f"OCSVM: anomalies_detected={y_pred_ocsvm.sum()}")
else:
    print("OCSVM artifacts missing, skipping OCSVM evaluation.")

if y is not None:
    print('\nGround-truth labels found. Computing metrics...') 
    results = {}
    if ae_available:
        p,r,f,_ = precision_recall_fscore_support(y, y_pred_ae, average='binary', zero_division=0)
        results['AE'] = (p,r,f)
    if ocsvm_available:
        p,r,f,_ = precision_recall_fscore_support(y, y_pred_ocsvm, average='binary', zero_division=0)
        results['OCSVM'] = (p,r,f)
    for k,(p,r,f) in results.items():
        print(f"{k}: Precision={p:.3f}, Recall={r:.3f}, F1={f:.3f}")