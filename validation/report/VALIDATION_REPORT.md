# B18 VALIDATION REPORT - outbreak-mutation early-warning engine

Slice: validation/hindcasting of the reference engine (structure-weighted growth scan on SARS-CoV-2 spike and genome mutations).
Base commit for this closeout: 51d9d70. Data: LAPIS open v2 snapshot 1790179197 (byte-locked, bfa76d8).

## 1. Bottom line (qualified result, not a clean win)

- The locked catch test **FAILED its pre-registered bar**: 1 of 3 controls flagged before literature recognition (bar: at least 2 of 3).
- N501Y was flagged at the 2020-10-31 freeze, **48 days** before COG-UK recognition (2020-12-18).
- D614G and L452R were **never flagged** (honest negatives). The bar failure is reported as found and was not re-fished.
- The growth-only comparator caught exactly the same single control (N501Y, same freeze, same 48 days). Structural weighting gave **no catch advantage**.
- Negative-control window (May-Aug 2021 freezes): weighted precision **0.750** (24 TP / 32 alerts) vs growth-only **0.714** (30 TP / 42 alerts). The difference is small and **not statistically distinguishable** (Fisher exact, two-sided p = 0.80). The weighted engine also caught the Delta constellation (T478K, P681R, G142D, D950N) at the 2021-05-31 freeze.
- Reached only after **two methodological pivots** that were made after seeing failures on the test windows (see sections 3 and 6).
- Finding: log-proportion slopes are not time-invariant across about 100x growth in sequencing volume, so no single global slope threshold works across eras.

## 2. Pre-registered protocol (GATES_LOCKED.md, commit 209667f, 2026-09-23 22:10 IST)

Candidates: count in last 4 weeks >= 20, proportion >= 0.001, positive slope g of log10((count+0.5)/(total+1)) over the last 6 visible weeks. Structural score S for spike mutations (epitope surface 0.35, ACE2 interface 0.25, cleavage sites 0.15, critical domains 0.15, SARS-1 conservation 0.10) from PDB 6M0J, 6WPT, 6XDG, 7C2L; S = 0 for non-spike mutations. Alert score A = g * (0.5 + S). Monthly freezes 2020-01-31 to 2021-09-30. Controls: D614G (recognition 2020-04-30), N501Y (2020-12-18), L452R (2021-01-17). Pass bar: at least 2 of 3 flagged strictly before recognition. Negative-control window: freezes 2021-05-31 to 2021-08-31; true positive = reaches 20% weekly share within 26 weeks.

## 3. Pivot chain (all preserved in git history)

| Step | Commit | What happened | Result |
|---|---|---|---|
| Locked run | 55bd7e1 | Locked constants G_MIN 0.4141, THETA 0.4716, THETA_G 0.6088 | 0/3 controls; weighted 4 alerts, growth-only 150 alerts in negative window, 0 TP |
| Pivot 1 gates | 47f1a7f | Slope fit on observed weeks only (>=4 of 6); constants re-derived by the same calibration rule: G_MIN 0.2347, THETA 0.3525, THETA_G 0.4663 | committed before rerun |
| Pivot 1 run | 04d9280 | Rerun | 0/3 controls; 0 alerts in negative window |
| Pivot 2 gates | b08e624 | Per-scan robust z-score on A (and on g for comparator); Z = 6.6, Z_G = 4.8 from the same calibration budget rule | committed before rerun |
| Pivot 2 run | 51d9d70 | Rerun plus LAPIS proportion measurement fix | 1/3 controls; precision 0.75 vs 0.714 |

Root cause 1 (original failure): weeks below the 0.1% LAPIS query floor were fitted as exact zeros (log value near -7). That inflated calibration slopes for noise mutations crossing the floor, so G_MIN measured floor artifacts. Below-floor weeks are censored, not zero.

Root cause 2 (pivot-1 failure): with the estimator fixed, the calibration p95 slope (0.2347, from May-Aug 2020, a low-volume era) was above the true slope of the most consequential later risers (for example S:T478K at 0.224 on 2021-05-31). Sequencing volume grew about 100x, which compresses log-proportion slopes in later eras.

