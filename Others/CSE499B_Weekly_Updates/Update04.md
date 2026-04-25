# Update Report 04

## Reliability and Calibration of ML-based NIDS Under Cross-Dataset Distribution Shift  

**Course:** CSE499B  
**Section:** 15  
**Group:** 02  

---

## Team Members

| Name | ID |
| ------ | ---- |
| Kazi Safin Arafat | 2211778642 |
| Khondokar Sajid | 2211954042 |
| Moushumi Akter Mow | 2021983642 |
| Rakibul Hasan Ridoy | 1731339042 |

---

## Summary

In this phase, we moved from theoretical understanding to full system implementation. We designed and developed a multi-layer intrusion detection framework that integrates phishing detection, network traffic analysis, and a fusion-based decision mechanism.

The system combines URL-based phishing detection with behavioral analysis of encrypted network traffic. A hybrid deep learning architecture was used to learn complex traffic patterns, and a fusion mechanism was introduced to handle conflicting signals between different detection components.

Additionally, real-world mobile traffic data was collected and used to evaluate system performance in practical scenarios. This ensures that the system is not limited to benchmark datasets but can generalize to real environments.

---

## Contributions

### Khondokar Sajid (2211954042)

Implemented the core system pipeline, including phishing detection, network traffic analysis, and deep learning–based feature representation. Developed the hybrid attention-based model to capture complex relationships in network data and designed the fusion mechanism to combine multiple signals into a final decision.

Also handled real-world data collection using mobile traffic (PCAPdroid) and performed testing on both normal and attack-injected scenarios to evaluate system behavior in realistic conditions.

---

### Moushumi Akter Mow (2021983642)

Worked on network dataset preparation and analysis. Conducted detailed exploration of the CICIDS2017 dataset, including feature understanding, cleaning, and preprocessing. Implemented feature selection and scaling techniques and supported preparation of structured data for model training and evaluation.

---

### Rakibul Hasan Ridoy (1731339042)

Assisted in data preprocessing and pipeline setup. Contributed to handling feature transformations, organizing datasets, and supporting the implementation of the network traffic processing workflow. Helped in preparing data for experiments and validation.

---

## Completed Tasks

- Implemented phishing detection model
- Processed and prepared network traffic dataset
- Built hybrid deep learning model for traffic analysis
- Designed fusion-based decision mechanism
- Conducted initial evaluation and validation
- Collected real-world mobile traffic data
- Performed testing on real and synthetic attack scenarios

---

## Tasks in Progress

- Improving model reliability and calibration
- Reducing false positives and false negatives
- Enhancing decision-making under conflicting signals
- Evaluating performance under distribution shift

---

## Future Tasks

- Apply calibration methods (ECE, Brier Score)
- Implement uncertainty-aware decision mechanism
- Perform cross-dataset evaluation
- Improve robustness for real-world deployment
- Final evaluation and research paper preparation

---
