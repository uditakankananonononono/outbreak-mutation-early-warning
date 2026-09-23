#!/usr/bin/env python3
"""Vectorized engine: same rules as engine.py, numpy matrix backend."""
import json, os, glob, datetime as dt
import numpy as np

HERE = os.path.dirname(__file__)
RAW = os.path.join(HERE, "..", "data", "raw")
STATIC = os.path.join(HERE, "..", "data", "static")

def _load_struct():
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
    gene, rest = mut.split(":", 1)
    if gene != "S": return 0.0
    pos = int(rest[1:-1])
    return (W["epitope"]*(pos in S["epitope"]) + W["ace2"]*(pos in S["ace2"]) +
            W["cleavage"]*(pos in S["cleavage"]) + W["domain"]*(pos in S["domain"]) +
            W["conserved"]*(pos in S["conserved"]))

class FastEngine:
    def __init__(self):
        files = sorted(glob.glob(os.path.join(RAW, "aaMut_*.json")))
        self.weeks = []
        for f in files:
            b = os.path.basename(f)[len("aaMut_"):-5]
            a, bb = b.split("_")
            self.weeks.append((dt.date.fromisoformat(a), dt.date.fromisoformat(bb)))
        dailyf = glob.glob(os.path.join(RAW, "totals_by_date_*.json"))[0]
        daily = {dt.date.fromisoformat(r["date"]): r["count"]
                 for r in json.load(open(dailyf))["data"] if r["date"]}
        self.totals = np.array([sum(daily.get(a+dt.timedelta(days=k), 0) for k in range(7))
                                for a, b in self.weeks], dtype=float)
        mutset = {}
        for i, (a, b) in enumerate(self.weeks):
            for r in json.load(open(files[i]))["data"]:
                mutset.setdefault(r["mutation"], {})[i] = r["count"]
        self.muts = sorted(mutset)
        midx = {m: i for i, m in enumerate(self.muts)}
        self.M = np.zeros((len(self.muts), len(self.weeks)))
        for m, wk in mutset.items():
            for i, c in wk.items(): self.M[midx[m], i] = c
        self.struct = _load_struct()
        self.Svec = np.array([structural_score(m, self.struct) for m in self.muts])
        self.logit = np.log10((self.M + 0.5) / (self.totals[None, :] + 1))

    def scan(self, freeze, lookback=6, count4_min=20, p4_min=0.001, g_min=None, theta=None):
        vis = np.array([b <= freeze for a, b in self.weeks])
        vi = np.where(vis)[0]
        if len(vi) < lookback + 4: return []
        last = vi[-1]
        li = vi[vi > last - lookback]
        c4 = self.M[:, vi[vi > last - 4]].sum(axis=1)
        t4 = self.totals[vi[vi > last - 4]].sum()
        ok = (c4 >= count4_min) & ((c4 / max(t4, 1)) >= p4_min)
        idx = np.where(ok)[0]
        if len(idx) == 0: return []
        # amended estimator (GATES_AMENDED_PIVOT1): observed weeks only, >=4 of 6
        OBS = (self.M[np.ix_(idx, li)] > 0)
        nobs = OBS.sum(axis=1)
        xs_all = li.astype(float)
        rows = []
        for j, mut_i in enumerate(idx):
            if nobs[j] < 4: continue
            xs = xs_all[OBS[j]]
            ys = self.logit[mut_i, li][OBS[j]]
            mx = xs.mean(); my = ys.mean()
            denom = ((xs - mx)**2).sum()
            if denom == 0: continue
            gj = float(((xs - mx) * (ys - my)).sum() / denom)
            if gj <= 0: continue
            S = float(self.Svec[mut_i]); A = gj * (0.5 + S)
            if g_min is not None and gj < g_min: continue
            if theta is not None and A < theta: continue
            rows.append({"mutation": self.muts[mut_i], "g": gj, "S": S, "A": A,
                         "count4": int(c4[mut_i]), "p4": float(c4[mut_i]/max(t4,1))})
        return sorted(rows, key=lambda r: -r["A"])

    def weekly_share(self, mut, after, weeks=26):
        lim = after + dt.timedelta(weeks=weeks)
        if mut not in {m: i for i, m in enumerate(self.muts)}: return 0.0
        i = self.muts.index(mut)
        best = 0.0
        for w, (a, b) in enumerate(self.weeks):
            if b <= after or a > lim: continue
            if self.totals[w] > 0:
                best = max(best, self.M[i, w] / self.totals[w])
        return float(best)
