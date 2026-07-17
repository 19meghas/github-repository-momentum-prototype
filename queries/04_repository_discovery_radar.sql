WITH params AS (
    SELECT DATE '2016-06-22' AS analysis_date
),

repo_activity AS (
    SELECT
        repo_name,
        author.name AS author_name,
        DATE(committer.date) AS commit_date
    FROM
        `bigquery-public-data.github_repos.sample_commits`
    WHERE
        author.name IS NOT NULL
        AND repo_name IS NOT NULL
),

repo_metrics AS (
    SELECT
        repo_name,
        COUNT(*) AS total_commits,
        COUNT(DISTINCT author_name) AS contributor_count,
        COUNTIF(
            commit_date BETWEEN DATE_SUB(p.analysis_date, INTERVAL 30 DAY)
            AND p.analysis_date
        ) AS commits_last_30_days,
        COUNTIF(
            commit_date BETWEEN DATE_SUB(p.analysis_date, INTERVAL 60 DAY)
            AND DATE_SUB(p.analysis_date, INTERVAL 31 DAY)
        ) AS commits_prev_30_days
    FROM repo_activity
    CROSS JOIN params p
    GROUP BY repo_name
),

growth_metrics AS (
    SELECT
        repo_name,
        total_commits,
        contributor_count,
        commits_last_30_days,
        commits_prev_30_days,
        ROUND(
            SAFE_DIVIDE(
                commits_last_30_days - commits_prev_30_days,
                commits_prev_30_days
            ) * 100,
            2
        ) AS growth_rate
    FROM repo_metrics
),

adjusted_metrics AS (
    SELECT
        repo_name,
        total_commits,
        contributor_count,
        LOG10(contributor_count) AS log_contributor_count,
        commits_last_30_days,
        commits_prev_30_days,
        growth_rate,
        CASE
            WHEN commits_prev_30_days = 0
                AND commits_last_30_days > 0
            THEN 100.0
            ELSE growth_rate
        END AS adjusted_growth_rate
    FROM growth_metrics
),

repository_percentiles AS (
    SELECT
        repo_name,
        total_commits,
        contributor_count,
        log_contributor_count,
        commits_last_30_days,
        commits_prev_30_days,
        growth_rate,
        adjusted_growth_rate,
        PERCENT_RANK() OVER (
            ORDER BY log_contributor_count
        ) AS contributor_percentile,
        PERCENT_RANK() OVER (
            ORDER BY adjusted_growth_rate
        ) AS growth_percentile
    FROM adjusted_metrics
),

repo_radar_scoring AS (
    SELECT
        repo_name,
        total_commits,
        contributor_count,
        log_contributor_count,
        commits_last_30_days,
        commits_prev_30_days,
        growth_rate,
        adjusted_growth_rate,
        growth_percentile,
        contributor_percentile,
        ROUND(
            0.5 * (growth_percentile + contributor_percentile) * 100,
            2
        ) AS repository_radar_score
    FROM repository_percentiles
),

radar_reference_values AS (
    SELECT
        APPROX_QUANTILES(log_contributor_count, 2)[OFFSET(1)]
            AS median_log_contributor_count,
        APPROX_QUANTILES(repository_radar_score, 2)[OFFSET(1)]
            AS median_repository_radar_score
    FROM repo_radar_scoring
)

SELECT
    r.repo_name,
    r.total_commits,
    r.contributor_count,
    r.log_contributor_count,
    r.commits_last_30_days,
    r.commits_prev_30_days,
    r.growth_rate,
    r.adjusted_growth_rate,
    r.growth_percentile,
    r.contributor_percentile,
    r.repository_radar_score,
    v.median_log_contributor_count,
    v.median_repository_radar_score,
    CASE
        WHEN r.growth_percentile >= 0.5
            AND r.contributor_percentile >= 0.5
        THEN 'Momentum Leader'

        WHEN r.growth_percentile >= 0.5
            AND r.contributor_percentile < 0.5
        THEN 'Growing Candidate'

        WHEN r.growth_percentile < 0.5
            AND r.contributor_percentile >= 0.5
        THEN 'Stable Monitor'

        ELSE 'Watchlist'
    END AS radar_zone
FROM repo_radar_scoring r
CROSS JOIN radar_reference_values v
ORDER BY r.repository_radar_score DESC NULLS LAST;