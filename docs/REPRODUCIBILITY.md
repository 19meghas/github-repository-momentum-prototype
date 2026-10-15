# Reproducibility Notes

This project uses the public BigQuery dataset:

`bigquery-public-data.github_repos.sample_commits`

The analysis uses a fixed analysis date of:

`2016-06-22`

## Suggested Reproduction Order

Run the SQL workflow in sequence:

1. `queries/01_growth_analysis.sql`
2. `queries/02_repository_momentum_score.sql`
3. `queries/03_normalized_momentum_score.sql`
4. `queries/04_repository_discovery_radar.sql`

The resulting processed outputs are used by:

- `notebooks/01_repository_momentum_dashboard.ipynb`
- `app/streamlit_app.py`

Using a fixed analysis date helps keep the prototype internally consistent and makes the analytical logic easier to reproduce and review.

Because the project relies on GitHub's public sample commit dataset, results should be interpreted within the scope and limitations of that sample rather than as complete current GitHub activity.