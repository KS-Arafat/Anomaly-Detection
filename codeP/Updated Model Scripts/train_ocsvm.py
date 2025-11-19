#!/usr/bin/env python3
"""train_ocsvm.py - Train One-Class SVM on TON-IoT numeric features."""
import argparse, os
import numpy as np
import pandas as pd
import joblib
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler

parser = argparse.ArgumentParser()
parser.add_argument('--data', type=str, default='DATA/TON_IoT/ton_iot.csv')
parser.add_argument('--kernel', type=str, default='rbf', choices=['rbf','linear','poly','sigmoid'])
parser.add_argument('--nu', type=float, default=0.05)
parser.add_argument('--gamma', type=str, default='scale')  # or float
args = parser.parse_args()

os.makedirs('RESULTS/models', exist_ok=True)

if not os.path.exists(args.data):
    raise FileNotFoundError(f"Data file not found: {args.data}")
df = pd.read_csv(args.data)
X = df.select_dtypes(include=['number']).fillna(0)
if X.shape[1] == 0:
    raise ValueError('No numeric features found in dataset.')

label_col = None
for c in ['label','Label','attack','isattack']:
    if c in df.columns:
        label_col = c
        break

if label_col:
    normal_df = df[df[label_col].isin([0,'0','normal','Normal', False])]
    X_train = normal_df.select_dtypes(include=['number']).fillna(0)
else:
    X_train = X.copy()

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_train)
joblib.dump(scaler, 'RESULTS/models/scaler_ocsvm.joblib')

gamma_val = None if args.gamma == 'scale' else float(args.gamma)
ocsvm = OneClassSVM(kernel=args.kernel, nu=args.nu, gamma=gamma_val)
ocsvm.fit(X_scaled)

joblib.dump(ocsvm, 'RESULTS/models/ocsvm_model.joblib')
print(f"OCSVM trained and saved to RESULTS/models/ocsvm_model.joblib (kernel={args.kernel}, nu={args.nu})")
