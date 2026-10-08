# GATES_LOCKED - B17 structural-criticality scoring slice (outbreak mutation early-warning engine)

Locked: 2026-10-08 19:10 IST, builder B17. This commit contains ONLY the scoring-slice
gates. No scoring results, no generated structural sets, and no extension data have been
computed or committed before this lock. Any later change to these gates requires a new
amended-gates commit BEFORE any new results (pivot rule), with the original failure
preserved.

## 0. Slice and context

Structural-criticality scoring slice of project 9 (repo shared with B16 scanner and B18
validation). The scoring module weights mutations by structurally-validated criticality
from published PDB contact geometry - the differentiating angle of the whole project
(see section 1). B18's validation slice implements a reference version
(validation/code/build_structural.py) and its locked protocol "applies unchanged" to this
module once it lands (validation/GATES_LOCKED.md section 0).

Repo state at takeover (verified 2026-10-08 ~19:04 IST against the live clone, main =
51d9d702ec5a22174b19cb6c32efd7c2ef2abe7f): no scoring/, scorer/, or model/ directory
exists. Three earlier B17 lanes died 2026-09-23 (18:13, 20:32, 23:33, platform errors)
and pushed nothing. All reference inputs verified byte-identical against
validation/MANIFEST_DATA_CODE.sha256: build_structural.py, the four PDB complexes
(6M0J/6WPT/6XDG/7C2L), both spike fastas, and the reference structural_sets.json
(sha256 8db84b01aae7b5ef0ad911ef163e5aeb2a95cebf7629a7889e4fd8122bf3e7c1).

## 1. Prior-art verdict: CROWDED (reused from B18's locked gates; angle survives)

Reused unchanged from validation/GATES_LOCKED.md (locked 2026-09-23 22:10 IST), and each
source re-verified 2026-10-08 ~19:08 IST to still say what the record claims:
1. VirusWarn (doi:10.1016/j.csbj.2025.03.010; github.com/rki-mf1/viruswarn-sc2):
   mutation-based early warning prioritizing concerning SARS-CoV-2/influenza variants
   from sequencing data; sequence-composition/keyword ranking, no structure-validated
   criticality scoring. (Re-verified: spj.science.org/doi/10.1016/j.csbj.2025.03.010.)
2. FEVER (doi:10.1371/journal.pgph.0000207): computational biosurveillance, diagnostics
   and mutation typing; statistical risk from observed lineage outcomes; no structural
   impact model. (Re-verified: journals.plos.org/globalpublichealth/article?id=10.1371/journal.pgph.0000207.)
3. CoVerage (doi:10.1038/s41467-025-60231-4): in-silico genomic surveillance predicting
   and characterizing SARS-CoV-2 variants of interest; antigenic scoring of S-protein
   mutations with epidemiological dynamics; closest to the angle, but its antigenic score
   is a curated literature score, not derived from antibody-complex/ACE2 contact
   geometry, and it ships no frozen-window pre-registered catch test. (Re-verified:
   nature.com/articles/s41467-025-60231-4.)
4. Nextstrain (doi:10.1093/bioinformatics/bty400): real-time tracking of pathogen
   evolution; descriptive, does not score mutations by predicted structural criticality.
   (Re-verified: academic.oup.com/bioinformatics/article/34/23/4121/5001388.)

UNCOVERED ANGLE (unchanged): criticality weights derived entirely from published
experimental structural data - antibody-spike and ACE2-spike contact geometry from PDB
complexes plus SARS-CoV-1 conservation from alignment. None of the four does this.

## 2. Scoring contract (the interface B16 and B18 consume)

Input: one mutation string, LAPIS aminoAcidMutations format, e.g. "S:N501Y".
Output: criticality weight S in [0, 1] plus a breakdown and a confidence tier.

Base weights (identical to the locked reference formula, so B18's protocol applies
unchanged):
  S = 0.35*epitope_surface + 0.25*ace2_interface + 0.15*cleavage_sites(681-685, 815)
    + 0.15*critical_domains(RBM 437-508, FP 816-837, HR1 920-970)
    + 0.10*conserved_SARS1
where epitope_surface and ace2_interface come from 5 A contact geometry over the
byte-locked PDB complexes, and conserved_SARS1 from the byte-locked global alignment.

Non-spike mutations get S = 0 (documented limitation, inherited from the reference:
structural weighting covers spike only). Malformed mutation strings are rejected with a
documented error, never silently scored.

