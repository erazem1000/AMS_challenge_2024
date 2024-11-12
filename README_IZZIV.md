# AMS_IZZIV_2024

**Author**: Erazem Stonič  
**Period**: 1st Semester, Academic Year 2024/2025  
**Course**: Analiza medicinskih slik (Analysis of Medical Images)  
**Faculty**: Fakulteta za elektrotehniko, Univerza v Ljubljani  
**Mentor**: Dr. Žiga Bizjak, dr. Žiga Špiclin

---

## Project Overview

This project is part of a seminar assignment for the Analysis of Medical Images course. The primary aim is to test the multiGradICON model on a specified dataset to evaluate its performance in multimodal medical image registration. multiGradICON is a deep learning model designed to perform versatile image registration tasks, including both monomodal and multimodal scenarios, which is essential for aligning medical images of various types (e.g., MRI, CT) across different anatomical regions.

### Motivation

Medical image registration is critical for combining information from various imaging modalities, providing comprehensive insights for diagnosis, treatment planning, and research. Conventional methods often require anatomy-specific configurations, while multiGradICON offers a more universal, data-driven approach.

### Objective

The objective of this seminar is to evaluate the performance of multiGradICON on a specific dataset, assessing its accuracy and adaptability in relation to the number of epochas. Evaluate its accuracy in unimodal and multimodal registration tasks and thereby determine its potential for cross-adaptation and universal applicability.

## Methodology

### multiGradICON Model

multiGradICON builds upon the foundational uniGradICON model, extending its capabilities to multimodal registration. It can be achieved by integrating:
- **Multimodal Similarity Measures**: Tailored to handle images of differing appearance via utilising similarity measures depending on image self-similarity, Dice loss computed from image segmentations.
- **Similarity Loss Randomization**: Enhances the model's robustness by randomly selecting modalities during training, facilitating improved generalization across unseen modalities.
- **Comprehensive Dataset Usage**: Incorporates diverse anatomical regions and modalities, promoting robust learning.

### Dataset

For this project, a predefined dataset will be used, containing various imaging modalities that simulate real-world clinical scenarios. This dataset enables an in-depth examination of multiGradICON's strengths and limitations across different types of images and anatomical regions. End goal is to sucessfully register multimodal images of the same anatomical region after determining optimal hyperparameters.
