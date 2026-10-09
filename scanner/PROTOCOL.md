# PROTOCOL - B16 scanner slice

Adopted lane (bioplex13 executor, 2026-10-10). Builds the early-warning scanner
module under GATES_LOCKED.md (locked 2026-10-10 00:25 IST, pre-outcome).

Steps (locked order):
1. Port the detection layer of validation/code/engine.py into
   scanner/code/scan.py as a clean module (no changes to semantics; reference
   behavior is ground truth).
2. REPRODUCE GATE (S1/S2): run the module on the pinned LAPIS bytes at all
   reference freezes; compare candidate sets, flags, and S scores verbatim.
3. CLI (S3): scanner/tool/omew_scan.py with malformed-input rejection.
4. MODULE SELF-CHECK (S4): control-flag agreement vs
   validation/results/validation_results.json.
5. Report + paper section (Times, blue borders, per program format), manifests,
   seal "B16 COMPLETE" only if S1-S5 pass; otherwise documented unsealed closeout.

Out of scope (locked): live LAPIS queries, current-variant surveillance, any
retuning of G_MIN/THETA/THETA_G, re-running the B18 catch test as a new claim.

Note (seal): scanner/paper/paper.pdf is binary and lives in the Drive
science-artifacts folder (web-UI push route is text-only); paper.tex +
make_paper.py reproduce it. The scanner manifest therefore excludes paper.pdf.
