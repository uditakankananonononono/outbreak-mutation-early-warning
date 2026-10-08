#!/usr/bin/env python3
"""Build the B17 scoring slice's structural_sets.json from byte-locked inputs.

Reproduce gate (scoring/GATES_LOCKED.md section 3): on the same inputs
(validation/data/raw PDBs + fastas, read-only) the output must be BYTE-IDENTICAL
to validation/data/static/structural_sets.json. Run:

    python3 build_sets.py            # build into ../data/static/ + verify
    python3 build_sets.py --verify-only   # verify against reference, no write

Prints the sha256 of the regenerated file and the byte-diff result.
"""
import hashlib, json, os, sys
from structural import build_reference_sets

HERE = os.path.dirname(os.path.abspath(__file__))
SLICE = os.path.join(HERE, "..")
RAW = os.path.join(SLICE, "..", "validation", "data", "raw")          # read-only inputs
REFERENCE = os.path.join(SLICE, "..", "validation", "data", "static", "structural_sets.json")
OUT_DIR = os.path.join(SLICE, "data", "static")
OUT = os.path.join(OUT_DIR, "structural_sets.json")

def main():
    verify_only = "--verify-only" in sys.argv
    sets, stats = build_reference_sets(RAW)
    for pdb_id, label, n, sch, och in stats:
        print(pdb_id, label, n, "contact residues; spike chains", sch, "partners", och)
    print("epitope union:", len(sets["epitope_surface_union"]))
    print("conserved:", len(sets["conserved_sars1"]["residues"]))
    blob = json.dumps(sets, indent=1).encode()
    sha = hashlib.sha256(blob).hexdigest()
    print("regenerated sha256:", sha)
    ref = open(REFERENCE, "rb").read()
    ref_sha = hashlib.sha256(ref).hexdigest()
    print("reference   sha256:", ref_sha)
    if blob == ref:
        print("REPRODUCE GATE: PASS (byte-identical to reference)")
        rc = 0
    else:
        print("REPRODUCE GATE: FAIL (not byte-identical); no extension may land")
        rc = 1
    if not verify_only and rc == 0:
        os.makedirs(OUT_DIR, exist_ok=True)
        with open(OUT, "wb") as fh:
            fh.write(blob)
        print("wrote", OUT)
    sys.exit(rc)

if __name__ == "__main__":
    main()
