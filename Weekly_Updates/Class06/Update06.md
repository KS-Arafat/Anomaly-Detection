# Group 02: Project Update Week 06

## Khondokar Sajid 2211954042

This week, I focused on implementing and testing different anomaly detection methods for IoT network data using the TON-IoT dataset.
I applied the Isolation Forest algorithm for efficient outlier detection and experimented with DBSCAN clustering to identify dense attack regions.
Additionally, I explored the Local Outlier Factor (LOF) method to compare neighborhood-based anomaly detection performance.
These experiments will guide the selection of the most accurate and lightweight model for IoT intrusion detection.

## Rakibul Hasan Ridoy 1731339042

This week, my focus was on advancing the model development pillar of our project. I successfully implemented and began fine-tuning the Autoencoder (AE) and One-Class SVM (OCSVM) models using the TON-IoT dataset.
For the Autoencoder, I experimented with different architectures (varying the number of layers and neurons) to find the optimal balance between reconstruction error and model complexity. I'm currently evaluating its performance based on the reconstruction error threshold for classifying anomalies.

## Moushumi Akter Mow 2021983642

This week,i focused For the One-Class SVM, I tested different kernels (like RBF and linear) and tuned hyperparameters such as nu to effectively define the boundary around normal network traffic. These experiments are crucial as they provide the initial performance baselines for two key components of our proposed hybrid system. My next step is to consolidate these results with my group members findings on Isolation Forest and DBSCAN to inform our model selection for the final hybrid pipeline
