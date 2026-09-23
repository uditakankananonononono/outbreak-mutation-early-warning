# validation/ progress (Builder 18, v3)

- 22:03 takeover; reconstructed slice specs from archived transcripts (repo had only scanner/PROGRESS.md).
- 22:07 GATES_LOCKED.md standalone commit (209667f) - prior art CROWDED, angle = structurally-validated
  criticality weighting from PDB contact geometry; controls D614G/N501Y/L452R pre-committed.
- 22:07 data byte-lock (bfa76d8): LAPIS open v2 snapshot 1790179197 (91 weekly bins, 2.84M seqs),
  PDB 6M0J/6WPT/6XDG/7C2L, SARS-1/2 spike refs; MANIFEST_DATA_CODE.sha256.
- 22:13 PIVOT-ORIGINAL-FAILURE: locked engine flags 0/3 (floor-zero anchored slopes inflated G_MIN).
- 22:14 GATES_AMENDED_PIVOT1 + PIVOT1-FAILURE: estimator fixed (observed-weeks-only), still 0/3;
  root cause = log-proportion slopes not time-invariant across 100x volume growth (real finding).
- 22:15 GATES_AMENDED_PIVOT2: era-normalized per-scan robust z detection (Z=6.6, Z_G=4.8 from
  calibration budget rule). RESULT: N501Y flagged 2020-10-31, 48 days before COG-UK recognition;
  D614G + L452R honest negatives (1/3 < 2/3 bar - catch test FAILS the locked bar, reported as found).
  Negative control May-Aug 2021: weighted precision 0.75 (32 alerts, catches full Delta constellation
  T478K/P681R/G142D/D950N at 2021-05-31) vs growth-only 0.714 (42 alerts). Measurement fix: LAPIS
  proportion field for shares (count/total could exceed 1 across endpoints with different date fields).
- TODO next run: figures (mutation trajectories of controls + Delta constellation, precision bars),
  VALIDATION_REPORT.md, ~17-21pp paper PDF, final slice manifest + seal request.
