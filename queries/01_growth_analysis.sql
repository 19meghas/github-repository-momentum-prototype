WITH params AS (
    SELECT DATE '2016-06-22' AS analysis_date
),
recent_activity AS (
    SELECT
        repo_name,
        COUNT(commit) AS commits_last_30_days
    FROM
        `bigquery-public-data.github_repos.sample_commits`
        CROSS JOIN params p
    WHERE
        DATE(committer.date)
        BETWEEN DATE_SUB(p.analysis_date, INTERVAL 29 DAY)
        AND p.analysis_date
    GROUP BY repo_name
),

past_activity AS (
    SELECT
        repo_name,
        COUNT(commit) AS commits_prev_30_days
    FROM
        `bigquery-public-data.github_repos.sample_commits`
        CROSS JOIN params p
    WHERE
        DATE(committer.date)
        BETWEEN DATE_SUB(p.analysis_date, INTERVAL 59 DAY)
        AND DATE_SUB(p.analysis_date, INTERVAL 30 DAY)
    GROUP BY repo_name
)

SELECT
    r.repo_name,
    r.commits_last_30_days,
    p.commits_prev_30_days,
    ROUND(
        SAFE_DIVIDE(
            r.commits_last_30_days - p.commits_prev_30_days,
            p.commits_prev_30_days
        ) * 100,
        2
    ) AS growth_rate
FROM recent_activity r
LEFT JOIN past_activity p
USING (repo_name)
WHERE r.commits_last_30_days > 20
ORDER BY growth_rate DESC NULLS LAST;
