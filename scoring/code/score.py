#!/usr/bin/env python3
"""B17 scoring CLI - structural-criticality weight for mutations.

Contract (scoring/GATES_LOCKED.md sections 2 and 5):
  python3 score.py --mutation "S:N501Y"        -> one JSON object on stdout
  python3 score.py --input mutations.txt       -> JSON array, one object per line of input
Output object: {mutation, S, tier, breakdown:{...}, (reason if THIN/UNRESOLVED),
                (S_ext if extended sets present)}
Exit codes: 0 = all scored, 2 = malformed input.
S = locked base formula (identical to the reference engine); the B18 validation
protocol consumes S unchanged. S_ext adds the extended-set bonus (cap +0.15).
"""
import argparse, json, os, sys
from structural import load_score_sets, structural_score, score_breakdown, parse_mutation

HERE = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(HERE, "..", "data", "static")
EXT = os.path.join(STATIC, "extended", "extended_sets.json")

def load_all():
    sets = json.load(open(os.path.join(STATIC, "structural_sets.json")))
    S = load_score_sets(sets)
    ext = None
    if os.path.exists(EXT):
        e = json.load(open(EXT))
        ext = {k: set(v["residues"]) for k, v in e["sources"].items()}
    return S, ext

def ext_bonus(pos, ext):
    """Extended-set bonus: +0.05 per extended interface-class set hit, capped +0.15."""
    if not ext or not (1 <= pos <= 1273):
        return 0.0
    hits = sum(pos in v for v in ext.values())
    return min(0.05 * hits, 0.15)

def score_one(mut, S, ext):
    b = score_breakdown(mut, S)
    row = {"mutation": mut, "S": b["S"], "tier": b["tier"], "breakdown": b["components"]}
    if "reason" in b:
        row["reason"] = b["reason"]
    if ext is not None:
        _g, _r, pos, _a = parse_mutation(mut)
        eb = ext_bonus(pos, ext) if _g == "S" else 0.0
        row["S_ext"] = round(b["S"] + eb, 6)
        row["S_ext_bonus"] = eb
    return row

def main():
    ap = argparse.ArgumentParser(description="Structural-criticality mutation scorer (B17)")
    ap.add_argument("--mutation", help="one mutation, e.g. S:N501Y")
    ap.add_argument("--input", help="file with one mutation per line")
    a = ap.parse_args()
    if not a.mutation and not a.input:
        ap.error("give --mutation or --input")
    muts = [a.mutation] if a.mutation else [
        l.strip() for l in open(a.input) if l.strip() and not l.startswith("#")]
    S, ext = load_all()
    rows = []
    try:
        for m in muts:
            parse_mutation(m)  # validate first; malformed -> exit 2
            rows.append(score_one(m, S, ext))
    except ValueError as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(2)
    if a.mutation:
        print(json.dumps(rows[0], indent=1))
    else:
        print(json.dumps(rows, indent=1))

if __name__ == "__main__":
    main()