Confidence tiers (mirroring the fleet THIN/unresolved convention):
  TIER-1 STRUCTURE-DIRECT: the residue sits in >=1 PDB-derived contact set
    (epitope_surface or ace2_interface).
  TIER-2 DOMAIN-INFERRED: no direct contact evidence, but the residue falls in a
    locked critical domain or cleavage site.
  TIER-3 CONSERVATION-ONLY: only the SARS-CoV-1 conservation term fires.
  THIN: S = 0 but the residue is in canonical spike range (1-1273) - scored, no
    structural signal found. Reported as THIN, not silently dropped.
  UNRESOLVED: residue outside canonical spike range or non-spike gene - the module
    says so explicitly.
The tier is metadata only; it never changes S.

## 3. Reproduce-then-extend gate (agreement check)

HARD GATE, in this order:
  1. scoring/code/build_sets.py run on the same byte-locked inputs (the four PDB files
     and two fastas in validation/data/raw, read-only) must produce a structural_sets.json
     BYTE-IDENTICAL to validation/data/static/structural_sets.json
     (sha256 8db84b01aae7b5ef0ad911ef163e5aeb2a95cebf7629a7889e4fd8122bf3e7c1).
     Proof: sha256 of the regenerated file + a byte diff, both recorded in
     scoring/PROGRESS.md and committed with the module.
  2. Only if that passes may any extension land. If it fails, the failure is preserved
     as an honest negative and no extension is committed (pivot rule applies).

## 4. Extension beyond the reference (committed only after gate 3 passes)

Additive only - the reference outputs above never change after the reproduce gate:
  a. Additional published complexes: each new complex is fetched from RCSB PDB (free,
     no auth), byte-locked under scoring/data/raw/ with its own manifest entry, and
     yields an additional contact set under scoring/data/static/extended/. The reference
     structural_sets.json regeneration remains the agreement artifact; extended sets live
     in separate files so the B18 protocol never sees a schema change.
  b. Interface classes: extended sets are labeled by interface class
     (ace2, epitope_class_1_2 (RBD-up binders), epitope_class_3_4 (other RBD faces),
     NTD) so consumers can weight by class.
  c. Extended score S_ext = base S plus a documented bonus capped at +0.15 from the
     extended sets (same 5 A method); base S is always reported alongside. The locked
     B18 protocol uses base S only.
  d. scoring/data/static/structural_sets.json (this slice's copy) keeps the reference
     schema EXACTLY: top keys method/sources/epitope_surface_union/conserved_sars1/
     functional_domains; the four source keys ace2_interface/epitope_S309/epitope_REGN/
     epitope_4A8_NTD; residues as sorted int lists. Byte-identical to the reference on
     the same inputs, per gate 3.

## 5. Integration contract

- B16 scanner (in flight) consumes: scoring/code/score.py --mutation "S:N501Y" -> JSON
  {mutation, S, tier, breakdown}; and batch mode over a mutation list file. Exit codes
  documented (0 scored, 2 malformed input).
- B18 validation protocol runs against this module unchanged: it reads
  structural_sets.json schema per section 4d and the base formula per section 2.
- This slice touches ONLY scoring/. scanner/ and validation/ are read-only inputs.
  Push rule: fetch + rebase onto latest remote main before every push, FF-only.

## 6. Honest negatives / pivot policy

Negative results are preserved and reported; nothing is retuned after seeing outcomes;
if the reproduce gate or an extension fails, the failure is committed as found and any
new approach is locked in an amended-gates commit BEFORE new results.

## 7. Access-only rule

Free tools only: RCSB/PDB and NCBI eutils, no logins, no keys beyond the git deploy key,
no payment. If anything needs a login, key, or payment, stop and report.

## 8. Deliverables of this slice

- scoring/GATES_LOCKED.md (this standalone commit)
- scoring/code/ (build_sets.py, score.py CLI, extended-set builder) + scoring/tests/
- scoring/data/ (extended raw/static, byte-locked, own manifest section)
- scoring/report/SCORING_REPORT.md and scoring/paper/ (~17-21 pp PDF, Times, figures;
  quantified vs the four named crowded prior-art works)
- scoring/results/ (reproduce-gate proof, extension outputs, example scores)
- scoring/MANIFEST.sha256 over the committed scoring tree; top-level manifest update;
  seal commit "B17 COMPLETE"
