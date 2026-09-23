# GATES AMENDMENT 2 (pivot) - B18 validation slice

Amended: 2026-09-23 ~22:16 IST. Committed BEFORE any results under the amended rule.
Prior gates: GATES_LOCKED.md (209667f), GATES_AMENDED_PIVOT1.md (47f1a7f). Both prior
failures preserved: results/validation_results.json history (PIVOT-ORIGINAL-FAILURE,
PIVOT1-FAILURE commits).

## Root cause of the pivot-1 failure (diagnosed, preserved)

Under any fixed global threshold on log-proportion slope, calibration on May-Aug 2020
(low-volume era) yields a p95 slope (0.2347) ABOVE the true slopes of the most
consequential risers in the high-volume era (e.g. S:T478K, the defining Delta RBD
mutation, slope 0.224 at 2021-05-31; diagnosis numbers in the pivot-1 failure commit).
Log-proportion slopes are not time-invariant: sequencing volume grew ~100x across the
study period, compressing slopes in later eras. No single global threshold can separate
signal from noise across eras. This non-stationarity is itself a reported finding.

## Amended detection rule (steering the method, per the user pivot rule)

Detection becomes era-normalized ranking WITHIN each scan:
- candidacy filters unchanged (count4>=20, p4>=0.001, >=4 of 6 observed weeks, g>0);
- per-scan robust z-score of the alert score: z_A = (A - median(A)) / (1.4826*MAD(A))
  over that scan's candidate set; flag if z_A >= Z;
- Z is derived ONLY from the calibration window by the unchanged budget rule:
  smallest Z such that each of the four calibration scans (2020-05-31..2020-08-31)
  yields <=3 alerts. Growth-only comparator: same per-scan z on g, threshold Z_G,
  budget <=12 total alerts across calibration scans;
- structural score S, alert A = g*(0.5+S), controls, windows, dedupe, metrics and
  pass bars unchanged from GATES_LOCKED.md.
Constants (from calibration scans under this rule, before the amended test runs):
Z = 6.6, Z_G = 4.8.

## Policy

This is the final methodological pivot for this slice. Whatever the amended test
returns is reported as the result, including failure.
