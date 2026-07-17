WITH params AS (
    SELECT DATE '2016-06-22' AS analysis_date
),

recent_activity AS (
    SELECT
        repo_name,
        COUNT(commit) AS commits_last_30_days
    FROM
        `bigquery-public-data.github_repos.sample_commits`
        CROSS JOIN 
        params p
    WHERE
        DATE(committer.date)
        BETWEEN DATE_SUB(p.analysis_date, INTERVAL 30 DAY)
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
        BETWEEN DATE_SUB(p.analysis_date, INTERVAL 60 DAY)
        AND DATE_SUB(p.analysis_date, INTERVAL 31 DAY)
    GROUP BY repo_name
),

growth_analysis AS (
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
),

contributor_analysis AS (
    SELECT
        repo_name,
        COUNT(DISTINCT author.name) AS contributor_count
    FROM
        `bigquery-public-data.github_repos.sample_commits`
        CROSS JOIN 
        params p
    WHERE
        DATE(committer.date)
        BETWEEN DATE_SUB(p.analysis_date, INTERVAL 30 DAY)
        AND p.analysis_date
    GROUP BY repo_name
)

SELECT
    repo_name,
    commits_last_30_days,
    commits_prev_30_days,
    growth_rate,
    contributor_count,
    CASE
        WHEN commits_prev_30_days IS NULL THEN 'New/Emerging'
        WHEN growth_rate >= 20 THEN 'Growing'
        ELSE 'Stable'
    END AS activity_status,
    ROUND(
        (0.5 * COALESCE(growth_rate, 0)) +
        (0.3 * commits_last_30_days) +
        (0.2 * contributor_count),
        2
    ) AS momentum_score
FROM growth_analysis
JOIN contributor_analysis
USING (repo_name)
ORDER BY momentum_score DESC;
