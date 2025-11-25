import numpy as np
import pandas as pd
from tensorflow.keras import layers, models
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

# === Load TON-IoT Dataset ===
df = pd.read_csv("DATA/TON_IoT/ton_iot.csv")

# === Select numeric features only ===
features = df.select_dtypes(include=[np.number]).fillna(0)
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(features)

# === Split data into train and test sets ===
X_train, X_test = train_test_split(X_scaled, test_size=0.2, random_state=42)

# === Build Autoencoder Model ===
input_dim = X_train.shape[1]
encoding_dim = 16

autoencoder = models.Sequential([
    layers.Input(shape=(input_dim,)),
    layers.Dense(64, activation='relu'),
    layers.Dense(32, activation='relu'),
    layers.Dense(encoding_dim, activation='relu'),
    layers.Dense(32, activation='relu'),
    layers.Dense(64, activation='relu'),
    layers.Dense(input_dim, activation='linear')
])

autoencoder.compile(optimizer='adam', loss='mse')
history = autoencoder.fit(
    X_train, X_train,
    epochs=50,
    batch_size=256,
    validation_split=0.1,
    verbose=1
)

# === Calculate reconstruction error ===
reconstructions = autoencoder.predict(X_test)
mse = np.mean(np.square(X_test - reconstructions), axis=1)

# === Determine threshold (95th percentile) ===
threshold = np.percentile(mse, 95)
print("Reconstruction Error Threshold:", threshold)

# === Save model ===
autoencoder.save("RESULTS/models/autoencoder.h5")
np.save("RESULTS/ae_threshold.npy", threshold)
print("Model saved successfully!")
