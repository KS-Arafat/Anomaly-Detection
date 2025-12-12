# CodeP

Minimal README for the scripts and notebooks in this folder.

## Overview

Collection of training and evaluation scripts and notebooks for anomaly / zero-day detection experiments (Autoencoder, One-Class SVM, and baseline notebooks).

## Structure

- README.md — this file
- Autoencoder/
  - train_autoencoder.py — train an autoencoder model
  - train_ocsvm.py — train One-Class SVM (in same folder)
- basic_train/
  - NSL_KDD_IoT_Outlier_Compact (1).ipynb — notebook for baseline experiments (NSL-KDD)
  - NSL-KDD_base_models.ipynb — baseline model comparisons
- iot_ide/
  - ton-iot_ide.ipynb — TON‑IoT dataset exploration / experiments
- Updated Model Scripts/
  - train_autoencoder.py — updated autoencoder training script
  - train_ocsvm.py — updated OCSVM training script
  - evaluate_models.py — evaluation utilities and model comparison

## Quick start

1. Create a Python environment (recommended Python 3.7+):
     - python -m venv .venv && source .venv/bin/activate (Linux/macOS) or .venv\Scripts\activate (Windows)
2. Install common dependencies:
     - pip install numpy pandas scikit-learn matplotlib seaborn jupyter
     - If using deep learning scripts, also install one of: tensorflow (pip install tensorflow) or torch (pip install torch torchvision)
3. Run scripts / notebooks:
     - Scripts: python Autoencoder/train_autoencoder.py
     - Evaluation: python "Updated Model Scripts"/evaluate_models.py
     - Notebooks: jupyter notebook basic_train/*.ipynb or iot_ide/ton-iot_ide.ipynb

Note: each script/notebook may expect dataset files and specific CLI arguments. Inspect the top of each .py file or the notebook cells for required arguments, input paths, and hyperparameters.

## Datasets

Examples use NSL-KDD and TON‑IoT datasets. Place raw CSV/NPY files in a data/ or specified path and update paths in scripts or notebooks.

## Outputs

Models, logs, and metrics are saved by the scripts to the working directory or to paths defined in the script. Create an outputs/ or models/ folder if needed.

## Recommendations

- Inspect each script header to confirm dependency versions and CLI arguments.
- Use GPUs when training deep models (TensorFlow/PyTorch).
- Run notebooks interactively for exploratory analysis and visualization.
