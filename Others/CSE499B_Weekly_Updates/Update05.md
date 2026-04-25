# Update Report 05

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

## Contributions

### Khondokar Sajid (2211954042)

I worked on final system model design with different approaches and selected ECAFN .It is the full fusion engine that combines phishing probability (pp), network anomaly score (ap), and the 12-dim context using ReliabilityMLP + CrossAttentionFusion + DST .
1.CATF -- Context-Aware Threat Fusion
2.CGF -- CrossGated Fusion (or CrossAttentionFusion)
3.ECAFN -- Evidence Context Aware Fusion Network

---

### Kazi Safi  Arafat (2211778642)

I contributed to the development of a network logging system by designing and implementing a frontend interface integrated with a Python-based backend. The backend was powered by a Network Intrusion Detection System (NIDS) model that we trained to identify and analyze suspicious network activity in real time. In addition, I configured and deployed the system on a Raspberry Pi, ensuring efficient performance in a resource-constrained environment. This involved optimizing the runtime setup, managing dependencies, and validating the end-to-end pipeline from data capture to visualization. The overall system provides a compact, scalable solution for monitoring network traffic and detecting potential threats.

---

### Moushumi Akter Mow (2021983642)

  I Contributed to reviewing and improving the feature processing pipeline, including the generation and handling of embeddings from the model. Actively assisted in analyzing anomaly detection outputs, ensuring a clear and reliable distinction between known and unknown attack samples. Verified the correctness and consistency of input feature scaling and feature selection processes to maintain data quality and model performance. Additionally, supported debugging efforts by identifying and helping resolve issues during implementation, and participated in thorough result checking and validation to ensure the overall reliability and accuracy of the system.

### Rakibul Hasan Ridoy (1731339042)

"This week, I moved from pipeline construction to active data deployment. I focused on integrating the preprocessed datasets into the model environment and validating the end-to-end flow of the network traffic workflow. By running initial baseline experiments, I verified that the feature transformations are functioning as intended and identified key areas in the pipeline for further performance optimization.Additionally,refined the data loading process to handle high-volume traffic datasets, significantly reducing preprocessing latency.

---

## Completed Tasks

---
