# Machine Learning Approach to Network Intrusion Detection for IoT Devices

This project focuses on creating NIDS model using maching learning and deep learning technques that can run on IoT devices which can enhance the security and reliability of Iots even after EOL.

## Table of Content

- [Machine Learning Approach to Network Intrusion Detection for IoT Devices](#machine-learning-approach-to-network-intrusion-detection-for-iot-devices)
  - [Table of Content](#table-of-content)
  - [Introduction](#introduction)
  - [Datasets](#datasets)
  - [Project Structure](#project-structure)
  - [How to Run](#how-to-run)
    - [Hardware](#hardware)
    - [Software](#software)
  - [Fuzzing](#fuzzing)
  - [Contributors](#contributors)

## Introduction

In this age of tech revolution, we often forget that how many things are connected to internet constantly sending usage metrics to the backend of companies all over the world. From Automated Home system to smart bed we can't comprehend how much IoT devices are we relying on. And that's the problem. Most Iot are cheap electronics stuck together to create a server that controls certain part of our life but these IoTs often comes with no security patch after certain time or EOL. But they are still being used everyday without knowing the potential harm it can cause.

Our target is that to create a AI/ML based NIDS that can work even after the IoT reaches it's EOL.

## Datasets

- [NSL-KDD](https://www.unb.ca/cic/datasets/nsl.html) with 125k(approx.) records, 41 features, only problem is that it has outdated attacks
- [UNSW-NB15](https://research.unsw.edu.au/projects/unsw-nb15-dataset) size 2.5M, 49 records. Quite big but we will trim it according to our need.
- [TON_IoT](https://research.unsw.edu.au/projects/toniot-datasets) contains records for specific type of IoT and contains variety of attack factors to train

## Project Structure

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

## How to Run

### Hardware

Our project is compatible with almost all Raspberry PI models. For our case we are using [Raspberry PI 4B](https://store.roboticsbd.com/raspberry-pi/1076-76-raspberry-pi-4-robotics-bangladesh.html).

### Software

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

## Fuzzing

To attack/test our endpoint, we used our windows host machine powershell

```bash
git clone https://github.com/KS-Arafat/Anomaly-Detection/tree/main
cd .\codeB\Endpoint-Fuzzing\
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

## Contributors

| Name                  |   | ID         |
|:----------------------|---|-----------:|
|   Kazi Safin Arafat   |   | 2211778642 |
|   Khondokar Sajid     |   | 2211954042 |
|   Moushumi Akter Mow  |   | 2021983642 |
|   Rakibul Hasan Ridoy |   | 1731339042 |
