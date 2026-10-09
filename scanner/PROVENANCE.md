# PROVENANCE - B16 scanner slice (builder-reported evidence)

Added 2026-10-10 post-audit. The independent audit correctly noted that
lock-before-run is NOT provable from the public repo alone: the public commits
were recreated file-by-file through the GitHub web UI, so their timestamps
reflect recreation time, not original order. This file supplies the local git
chain as BUILDER-REPORTED evidence. It is a claim with supporting artifacts,
not a public proof.

## Clock

All times below are IST (UTC+5:30), the build machine's local clock.
reproduce_gate.json records "run_at": "2026-10-10T00:22:36" with NO timezone
suffix; that value is IST machine-local time.

## Local commit chain (hashes + committer dates, from `git log` in the build clone)

1. d591f24b2200e88de44debcab19d4d8464619599  2026-10-10T00:21:28+05:30
   B16 scanner: GATES_LOCKED + PROTOCOL (standalone, pre-outcome)
2. 18b65d1fbbfc1e51e1fcfaccf714ede70a95ca46  2026-10-10T00:22:22+05:30
   B16: GATES_AMENDED_1 + scanner/code/scan.py module port (no runs yet)
3. GATE RUN: 2026-10-10T00:22:36 IST (run_at in reproduce_gate.json) - AFTER
   commits 1 and 2, BEFORE the seal commit 4.
4. 6aa5f391e14320c81f97024dee0490f80d1fde53  2026-10-10T00:24:44+05:30
   B16 COMPLETE: scanner slice sealed (results + report committed after run)
5. dc36c47a6d77a1bf8ea6b929ba4b15ec046b8b28  2026-10-10T00:32:21+05:30
   B16 seal: scanner manifest, paper sources, top-level manifest

## Apparent contradiction resolved

The audit flagged: reproduce_gate.json run_at 00:22:36 vs GATES_LOCKED uploaded
to GitHub at ~00:29 IST vs REPRODUCE_REPORT header "run 00:33 IST".
- GATES_LOCKED was committed LOCALLY at 00:21:28 IST (commit 1) and recreated
  on github.com via the web UI minutes later; the ~00:29 upload time is the
  recreation time, not the lock time.
- The report header's "00:33 IST" was the report-AUTHORING time, mislabeled as
  the run time; corrected in REPRODUCE_REPORT.md. The gate itself ran at
  00:22:36 IST.

## Status of the claim

"Gates locked before any output was computed" is supported by this
builder-reported chain and by the absence of any scanner result files in
commits 1-2. It is not independently verifiable from the public repo and is
presented as such.
