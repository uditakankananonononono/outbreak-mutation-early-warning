# GATES_AMENDED_1 - B16 scanner slice

Filed 2026-10-10 00:30 IST BEFORE any scanner results, per the amendment rule in
GATES_LOCKED.md section 0/5. No scan outputs have been computed yet.

Ambiguity found while reading the validation slice: GATES_LOCKED.md S1 named
"validation/code/engine.py" as the reference engine. The committed B18 results
(validation/results/validation_results.json) were produced by
validation/code/engine_fast.py (numpy port) run through
validation/code/run_validation.py, which applies the GATES_AMENDED_PIVOT1
estimator (observed weeks only, >=4 of 6) and the GATES_AMENDED_PIVOT2 per-scan
robust z-score alert rule (Z=6.6 weighted on A, Z_G=4.8 growth-only on g),
superseding the original g_min/THETA threshold rule. engine.py alone would NOT
reproduce the committed results.

Amendment (clarification, not a loosening): S1/S4 ground truth = the FINAL
amended reference pipeline, i.e. engine_fast.FastEngine + run_validation.py's
z-filter, as evidenced by the committed validation_results.json. The scanner
module must reproduce THAT behavior exactly. The frozen constants G_MIN/THETA/
THETA_G remain locked and untouched (they fed the superseded threshold rule;
the z-rule constants Z=6.6/Z_G=4.8 come from the committed PIVOT2 amendment and
are likewise frozen - no retuning).

Everything else in GATES_LOCKED.md stands unchanged.
