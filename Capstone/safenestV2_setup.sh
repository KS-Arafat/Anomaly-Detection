#!/bin/bash
set -e

echo "Updating packages..."
sudo apt update

echo "Installing required tools..."
sudo apt install -y curl p7zip-full git

source ~/.bashrc

if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.bashrc
fi

source ~/.bashrc

cd /tmp/

echo "Downloading Safenest Guard backend..."
curl -O https://raw.githubusercontent.com/KS-Arafat/Anomaly-Detection/refs/heads/main/Capstone/Capstone.7z
echo "Download complete"

USER_HOME=$(eval echo ~${SUDO_USER:-$USER})

echo "Extracting to $USER_HOME..."
7z x /tmp/Capstone.7z -o"$USER_HOME/"

cd "$USER_HOME/Capstone"

echo "Creating Python 3.12.13 virtual environment..."
uv venv --python 3.12.13

source .venv/bin/activate

python3 -m ensurepip --upgrade

if [ -f requirements.txt ]; then
   pip3 install -r requirements.txt
else
    echo "No requirements.txt found. Skipping dependency install."
fi

cat > "$USER_HOME/Capstone/.env" <<'EOF'
# DiveMQ
MQTT_HOST=''
MQTT_USER=''
MQTT_PASSWORD=''
MQTT_PORT=
MQTT_TOPIC=''

# Telegram Bot
TELEGRAM_TOKEN=''
TELEGRAM_CHAT_ID=''
EOF

echo ".env file created successfully."
echo "Setup complete!"

echo "To start the server:"
echo "Please fill in the .env file HiveMQTT and Telegram Bot credentials. Then run:"
echo "python safenest_server.py"

