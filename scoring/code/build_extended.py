#!/usr/bin/env python3
"""Build B17 extended structural sets: additional published complexes beyond the
four reference ones. Additive only (scoring/GATES_LOCKED.md section 4); the
reference regeneration in ../data/static/structural_sets.json is untouched.

Each complex is byte-locked in ../data/raw/ (fetched from RCSB PDB, free, no auth)
and yields one contact set labeled by interface class:
  ace2              - spike-ACE2 complexes
  epitope_class_1_2 - RBD binders overlapping the ACE2 footprint (class 1/2)
  epitope_class_3_4 - RBD binders outside the ACE2 footprint (class 3/4)
  NTD               - NTD-directed antibodies
Output: ../data/static/extended/extended_sets.json
"""
import json, os
from Bio.PDB import PDBParser, PPBuilder
from structural import contact_residues

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "data", "raw")
OUT_DIR = os.path.join(HERE, "..", "data", "static", "extended")

EXTENDED_COMPLEXES = [
    ("6M17", "ace2_6M17", "ace2",
     "Yan et al. 2020 Science doi:10.1126/science.abb2762"),
    ("6XCM", "epitope_B38", "epitope_class_1_2",
     "Wu et al. 2020 Science doi:10.1126/science.abb2241"),
    ("7C01", "epitope_LYCoV555", "epitope_class_1_2",
     "Jones et al. 2021 Science doi:10.1126/science.abf9193"),
    ("6W41", "epitope_CR3022", "epitope_class_3_4",
     "Yuan et al. 2020 Science doi:10.1126/science.abb7269"),
]

def main():
    parser = PDBParser(QUIET=True); ppb = PPBuilder()
    out = {"method": "as reference (5 A any-atom contact, motif-identified spike chains); "
                     "extended complexes, additive to the reference sets",
           "sources": {}}
    for pdb_id, label, iclass, cite in EXTENDED_COMPLEXES:
        contacts, sch, och = contact_residues(os.path.join(RAW, pdb_id + ".pdb"),
                                              pdb_id, parser, ppb)
        res = sorted({n for (_c, n) in contacts if 1 <= n <= 1273})
        out["sources"][label] = {"pdb": pdb_id, "citation": cite,
                                 "interface_class": iclass,
                                 "spike_chains": sch, "partner_chains": och,
                                 "residues": res}
        print(pdb_id, label, iclass, len(res), "contact residues; spike chains", sch,
              "partners", och)
        if not res:
            print("WARNING: empty contact set for", pdb_id)
    os.makedirs(OUT_DIR, exist_ok=True)
    p = os.path.join(OUT_DIR, "extended_sets.json")
    json.dump(out, open(p, "w"), indent=1)
    print("wrote", p)

if __name__ == "__main__":
    main()
