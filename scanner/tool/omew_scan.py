#!/usr/bin/env python3
"""omew_scan - B16 scanner CLI (GATES_LOCKED S3 contract).

  omew_scan.py scan --freeze YYYY-MM-DD       pinned-data frozen scan, JSON alerts
  omew_scan.py score --mutations S:E484K,S:N501Y   B17 structural-criticality passthrough

Exit 0 on valid input, 2 on malformed input (e.g. "S:501", ":N501Y", bad dates).
"""
import argparse, datetime as dt, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "scanner", "code"))

MUT_RE = re.compile(r"^[A-Za-z0-9]+:[A-Z][0-9]+[A-Z]$")

def die2(msg):
    print(json.dumps({"error": msg}))
    sys.exit(2)

def cmd_scan(freeze):
    try:
        f = dt.date.fromisoformat(freeze)
    except ValueError:
        die2("bad freeze date %r (want YYYY-MM-DD)" % freeze)
    from scan import Scanner, zfilter, Z_WEIGHTED, Z_GROWTH
    sc = Scanner()
    rows = sc.scan(f)
    aw = zfilter(rows, "A", Z_WEIGHTED)
    ag = zfilter(rows, "g", Z_GROWTH)
    json.dump({"freeze": str(f), "snapshot": "LAPIS open v2 dataVersion 1790179197 (pinned 2026-09-23)",
               "n_candidates": len(rows),
               "alerts_weighted": [(r["mutation"], round(r["g"], 4), round(r["S"], 3), round(r["A"], 4)) for r in aw],
               "n_alerts_growth_only": len(ag)}, sys.stdout, indent=1)
    print()

def cmd_score(muts_csv):
    muts = [m.strip() for m in muts_csv.split(",") if m.strip()]
    if not muts:
        die2("no mutations given")
    bad = [m for m in muts if not MUT_RE.match(m)]
    if bad:
        die2("malformed mutation(s): %s (want GENE:RefPosAlt, e.g. S:N501Y)" % ", ".join(bad))
    scorer = os.path.join(REPO, "scoring", "code", "score.py")
    lst = os.path.join(REPO, "scanner", "results", ".cli_mutations.tmp")
    open(lst, "w").write("\n".join(muts) + "\n")
    try:
        r = subprocess.run([sys.executable, scorer, "--input", lst],
                           capture_output=True, text=True)
        sys.stdout.write(r.stdout)
        if r.returncode != 0:
            sys.stderr.write(r.stderr)
            sys.exit(r.returncode)
    finally:
        os.unlink(lst)

def main():
    ap = argparse.ArgumentParser(prog="omew_scan", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("scan"); p.add_argument("--freeze", required=True)
    p = sub.add_parser("score"); p.add_argument("--mutations", required=True)
    a = ap.parse_args()
    if a.cmd == "scan":
        cmd_scan(a.freeze)
    else:
        cmd_score(a.mutations)

if __name__ == "__main__":
    main()
