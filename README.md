# Machine Learning Approach to Network Intrusion Detection for IoT Devices

This project focuses on creating NIDS model using maching learning and deep learning technques that can run on IoT devices which can enhance the security and reliability of Iots even after EOL.

## Table of Content

- [Introduction](#introduction)
- [Datasets](#datasets)
- [Project Structure](#project-structure)
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
└── Weekly_Updates  [Contains Weekly Updates]
    │
    └──Class(01,02,03,...)
```

## Contributors

| Name                  |   | ID         |
|:----------------------|---|-----------:|
|   Kazi Safin Arafat   |   | 2211778642 |
|   Khondokar Sajid     |   | 2211954042 |
|   Moushumi Akter Mow  |   | 2021983642 |
|   Rakibul Hasan Ridoy |   | 1731339042 |
