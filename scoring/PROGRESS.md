# scoring/ progress (Builder 17)

- 2026-10-08 19:04 grounded: repo cloned at 51d9d70; all reference inputs byte-verify
  against validation/MANIFEST_DATA_CODE.sha256; biopython 1.88 env ready.
- 19:09 GATES_LOCKED standalone commit 41bf214 (rebased+FF-pushed as 9c8cd55 onto B18
  closeout d247635). Prior-art CROWDED verdict reused; all 4 sources re-verified live.
- 19:10 REPRODUCE GATE PASS: build_sets.py on the byte-locked inputs regenerates
  structural_sets.json byte-identical to the reference
  (sha256 8db84b01aae7b5ef0ad911ef163e5aeb2a95cebf7629a7889e4fd8122bf3e7c1,
  cmp exit 0; proof in results/reproduce_gate_proof.txt). Per-sets: 6M0J 21, 6WPT 22,
  6XDG 37, 7C2L 16 contact residues; epitope union 72; conserved 967.
- 19:10 EXTENSION (post-gate, additive): 4 further published complexes from RCSB -
  6M17 (ace2, 23 res), 6XCM B38 (class 1/2, 33 res), 7C01 LY-CoV555 (class 1/2, 44 res),
  6W41 CR3022 (class 3/4, 28 res); byte-locked in scoring/data/raw/; interface-class
  labels; S_ext = S + min(0.05*hits, 0.15).
- 19:11 score.py CLI per locked contract (exit 0 scored / 2 malformed); tiers metadata-
  only. Parser hardened after test caught two malformed-input accepts ("S:501",
  ":N501Y").
- 19:11 B18 protocol agreement: module score == validation/code/engine.py
  structural_score on all 1273 canonical spike residues, 0 mismatches
  (results/b18_protocol_agreement.txt). tests: ALL PASS (26 checks).
- Next: SCORING_REPORT.md, paper PDF (~17-21pp Times, figures), slice manifest,
  top-level manifest, seal "B17 COMPLETE".
- 19:19 SCORING_REPORT.md committed; paper.pdf 17pp Times (5 tables incl. 191-residue
  scored map, 4 figures), compiled with pdflatex, visually verified; layout defects
  (longtable-in-float, DOI overflow, texttt overflow) found on inspection and fixed.
- Next: slice MANIFEST.sha256, top-level manifest, seal "B17 COMPLETE".
