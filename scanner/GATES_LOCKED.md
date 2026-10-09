# GATES_LOCKED - B16 scanner slice (outbreak mutation early-warning engine)

Locked: 2026-10-10 00:25 IST, bioplex13 executor (adopted lane). This commit contains
ONLY gates and protocol. No scanner results have been computed or committed before
this lock. Any later change requires an amended-gates commit BEFORE new results,
with the original failure preserved (repo pivot rule).

## 0. Why these gates are dated 2026-10-10, not 2026-09-23

B16 stalled 2026-09-23 at its prior-art check; its planned GATES_LOCKED commit never
landed (scanner/ held only PROGRESS.md until now; verified from the Sep-23..Oct-08
commit history and the B18 gates' own takeover note). These are therefore the
slice's first and only locked gates, written before any B16 outcome data.

## 1. Slice spec (recovered, unchanged)

From the 2026-09-23 13:29 IST slice spec quoted in validation/GATES_LOCKED.md:
B16 is the SCANNER module: scan new public genome submissions (operationalized as
weekly LAPIS aminoAcidMutations scans on the pinned snapshot) and flag structurally
critical mutations, weighted by the B17 structural-criticality scorer. B18 validates
the documented reference engine; B16 implements that engine as a clean, reusable
module and proves agreement with it. B16 does NOT re-run or re-claim the B18
retrospective catch test - that validation belongs to B18.

## 2. Data (pinned byte-lock; staleness is by design)

- LAPIS open v2 snapshot dataVersion 1790179197, byte-locked Sep 23 in
  validation/data/raw (MANIFEST_DATA_CODE.sha256, re-verified byte-identical
  2026-10-10). The snapshot is frozen by design: this slice targets the LOCKED
  ESTIMAND (reproduce the reference engine's scan behavior on pinned bytes),
  not current-variant surveillance. Live scanning is explicitly out of scope.
- Structural ground data: byte-locked PDB files in validation/data/static and
  scoring/data/raw (re-verified 2026-10-10). No new structural inputs.
- Prior-art verdict: CROWDED, angle survives (VirusWarn, FEVER, CoVerage,
  Nextstrain) - adopted unchanged from B18's locked gates; no re-litigation.

## 3. Module contract (locked)

scanner/code/scan.py implements EXACTLY the detection layer of
validation/GATES_LOCKED.md section 3:
- weekly bins (Mon+7d); candidate at freeze F iff, using only weeks ending <= F:
  count in last 4 weeks >= 20 AND proportion in last 4 weeks >= 0.001 AND slope g
  of log10((count+0.5)/(total+1)) over last 6 visible weeks > 0;
- alert score A = g*(0.5+S) with S from the B17 scorer (scoring/code/score.py);
  flag iff g >= G_MIN AND A >= THETA with the frozen constants G_MIN=0.4141,
  THETA=0.4716 (from validation/results/calibration.json; never retuned);
- comparator growth-only flag g >= THETA_G=0.6088, same alert budget.

## 4. Gates

- S1 REPRODUCE-DETECTION: on the pinned bytes, scanner candidate sets and flag
  decisions match the validation reference engine (validation/code/engine.py)
  at every freeze the reference engine evaluated (4 calibration freezes + the
  monthly test-freeze schedule). Agreement must be 100%; every mismatch is
  reported verbatim with its residue and freeze. Any mismatch is a FAIL.
- S2 SCORER AGREEMENT: for every flagged spike mutation, S equals
  scoring/code/score.py output for the same input (per B17's locked contract);
  0 mismatches required.
- S3 CLI CONTRACT: scanner/tool/omew_scan.py exposes scan --freeze YYYY-MM-DD
  (pinned-data scan) and score --mutations S:E484K,... (B17 passthrough).
  Exit 0 on valid input, exit 2 on malformed input (incl. "S:501", ":N501Y").
  Malformed-input tests must fail before the CLI is accepted.
- S4 MODULE SELF-CHECK (not a new validation claim): the module's scan at the
  B18 test freezes flags the same pre-committed controls (S:D614G, S:N501Y,
  S:L452R) at the same freezes as the committed B18 results
  (validation/results/validation_results.json). Byte-level or field-level
  agreement required; deltas reported verbatim, never patched silently.
- S5 HYGIENE: no pycache committed; all outputs under scanner/results/;
  scanner/MANIFEST.sha256 covers every scanner file; top-level
  MANIFEST.sha256 updated at seal.

## 5. Honesty rules (unchanged program standard)

Run once; verbatim results; negatives preserved in the record but never the
paper's centerpiece. If S1 fails and the cause is a reference-engine ambiguity
(not a scanner bug), the ambiguity is documented, the reference behavior is
treated as ground truth, and the amendment lands BEFORE any rerun.
