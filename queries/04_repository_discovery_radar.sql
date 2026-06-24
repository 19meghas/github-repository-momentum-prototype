With repo_activity AS (
    SELECT
        Repo_name,
author.name as author_name,
DATE(committer.date) as commit_date
            FROM
        `bigquery-public-data.github_repos.sample_commits`
where
    author.name is not null
And
Repo_name is not null
),

Repo_metrics as (
SELECT
    repo_name,
COUNT(*) AS total_commits,
COUNT(DISTINCT author_name) AS contributor_count,
    Countif (
commit_date between date_sub(DATE '2016-06-22',interval 30 day) and DATE '2016-06-22'
) as commits_last_30_days,
Countif (
commit_date between  date_sub(DATE '2016-06-22',interval 60 day) and date_sub(DATE '2016-06-22',interval 31 day)
) as  commits_prev_30_days
FROM repo_activity
group by repo_name
)
Select
repo_name,
Total_commits,
contributor_count,
Commits_last_30_days,
 Commits_prev_30_days,
ROUND(
SAFE_DIVIDE(
            commits_last_30_days - commits_prev_30_days,
            commits_prev_30_days) * 100, 2
    ) AS growth_rate
From
Repo_metrics
ORDER BY growth_rate DESC NULLS LAST;
