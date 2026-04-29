<p align="center">
    <picture>
      <source media="(prefers-color-scheme: dark)">
      <img src="https://raw.githubusercontent.com/KS-Arafat/Anomaly-Detection/main/Poster/Anomaly%20Detection%20of%20IoT%20Devices.png" width="100%">
    </picture>
</p>

# CSE 499: Senior Project Design

This project focuses on creating NIDS model using maching learning and deep learning technques that can run on IoT devices which can enhance the security and reliability of Iots even after EOL. This research investigates the trustworthiness of ML-based Network Intrusion Detection Systems (NIDS) when they encounter unseen network traffic patterns. While traditional metrics like accuracy and F1-score suggest high performance, they often mask a model's tendency to be "overconfident" even when making incorrect predictions. By evaluating Model Calibration alongside standard performance metrics, this project aims to quantify the true reliability of NIDS in dynamic, heterogeneous environments. The goal is to move beyond simple detection rates and ensure that when an AI system flags a threat, security analysts can trust the probability score attached to it.

## Table of Content

- [CSE499A: Senior Project Design I](.)
  - [Machine Learning Approach to Network Intrusion Detection for IoT Devices](#cse499a-machine-learning-approach-to-network-intrusion-detection-for-iot-devices)
    - [Introduction](#introduction---a)
    - [Datasets](#datasets---a)
    - [Project Structure](#project-structure---a)
    - [How to Run](#how-to-run---a)
      - [Hardware](#hardware---a)
      - [Software](#software---a)
    - [Fuzzing](#fuzzing---a)
    - [Contributors](#contributors---a)
- [CSE499B: Senior Project Dsign II](#cse499b-reliability-and-calibration-of-ml-based-nids-under-cross-dataset-distribution-shift)
  - [Reliability and Calibration of ML-based NIDS Under Cross-Dataset Distribution Shift](#cse499b-reliability-and-calibration-of-ml-based-nids-under-cross-dataset-distribution-shift)
    - [Introduction](#introduction---b)

## CSE499A: Machine Learning Approach to Network Intrusion Detection for IoT Devices

## Introduction - A

In this age of tech revolution, we often forget that how many things are connected to internet constantly sending usage metrics to the backend of companies all over the world. From Automated Home system to smart bed we can't comprehend how much IoT devices are we relying on. And that's the problem. Most Iot are cheap electronics stuck together to create a server that controls certain part of our life but these IoTs often comes with no security patch after certain time or EOL. But they are still being used everyday without knowing the potential harm it can cause.

Our target is that to create a AI/ML based NIDS that can work even after the IoT reaches it's EOL.

## Datasets - A

- [NSL-KDD](https://www.unb.ca/cic/datasets/nsl.html) with 125k(approx.) records, 41 features, only problem is that it has outdated attacks
- [UNSW-NB15](https://research.unsw.edu.au/projects/unsw-nb15-dataset) size 2.5M, 49 records. Quite big but we will trim it according to our need.
- [TON_IoT](https://research.unsw.edu.au/projects/toniot-datasets) contains records for specific type of IoT and contains variety of attack factors to train

## Project Structure - A

```bash
Project 
│
├── codeP   [All the python Code]
│
├── codeB   [Shell scripts]
│
├── DATA    [Contains Datasets]
│   │
│   ├── Training    [Training Set]
│   │
│   └── Testing     [Test Set]
│
├── .gitignore
│
├── RESULTS [Final Outcome]
│
└── Others
    │
    ├── Weekly_Updates  [Contains Weekly Updates]
    │   │
    │   └──Class(01,02,03,...)
    │
    └── Presentations, Videos, Proposals, Reports, Misc.
```

## How to Run - A

### Hardware - A

Our project is compatible with almost all Raspberry PI models. For our case we are using [Raspberry PI 4B](https://store.roboticsbd.com/raspberry-pi/1076-76-raspberry-pi-4-robotics-bangladesh.html).

### Software - A

First ssh into Pi with/out GUI. We are using Raspberry PI OS Lite x64. After ssh into it, make sure it has internet access for modules to install.

```bash
sudo apt update
curl -O https://raw.githubusercontent.com/KS-Arafat/Anomaly-Detection/refs/heads/main/codeB/setup.sh
chmod +x ./setup.sh
sudo ./setup.sh
python ./main.py
```

This will get the setup srcipt and install all the necessary packages for our project.

This will also create Venv for our python environment.

If the script doesn't work first time, then

```bash
source ~/.barhrc
sudo ./setup.sh
python ./main.py
```

Hopefully it will work

## Fuzzing - A

To attack/test our endpoint, we used our windows host machine powershell

```bash
git clone https://github.com/KS-Arafat/Anomaly-Detection/tree/main
cd .\Anomaly-Detection\codeB\Endpoint-Fuzzing\
python -m venv .venv
./.venv/scripts/activate.ps1
python -m ensurepip --upgrade
pip3 install -r ./requirements.txt
```

After we can test our endpoint with desired amount of attacks,

```bash
python .\fuzzing.py [Number of Attacks]
```

And Done.

## Contributors - A

| Name                  |   | ID         |
|:----------------------|---|-----------:|
|   Kazi Safin Arafat   |   | 2211778642 |
|   Khondokar Sajid     |   | 2211954042 |
|   Moushumi Akter Mow  |   | 2021983642 |
|   Rakibul Hasan Ridoy |   | 1731339042 |

## CSE499B: Reliability and Calibration of ML-based NIDS Under Cross-Dataset Distribution Shift

## Introduction - B

Beyond classification accuracy we did in CSE499A, another critical yet often overlooked aspect is model calibration, which measures how well the predicted confidence scores reflect the true likelihood of correctness. Poor calibration can lead to overconfident predictions, making ML-based NIDS unreliable in security-critical applications where trustworthiness is essential.

This project investigates the reliability and calibration of ML-based Network Intrusion Detection Systems under cross-dataset distribution shift. Specifically, models are trained on one dataset and evaluated on different datasets to simulate real-world deployment conditions. The study evaluates both performance metrics (Accuracy, Precision, Recall, F1-Score, ROC-AUC) and calibration metrics such as Expected Calibration Error (ECE) and Brier Score. Additionally, calibration techniques including Temperature Scaling, Platt Scaling, and Isotonic Regression are applied to analyze their effectiveness in improving model reliability.

The goal of this project is to provide a comprehensive analysis of how distribution shift affects ML-based NIDS and to identify methods that improve their trustworthiness and robustness in real-world cybersecurity environments.
