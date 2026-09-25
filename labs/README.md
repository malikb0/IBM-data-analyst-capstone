# Course Labs — IBM Data Analyst Professional Certificate

These are the completed lab notebooks from the **IBM Data Analyst Professional
Certificate** (Coursera). They record how the skills used in the capstone were learned.

> **Attribution:** the lab instructions, starter templates and course datasets belong to
> IBM/Coursera. These notebooks are **not** covered by this repository's MIT license —
> see [`../NOTICE.md`](../NOTICE.md) §2 and §3. This is independent coursework, not an
> official IBM/Coursera repository.

```text
labs/
├── notebooks/   # 26 completed lab notebooks
└── data/        # small sample files the labs read (public samples only)
```

## Contents

### Data collection & wrangling

| # | Notebook | Topic |
|---|---|---|
| 0 | `0 PY0101EN-5.ipynb` | Python basics |
| 1 | `1 Collecting_Jobs_data_Using_API-Questions.ipynb` | APIs |
| 2 | `2 Jobs_API.ipynb` | APIs |
| 3 | `3 Web-Scraping-Review-Lab-v1.ipynb` | Web scraping |
| 4 | `4 Web-Scraping-Lab.ipynb` | Web scraping |
| 5 | `5 M1ExploreDataSet-lab-V2-v1.ipynb` | Exploratory data analysis |
| 6 | `6 Hands-on Lab- Finding Duplicates-v2-v1.ipynb` | Data cleaning |
| 7 | `7 Hands-on Lab 7- Removing Duplicates-v2-v1.jupyterlite.ipynb` | Data cleaning |
| 8 | `8 Hands-on Lab 8 - Finding Missing Values-v1.ipynb` | Data cleaning |
| 9 | `9 Hands-on Lab 9 - Imput Missing Values-v1.ipynb` | Data cleaning |
| 10 | `10 Hands-on Lab 10 - Normalizing Data-v1.ipynb` | Data wrangling |
| 11 | `11 M2DataWrangling-lab-v2-v1.ipynb` | Data wrangling |

### Exploratory analysis & statistics

| # | Notebook | Topic |
|---|---|---|
| 12 | `12 Hands-on Lab 11 - Exploratory Data Analysis-v1.ipynb` | EDA |
| 13 | `13 Lab 11 - Finding How The Data is Distributed-v1.ipynb` | Statistics |
| 14 | `14_Lab_12_Finding_Outliers_Refactored.ipynb` | Statistics |
| 15 | `15 Lab 13 - Finding Correlation-v1.ipynb` | Statistics |

### Visualization

| # | Notebook | Topic |
|---|---|---|
| 16 | `16 Lab  - Data Visualization-v1.ipynb` | Visualization |
| 17 | `17 Lab 14 - Data Visualization-v1.ipynb` | Visualization |
| 17-A | `17-A Lab 14 - Data Visualization-v1.ipynb` | Visualization |
| 18 | `18 Lab 15 -Box Plot-v1.ipynb` | Visualization |
| 19 | `19 Lab 16 -Scatter Plot-v1.ipynb` | Visualization |
| 20 | `20 Lab 17 - Bubble Plots-v1.ipynb` | Visualization |
| 21 | `21 Lab 18 - Pie Charts-v1.ipynb` | Visualization |
| 22 | `22 Lab 19 - Stacked Charts-v1.ipynb` | Visualization |
| 23 | `23 Lab 20 - Line Charts-v1.ipynb` | Visualization |
| 24 | `24 Lab 21 - Bar-v1.ipynb` | Visualization |

## Supporting data (`labs/data/`)

| File | Used by |
|---|---|
| `astros.json` | NASA APOD API lesson |
| `jobs.json`, `job-postings.xlsx` | Jobs API lesson |
| `popular-languages.csv`, `popular-languages.xlsx` | Visualization labs |
| `survey_data-for-visualization-labs.csv`, `12_modified_survey_data.csv` | Visualization labs |
| `sample-promt.md` | Working notes for the labs |

The larger survey extracts are kept local and git-ignored; only small public samples are
committed.

## A note on running these

These are historical lab artifacts, not part of the reproducible pipeline in the
repository root. Some cells fetch data from the course CDN, so a few notebooks need
network access to run unmodified. They are committed **with outputs stripped** to keep
the repository small. For the reproducible analysis, use the root
[`README.md`](../README.md) and `make demo`.
