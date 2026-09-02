-- ============================================================
-- Activity Window Audit
-- github-repository-momentum-prototype
--
-- Purpose:
-- Compare the existing 31-date recent / 30-date previous
-- implementation against the documented 30-day / 30-day intent.
--
-- Production Queries 01-04 were not modified during validation.
-- ============================================================


-- ============================================================
-- 1. DATE-WINDOW VALIDATION
-- ============================================================

WITH params AS (
  SELECT DATE '2016-06-22' AS analysis_date
),

windows AS (
  SELECT
    'current' AS logic_version,
    'recent' AS period,
    DATE_SUB(analysis_date, INTERVAL 30 DAY) AS start_date,
    analysis_date AS end_date
  FROM params

  UNION ALL

  SELECT
    'current',
    'previous',
    DATE_SUB(analysis_date, INTERVAL 60 DAY),
    DATE_SUB(analysis_date, INTERVAL 31 DAY)
  FROM params

  UNION ALL

  SELECT
    'corrected_candidate',
    'recent',
    DATE_SUB(analysis_date, INTERVAL 29 DAY),
    analysis_date
  FROM params

  UNION ALL

  SELECT
    'corrected_candidate',
    'previous',
    DATE_SUB(analysis_date, INTERVAL 59 DAY),
    DATE_SUB(analysis_date, INTERVAL 30 DAY)
  FROM params
)

SELECT
  logic_version,
  period,
  start_date,
  end_date,
  ARRAY_LENGTH(
    GENERATE_DATE_ARRAY(start_date, end_date)
  ) AS included_calendar_dates
FROM windows
ORDER BY
  logic_version,
  CASE period
    WHEN 'previous' THEN 1
    WHEN 'recent' THEN 2
  END;


-- ============================================================
-- 2. QUERY 03 NORMALIZED MOMENTUM IMPACT VALIDATION
-- ============================================================

WITH params AS (
    SELECT DATE '2016-06-22' AS analysis_date
),

window_definitions AS (
    SELECT
        'current' AS logic_version,
        DATE_SUB(analysis_date, INTERVAL 30 DAY) AS recent_start,
        analysis_date AS recent_end,
        DATE_SUB(analysis_date, INTERVAL 60 DAY) AS previous_start,
        DATE_SUB(analysis_date, INTERVAL 31 DAY) AS previous_end
    FROM params

    UNION ALL

    SELECT
        'corrected_candidate',
        DATE_SUB(analysis_date, INTERVAL 29 DAY),
        analysis_date,
        DATE_SUB(analysis_date, INTERVAL 59 DAY),
        DATE_SUB(analysis_date, INTERVAL 30 DAY)
    FROM params
),

recent_activity AS (
    SELECT
        w.logic_version,
        c.repo_name,
        COUNT(c.commit) AS commits_last_30_days
    FROM
        `bigquery-public-data.github_repos.sample_commits` c
    CROSS JOIN window_definitions w
    WHERE
        DATE(c.committer.date)
        BETWEEN w.recent_start AND w.recent_end
    GROUP BY
        w.logic_version,
        c.repo_name
),

past_activity AS (
    SELECT
        w.logic_version,
        c.repo_name,
        COUNT(c.commit) AS commits_prev_30_days
    FROM
        `bigquery-public-data.github_repos.sample_commits` c
    CROSS JOIN window_definitions w
    WHERE
        DATE(c.committer.date)
        BETWEEN w.previous_start AND w.previous_end
    GROUP BY
        w.logic_version,
        c.repo_name
),

growth_analysis AS (
    SELECT
        r.logic_version,
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
        ON r.logic_version = p.logic_version
       AND r.repo_name = p.repo_name
    WHERE
        r.commits_last_30_days > 20
),

contributor_analysis AS (
    SELECT
        w.logic_version,
        c.repo_name,
        COUNT(DISTINCT c.author.name) AS contributor_count
    FROM
        `bigquery-public-data.github_repos.sample_commits` c
    CROSS JOIN window_definitions w
    WHERE
        DATE(c.committer.date)
        BETWEEN w.recent_start AND w.recent_end
    GROUP BY
        w.logic_version,
        c.repo_name
),

