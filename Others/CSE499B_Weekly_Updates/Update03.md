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

Summary

During this reporting period, our team moved from dataset exploration to the implementation stage of the experimental pipeline. We worked with the CICIDS2017 dataset, performing preprocessing steps such as cleaning duplicate records, handling missing values, transforming labels into binary format (Benign vs Attack), and applying feature scaling to prepare the data for machine learning models.

After preprocessing, the dataset was divided into training and testing subsets. A baseline Random Forest classifier was implemented to establish initial intrusion detection performance. In addition, we started implementing reliability evaluation metrics such as Expected Calibration Error (ECE) and Brier Score to measure how well the model’s predicted probabilities reflect actual prediction correctness.

This phase represents the transition from theoretical planning to practical experimentation and establishes the foundation for reliability evaluation in the later stages of the project.

Contributions
Khondokar Sajid (2211954042)

I focused on the methodological and evaluation aspects of the project. I implemented initial code for calculating calibration metrics such as Expected Calibration Error (ECE) and Brier Score. I also helped structure the experimental evaluation pipeline to ensure that both classification performance and reliability metrics are properly measured.

Kazi Safin Arafat (2211778642)

I worked on dataset preparation and preprocessing tasks. This included handling missing values, verifying dataset consistency, and applying feature scaling techniques. I also assisted in preparing the dataset for baseline model training and conducting exploratory data analysis.

Moushumi Akter Mow (2021983642)

I assisted in reviewing additional research materials related to intrusion detection architectures and calibration techniques. I contributed to summarizing relevant findings from the literature and supporting discussions on how these methods relate to our project framework.

Rakibul Hasan Ridoy (1731339042)

I supported the literature review process by analyzing research papers related to model reliability and uncertainty in intrusion detection systems. I also helped organize references and contributed to documenting the experimental planning process.

Completed Tasks

Literature review on reliability and probabilistic calibration in ML-based intrusion detection systems

Identification of research gap related to calibration under cross-dataset distribution shift

Selection of benchmark dataset for experimentation (CICIDS2017)

Dataset Preprocessing

Removal of duplicate records

Handling missing values

Label transformation (Benign vs Attack)

Exploratory Data Analysis (EDA)

Feature distribution inspection

Correlation analysis among network traffic features

Visualization of class imbalance

Feature Preparation

Normalization and scaling of numerical features

Preparation of feature matrices for machine learning models

Model Implementation

Dataset splitting into training and testing subsets

Implementation of a baseline Random Forest classifier

Verification of model prediction outputs and probability scores

Calibration Evaluation

Initial implementation of calibration metrics:

Expected Calibration Error (ECE)

Brier Score

Tasks in Progress

Training baseline machine learning models

Generating classification performance metrics:

Accuracy

Precision

Recall

F1-score

Producing reliability diagrams to visualize calibration performance

Testing calibration metric implementation

Future Tasks

Conduct cross-dataset experiments

Apply post-hoc calibration methods:

Temperature Scaling

Isotonic Regression

Implement entropy-based uncertainty detection mechanism

Evaluate selective accuracy and UNKNOWN prediction behavior

Prepare final experimental analysis and report
