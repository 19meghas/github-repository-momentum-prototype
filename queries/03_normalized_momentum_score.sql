with recent_activity as
(
  select
repo_name,
Count(commit) commits_last_30_days
from
`bigquery-public-data.github_repos.sample_commits`
where
date(committer.date) between date_sub(current_date(),interval 30 day) and current_date()
group by repo_name
),
past_activity as 
(
  select
 repo_name,
Count(commit) commits_prev_30_days
  from
 `bigquery-public-data.github_repos.sample_commits`
  where
  date(committer.date) between  date_sub(current_date(),interval 60 day) and date_sub(current_date(),interval 31 day)
  group by repo_name
),
growth_analysis as
(
select
r.repo_name,
r.commits_last_30_days,
MAX(r.commits_last_30_days) OVER () max_commits_last_30_days,
p.commits_prev_30_days,
round(safe_divide(r.commits_last_30_days-p.commits_prev_30_days,p.commits_prev_30_days)*100,2) growth_rate,
Max(round(safe_divide(r.commits_last_30_days-p.commits_prev_30_days,p.commits_prev_30_days)*100,2)) over() max_growth_rate
from
recent_activity r
left join
past_activity p using (repo_name)
where r.commits_last_30_days>20
),
contributor_analysis as
(
  select
  repo_name,
  count(distinct author.name) contributor_count
  from
`bigquery-public-data.github_repos.sample_commits`
where
date(committer.date) between date_sub(current_date(),interval 30 day) and current_date()
group by repo_name
),
contributor_normalization as
(
  select
  repo_name,
  contributor_count,
  Max(contributor_count) over () max_contributor_count
  from
 contributor_analysis
)
select
repo_name,
commits_last_30_days,
commits_prev_30_days,
growth_rate,
contributor_count,
case
WHEN commits_prev_30_days IS NULL THEN 'New/Emerging'
when
growth_rate>100 then 'Exploding'
when growth_rate between 20 and 100 then 'Growing'
else 'Stable'
end activity_status,
round((0.5*COALESCE(SAFE_DIVIDE(growth_rate,max_growth_rate),0))+(0.3*(SAFE_DIVIDE(commits_last_30_days,max_commits_last_30_days)))+(0.2*SAFE_DIVIDE(contributor_count,max_contributor_count)),2) momentum_score
from
growth_analysis
join
contributor_normalization using (repo_name)
order by momentum_score desc
