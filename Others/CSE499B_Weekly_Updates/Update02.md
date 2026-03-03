# Update Report 02

Reliability and Calibration of ML-based NIDS Under Cross-Dataset Distribution Shift

CSE499B

Section 15

Group 02

| Name                  |   | ID         |
|:----------------------|---|-----------:|
|   Kazi Safin Arafat   |   | 2211778642 |
|   Khondokar Sajid     |   | 2211954042 |
|   Moushumi Akter Mow  |   | 2021983642 |
|   Rakibul Hasan Ridoy |   | 1731339042 |

## Summary

Over the reporting period, our team made substantive progress on the research project centered on the reliability and calibration of machine learning–based Network Intrusion Detection Systems (ML-NIDS) under cross-dataset distribution shifts. We began by conducting an extensive literature review, reading and synthesizing findings from numerous research papers that explore how distribution shifts affect ML model performance, calibration techniques for reliable uncertainty estimation, and best practices for evaluating NIDS robustness across varying traffic distributions. This review helped us identify key challenges in handling domain shifts and informed our methodological planning.

Following the literature review, we shifted focus to practical dataset work using the CIC-IDS-2017 dataset. We carried out comprehensive preprocessing steps, including cleaning, normalization, feature selection, and appropriate handling of class imbalance. With the preprocessed data, we conducted exploratory data analysis (EDA) to visually inspect patterns, feature distributions, and potential anomalies. Visualization tools such as distribution plots, correlation heatmaps, and class frequency charts were used to better understand the dataset structure and inform downstream modeling decisions.

## Contibutions

### Kazi Safin Arafat (2211778642)

I worked on the dataset preparation and exploratory data analysis phase. My responsibilities included loading and inspecting the dataset structure (rows and columns), performing data cleaning by handling duplicate records and missing values, and preparing the data for analysis. I conducted detailed exploratory analysis using visual techniques, including correlation analysis, heatmaps, and evaluation of linear relationships among numerical features. Additionally, I analyzed relationships involving categorical variables to better understand feature distributions and dependencies. These efforts helped ensure data quality and provided meaningful insights to support subsequent modeling work.

### Khondokar Sajid (2211954042)

I focused on the research and methodological aspects of the project, particularly reliability and calibration of ML-based NIDS. I reviewed key concepts such as Expected Calibration Error (ECE), Brier Score, temperature scaling, and isotonic regression, and helped design the evaluation framework for cross-dataset analysis.
Also, I contributed to the initial implementation of calibration evaluation by writing basic code for computing ECE and Brier Score, ensuring that both performance and probability reliability can be properly measured in our experiments.

### Moushumi Akter Mow (2021983642)

### Rakibul Hasan Ridoy (1731339042)

## Completed Tasks

- Literature review on:

  - ML reliability and probabilistic calibration
  - Calibration metrics (ECE, Brier Score, reliability diagrams)
  - Distribution shift in ML-based NIDS

- Identification of research gap

- Shortlisting of suitable benchmark NIDS datasets

- Drafting preliminary experimental framework

- Detailed analysis of selected dataset structure and features
- Designing preprocessing strategy (encoding, scaling, imbalance handling)
- Selecting appropriate baseline model architecture

## Tasks in Progress

- Implement data preprocessing pipeline
- Train baseline model
- Perform in-domain evaluation

## Future Tasks

- Implement calibration measurement (ECE, Brier Score)
- Conduct cross-dataset evaluation
- Apply recalibration methods
- Perform uncertainty and OOD experiments
- Final analysis and report preparation
