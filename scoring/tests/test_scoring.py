#!/usr/bin/env python3
"""B17 scoring tests. Run: python3 scoring/tests/test_scoring.py (from repo root).
Locks: reproduce-gate byte identity, contract agreement with the reference engine's
formula, tier semantics, CLI exit codes."""
import hashlib, json, os, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CODE = os.path.join(ROOT, "scoring", "code")
sys.path.insert(0, CODE)
from structural import load_score_sets, structural_score, score_breakdown, parse_mutation

SETS = json.load(open(os.path.join(ROOT, "scoring", "data", "static", "structural_sets.json")))
S = load_score_sets(SETS)
FAILS = []

def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ((" | " + detail) if detail else ""))
    if not cond: FAILS.append(name)

# 1. reproduce gate: slice copy byte-identical to the byte-locked reference
ref = open(os.path.join(ROOT, "validation", "data", "static", "structural_sets.json"), "rb").read()
mine = open(os.path.join(ROOT, "scoring", "data", "static", "structural_sets.json"), "rb").read()
check("reproduce-gate byte identity", ref == mine,
      "sha256 " + hashlib.sha256(mine).hexdigest())

# 2. agreement with reference engine on its own locked constants
#    (computed from validation/code/engine.py semantics on the same sets)
check("N501Y base S == 0.40 (ace2+domain)", abs(structural_score("S:N501Y", S) - 0.40) < 1e-12)
check("D614G base S == 0.10 (conserved-only)", abs(structural_score("S:D614G", S) - 0.10) < 1e-12)
check("P681R cleavage hit == 0.15", abs(structural_score("S:P681R", S) - 0.15) < 1e-12)
check("E484K epitope+ace2+domain == 0.75",
      abs(structural_score("S:E484K", S) - (0.35 + 0.25 + 0.15)) < 1e-12)
check("non-spike ORF1a -> 0.0", structural_score("ORF1a:P4715L", S) == 0.0)

# 3. tiers never change S and classify as locked
check("N501Y tier TIER-1", score_breakdown("S:N501Y", S)["tier"] == "TIER-1 STRUCTURE-DIRECT")
check("P681R tier TIER-2", score_breakdown("S:P681R", S)["tier"] == "TIER-2 DOMAIN-INFERRED")
cons = sorted(S["conserved"] - S["epitope"] - S["ace2"] - S["cleavage"] - S["domain"])
check("conservation-only residue exists", len(cons) > 0)
if cons:
    b = score_breakdown("S:A%dV" % cons[0], S)
    check("conservation-only tier TIER-3", b["tier"] == "TIER-3 CONSERVATION-ONLY",
          "residue %d S=%.2f" % (cons[0], b["S"]))
check("D614G tier TIER-3", score_breakdown("S:D614G", S)["tier"] == "TIER-3 CONSERVATION-ONLY")
thin = [n for n in range(1, 1274)
        if n not in S["epitope"] | S["ace2"] | S["cleavage"] | S["domain"] | S["conserved"]]
check("THIN residue exists", len(thin) > 0)
if thin:
    check("THIN tier", score_breakdown("S:A%dV" % thin[0], S)["tier"] == "THIN",
          "residue %d" % thin[0])
check("S:X2000A tier UNRESOLVED", score_breakdown("S:X2000A", S)["tier"] == "UNRESOLVED")
check("non-spike tier UNRESOLVED", score_breakdown("N:S194L", S)["tier"] == "UNRESOLVED")

# 4. malformed input handling
for bad in ("garbage", "S:", "S:501", ":N501Y", "S:N501Y:extra"):
    try:
        parse_mutation(bad); check("rejects %r" % bad, False)
    except ValueError:
        check("rejects %r" % bad, True)

# 5. CLI exit codes + JSON shape
def cli(*args):
    return subprocess.run([sys.executable, os.path.join(CODE, "score.py")] + list(args),
                          capture_output=True, text=True)
r = cli("--mutation", "S:N501Y")
row = json.loads(r.stdout)
check("CLI exit 0 on valid", r.returncode == 0)
check("CLI JSON keys", set(row) >= {"mutation", "S", "tier", "breakdown"})
r = cli("--mutation", "garbage")
check("CLI exit 2 on malformed", r.returncode == 2)
tf = os.path.join(ROOT, "scoring", "tests", "_batch.txt")
open(tf, "w").write("S:N501Y\nS:D614G\n# comment\nORF1a:P4715L\n")
r = cli("--input", tf)
rows = json.loads(r.stdout)
check("CLI batch mode", r.returncode == 0 and len(rows) == 3)
os.remove(tf)

# 6. extended sets (if present): additive bonus capped, base S untouched
extp = os.path.join(ROOT, "scoring", "data", "static", "extended", "extended_sets.json")
if os.path.exists(extp):
    ext = {k: set(v["residues"]) for k, v in json.load(open(extp))["sources"].items()}
    check("extended sets non-empty", all(len(v) > 0 for v in ext.values()),
          "%d sets" % len(ext))
    r = cli("--mutation", "S:N501Y")
    row = json.loads(r.stdout)
    check("S_ext = S + bonus, S unchanged", abs(row["S_ext"] - (row["S"] + row["S_ext_bonus"])) < 1e-9
          and row["S"] == 0.4)
    check("bonus cap <= 0.15", row["S_ext_bonus"] <= 0.15 + 1e-12)

print()
if FAILS:
    print("FAILURES:", FAILS); sys.exit(1)
print("ALL TESTS PASS")
