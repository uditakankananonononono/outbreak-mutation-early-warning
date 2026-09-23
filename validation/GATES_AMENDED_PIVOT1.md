# GATES AMENDMENT 1 (pivot) - B18 validation slice

Amended: 2026-09-23 ~22:15 IST. Committed BEFORE any results under the amended rule.
Original gates: validation/GATES_LOCKED.md (commit 209667f). Original failure preserved
in validation/results/validation_results.json (tagged PIVOT-ORIGINAL-FAILURE):
the locked engine flagged 0/3 positive controls. A documented negative alone is not
an acceptable endpoint (user pivot rule), so the detection statistic is amended once,
with the root cause named, and the amended gates locked before the amended test runs.

## Root cause (diagnosed from the preserved failure)

The 6-week slope was fit on log10((count+0.5)/(total+1)) treating weeks below the
LAP IS 0.1% query floor as exact zeros (count=0 -> log ~ -7 anchor). Two effects:
(1) calibration-window noise mutations that cross the floor mid-window get hugely
inflated slopes (fake -7 anchors), so G_MIN (p95 of calibration slopes) = 0.4141
measures floor-crossing artifacts, not biology; (2) true risers observed in all 6
weeks (all three controls are; diagnosis counts recorded in the pivot commit) get
modest true slopes (N501Y ~0.2/wk) and fall below the inflated thresholds.
Below-floor weeks are censored, not zero: fitting them as zeros is an estimator bug.

## Amended estimator (only change)

Slope g is fit on observed weeks only (count>0) among the last 6 visible weeks;
a candidate requires >=4 observed weeks of the last 6. Count/proportion candidacy
filters (count4>=20, p4>=0.001) and the structural score S, alert score A=g*(0.5+S),
dedupe rules, controls, windows, metrics, and pass bars are UNCHANGED from
GATES_LOCKED.md. The calibration procedure is UNCHANGED (same four calibration
freezes 2020-05-31..2020-08-31, G_MIN = p95 of positive candidate slopes under the
amended estimator, THETA = smallest threshold with <=3 alerts per calibration scan,
THETA_G = smallest slope threshold with <=12 total growth-only calibration alerts).
Constants (computed by the locked procedure under the amended estimator, before the
amended test runs): G_MIN = 0.2347, THETA = 0.3525, THETA_G = 0.4663.

## Policy restated

This is the single pivot for this slice. If the amended engine still fails the pass
bar, the failure is reported as the result (no further retuning on test outcomes).