## 4. Re-verification done at closeout

Re-ran validation/code/run_validation.py from the byte-locked data. The regenerated validation_results.json is byte-identical to the committed file (cmp clean). See validation/QC_RECORD.md.

## 5. Results

### 5.1 Catch test (final rule)

| Control | Recognition | First flag (weighted) | Lead (days) | First flag (growth-only) |
|---|---|---|---|---|
| S:D614G | 2020-04-30 | never | - | never |
| S:N501Y | 2020-12-18 | 2020-10-31 | 48 | 2020-10-31 (48 d) |
| S:L452R | 2021-01-17 | never | - | never |

Controls passed: 1 of 3 for both rules. Bar (2 of 3): **FAILED**.

Notes on the negatives. D614G was already near 90% share by the first scan with enough data, so little of its rise was observable inside the scan schedule (Figure 1). L452R shows a long low plateau (about 5-10% share, Nov 2020 to Mar 2021) before its rise, so its growth signal was weak until after recognition. N501Y was flagged when its share was about 2%.

### 5.2 Negative-control window

| Rule | Alerts | TP | Precision |
|---|---|---|---|
| Structure-weighted | 32 | 24 | 0.750 |
| Growth-only | 42 | 30 | 0.714 |

31 of the weighted alerts are also growth-only alerts. The weighted rule has one alert growth-only lacks (S:T250I). Growth-only has 11 that weighted lacks, all non-spike (list in results/derived_stats.json). Only 7 of 32 weighted alerts have S > 0, so the weighted rule differs from growth-only mainly by dropping low-A alerts, not by structural insight. Fisher exact p = 0.796. The pre-stated claim "structure weighting beats growth-only on precision at comparable lead" is **not supported at any usable confidence**; the point difference is 0.036.

Delta constellation caught at the 2021-05-31 freeze: S:T478K, S:P681R, S:G142D, S:D950N (Figure 2; confirmed in validation_results.json).

## 6. Limitations and caveats (read before citing)

1. **Test-window information in the pivots.** Pivot 2's diagnosis cited S:T478K's slope on 2021-05-31, a date inside the negative-control window. The pivots were therefore informed by test-window outcomes. Each amended gate was committed before its own rerun, but the amended rule is not a clean pre-registered test. GATES_AMENDED_PIVOT1.md called itself "the single pivot"; a second pivot followed.
2. **Only three controls.** Pass or fail on 2 of 3 is very coarse. One catch is an anecdote.
3. **Precision depends on an ad hoc truth definition** (20% share within 26 weeks) applied to a Delta-sweep window where most rising mutations are hitchhikers on one lineage. Many "true positives" are linked mutations, not independent detections.
4. **Structural weighting covers spike only** (S = 0 elsewhere).
5. **Single snapshot, single virus, retrospective.** Recognition dates are literature dates; real-time sequencing latency is not modelled (the snapshot is fixed after the fact).
6. Calibration counts differ across rule versions because the estimator changed; constants in GATES_LOCKED.md (0.4141 etc.) are superseded by calibration.json for the final rule.

7. Build note: the paper was compiled without booktabs/hyperref (unavailable in the build environment), so tables use plain rules and there are no hyperlinks.

## 7. Artifacts

- results/validation_results.json, results/calibration.json (committed, reproduced)
- results/derived_stats.json (overlap and Fisher test; produced by code/make_figures.py)
- figures/fig1 to fig4 (PDF + PNG)
- paper/paper.pdf (LaTeX source in paper/)
- QC_RECORD.md, MANIFEST.sha256

## 8. Prior art

VirusWarn (doi:10.1016/j.csbj.2025.03.010), FEVER (doi:10.1371/journal.pgph.0000207), CoVerage (doi:10.1038/s41467-025-60231-4), Nextstrain (doi:10.1093/bioinformatics/bty400), as recorded in GATES_LOCKED.md section 1 (checked 2026-09-23). Not re-verified in this closeout.
