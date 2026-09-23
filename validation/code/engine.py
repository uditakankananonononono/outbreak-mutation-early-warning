#!/usr/bin/env python3
"""Outbreak mutation early-warning engine - reference implementation inside validation/
(B16 scanner + B17 structurally-weighted scoring, per the 2026-09-23 13:29 slice specs).

Detection layer (scanner): weekly amino-acid mutation scan (LAPIS open v2 snapshot),
frozen at a date F: only weeks ending <= F are visible.
Scoring layer: growth slope x structurally-validated criticality weight (spike).
"""
import json, os, glob, math, datetime as dt
from collections import defaultdict

HERE = os.path.dirname(__file__)
RAW = os.path.join(HERE, "..", "data", "raw")
STATIC = os.path.join(HERE, "..", "data", "static")

def load_weeks():
    files = sorted(glob.glob(os.path.join(RAW, "aaMut_*.json")))
    weeks = []
    for f in files:
        b = os.path.basename(f)
        a, bb = b[len("aaMut_"):-len(".json")].split("_")
        weeks.append((dt.date.fromisoformat(a), dt.date.fromisoformat(bb), f))
    return weeks

def load_totals():
    f = glob.glob(os.path.join(RAW, "totals_by_date_*.json"))[0]
    daily = json.load(open(f))["data"]
    return {dt.date.fromisoformat(r["date"]): r["count"] for r in daily if r["date"]}

def week_total(daily, a, b):
    d = a; n = 0
    while d < b:
        n += daily.get(d, 0); d += dt.timedelta(days=1)
    return n

def load_struct():
    s = json.load(open(os.path.join(STATIC, "structural_sets.json")))
    dom = s["functional_domains"]
    return {
        "epitope": set(s["epitope_surface_union"]),
        "ace2": set(s["sources"]["ace2_interface"]["residues"]),
        "cleavage": set(range(dom["furin_cleavage_site"][0], dom["furin_cleavage_site"][1]+1)) |
                    set(range(dom["S2_prime"][0], dom["S2_prime"][1]+1)),
        "domain": (set(range(dom["RBM"][0], dom["RBM"][1]+1)) |
                   set(range(dom["fusion_peptide"][0], dom["fusion_peptide"][1]+1)) |
                   set(range(dom["HR1"][0], dom["HR1"][1]+1))),
        "conserved": set(s["conserved_sars1"]["residues"]),
    }

W = {"epitope": 0.35, "ace2": 0.25, "cleavage": 0.15, "domain": 0.15, "conserved": 0.10}

def structural_score(mut, S):
    """mut like 'S:N501Y'; spike-only weighting (non-spike -> 0, documented limitation)."""
    gene, rest = mut.split(":", 1)
    if gene != "S": return 0.0
    pos = int(rest[1:-1])
    return (W["epitope"] * (pos in S["epitope"]) + W["ace2"] * (pos in S["ace2"]) +
            W["cleavage"] * (pos in S["cleavage"]) + W["domain"] * (pos in S["domain"]) +
            W["conserved"] * (pos in S["conserved"]))

class Engine:
    def __init__(self):
        self.weeks = load_weeks()
        self.daily = load_totals()
        self.totals = [week_total(self.daily, a, b) for a, b, _ in self.weeks]
        self.struct = load_struct()
        self.mut_counts = defaultdict(dict)  # mut -> week_idx -> (count, coverage)
        for i, (a, b, f) in enumerate(self.weeks):
            for r in json.load(open(f))["data"]:
                self.mut_counts[r["mutation"]][i] = (r["count"], r["coverage"])

    def scan(self, freeze, lookback=6, count4_min=20, p4_min=0.001, g_min=None, theta=None):
        """Frozen scan: only weeks with week_end <= freeze visible.
        Returns list of alerts: (mut, slope g, struct S, alert A)."""
        vis = [i for i, (a, b, _) in enumerate(self.weeks) if b <= freeze]
        if len(vis) < lookback + 4: return []
        last = vis[-1]
        alerts = []
        for mut, wk in self.mut_counts.items():
            idx = [i for i in vis if i > last - lookback]
            c4 = sum(wk.get(i, (0, 0))[0] for i in vis if i > last - 4)
            t4 = sum(self.totals[i] for i in vis if i > last - 4)
            if t4 == 0 or c4 < count4_min or c4 / t4 < p4_min: continue
            xs, ys = [], []
            for i in idx:
                c = wk.get(i, (0, 0))[0]
                xs.append(i)
                ys.append(math.log10((c + 0.5) / (self.totals[i] + 1)))
            n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
            g = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx)**2 for x in xs)
            if g <= 0: continue
            S = structural_score(mut, self.struct)
            A = g * (0.5 + S)
            row = {"mutation": mut, "g": g, "S": S, "A": A, "count4": c4, "p4": c4 / t4}
            if g_min is not None and g < g_min: continue
            if theta is not None and A < theta: continue
            alerts.append(row)
        return sorted(alerts, key=lambda r: -r["A"])

    def candidates_calibration(self, freezes):
        """All growth-positive candidates at the calibration freezes (pre-threshold)."""
        rows = []
        for f in freezes:
            for r in self.scan(dt.date.fromisoformat(f)):
                rows.append((f, r))
        return rows

if __name__ == "__main__":
    import sys
    e = Engine()
    print("weeks:", len(e.weeks), "first", e.weeks[0][0], "last", e.weeks[-1][1])
    print("total sequences:", sum(e.totals))
    print("mutations tracked:", len(e.mut_counts))
