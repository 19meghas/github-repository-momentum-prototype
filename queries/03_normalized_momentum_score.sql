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
    CROSS JOIN params p
    WHERE
        DATE(committer.date)
        BETWEEN DATE_SUB(p.analysis_date, INTERVAL 30 DAY)
        AND p.analysis_date
    GROUP BY repo_name
),

scoring_base AS (
    SELECT
        g.repo_name,
        g.commits_last_30_days,
        g.commits_prev_30_days,
        g.growth_rate,
        c.contributor_count,
        CASE
            WHEN g.commits_prev_30_days IS NULL THEN 'New/Emerging'
            WHEN g.growth_rate >= 20 THEN 'Growing'
            ELSE 'Stable'
        END AS activity_status,
        MAX(g.growth_rate) OVER () AS max_growth_rate,
        MAX(g.commits_last_30_days) OVER () AS max_commits_last_30_days,
        MAX(c.contributor_count) OVER () AS max_contributor_count
    FROM growth_analysis g
    JOIN contributor_analysis c
    USING (repo_name)
),

score_components AS (
    SELECT
        repo_name,
        commits_last_30_days,
        commits_prev_30_days,
        growth_rate,
        contributor_count,
        activity_status,
        ROUND(
            0.5 * COALESCE(SAFE_DIVIDE(growth_rate, max_growth_rate), 0),
            4
        ) AS growth_component,
        ROUND(
            0.3 * COALESCE(SAFE_DIVIDE(commits_last_30_days, max_commits_last_30_days), 0),
            4
        ) AS recent_activity_component,
        ROUND(
            0.2 * COALESCE(SAFE_DIVIDE(contributor_count, max_contributor_count), 0),
            4
        ) AS contributor_component
    FROM scoring_base
)

SELECT
    repo_name,
    commits_last_30_days,
    commits_prev_30_days,
    growth_rate,
    contributor_count,
    activity_status,
    growth_component,
    recent_activity_component,
    contributor_component,
    ROUND(
        growth_component
        + recent_activity_component
        + contributor_component,
        2
    ) AS momentum_score
FROM score_components
ORDER BY momentum_score DESC;