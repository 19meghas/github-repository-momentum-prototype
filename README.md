# GitHub Repository Momentum Prototype

A SQL, Python, and Streamlit analytics project for exploring repository-level momentum using public GitHub commit data.

This project transforms raw GitHub commit records into interpretable repository signals, including recent activity, prior-period activity, growth rate, contributor participation, normalized momentum score, and discovery-zone classification.

The goal is not to create a production-grade GitHub ranking system. Instead, this project demonstrates how public developer activity data can be cleaned, modeled, scored, visualized, and interpreted as a portfolio-ready analytics workflow.

---

## Live Dashboard

Explore the interactive Repository Momentum Explorer:

[Launch the Live Streamlit Dashboard](https://repository-momentum-explorer.streamlit.app)

---

## Interactive Dashboard Preview

The Streamlit dashboard provides filter-responsive KPI summaries and four interactive Plotly views built from the finalized repository momentum outputs.

![Interactive Streamlit Dashboard](docs/assets/streamlit/streamlit_dashboard_overview.png)

---


## Analytical Question

GitHub repositories generate large amounts of activity data, but raw commit counts alone do not explain whether a repository is gaining momentum, slowing down, or simply large because of its historical scale.

This project explores the question:

> How can public GitHub commit data be used to compare repository activity, growth, and contributor participation in a more interpretable way?

---

## Project Objective

The project builds a repository-level momentum prototype that:

- compares recent commit activity against prior-period activity,
- calculates repository growth rate,
- measures contributor participation,
- normalizes activity signals for fairer comparison,
- creates a composite momentum score,
- separates repositories into discovery zones,
- and visualizes the results through notebook-based and interactive Streamlit dashboards.

---

## Notebook Analysis Preview

### 1. Repository Momentum Ranking

This chart ranks repositories by normalized momentum score.

![Repository Momentum Ranking](docs/assets/charts/01_repository_momentum_ranking.png)

---

### 2. What Drives Repository Momentum?

This chart compares growth rate, contributor count, and recent activity to explain what is driving each repository’s momentum.

![What Drives Repository Momentum](docs/assets/charts/02_repository_momentum_drivers.png)

---

### 3. Momentum Driver Fingerprint

This heatmap breaks the final momentum score into its underlying components: growth, recent activity, and contributor participation.

![Momentum Driver Fingerprint](docs/assets/charts/03_momentum_driver_fingerprint.png)

---

### 4. Repository Discovery Zone Matrix

This matrix classifies repositories into discovery zones using commit growth rate percentile and observed contributor breadth percentile.

![Repository Discovery Zone Matrix](docs/assets/charts/04_repository_discovery_zone_matrix.png)

---

## Analytical Framework

- **Data source:** `bigquery-public-data.github_repos.sample_commits`
- **Fixed analysis date:** `2016-06-22`

The project follows a staged SQL-based analytical workflow.

### 1. Growth Analysis

Recent repository activity is compared with the previous 30-day period.

The growth rate is calculated as:

```text
(commits_last_30_days - commits_prev_30_days) / commits_prev_30_days
```

This allows the analysis to distinguish repositories that are currently accelerating from repositories that are active but slowing down.

### 2. Repository Momentum Score

The first momentum score combines three signals:

- growth rate,
- recent commit activity,
- recent distinct-contributor count.

This creates a simple composite view of repository momentum rather than relying on raw commit volume alone.

### 3. Normalized Momentum Score

Because raw commit counts and contributor counts can be on very different scales, the project normalizes major score components before combining them.

The normalized score helps compare repositories more fairly across different activity levels.

### 4. Repository Discovery Zone Matrix

The discovery matrix provides a separate analytical lens from the finalized
momentum score.

It compares:

- **Observed contributor breadth percentile** — the relative position of a
  repository based on distinct commit authors represented across the available
  historical sample through the analysis cutoff.
- **Commit growth rate percentile** — the repository's relative recent-growth
  position based on the recent 30-day period versus the preceding 30-day period.

Repositories are classified using 50th-percentile thresholds:

- at or above the 50th percentile on both dimensions → Momentum Leader,
- at or above the 50th percentile on growth and below the 50th percentile on observed contributor breadth → Growing Candidate,
- below the 50th percentile on growth and at or above the 50th percentile on observed contributor breadth → Stable Monitor,
- below the 50th percentile on both dimensions → Watchlist.

This classification is separate from the finalized normalized momentum score.
Charts 1–3 rank and explain repositories using weighted recent growth, recent
activity, and recent contributor breadth, while Chart 4 compares recent growth
with broader observed contributor participation across the available sample history.

For repositories without a usable prior-period baseline, the discovery query
applies an adjusted growth value before percentile ranking. This is why
`twbs/bootstrap` requires cautious interpretation despite appearing in the
Momentum Leader zone.

Observed contributor breadth reflects contributors represented in the public
sample dataset and should not be interpreted as a guaranteed complete lifetime
GitHub contributor count.

---

## Dashboard Story

The notebook prototype and interactive Streamlit dashboard follow the same analytical walkthrough:

1. **Repository Momentum Ranking** — which repositories score highest?
2. **What Drives Repository Momentum?** — is momentum driven by growth, recent contributor breadth, or recent activity?
3. **Momentum Driver Fingerprint** — which score components explain each repository’s position?
4. **Repository Discovery Zone Matrix** — how can repositories be grouped into interpretable discovery zones?

Together, these views move from ranking to explanation to classification.

---

## Tools Used

- Google BigQuery
- SQL
- Python
- Pandas
- Plotly
- Streamlit
- Jupyter Notebook
- GitHub

---

## Project Structure

| Folder / File | Purpose |
|---|---|
| `queries/` | SQL queries used to create repository-level momentum metrics. |
| `queries/01_growth_analysis.sql` | Calculates recent versus prior-period commit growth. |
| `queries/02_repository_momentum_score.sql` | Builds the first composite repository momentum score. |
| `queries/03_normalized_momentum_score.sql` | Normalizes growth, recent activity, and contributor components. |
| `queries/04_repository_discovery_radar.sql` | Creates percentile-based discovery zones for repository classification. |
| `data/README.md` | Notes on data sourcing and why raw datasets are not stored in the repository. |
| `data/processed/` | Final processed CSV outputs used by the notebook and dashboard. |
| `notebooks/01_repository_momentum_dashboard.ipynb` | Notebook-based dashboard prototype built with Python and Plotly. |
| `docs/assets/charts/` | Exported PNG chart assets used in the README and documentation. |
| `app/streamlit_app.py` | Interactive Streamlit dashboard built from the finalized processed CSV outputs. |
| `.streamlit/config.toml` | Streamlit theme and application configuration. |
| `requirements.txt` | Python package dependencies required to run the dashboard. |
| `INSIGHTS.md` | Summary of key analytical insights and project limitations. |

---

## Key Insights

- Raw commit activity alone is not enough to describe repository momentum.
- Growth rate needs context because high growth can result from a small prior-period baseline.
- Contributor participation adds context beyond raw commit volume, while the Discovery Matrix separately uses observed historical contributor breadth as a broader participation signal.
- Normalization makes repositories easier to compare across different activity levels.
- Discovery zones provide an interpretable portfolio-style view of repository activity.


### Selected Findings

- `tensorflow/tensorflow` records the highest finalized normalized momentum
  score in the sample at `0.76`, supported primarily by its strong growth
  component.
- `Microsoft/vscode` ranks second at `0.53`, combining positive growth with
  substantial recent activity.
- `torvalds/linux` has the broadest observed contributor base in the available sample history within the comparison set
- `twbs/bootstrap` is classified as New/Emerging because it lacks a usable
  prior-period baseline. Its Momentum Leader discovery-zone placement partly
  reflects an imputed top growth percentile and should therefore be interpreted
  cautiously.

---

## Scope and Limitations

This is a repository-level exploratory analytics prototype.

It uses public GitHub sample commit data and focuses on commit activity, growth, and contributor participation.

It does not include:

- stars,
- forks,
- issues,
- pull requests,
- topics,
- bot filtering,
- repository metadata,
- or real-time GitHub activity.

The results should be interpreted as an exploratory momentum analysis, not as a production GitHub ranking system or real-time technology trend engine.

---

## Future Improvements

Potential extensions include:

- adding stars, forks, issues, pull requests, and watchers,
- filtering bot and automation activity,
- adding repository topics and metadata,
- expanding the analysis across multiple months,
- tracking consistency and acceleration over time,
- extending the deployed dashboard with broader time-series coverage and additional repository signals.

---

## Current Status

The repository momentum analysis, SQL workflow, notebook prototype, and redesigned interactive Streamlit dashboard are complete.

The dashboard is publicly deployed on Streamlit Community Cloud:

[Launch the Live Streamlit Dashboard](https://repository-momentum-explorer.streamlit.app)

Run the dashboard locally with:

```bash
python -m streamlit run app/streamlit_app.py
```