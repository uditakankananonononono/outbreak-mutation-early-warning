# CORRECTIONS - 2026-10-10 (post independent audit)

Independent audit verdict on the B16 seal (delivered 2026-10-10 00:40 IST by the
program gate): SCOPED PASS on engineering, OVERSTATED on paper framing. Five
corrections were ordered; all five are applied in this commit. No scan results,
gate outputs, or verdicts changed; this commit touches documentation, comments,
and manifests only.

1. PROVENANCE. Lock-before-run is not provable from the public repo, and the
   artifacts carried an apparent timestamp contradiction. Fixed: run_at clock
   timezone (IST, UTC+5:30) stated explicitly in REPRODUCE_REPORT.md; local
   git chain (hashes + committer dates) published in scanner/PROVENANCE.md as
   builder-reported evidence; paper + report now present the pre-result lock
   as builder-reported, not shown.
2. CONSTANTS CITATION. GATES_LOCKED.md section 3 and scan.py cited
   G_MIN=0.4141 / THETA=0.4716 / THETA_G=0.6088 as "from
   validation/results/calibration.json". calibration.json actually records
   G_MIN=0.2347, THETA=0.3525, THETA_G=0.4663. The cited values are the
   ORIGINAL 2026-09-23 threshold-rule constants (superseded by the PIVOT2
   z-rule; they never entered the executed scan path). Fixed in
   GATES_LOCKED.md, scan.py comments, REPRODUCE_REPORT.md erratum.
3. S1 WORDING. The locked text said "candidate sets and flag decisions"; the
   executed comparison is narrower: weighted alert lists (mutation + slope g)
   and growth-only alert COUNTS. GATES_LOCKED.md S1 wording amended in place,
   with the original wording quoted and the amendment dated. Paper and report
   already used the narrower wording.
4. MANIFESTS. scanner/MANIFEST.sha256 failed `sha256sum -c` as shipped
   (PROTOCOL.md hash mismatch, paper.aux/paper.log listed but absent, a
   leading space breaking -c); the top-level MANIFEST.sha256 listed two
   __pycache__ files not in the repo. Both manifests rebuilt from the exact
   post-commit remote bytes and re-pinned; verification command:
   `sha256sum -c scanner/MANIFEST.sha256` and `sha256sum -c MANIFEST.sha256`
   from the repo root.
5. PAPER FRAMING. paper.tex called the reference engine "validated
   retrospectively". B18's own committed results show its pre-registered
   catch test FAILED its bar (1 of 3 controls flagged; bar 2 of 3) and
   structural weighting gave NO catch advantage over the growth-only
   comparator (precision 0.750 vs 0.714, Fisher p = 0.80), on a single
   pinned snapshot. paper.tex + make_paper.py (regenerated PDF) now state
   the failed bar, the absent advantage, and the single-snapshot hindcast,
   and adopt the audit's narrowed supportable claim verbatim:

   "On a byte-locked LAPIS snapshot, the B16 module reproduces the committed
   B18 reference engine's weekly alert lists and growth-only alert counts at
   all 21 monthly freezes (0 mismatches), its structural scores equal the B17
   scorer on 22/22 flagged spike substitutions, and its CLI rejects malformed
   input with exit 2. It reproduces the reference's behavior including its
   failed catch test (1 of 3 controls); it is not a validation of
   early-warning ability."
