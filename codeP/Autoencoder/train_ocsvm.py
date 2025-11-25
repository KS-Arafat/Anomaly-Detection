import numpy as np
import pandas as pd
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
import joblib

# === Load TON-IoT Dataset ===
df = pd.read_csv("DATA/TON_IoT/ton_iot.csv")

# === Select numeric features only ===
features = df.select_dtypes(include=[np.number]).fillna(0)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(features)

# === Train One-Class SVM ===
ocsvm = OneClassSVM(kernel='rbf', nu=0.05, gamma='scale')
ocsvm.fit(X_scaled)

# === Predict anomalies (-1 = anomaly, 1 = normal) ===
predictions = ocsvm.predict(X_scaled)
predictions = np.where(predictions == -1, 1, 0)  # 1 = anomaly, 0 = normal

# === Save model ===
joblib.dump(ocsvm, "RESULTS/models/ocsvm_model.joblib")
print("OCSVM model trained and saved successfully!")
