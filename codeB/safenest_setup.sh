#!/bin/bash
set -e

echo "Updating packages..."
sudo apt update

echo "Installing required tools..."
sudo apt install -y curl p7zip-full git


if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.bashrc
fi

cd /tmp/

echo "Downloading backend..."
curl -L -o "pi-backend.7z" https://github.com/KS-Arafat/Anomaly-Detection/raw/refs/heads/main/codeB/safenest.7z
echo "Download complete"

USER_HOME=$(eval echo ~${SUDO_USER:-$USER})

echo "Extracting to $USER_HOME..."
7z x /tmp/safenest.7z -o"$USER_HOME/"

cd "$USER_HOME/safenest"

echo "Creating Python 3.12.13 virtual environment..."
uv venv --python 3.12.13

source .venv/bin/activate

python3 -m ensurepip --upgrade

if [ -f requirements.txt ]; then
    pip3 install -r requirements.txt
else
    echo "No requirements.txt found. Skipping dependency install."
fi

echo "Setup complete!"
echo "To start the server:"
echo "python safenest_api.py"
