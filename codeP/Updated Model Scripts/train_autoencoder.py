#!/usr/bin/env python3
"""train_autoencoder.py - Train an Autoencoder on TON-IoT numeric features."""
import argparse, os
import numpy as np
import pandas as pd
import joblib
from tensorflow.keras import layers, models, callbacks, optimizers
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

parser = argparse.ArgumentParser()
parser.add_argument('--data', type=str, default='DATA/TON_IoT/ton_iot.csv')
parser.add_argument('--epochs', type=int, default=50)
parser.add_argument('--batch', type=int, default=256)
parser.add_argument('--encoding_dim', type=int, default=16)
parser.add_argument('--hidden', type=str, default='64,32')  # comma separated sizes
parser.add_argument('--activation', type=str, default='relu')
parser.add_argument('--val_size', type=float, default=0.1)
parser.add_argument('--threshold_percentile', type=float, default=95.0)
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
    X_norm = normal_df.select_dtypes(include=['number']).fillna(0)
else:
    X_norm = X.copy()

scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X_norm)
joblib.dump(scaler, 'RESULTS/models/scaler_ae.joblib')

X_train, X_val = train_test_split(X_scaled, test_size=args.val_size, random_state=42)

input_dim = X_train.shape[1]
hidden_sizes = [int(x) for x in args.hidden.split(',') if x.strip()!='']

inp = layers.Input(shape=(input_dim,))
x = inp
for h in hidden_sizes:
    x = layers.Dense(h, activation=args.activation)(x)
latent = layers.Dense(args.encoding_dim, activation=args.activation, name='latent')(x)
x = latent
for h in reversed(hidden_sizes):
    x = layers.Dense(h, activation=args.activation)(x)
out = layers.Dense(input_dim, activation='linear')(x)
ae = models.Model(inputs=inp, outputs=out, name='autoencoder')

ae.compile(optimizer=optimizers.Adam(learning_rate=1e-3), loss='mse')
es = callbacks.EarlyStopping(monitor='val_loss', patience=6, restore_best_weights=True)

ae.fit(X_train, X_train,
       validation_data=(X_val, X_val),
       epochs=args.epochs,
       batch_size=args.batch,
       callbacks=[es],
       verbose=2)

recon_val = ae.predict(X_val)
mse_val = np.mean(np.square(X_val - recon_val), axis=1)
threshold = float(np.percentile(mse_val, args.threshold_percentile))
np.save('RESULTS/ae_threshold.npy', threshold)
ae.save('RESULTS/models/autoencoder.h5')
print(f"Autoencoder trained. Saved to RESULTS/models/autoencoder.h5\nThreshold (percentile {args.threshold_percentile}) = {threshold:.6g}")
