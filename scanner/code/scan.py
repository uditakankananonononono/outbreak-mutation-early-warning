#!/usr/bin/env python3
"""B16 scanner module - outbreak mutation early-warning detection layer.

Clean modular port of the amended reference pipeline:
  validation/code/engine_fast.py (FastEngine) + run_validation.py z-filter
  (GATES_AMENDED_PIVOT1 estimator, GATES_AMENDED_PIVOT2 per-scan robust z).
Reference behavior is ground truth (GATES_LOCKED S1, GATES_AMENDED_1).
No threshold choices live here; all constants are the frozen committed ones.
"""
import json, os, glob, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
RAW = os.path.join(REPO, "validation", "data", "raw")
STATIC = os.path.join(REPO, "validation", "data", "static")

# Frozen constants (validation/results/calibration.json + GATES_AMENDED_PIVOT2)
G_MIN, THETA, THETA_G = 0.4141, 0.4716, 0.6088   # locked 2026-09-23 (superseded rule, kept for contract)
Z_WEIGHTED, Z_GROWTH = 6.6, 4.8                   # GATES_AMENDED_PIVOT2, frozen

W = {"epitope": 0.35, "ace2": 0.25, "cleavage": 0.15, "domain": 0.15, "conserved": 0.10}

def load_struct(static_dir=STATIC):
    s = json.load(open(os.path.join(static_dir, "structural_sets.json")))
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

def structural_score(mut, S):
    """Spike-only weighting (non-spike -> 0; documented limitation, unchanged)."""
    gene, rest = mut.split(":", 1)
    if gene != "S":
        return 0.0
    pos = int(rest[1:-1])
    return (W["epitope"]*(pos in S["epitope"]) + W["ace2"]*(pos in S["ace2"]) +
            W["cleavage"]*(pos in S["cleavage"]) + W["domain"]*(pos in S["domain"]) +
            W["conserved"]*(pos in S["conserved"]))

class Scanner:
    """Detection layer: weekly pinned-LAPIS scan, amended estimator, frozen constants."""

    def __init__(self, raw_dir=RAW, static_dir=STATIC):
        files = sorted(glob.glob(os.path.join(raw_dir, "aaMut_*.json")))
        if not files:
            raise FileNotFoundError("no pinned LAPIS aaMut_*.json under %s" % raw_dir)
        self.files = files
        self.weeks = []
        for f in files:
            a, bb = os.path.basename(f)[len("aaMut_"):-5].split("_")
            self.weeks.append((dt.date.fromisoformat(a), dt.date.fromisoformat(bb)))
        dailyf = glob.glob(os.path.join(raw_dir, "totals_by_date_*.json"))[0]
        daily = {dt.date.fromisoformat(r["date"]): r["count"]
                 for r in json.load(open(dailyf))["data"] if r["date"]}
        self.totals = np.array(
            [sum(daily.get(a + dt.timedelta(days=k), 0) for k in range(7))
             for a, b in self.weeks], dtype=float)
        mutset = {}
        for i in range(len(self.weeks)):
            for r in json.load(open(files[i]))["data"]:
                mutset.setdefault(r["mutation"], {})[i] = r["count"]
        self.muts = sorted(mutset)
        midx = {m: i for i, m in enumerate(self.muts)}
        self.M = np.zeros((len(self.muts), len(self.weeks)))
        for m, wk in mutset.items():
            for i, c in wk.items():
                self.M[midx[m], i] = c
        # LAPIS-reported proportions (measurement fix from GATES_AMENDED_PIVOT1)
        self.P = np.zeros_like(self.M)
        for i in range(len(self.weeks)):
            for r in json.load(open(files[i]))["data"]:
                self.P[midx[r["mutation"]], i] = r.get("proportion", 0.0)
        self.struct = load_struct(static_dir)
        self.Svec = np.array([structural_score(m, self.struct) for m in self.muts])
        self.logit = np.log10((self.M + 0.5) / (self.totals[None, :] + 1))

    def scan(self, freeze, lookback=6, count4_min=20, p4_min=0.001):
        """Frozen scan: only weeks ending <= freeze visible. Candidate rows only;
        alert selection happens via zfilter (PIVOT2 rule)."""
        vis = np.array([b <= freeze for a, b in self.weeks])
        vi = np.where(vis)[0]
        if len(vi) < lookback + 4:
            return []
        last = vi[-1]
        li = vi[vi > last - lookback]
        c4 = self.M[:, vi[vi > last - 4]].sum(axis=1)
        t4 = self.totals[vi[vi > last - 4]].sum()
        ok = (c4 >= count4_min) & ((c4 / max(t4, 1)) >= p4_min)
        idx = np.where(ok)[0]
        if len(idx) == 0:
            return []
        OBS = (self.M[np.ix_(idx, li)] > 0)
        nobs = OBS.sum(axis=1)
        xs_all = li.astype(float)
        rows = []
        for j, mut_i in enumerate(idx):
            if nobs[j] < 4:
                continue
            xs = xs_all[OBS[j]]
            ys = self.logit[mut_i, li][OBS[j]]
            mx = xs.mean(); my = ys.mean()
            denom = ((xs - mx)**2).sum()
            if denom == 0:
                continue
            gj = float(((xs - mx) * (ys - my)).sum() / denom)
            if gj <= 0:
                continue
            S = float(self.Svec[mut_i]); A = gj * (0.5 + S)
            rows.append({"mutation": self.muts[mut_i], "g": gj, "S": S, "A": A,
                         "count4": int(c4[mut_i]), "p4": float(c4[mut_i] / max(t4, 1))})
        return sorted(rows, key=lambda r: -r["A"])

def zfilter(rows, key, zth):
    """Per-scan robust z-score alert rule (GATES_AMENDED_PIVOT2), verbatim."""
    if len(rows) < 2:
        return []
    v = np.array([r[key] for r in rows])
    med = np.median(v)
    mad = np.median(np.abs(v - med)) * 1.4826
    if mad == 0:
        return []
    return [r for r in rows if (r[key] - med) / mad >= zth]

def month_end_freezes(start=(2020, 1), end=(2021, 9)):
    out = []
    y, m = start
    while (y, m) <= end:
        ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
        out.append(dt.date(ny, nm, 1) - dt.timedelta(days=1))
        y, m = ny, nm
    return out

CALIBRATION_FREEZES = [dt.date.fromisoformat(f) for f in
                       ("2020-05-31", "2020-06-30", "2020-07-31", "2020-08-31")]

def run_schedule(scanner, freezes):
    """Alerts per freeze: weighted (z on A) and growth-only comparator (z on g)."""
    log = []
    for f in freezes:
        rows = scanner.scan(f)
        aw = zfilter(rows, "A", Z_WEIGHTED)
        ag = zfilter(rows, "g", Z_GROWTH)
        log.append({"freeze": str(f),
                    "n_alerts_weighted": len(aw),
                    "weighted": [(r["mutation"], round(r["g"], 4), round(r["S"], 3), round(r["A"], 4)) for r in aw],
                    "n_alerts_growth_only": len(ag),
                    "growth_only": [(r["mutation"], round(r["g"], 4)) for r in ag]})
    return log
