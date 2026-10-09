# B16 reproduce report (S1/S2/S3/S4) - run 2026-10-10 00:33 IST, run once

Locked gates: scanner/GATES_LOCKED.md (00:25 IST) + GATES_AMENDED_1.md (00:30 IST),
both committed before any scanner output. Data: pinned LAPIS open v2 snapshot
dataVersion 1790179197 (byte-locked 2026-09-23; staleness by design - the slice
targets the locked estimand, not live surveillance).

## S1 REPRODUCE-DETECTION: PASS
Module (scanner/code/scan.py) vs committed B18 reference outputs
(validation/results/validation_results.json): all 21 month-end freezes
2020-01-31..2021-09-30 compared field-level - weighted alert lists (mutation +
slope) and growth-only alert counts. 0 mismatches
(scanner/results/reproduce_gate.json, verbatim).

## S2 SCORER AGREEMENT: PASS
22/22 flagged spike SUBSTITUTIONS: module S == B17 scoring/code/score.py base S
(scoring/results path, exit 0, 0 mismatches; scanner/results/s2_scorer_agreement.json).
4 flagged spike DELETIONS (S:E156-, S:F157-, S:K310-, S:Y144-) are outside B17's
CLI contract (its parser requires GENE:RefPosAlt amino-acid alt, exit 2); the
module scores them with the same locked formula as the reference engine
(S = 0.0, 0.0, 0.1, 0.35). Documented, not patched.

## S3 CLI CONTRACT: PASS
scanner/tool/omew_scan.py:
- scan --freeze 2020-10-31 -> exit 0, 407 candidates, weighted alerts led by
  S:E484K (g 0.1893, S 0.75, A 0.2366).
- score --mutations S:E484K,S:N501Y -> exit 0, S 0.75 / 0.4 via B17 passthrough.
- Malformed inputs rejected BEFORE acceptance, exit 2 each: "S:501", ":N501Y",
  "n501y", "S:N501"; bad date "31-10-2020" -> exit 2.

## S4 MODULE SELF-CHECK: PASS
Control first-flags agree with committed B18 catch_test exactly:
- S:D614G: module null, reference null (honest negative, preserved).
- S:N501Y: module 2020-10-31, reference 2020-10-31 (48 days before recognition).
- S:L452R: module null, reference null (honest negative, preserved).
This is agreement-with-reference only; it re-claims none of B18's validation.

## Calibration-freeze informational scans
2020-05-31..2020-08-31 weighted alert counts: see reproduce_gate.json
(constants derive from these scans; module agreement here is informational).
