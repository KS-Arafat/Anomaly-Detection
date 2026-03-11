# Proposed Solution

## Reliability and Calibration of ML-based NIDS Under Cross-Dataset Distribution Shift

This project proposes a **shift-aware reliability enhancement framework** for machine learning–based Network Intrusion Detection Systems (ML-NIDS) operating under cross-dataset distribution shift.

Traditional IDS evaluation assumes that training and testing data follow the same distribution. However, real-world network environments often differ due to changes in traffic patterns, devices, and attack behaviors. These differences create **distribution shift**, which can significantly reduce model reliability and lead to overconfident incorrect predictions.

To address this issue, the proposed framework introduces a reliability evaluation and calibration pipeline consisting of several stages.

---

## 1. Baseline Intrusion Detection Model

The system first trains a machine learning classifier using network traffic features extracted from the **CICIDS2017 dataset**.

Before training, the dataset undergoes several preprocessing steps:

- Removing duplicate records
- Handling missing and infinite values
- Converting attack labels into binary format (**Benign vs Attack**)
- Applying feature scaling

After preprocessing, the dataset is split into **training and testing subsets**.  
A **Random Forest classifier** is used as the baseline intrusion detection model to establish initial detection performance.

This model produces prediction probabilities that will later be analyzed for reliability.

---

## 2. Calibration Reliability Evaluation

After training the baseline model, the reliability of its predicted probabilities is evaluated using calibration metrics.

Two key metrics are used:

- **Expected Calibration Error (ECE)** – measures the difference between model confidence and actual prediction accuracy.
- **Brier Score** – measures the squared difference between predicted probabilities and true outcomes.

These metrics help determine whether the model is **overconfident or underconfident** in its predictions.

---

## 3. Post-Hoc Probability Calibration

To improve reliability without retraining the classifier, **post-hoc calibration techniques** are applied.

The project evaluates two calibration methods:

- **Temperature Scaling**
- **Isotonic Regression**

These methods adjust the predicted probabilities so that the model’s confidence better reflects the true likelihood of correct predictions.

---

## 4. Uncertainty-Aware Decision Mechanism

In addition to calibration, the framework introduces an **entropy-based uncertainty detection mechanism**.

If the prediction entropy exceeds a predefined threshold, the system outputs an **UNKNOWN** decision instead of forcing a classification.

This approach helps prevent overconfident misclassifications and improves system safety when the model encounters unfamiliar network traffic.

---

## Proposed System Workflow
Network Traffic Data
↓
Feature Extraction and Preprocessing
↓
Baseline Machine Learning Model
↓
Probability Output
↓
Calibration Layer (Temperature Scaling / Isotonic Regression)
↓
Uncertainty Detection (Entropy-based)
↓
Final Decision (Benign / Attack / UNKNOWN)

---

## Expected Outcome


The proposed framework aims to demonstrate that:

- Cross-dataset deployment increases calibration error in ML-based NIDS.
- Post-hoc calibration techniques reduce model overconfidence.
- Uncertainty-aware decision mechanisms improve system reliability.

Ultimately, the system provides a **lightweight reliability enhancement layer** that can be integrated with existing machine learning–based intrusion detection models without modifying their core architecture.
