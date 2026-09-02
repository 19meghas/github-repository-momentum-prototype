# Activity Window Audit

## Issue
The recent activity window used an inclusive range that produced 31 calendar dates, while the previous window contained 30.

## Original intent
Two comparable short-term 30-day windows.

## Existing ranges
The prototype uses a fixed analysis date of `2016-06-22`.

BigQuery validation confirmed that the existing SQL produces:

- Previous period: `2016-04-23` through `2016-05-22` = 30 inclusive calendar dates
- Recent period: `2016-05-23` through `2016-06-22` = 31 inclusive calendar dates

## Corrected ranges
The candidate implementation consistent with the documented 30-day-vs-30-day intent is:

- Previous period: `2016-04-24` through `2016-05-23` = 30 inclusive calendar dates
- Recent period: `2016-05-24` through `2016-06-22` = 30 inclusive calendar dates

## Validation performed
A date-only BigQuery validation was run using `GENERATE_DATE_ARRAY` to independently count the calendar dates included in each current and candidate-corrected window.

The validation confirmed the existing 31-day recent / 30-day previous comparison as an implementation discrepancy.

No production SQL has been modified at this stage.

## Impact
- repositories affected: all six repositories remain in the analysis set; no repository enters or leaves the `>20` recent-commit threshold
- count changes: recent and previous commit counts change for several repositories due to the corrected boundary dates
- growth changes: growth rates change for five repositories with calculable prior-period growth; the largest changes are VS Code (30.90% → 18.02%) and TensorFlow (57.43% → 44.84%)
- ranking changes: none; the normalized momentum ordering remains unchanged
- classification changes: VS Code changes from `Growing` to `Stable`; all other classifications remain unchanged

### Discovery Matrix impact
The corrected activity windows change the underlying numerical growth rates, but the relative growth ordering of the six repositories remains unchanged.

As a result:

- cumulative observed contributor breadth is unchanged
- contributor percentiles are unchanged
- growth percentiles are unchanged
- repository radar scores are unchanged
- Discovery Matrix rankings are unchanged
- Discovery Matrix zones are unchanged
- the median repository radar score remains 50.0

No Discovery Matrix repository changes classification.

## Decision

The activity-window correction is approved.

The existing 31-day recent / 30-day previous implementation is a confirmed implementation error relative to the documented original 30-day-vs-30-day intent.

The approved correction is limited to the affected date-window boundaries. No contributor, bot-handling, scoring, threshold, or Discovery Matrix methodology will be redesigned as part of this fix.

## Files updated
...

## Validation outcome
PASS / FAIL