scoring_base AS (
    SELECT
        g.logic_version,
        g.repo_name,
        g.commits_last_30_days,
        g.commits_prev_30_days,
        g.growth_rate,
        c.contributor_count,

        CASE
            WHEN g.commits_prev_30_days IS NULL
                THEN 'New/Emerging'
            WHEN g.growth_rate >= 20
                THEN 'Growing'
            ELSE 'Stable'
        END AS activity_status,

        MAX(g.growth_rate) OVER (
            PARTITION BY g.logic_version
        ) AS max_growth_rate,

        MAX(g.commits_last_30_days) OVER (
            PARTITION BY g.logic_version
        ) AS max_commits_last_30_days,

        MAX(c.contributor_count) OVER (
            PARTITION BY g.logic_version
        ) AS max_contributor_count

    FROM growth_analysis g
    JOIN contributor_analysis c
        ON g.logic_version = c.logic_version
       AND g.repo_name = c.repo_name
),

score_components AS (
    SELECT
        logic_version,
        repo_name,
        commits_last_30_days,
        commits_prev_30_days,
        growth_rate,
        contributor_count,
        activity_status,

        ROUND(
            0.5 * COALESCE(
                SAFE_DIVIDE(growth_rate, max_growth_rate),
                0
            ),
            4
        ) AS growth_component,

        ROUND(
            0.3 * COALESCE(
                SAFE_DIVIDE(
                    commits_last_30_days,
                    max_commits_last_30_days
                ),
                0
            ),
            4
        ) AS recent_activity_component,

        ROUND(
            0.2 * COALESCE(
                SAFE_DIVIDE(
                    contributor_count,
                    max_contributor_count
                ),
                0
            ),
            4
        ) AS contributor_component

    FROM scoring_base
),

scored AS (
    SELECT
        *,
        ROUND(
            growth_component
            + recent_activity_component
            + contributor_component,
            2
        ) AS momentum_score
    FROM score_components
),

ranked AS (
    SELECT
        *,
        RANK() OVER (
            PARTITION BY logic_version
            ORDER BY momentum_score DESC
        ) AS validation_rank
    FROM scored
),

current_logic AS (
    SELECT *
    FROM ranked
    WHERE logic_version = 'current'
),

corrected_logic AS (
    SELECT *
    FROM ranked
    WHERE logic_version = 'corrected_candidate'
)

SELECT
    COALESCE(c.repo_name, n.repo_name) AS repo_name,

    c.contributor_count
        AS current_contributor_count,

    n.contributor_count
        AS corrected_contributor_count,

    c.activity_status
        AS current_activity_status,

    n.activity_status
        AS corrected_activity_status,

    c.momentum_score
        AS current_momentum_score,

    n.momentum_score
        AS corrected_momentum_score,

    n.momentum_score - c.momentum_score
        AS momentum_score_delta,

    c.validation_rank
        AS current_rank,

    n.validation_rank
        AS corrected_rank,

    c.validation_rank - n.validation_rank
        AS rank_change,

    c.activity_status IS DISTINCT FROM n.activity_status
        AS classification_changed

FROM current_logic c

FULL OUTER JOIN corrected_logic n
    USING (repo_name)

ORDER BY
    corrected_rank,
    current_rank,
    repo_name;

-- ============================================================
-- 3. QUERY 04 DISCOVERY MATRIX IMPACT VALIDATION
-- ============================================================

WITH params AS (
    SELECT DATE '2016-06-22' AS analysis_date
),

