# An End-to-End System for Reproducibility Assessment of Source Code Repositories via Their Readmes

This repo contains the code for research titled "An End-to-End System for Reproducibility Assessment of Source Code Repositories via Their Readmes" (2023)

**Demo page is available at**: https://repro-der.streamlit.app/

# Content

- [An End-to-End System for Reproducibility Assessment of Source Code Repositories via Their Readmes](#an-end-to-end-system-for-reproducibility-assessment-of-source-code-repositories-via-their-readmes)
- [Content](#content)
- [How to Start?](#how-to-start)
  - [General Installation](#general-installation)
  - [Requirements](#requirements)
- [Project Structure](#project-structure)
  - [Data](#data)
  - [Models](#models)
  - [Notebooks](#notebooks)
  - [End-to-end System](#end-to-end-system)
  - [Util](#util)
- [Training](#training)
- [Evaluation](#evaluation)
- [Results](#results)
  - [Citation](#citation)

# How to Start?

## General Installation

1. Clone the Repo
2. Prepare the data

    1. Data ([download](https://mega.nz/file/5jFiAKoa#cNITq38YDnAyqS3eGzWncJJ7XPfO4FPvYPS5xjQMYqA))
    2. Model ([download](https://mega.nz/file/Eyk0Qa6L#IbLmo7_ZE_1TYyGnH7kM8uSOKkRhbBTGiLkbJiAyRCE))
      - Models are also available at [HuggingFace](https://huggingface.co/kaanakdeniz)

    Download all the data and model from the links provided above, unzip/ unarchive the data, and then copy the `data` ve `model` folders to the main directory in the repo.

3. Make sure you have `Python 3.9.13` installed on your system
4. In order to use the GitHub API, you need to rename the `example.config.ini` file to `config.ini` and enter your api token.
5. Follow the steps specified in [Requirements](#Requirements)

## Requirements

1. Use `pip install poetry` command to install poetry.
2. Install all the necessary using `poetry install` command.
3. Use `poetry shell` command to enter the poetry virtual environment.
4. (_Optional_) Install pytorch-cuda version with `poe install` command to run pytorch over GPU.

    _Note: CUDA must be installed in your system to do this step._
# Project Structure
## Data
1. **acl**:
The directory contains the Readme files corresponding to articles collected from the ACL Anthology site, and the training data composed of these Readme contents.
1. **constants**:
This directory is the repository for the static data utilized during the development process.
1. **paperswithcode**:
This includes the data used during the system's evaluation.
## Models

It is the directory where the pretrained models used in the system are located.
## Notebooks
1. **data-analysis-statistics:**
Data analyses and statistical analysis codes.
2. **data-gathering:**
Data collection process codes.
3. **data-preparation:**
Data preparation process codes.
4. **e2e-system:**
Evaluation of the system codes.
5. **labelling:**
Data labeling and agreement calculation codes.
6. **training:**
Model training codes.

## End-to-end System
The directory where the main code files of the system are located.  You can import the classes here and use them in different codes.

## Util
This directory contains helper classes such as readme parser, github helper.

# Training
In the _notebooks/training_ directory you can find the code for training both the hierarchical and the BERT model. It can be run after editing the data and model paths.

# Evaluation
In the _notebooks/e2e-system_ directory you can find the code for evaluating the system. It can be run after editing the data and model paths.

# Results
Performance results of the system are below.
| **Labelling Method** | **Labelling Content** | **Scoring Type** | **Correlation** | **Agreement** | **Accuracy** |
|---|---|---|---|---|---|
| Text Sim. | Content | Base | 0.549 | 0.521 | 0.665 |
| Text Sim. | Content | Consecutive | 0.554 | 0.521 | 0.665 |
| Text Sim. | Grouped | Base | 0.579 | 0.542 | 0.697 |
| Text Sim. | Grouped | Consecutive | 0.581 | 0.542 | 0.697 |
| Text Sim. | Header + Content | Base | 0.578 | 0.523 | 0.685 |
| Text Sim. | Header + Content | Consecutive | 0.571 | 0.523 | 0.685 |
| Text Sim. | Parent + Header + Content | Base | 0.568 | 0.528 | 0.692 |
| Text Sim. | Parent + Header + Content | Consecutive | 0.569 | 0.528 | 0.692 |
| Text Sim. | Parent + Header | Base | 0.602 | 0.613 | 0.668 |
| Text Sim. | Parent + Header | Consecutive | 0.597 | 0.613 | 0.668 |
| Text Sim. | Header | Base | 0.497 | 0.479 | 0.637 |
| Text Sim. | Header | Consecutive | 0.473 | 0.479 | 0.637 |
| Zero-Shot | Content | Base | 0.582 | 0.563 | 0.662 |
| Zero-Shot | Content | Consecutive | 0.586 | 0.563 | 0.662 |
| Zero-Shot | Grouped | Base | 0.651 | **0.648** | 0.697 |
| Zero-Shot | Grouped | Consecutive | **0.661** | **0.648** | 0.697 |
| Zero-Shot | Header + Content | Base | 0.631 | 0.631 | 0.665 |
| Zero-Shot | Header + Content | Consecutive | 0.626 | 0.631 | 0.665 |
| Zero-Shot | Parent + Header + Content | Base | 0.617 | 0.556 | **0.698** |
| Zero-Shot | Parent + Header + Content | Consecutive | 0.624 | 0.556 | **0.698** |
| Zero-Shot | Parent + Header | Base | 0.594 | 0.540 | 0.608 |
| Zero-Shot | Parent + Header | Consecutive | 0.587 | 0.540 | 0.608 |
| Zero-Shot | Header | Base | 0.399 | 0.419 | 0.587 |
| Zero-Shot | Header | Consecutive | 0.383 | 0.419 | 0.587 |

## Citation

If you find this repository useful in your research, please cite it as below:

```
@misc{akdeniz2023reproder,
      title={An End-to-End System for Reproducibility Assessment of Source Code Repositories via Their Readmes},
      author={Eyüp Kaan Akdeniz and Selma Tekir and Malik Nizar Asad Al Hinnawi},
      year={2023},
      eprint={2310.09634},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```