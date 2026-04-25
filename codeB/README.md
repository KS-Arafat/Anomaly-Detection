# CodeB

## Project overview

A small project for IoT zero-day detection with:

- a backend (pi-backend) serving a web UI and ML model,
- an endpoint fuzzing toolkit (Endpoint-Fuzzing) and dataset,
- helper scripts and a top-level setup.

## Repo structure

- README.md — this file
- setup.sh — environment/setup helper (A)
- safenest_setup.sh — Safenest environment/setup helper (B)
- Endpoint-Fuzzing/
  - fuzzing.py — endpoint fuzzing script to generate test inputs (A)
  - fuzzing_results.csv — sample/previous fuzzing output (A)
  - requirements.txt — Python deps for fuzzing (A)
  - dataset/TON_IoT.csv — dataset used for fuzzing/experiments (A)

- test_safenest
  - safenest_test_client.py — Test Safenest with a Balanced Dataset (B)
  - requirements.txt — Python deps for Safenest Test (B)
  - safenest_test_balanced.csv — Dataset for Testing Safenest  (B)

- pi-backend/
  - main.py — backend application (serves API + UI) (A)
  - preprocessor.py — data preprocessing utilities(A)
  - feature_fields.py — feature definitions / mapping used by model (A)
  - requirements.txt — Python deps for backend (A)
  - model/
    - randomforest_model — serialized trained model used by main.py (A)
  - static/ — frontend assets (css, js, images) (A)
  - templates/index.html — web UI (A)

## Quick start

### CSE499A

1. Clone/copy repository and make scripts executable:
     - On Unix: bash setup.sh
     - Or manually create a virtualenv and install deps.

2. Install dependencies
     - For backend:
         - pip install -r pi-backend/requirements.txt
     - For fuzzing:
         - pip install -r Endpoint-Fuzzing/requirements.txt

3. Run the backend (serves UI + inference API)
     - python pi-backend/main.py
     - Open the UI at the address printed by the app (commonly <http://localhost:5000> or similar).

4. Run endpoint fuzzing
     - python Endpoint-Fuzzing/fuzzing.py
     - Results will be saved/printed; sample output available in fuzzing_results.csv.

### CSE499B

1. On Raspberry pi/Linux `curl https://raw.githubusercontent.com/KS-Arafat/Anomaly-Detection/refs/heads/main/codeB/safenest_setup.sh | bash`.
2. After that `cd safenest`.
3. Activate evironment with `source ./.venv/bin/activate`.
4. Then run `python safenest_api.py`.
5. Lastly open browser at url `http://localhost:5000` to get the Dashboard.

## Notes

- The backend loads the model from pi-backend/model/randomforest_model. Replace or retrain the model if needed.
- Use preprocessor.py and feature_fields.py to inspect or adapt preprocessing and features expected by the model.
- The TON_IoT.csv in Endpoint-Fuzzing/dataset is provided as example data; confirm licensing before redistribution.

## Extending / Training

- To retrain: create a training script (not included) that produces a model compatible with feature_fields.py and saves it to pi-backend/model/randomforest_model.
- Update templates/static to change the UI.

## Troubleshooting

- Ensure Python version matches requirements files.
- Check logs printed by pi-backend/main.py for missing model or dependency errors.
