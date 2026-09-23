# GATES_LOCKED - B18 validation slice (outbreak mutation early-warning engine)

Locked: 2026-09-23 22:10 IST, builder B18 (v3). This commit contains ONLY gates (plus the
pre-registered calibration constants derived by the procedure defined below). No
validation-test results have been computed or committed before this lock. Any later
change to these gates requires a new amended-gates commit BEFORE any new results
(pivot rule), with the original failure preserved.

## 0. Slice and context

Validation/hindcasting slice of project 9 (repo shared with B16 scanner and B17
structural-criticality scoring). Recovered slice spec (2026-09-23 13:29 IST):
retrospective catch test as positive control - run the engine on a frozen historical
window; it must flag >=2 documented concerning mutations (chosen and written down
BEFORE the test) earlier than their literature recognition date; precision measured
against a negative-control window. Output: validation report + paper validation section.

Repo state at takeover: only scanner/PROGRESS.md (B16 stalled at prior-art check;
B16 v2/v3 and B17 v2 pushed nothing). With parent approval (22:03 IST) this slice
implements the documented reference engine (scanner + structurally-weighted scorer)
inside validation/ per the B16/B17 specs and validates THAT. If B16/B17 later land,
this validation protocol applies unchanged to their modules.

## 1. Prior-art verdict: CROWDED (angle survives)

Closest works, checked 2026-09-23:
1. VirusWarn (doi:10.1016/j.csbj.2025.03.010; github.com/rki-mf1/viruswarn-sc2):
   mutation-based early warning for SARS-CoV-2/influenza; ranks variants by mutation
   burden/keyword rules against VOC lists. Retrospective, sequence-composition based;
   no structure-validated criticality scoring.
2. FEVER (doi:10.1371/journal.pgph.0000207): biosurveillance + mutation typing;
   estimates empirical risk of mutations from observed lineage outcomes. Statistical
   risk scoring; no structural impact model.
3. CoVerage (doi:10.1038/s41467-025-60231-4): in-silico genomic surveillance;
   antigenic-scoring of S-protein mutations with epidemiological dynamics; closest to
   the angle but its antigenic score is a curated literature score, not derived from
   validated structural methods (no antibody-complex/ACE2 contact geometry, no
   conservation term), and it ships no frozen-window catch test with pre-registered
   controls.
4. Nextstrain (doi:10.1093/bioinformatics/bty400): real-time phylogenetic tracking
   and visualization; descriptive, does not score or flag mutations by predicted
   structural criticality.

UNCOVERED ANGLE (the twist): an early-warning engine whose flag ranking is weighted
by structural criticality derived entirely from published experimental structural
data (antibody-spike and ACE2-spike contact geometry from PDB complexes, SARS-CoV-1
conservation from alignment), benchmarked against growth-only ranking on a
pre-registered frozen-window catch test. None of the four above does this.

## 2. Data sources (all open, no auth, no cost)

- LAPIS open v2 instance at cov-spectrum (https://lapis.cov-spectrum.org/open/v2,
  dataset sars_cov-2_nextstrain_open), snapshot dataVersion 1790179197, fetched
  2026-09-23 ~22:05 IST. Weekly aminoAcidMutations scans (minProportion=0.001) and
  daily sequence totals, 2019-12-30 to 2021-10-04. Raw JSON byte-locked in
  validation/data/raw (manifest follows in the data byte-lock commit).
- Cross-check source: NCBI Virus via eutils (esearch dated queries), spot counts only.
- Structural ground data (byte-locked PDB files): 6M0J (Lan et al. 2020, Nature,
  doi:10.1038/s41586-020-2180-5), 6WPT (Pinto et al. 2020, Nature,
  doi:10.1038/s41586-020-2349-y), 6XDG (Hansen et al. 2020, Science,
  doi:10.1126/science.abd0827), 7C2L (Chi et al. 2020, Science,
  doi:10.1126/science.abc6952).
- Reference sequences: YP_009724390.1 (SARS-CoV-2 spike), NP_828851.1 (SARS-CoV-1
  spike) via NCBI eutils; LAPIS reference genome (Wuhan-Hu-1).

## 3. Engine spec (reference implementation)

Detection (scanner): weekly bins (Mon+7d). A mutation is a candidate at freeze F if,
using only weeks ending <= F: count in last 4 weeks >= 20 AND proportion in last 4
weeks >= 0.001 AND slope g of log10((count+0.5)/(total+1)) over the last 6 visible
weeks > 0. Structural-criticality score for spike mutations:
S = 0.35*epitope_surface + 0.25*ace2_interface + 0.15*cleavage_sites(681-685,815)
  + 0.15*critical_domains(RBM 437-508, FP 816-837, HR1 920-970) + 0.10*conserved_SARS1,
