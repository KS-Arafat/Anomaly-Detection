# DATA

## Summary

This folder contains datasets used for zeroday-detection experiments. It includes CSV data files and two subfolders (Training, Testing) with additional README files. Use this document as a practical guide to contents, quick inspection, recommended preprocessing, and suggested evaluation practices.

## Folder structure

- KDDTrain+.csv — primary CSV dataset (training-like file)
- TON_IoT.csv — IoT/network CSV dataset
- Training/README.md — notes specific to training split(s)
- Testing/README.md — notes specific to test split(s)

Open the subfolder READMEs first for any provenance or split-specific details.

## File descriptions

- KDDTrain+.csv
  - Tabular CSV. Typical uses: traffic/connection records, features + label column.
  - Intended as a training/benchmark file; inspect header to confirm exact column names.
- TON_IoT.csv
  - Tabular CSV likely containing IoT telemetry or network flow records. Check header for feature names and label.
- Training/ and Testing/
  - May contain curated splits, metadata, or instructions for reproducing experiments. Follow those files for official splits.

## Quick inspection (Python)

Use these commands to inspect structure and basic stats:

```python
import pandas as pd
df_kdd = pd.read_csv("KDDTrain+.csv")
df_ton = pd.read_csv("TON_IoT.csv")

print(df_kdd.shape); print(df_kdd.columns)
print(df_kdd.head())
print(df_kdd.isna().sum())

print(df_ton.shape); print(df_ton.columns)
print(df_ton.head())
print(df_ton.isna().sum())
```

## Recommended preprocessing

- Validate headers and data types; convert timestamps to datetime if present.
- Handle missing values: impute, drop, or flag depending on column importance.
- Encode categorical features (one-hot, ordinal, target encoding) after inspecting cardinality.
- Normalize/scale numeric features (StandardScaler/MinMax) where appropriate for algorithms.
- Remove exact duplicates and filter corrupted rows.
- Feature engineering: aggregate time-based features, protocol counts, byte-rate features, endpoint summaries.
- Label handling:
  - Confirm label column name and values (binary, multiclass).
  - Consolidate rare classes or map to binary attack/benign labels if required.
- Class imbalance:
  - Use stratified sampling, class weights, oversampling (SMOTE) or undersampling as appropriate.
- Save clean versions (CSV, Parquet) and record preprocessing steps in code or a notebook.

## Suggested experiments and evaluation

- Baselines: Random Forest, XGBoost, Logistic Regression, simple neural nets.
- Time-aware evaluation: if data is time-ordered, reserve later periods for test to simulate deployment.
- Cross-validation: use stratified CV for class-balanced estimates.
- Metrics: precision/recall, F1, ROC-AUC for binary; macro-F1 and per-class recall for multiclass.
- Robustness: test against concept drift (temporal splits), and evaluate false positive rate for production readiness.

## Reproducibility & provenance

- Check Training/README.md and Testing/README.md for dataset origin, preprocessing already applied, split definitions, and citation details.
- If original dataset sources or papers are required for citation or license terms, follow links or references inside the subfolder READMEs.
- Track preprocessing in code and attach a hash/timestamped copy of cleaned datasets used in experiments.

## Practical tips

- Work with column subsets first to speed iteration.
- Use Parquet for large CSVs to speed I/O.
- Version datasets and notebooks in the project repository.
- Keep label-mapping documented to avoid ambiguity in metrics.