window_definitions AS (
    SELECT
        'current' AS logic_version,
        DATE_SUB(analysis_date, INTERVAL 30 DAY) AS recent_start,
        analysis_date AS recent_end,
        DATE_SUB(analysis_date, INTERVAL 60 DAY) AS previous_start,
        DATE_SUB(analysis_date, INTERVAL 31 DAY) AS previous_end
    FROM params

    UNION ALL

    SELECT
        'corrected_candidate',
        DATE_SUB(analysis_date, INTERVAL 29 DAY),
        analysis_date,
        DATE_SUB(analysis_date, INTERVAL 59 DAY),
        DATE_SUB(analysis_date, INTERVAL 30 DAY)
    FROM params
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
        w.logic_version,
        a.repo_name,

        COUNT(*) AS total_commits,

        -- Intentionally cumulative observed contributor breadth
        COUNT(DISTINCT a.author_name) AS contributor_count,

        COUNTIF(
            a.commit_date
            BETWEEN w.recent_start AND w.recent_end
        ) AS commits_last_30_days,

        COUNTIF(
            a.commit_date
            BETWEEN w.previous_start AND w.previous_end
        ) AS commits_prev_30_days

    FROM repo_activity a
    CROSS JOIN window_definitions w

    GROUP BY
        w.logic_version,
        a.repo_name
),

growth_metrics AS (
    SELECT
        *,
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
        *,
        LOG10(contributor_count) AS log_contributor_count,

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
        *,

        PERCENT_RANK() OVER (
            PARTITION BY logic_version
            ORDER BY log_contributor_count
        ) AS contributor_percentile,

        PERCENT_RANK() OVER (
            PARTITION BY logic_version
            ORDER BY adjusted_growth_rate
        ) AS growth_percentile

    FROM adjusted_metrics
),

repo_radar_scoring AS (
    SELECT
        *,

        ROUND(
            0.5
            * (growth_percentile + contributor_percentile)
            * 100,
            2
        ) AS repository_radar_score

    FROM repository_percentiles
),

radar_reference_values AS (
    SELECT
        logic_version,

        APPROX_QUANTILES(
            log_contributor_count, 2
        )[OFFSET(1)] AS median_log_contributor_count,

        APPROX_QUANTILES(
            repository_radar_score, 2
        )[OFFSET(1)] AS median_repository_radar_score

    FROM repo_radar_scoring

    GROUP BY logic_version
),

classified AS (
    SELECT
        r.*,
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

    JOIN radar_reference_values v
        USING (logic_version)
),

ranked AS (
    SELECT
        *,

        RANK() OVER (
            PARTITION BY logic_version
            ORDER BY repository_radar_score DESC
        ) AS validation_rank

    FROM classified
),

current_logic AS (
    SELECT *
    FROM ranked
    WHERE logic_version = 'current'
),

corrected_logic AS (
    SELECT *
    FROM ranked
    WHERE logic_version = 'corrected_candidate'
)

SELECT
    c.repo_name,

    -- These should remain identical
    c.total_commits,
    c.contributor_count,

    c.contributor_percentile
        AS current_contributor_percentile,

    n.contributor_percentile
        AS corrected_contributor_percentile,

    -- Window-dependent metrics
    c.growth_rate
        AS current_growth_rate,

    n.growth_rate
        AS corrected_growth_rate,

    c.adjusted_growth_rate
        AS current_adjusted_growth_rate,

    n.adjusted_growth_rate
        AS corrected_adjusted_growth_rate,

    c.growth_percentile
        AS current_growth_percentile,

    n.growth_percentile
        AS corrected_growth_percentile,

    -- Final Discovery Matrix score
    c.repository_radar_score
        AS current_radar_score,

    n.repository_radar_score
        AS corrected_radar_score,

    n.repository_radar_score
        - c.repository_radar_score
        AS radar_score_delta,

    -- Ordering
    c.validation_rank
        AS current_rank,

    n.validation_rank
        AS corrected_rank,

    c.validation_rank
        - n.validation_rank
        AS rank_change,

    -- Zone
    c.radar_zone
        AS current_radar_zone,

    n.radar_zone
        AS corrected_radar_zone,

    c.radar_zone IS DISTINCT FROM n.radar_zone
        AS radar_zone_changed,

    -- Reference value
    c.median_repository_radar_score
        AS current_median_radar_score,

    n.median_repository_radar_score
        AS corrected_median_radar_score

FROM current_logic c

JOIN corrected_logic n
    USING (repo_name)

ORDER BY
    corrected_rank,
    repo_name;