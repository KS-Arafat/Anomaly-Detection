#!/bin/bash
set -e  # Exit on error

sudo apt update

cd /tmp/

curl -L -o "pi-backend.7z" https://github.com/KS-Arafat/Anomaly-Detection/raw/refs/heads/main/codeB/pi-backend.7z
echo "Pi Backend Download Done"

7z x /tmp/pi-backend.7z -o/home/safin/

if command -v git &> /dev/null; then
    echo "git is installed"
else
    echo "git is NOT installed"
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi



uv python install 3.11.13

source ~/.bashrc

cd /home/safin/pi-backend

uv venv --python 3.11.13


source .venv/bin/activate

 if [ -f requirements.txt ]; then
     python -m ensurepip --upgrade
     source .venv/bin/activate
     pip3 install -r requirements.txt
 else
     echo "No requirements.txt found. Skipping dependency installation."
 fi

echo "✅ Python 3.11.13 virtual environment setup complete!"
cd /home/safin/pi-backend
echo "To start the server"
echo "python ./main.py"

