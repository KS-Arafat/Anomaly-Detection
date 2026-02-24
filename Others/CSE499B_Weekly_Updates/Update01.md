# Update Report 01

CSE499B

Section 15

Group 03

| Name                  |   | ID         |
|:----------------------|---|-----------:|
|   Kazi Safin Arafat   |   | 2211778642 |
|   Khondokar Sajid     |   | 2211954042 |
|   Moushumi Akter Mow  |   | 2021983642 |
|   Rakibul Hasan Ridoy |   | 1731339042 |

## Summary

On the first day of the project, we focused on establishing the research foundation for studying reliability and calibration in ML-based Network Intrusion Detection Systems (NIDS). We conducted an initial literature review covering calibration techniques (such as Expected Calibration Error and Brier Score), reliability analysis, and the impact of distribution shift in intrusion detection models. We also explored commonly used benchmark NIDS datasets and identified potential candidates for experimentation. Based on the review, we clarified the research gap—most existing NIDS works prioritize classification performance while overlooking probabilistic calibration and robustness under cross-dataset conditions. A preliminary experimental roadmap has been outlined in alignment with the project timeline.

## Contibutions

### Kazi Safin Arafat (2211778642)

I conducted the primary and most extensive portion of the literature review. This included systematically analyzing recent research papers on reliability in machine learning, calibration techniques (such as Expected Calibration Error and Brier Score), and distribution shift challenges in ML-based NIDS. I identified the core research gap—namely the lack of focus on probabilistic calibration in intrusion detection systems—and structured the overall research direction. Additionally, the experimental roadmap and alignment with the proposed timeline were defined under their coordination.

### Khondokar Sajid (2211954042)

I supported the literature review by reviewing supplementary papers related to calibration methods and uncertainty estimation techniques. They summarized key methodologies used in prior studies and compared evaluation metrics adopted in different NIDS research works. I also helped in organizing references and consolidating insights to support the identification of the research gap.

### Moushumi Akter Mow (2021983642)

I contributed by exploring and comparing benchmark NIDS datasets, examining dataset characteristics such as feature types, class distribution, and attack categories. They documented dataset specifications and assessed their suitability for cross-dataset evaluation. Their contribution supported the dataset selection process.

### Rakibul Hasan Ridoy (1731339042)

I assisted in gathering supporting materials related to distribution shift and cross-domain evaluation in machine learning. They compiled notes on common experimental practices in NIDS research and helped organize the preliminary experimental framework documentation. Their work contributed to structuring the foundation for the next implementation phase.

## Completed Tasks

- Literature review on:

  - ML reliability and probabilistic calibration
  - Calibration metrics (ECE, Brier Score, reliability diagrams)
  - Distribution shift in ML-based NIDS

- Identification of research gap

- Shortlisting of suitable benchmark NIDS datasets

- Drafting preliminary experimental framework

## Tasks in Progress

- Detailed analysis of selected dataset structure and features
- Designing preprocessing strategy (encoding, scaling, imbalance handling)
- Selecting appropriate baseline model architecture

## Future Tasks

- Implement data preprocessing pipeline
- Train baseline model
- Perform in-domain evaluation
- Implement calibration measurement (ECE, Brier Score)
- Conduct cross-dataset evaluation
- Apply recalibration methods
- Perform uncertainty and OOD experiments
- Final analysis and report preparation
