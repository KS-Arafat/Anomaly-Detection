# Group 02: Project Update Week 07

# Rakibul Hasan Ridoy 1731339042

This week, my primary focus was on advancing the model development phase of our IoT-based anomaly detection project. I successfully implemented and fine-tuned two core models — the Autoencoder (AE) and the One-Class Support Vector Machine (OCSVM) — using the TON-IoT dataset.
For the Autoencoder, I experimented with different neural network architectures by varying the number of layers, neurons, and activation functions to find the optimal balance between reconstruction error and model complexity. The model is currently being evaluated based on the reconstruction error threshold, which determines whether a network traffic instance is normal or anomalous.
In parallel, I developed the One-Class SVM model and tested multiple kernel functions (RBF and linear) along with the ν (nu) hyperparameter to define a clear decision boundary around normal traffic patterns.
Both models are being analysed to identify their individual strengths and weaknesses. The insights from this evaluation will help in integrating them into a hybrid anomaly detection system, capable of detecting zero-day attacks and securing IoT environments even after their end-of-life (EOL) phase.


# Khondokar Sajid – 2211954042

- Implemented **Isolation Forest**, **DBSCAN**, and **LOF** models on the **NSL-KDD** dataset for IoT intrusion detection.  
- Preprocessed data by **label encoding**, **standard scaling**, and **stratified train-test splitting**.  
- Visualized anomaly results using **PCA(2D)** plots highlighting detected outliers.  
- Calculated key metrics — **AUC, Precision, Recall, F1-score**, and **runtime** for fair model comparison.  
- Found that **Isolation Forest** achieved the best balance of accuracy and speed for IoT devices.

# Kazi Safin Arafat - 2211778642

I have implemented Base models using NSL-KDD dataset. Models are trained on numeric attributes and visualized using pie charts. I use RobustScaler to handle the outliers and normalized the dataset. Models include Logistic regression, linear SVM, Decision Tree, KNN, Naïve Bayes. Models are evaluated with metrics like accuracy, precision, recall and confusion matrix. I have use model predict on both test and train data for better understanding.


# MOUSHUMI AKTER - 2021983642
This week, I focused on integrating the results from the One-Class SVM.
The main objective of this week was to compare performance metrics (accuracy, precision, recall, F1-score) among the models and analyze their behavior on normal vs. attack traffic in the TON_IoT dataset.
To achieve this, I implemented a unified evaluation script that loads preprocessed data, trains each model, and computes the key metrics. I also began initial work toward model stacking, where outputs from unsupervised models will serve as input features for a simple supervised classifier (like Logistic Regression) to enhance detection accuracy.
