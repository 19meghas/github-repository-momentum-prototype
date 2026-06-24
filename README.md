# GitHub Repository Momentum Prototype

## Project Overview

This project analyzes public GitHub repository activity using SQL and Python visualizations to identify repositories showing growth, activity momentum, and normalized engagement patterns.

The project was created as an initial repository-level analytics prototype before expanding into a broader GitHub Technology Radar and Innovation Intelligence project.

The focus of this prototype is repository-level momentum analysis, not technology/topic-level early detection.

---

## Business Problem

GitHub contains millions of repositories, but raw activity alone does not always explain which repositories are gaining momentum.

This project explores how repository activity data can be transformed into interpretable indicators such as:

* recent activity,
* historical activity,
* growth rate,
* contributor participation,
* and normalized momentum.

The goal is to create a simple analytical framework for identifying high-momentum repositories using SQL.

---

## Analytical Framework

The project includes three main analytical layers:

### 1. Repository Growth Analysis

Compares recent repository activity against prior activity to identify repositories with accelerating growth.

Key output:

```text
growth_rate
```

### 2. Repository Momentum Score

Combines repository activity and contributor participation into a momentum score.

Key outputs:

```text
commits_last_30_days
contributor_count
momentum_score
```

### 3. Normalized Momentum Score

Introduces normalization to reduce the risk of large repositories dominating the ranking purely because of scale.

Techniques used:

```text
window functions
SAFE_DIVIDE()
normalization
composite scoring
ranking
```

---

## Tools Used

* Google BigQuery
* SQL
* Python
* Plotly
* GitHub

---

## Project Structure

```text
queries/
├── 01_growth_analysis.sql
├── 02_repository_momentum_score.sql
└── 03_normalized_momentum_score.sql

notebooks/
└── Plotly analysis notebooks or visualization work

docs/
└── assets/
    └── charts/
```

---

## Key Learning Outcome

This project established the first SQL-based framework for analyzing repository activity and momentum.

It later informed a more advanced project focused on early technology detection using GH Archive event data, actor diffusion, automation filtering, and topic-level momentum analysis.

---

## Scope

This project is a repository-level analytics prototype.

It does not attempt to identify emerging technologies or technology topics directly. That broader problem is handled in the separate GitHub Technology Radar and Innovation Intelligence project.
