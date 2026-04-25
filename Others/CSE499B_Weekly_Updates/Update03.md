# Update Report 03

Reliability and Calibration of ML-based NIDS Under Cross-Dataset Distribution Shift

CSE499B

Section 15

Group 02

| Name                  |   | ID         |
|:----------------------|---|-----------:|
|   Khondokar Sajid     |   | 2211954042 |
|   Kazi Safin Arafat   |   | 2211778642 |
|   Moushumi Akter Mow  |   | 2021983642 |
|   Rakibul Hasan Ridoy |   | 1731339042 |

## Summary

During this reporting period, our team transitioned from dataset exploration to the **implementation stage of the experimental pipeline**.

Key activities completed in this phase include:

- Working with the **CICIDS2017 dataset** to prepare data for machine learning experiments.
- Performing preprocessing steps such as:
  - Removing duplicate records
  - Handling missing values
  - Converting labels to binary format (**Benign vs Attack**)
  - Applying **feature normalization and scaling**

- Splitting the dataset into **training and testing subsets** for model development.

- Implementing a **baseline Random Forest classifier** to establish initial intrusion detection performance.

- Developing initial reliability evaluation tools by implementing calibration metrics:
  - **Expected Calibration Error (ECE)**
  - **Brier Score**

These steps mark the transition from **theoretical planning to practical experimentation**, providing the foundation for evaluating reliability and calibration of ML-based NIDS under cross-dataset distribution shift

---

## Contributions

### Khondokar Sajid (2211954042)

- Focused on the **methodological and evaluation aspects** of the project.
- Implemented initial code for calibration metrics:
  - **Expected Calibration Error (ECE)**
  - **Brier Score**
- Helped design the **experimental evaluation pipeline** to ensure both:
  - classification performance
  - probability reliability  
  are properly measured.

---

### Kazi Safin Arafat (2211778642)

- Worked on **dataset preparation and preprocessing**.
- Performed tasks including:
  - handling missing values
  - verifying dataset consistency
  - applying **feature scaling**
- Assisted with **exploratory data analysis (EDA)** and dataset preparation for model training.

---

### Moushumi Akter Mow (2021983642)

- Assisted in reviewing research materials related to:
  - intrusion detection architectures
  - calibration techniques
- Helped summarize relevant findings from the literature and supported discussions on integrating these techniques into the project framework.

---

### Rakibul Hasan Ridoy (1731339042)

- Supported the literature review on:
  - model reliability
  - uncertainty handling in IDS
- Assisted in organizing references and documenting experimental planning.

---

## Completed Tasks

- Literature review on **reliability and probabilistic calibration** in ML-based NIDS
- Identification of **research gap** related to calibration under cross-dataset distribution shift
- Selection of benchmark dataset (**CICIDS2017**)

### Dataset Preprocessing

- Removal of duplicate records
- Handling missing values
- Label transformation (**Benign vs Attack**)

### Exploratory Data Analysis (EDA)

- Feature distribution inspection
- Correlation analysis among network traffic features
- Visualization of class imbalance

### Feature Preparation

- Normalization and scaling of numerical features
- Preparation of feature matrices for machine learning models

### Model Implementation

- Dataset splitting into **training and testing subsets**
- Implementation of a **baseline Random Forest classifier**
- Verification of model prediction outputs and probability scores

### Calibration Evaluation

- Initial implementation of calibration metrics:
  - **Expected Calibration Error (ECE)**
  - **Brier Score**

---

## Tasks in Progress

- Training baseline machine learning models

### Performance Evaluation

- Generating classification metrics:
  - Accuracy
  - Precision
  - Recall
  - F1-score

- Producing **reliability diagrams** to visualize calibration performance
- Testing calibration metric implementation

---

## Future Tasks

- Conduct **cross-dataset experiments**
- Apply post-hoc calibration methods:
  - Temperature Scaling
  - Isotonic Regression
- Implement **entropy-based uncertainty detection mechanism**
- Evaluate selective accuracy and **UNKNOWN prediction behavior**
- Prepare final experimental analysis and report
