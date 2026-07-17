# GitHub Repository Momentum Prototype

## Project Overview

This project is an exploratory GitHub repository analytics prototype built with SQL and Python.

It uses public GitHub sample commit data from BigQuery to examine how raw repository activity can be transformed into interpretable indicators such as recent activity, prior activity, growth rate, contributor participation, and normalized momentum.

The goal is not to build a production-grade GitHub ranking system, but to demonstrate how SQL-based feature engineering and Python visualizations can be used to explore repository behavior and surface useful analytical patterns.

---

## Analytical Question

GitHub repositories generate large amounts of activity data, but raw commit counts alone do not always explain which repositories are gaining momentum.

This project explores a simple analytical question:

> How can public GitHub commit data be used to compare repository activity, growth, and contributor participation?

The analysis converts raw commit records into repository-level indicators and uses those indicators to create a simple momentum ranking and discovery view.

---

## Analytical Framework

The project follows a simple SQL-based analytical progression:

### 1. Growth Analysis

Compares recent commit activity with prior-period commit activity to calculate repository growth.

### 2. Repository Momentum Score

Combines recent activity, growth rate, and contributor participation into a simple composite score.

### 3. Normalized Momentum Score

Applies normalization so repositories can be compared more fairly across different levels of activity and scale.

### 4. Repository Discovery View

Uses visual analysis to compare repositories by momentum, contributor base, and activity status.
---

## Tools Used

* Google BigQuery
* SQL
* Python
* Plotly
* GitHub

---




## Dashboard Story

The dashboard is designed as a visual walkthrough of the analysis:

1. Repository Momentum Ranking  
2. Growth vs Contributor Scale  
3. Momentum Score Components  
4. Repository Discovery Radar  
5. Key Insights and Limitations  

The goal is to show how a basic public dataset can be explored, transformed, and interpreted using SQL and Python.

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

## Scope and Limitations

This is a repository-level exploratory analytics prototype.

It focuses on commit activity and contributor participation from a public GitHub sample dataset. It does not include stars, forks, issues, pull requests, topics, bot filtering, or real-time GitHub activity.

The project should be interpreted as a learning and portfolio prototype showing how repository activity data can be transformed into analytical signals.
