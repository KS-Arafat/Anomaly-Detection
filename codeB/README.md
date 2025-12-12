# CodeB

## Project overview

A small project for IoT zero-day detection with:

- a backend (pi-backend) serving a web UI and ML model,
- an endpoint fuzzing toolkit (Endpoint-Fuzzing) and dataset,
- helper scripts and a top-level setup.

## Repo structure

- README.md — this file
- setup.sh — environment/setup helper
- Endpoint-Fuzzing/
  - fuzzing.py — endpoint fuzzing script to generate test inputs
  - fuzzing_results.csv — sample/previous fuzzing output
  - requirements.txt — Python deps for fuzzing
  - dataset/TON_IoT.csv — dataset used for fuzzing/experiments
- pi-backend/
  - main.py — backend application (serves API + UI)
  - preprocessor.py — data preprocessing utilities
  - feature_fields.py — feature definitions / mapping used by model
  - requirements.txt — Python deps for backend
  - model/
    - randomforest_model — serialized trained model used by main.py
  - static/ — frontend assets (css, js, images)
  - templates/index.html — web UI

## Quick start

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