where epitope_surface = union of spike residues within 5A of a partner chain in
6WPT+6XDG+7C2L (computed from the PDB files), ace2_interface likewise from 6M0J,
conserved from global alignment YP_009724390.1 vs NP_828851.1. Non-spike mutations
get S=0 (documented limitation: structural weighting covers spike only).
Alert score A = g*(0.5+S). Flag if g >= G_MIN and A >= THETA.
Comparator (benchmark): growth-only flag g >= THETA_G, same alert budget.

## 4. Pre-registered calibration (executed BEFORE this lock, disjoint freeze dates)

Procedure: candidate slopes are collected at calibration freezes 2020-05-31,
2020-06-30, 2020-07-31, 2020-08-31. G_MIN = 95th percentile of positive candidate
slopes. THETA = smallest alert threshold such that each calibration scan yields
<=3 alerts. THETA_G = smallest slope threshold such that total growth-only alerts
across the four calibration scans <= 12 (same total budget).
Constants (computed 22:07 IST, validation/results/calibration.json, n=1923
candidates): G_MIN = 0.4141, THETA = 0.4716, THETA_G = 0.6088.
Calibration-scan alerts under these constants: 0, 0, 0, 1 (S:N439K at 2020-08-31).
These constants are now frozen; they may not be retuned on test-window data.

## 5. Positive control: retrospective catch test

Scan schedule: monthly freezes 2020-01-31, then month-ends through 2021-09-30
(freeze uses only weeks ending <= freeze date). A mutation is "flagged at" the
first freeze whose scan flags it.
Pre-committed concerning mutations and literature recognition dates:
  C1 S:D614G - recognition 2020-04-30: Korber et al., bioRxiv
     doi:10.1101/2020.04.29.069054 ("Spike mutation pipeline reveals the emergence
     of a more transmissible form").
  C2 S:N501Y - recognition 2020-12-18: COG-UK/Rambaut et al., "Preliminary genomic
     characterisation of an emergent SARS-CoV-2 lineage in the UK"
     (gov.uk publication dated 2020-12-18; virological.org/t/563).
  C3 S:L452R - recognition 2021-01-17: CDPH news release NR21-020 on B.1.429
     (Epsilon), 2021-01-17.
Availability of all three controls in the dataset was count-checked before this
lock (D614G: 3,793 seqs 2020-02-16..03-15; N501Y: 379 seqs 2020-10-03..31;
L452R: 2,045 seqs 2020-11-16..12-15). No growth/flag outcome was inspected.
PASS bar: >=2 of 3 controls flagged at a freeze strictly earlier than their
recognition date. Lead time = recognition date minus first flag freeze (days).
A control never flagged, or flagged only after recognition, is an honest negative
and is reported as such.

## 6. Negative control and precision

Freezes: 2021-05-31, 2021-06-30, 2021-07-31, 2021-08-31 (Delta-plateau window).
Alerts are deduplicated across scans (a mutation counts at its first flag only).
Ground truth (data-driven, fixed here): a flagged mutation is a TRUE POSITIVE if it
reaches >=20% of global weekly sequences within 26 weeks after its flag date
(measured on this same byte-locked snapshot); otherwise FALSE POSITIVE.
Precision = TP/(TP+FP) over the negative-control scans, reported for the
structurally-weighted engine and the growth-only comparator. No numeric precision
threshold is promised; the number is reported as found.
Methodological contribution claim (tested, not assumed): structurally-weighted
ranking beats growth-only ranking on negative-control precision at comparable or
better positive-control lead time. If it does not, that is reported as the result.

## 7. Honest negatives / pivot policy

Negative results are preserved and reported; thresholds are never retuned after
seeing test outcomes; if a component yields no useful result, the pivot rule
applies: amended gates are committed BEFORE any new results and the original
failure is preserved in the report.

## 8. Deliverables of this slice

- validation/code/ (engine + analysis, runnable end to end)
- validation/data/ (raw byte-locked JSON/PDB/fasta + static structural sets + manifest)
- validation/results/ (catch-test + negative-control outputs, figures)
- validation/report/VALIDATION_REPORT.md and validation/paper/ (validation section,
  ~17-21 pp PDF with figures and tables)
- Slice manifest (sha256 over committed tree: data + results + code + paper sources)
