# outbreak-mutation-early-warning

Scanner for new public genome submissions that flags structurally critical mutations,
with retrospective catch-test validation (open data).

Slices:
- `scanner/` - mutation scanner: `GATES_LOCKED.md` (+ one disclosed amendment
  `GATES_AMENDED_1.md`), `MANIFEST.sha256`, `code/`, `results/`, `tool/`, `paper/` sources.
  Post-audit corrections documented in `CORRECTIONS_2026-10-10.md`.
- `scoring/` - scoring slice: `GATES_LOCKED.md`, `MANIFEST.sha256`, `code/`, `data/`,
  `results/`, `tests/`, `report/SCORING_REPORT.md`, `paper/paper.pdf`.
- `validation/` - validation slice: `GATES_LOCKED.md` (+ two disclosed pivot amendments),
  `MANIFEST.sha256`, `MANIFEST_DATA_CODE.sha256`, `code/`, `data/`, `results/`, `figures/`,
  `report/VALIDATION_REPORT.md`, `paper/paper.pdf`.

Top-level `MANIFEST.sha256` pins every tracked file (rebuilt from remote bytes post-audit).

Status: built; verification/seal pending independent review.
