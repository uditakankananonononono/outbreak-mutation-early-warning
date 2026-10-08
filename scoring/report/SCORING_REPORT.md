# SCORING_REPORT - B17 structural-criticality scoring slice

Date: 2026-10-08. Builder: B17. Repo: outbreak-mutation-early-warning (project 9,
shared with B16 scanner + B18 validation). Gates: scoring/GATES_LOCKED.md
(standalone commit, pushed as 9c8cd55).

## 1. What was built

scoring/ module that weights mutations by structurally-validated criticality from
published PDB contact geometry:

- scoring/code/structural.py - core library: 5 A any-atom contact sets over
  spike-chain/partner-chain geometry, SARS-CoV-1 conservation by global alignment,
  the locked base score S, confidence tiers, mutation parser.
- scoring/code/build_sets.py - builds this slice's structural_sets.json from the
  byte-locked validation inputs (read-only) and runs the reproduce gate.
- scoring/code/score.py - CLI per the locked contract: --mutation and --input batch
  mode, JSON output {mutation, S, tier, breakdown, S_ext}, exit 0 scored / 2 malformed.
- scoring/code/build_extended.py - additive extension over 4 further published
  complexes with interface-class labels.
- scoring/tests/test_scoring.py - 26 checks, ALL PASS.
- scoring/data/static/structural_sets.json - byte-identical to the reference.
- scoring/data/raw/{6M17,6XCM,7C01,6W41}.pdb + data/static/extended/extended_sets.json
  - extension, byte-locked below.

## 2. Reproduce gate (HARD GATE, locked before any extension)

PASS. build_sets.py regenerates validation's structural_sets.json BYTE-IDENTICALLY:
  regenerated sha256: 8db84b01aae7b5ef0ad911ef163e5aeb2a95cebf7629a7889e4fd8122bf3e7c1
  reference   sha256: 8db84b01aae7b5ef0ad911ef163e5aeb2a95cebf7629a7889e4fd8122bf3e7c1
  byte diff: IDENTICAL (cmp exit 0)
Proof: scoring/results/reproduce_gate_proof.txt. Per-complex contact counts:
6M0J 21, 6WPT 22, 6XDG 37, 7C2L 16; epitope union 72; conserved vs SARS-CoV-1: 967.

## 3. Agreement with the B18 protocol

module structural_score == validation/code/engine.py structural_score on all 1273
canonical spike residues, 0 mismatches (results/b18_protocol_agreement.txt). The B18
validation protocol runs against this module unchanged; the structural_sets.json
schema is exactly the reference schema (section 4d of the gates).

## 4. Extension (post-gate, additive only)

Four further published complexes (RCSB PDB, free, no auth), byte-locked in
scoring/data/raw/, each labeled by interface class:
  6M17 ace2_6M17        ace2              23 res  Yan et al. 2020 Science 10.1126/science.abb2762
  6XCM epitope_B38      epitope_class_1_2 33 res  Wu et al. 2020 Science 10.1126/science.abb2241
  7C01 epitope_LYCoV555 epitope_class_1_2 44 res  Jones et al. 2021 Science 10.1126/science.abf9193
  6W41 epitope_CR3022   epitope_class_3_4 28 res  Yuan et al. 2020 Science 10.1126/science.abb7269
S_ext = S + min(0.05 x extended-set hits, 0.15); base S always reported alongside and
is what the locked B18 protocol consumes.

## 5. Scoring contract behavior (results/example_scores.json)

  S:E484K  S=0.75 S_ext=0.80 TIER-1   (epitope+ace2+domain)
  S:Q498R  S=0.75 S_ext=0.85 TIER-1
  S:K417N  S=0.60 S_ext=0.75 TIER-1
  S:N501Y  S=0.40 S_ext=0.55 TIER-1   (the mutation B18 caught 48 d early)
  S:T478K  S=0.50 S_ext=0.50 TIER-1   (Delta constellation)
  S:N439K  S=0.50 S_ext=0.50 TIER-1
  S:L452R  S=0.15 S_ext=0.20 TIER-2
  S:P681R  S=0.15 S_ext=0.15 TIER-2   (furin cleavage site)
  S:D950N  S=0.25 S_ext=0.25 TIER-2
  S:D614G  S=0.10 S_ext=0.10 TIER-3   (conservation-only)
  S:G142D  S=0.00 S_ext=0.00 THIN     (scored, no structural signal)
  S:A222V  S=0.00 S_ext=0.00 THIN
  ORF1a:P4715L / N:S194L  S=0.00 UNRESOLVED (non-spike, documented limitation)

## 6. Honest negatives and limitations

- Structural weighting covers spike only; non-spike mutations score 0 by design
  (inherited from the locked reference, documented in B18's gates and repeated here).
- Two malformed-input forms ("S:501", ":N501Y") were initially accepted by the
  parser; caught by tests before commit and fixed. No results were computed with the
  weak parser.
- D614G and G142D show that a globally important mutation can carry little or no
  structural signal in this scheme (S=0.10 and 0.00); the score measures structural
  criticality, not fitness, and B18's catch test already records D614G and L452R as
  honest negatives at the engine level.
- THIN residues (S=0 in canonical range) are reported explicitly, never dropped.

## 7. Prior art (CROWDED; angle survives) - reused from B18's locked gates

VirusWarn (10.1016/j.csbj.2025.03.010), FEVER (10.1371/journal.pgph.0000207),
CoVerage (10.1038/s41467-025-60231-4), Nextstrain (10.1093/bioinformatics/bty400).
All four re-verified live 2026-10-08; none derives criticality weights from
antibody-spike/ACE2 contact geometry + SARS-CoV-1 conservation. Quantified
comparison in scoring/paper/paper.pdf.

## 8. Integration

- B16 scanner: python3 scoring/code/score.py --mutation "S:N501Y" or --input file.
- B18 validation: consumes scoring/data/static/structural_sets.json and base S
  unchanged (schema + formula identical to reference).
