#!/usr/bin/env python3
"""Figures + derived stats from committed results/data. No protocol constants changed."""
import os, sys, json, datetime as dt
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import fisher_exact
from engine_fast import FastEngine
H = os.path.dirname(__file__); FIG = os.path.join(H, "..", "figures"); RES = os.path.join(H, "..", "results")
plt.rcParams.update({"font.family": "serif", "font.serif": ["Liberation Serif", "Times New Roman"], "font.size": 9})
R = json.load(open(os.path.join(RES, "validation_results.json")))
e = FastEngine(); mids = [a + (b - a) / 2 for a, b in e.weeks]
def traj(m): return e.P[e.muts.index(m)] if m in e.muts else np.zeros(len(mids))
def flagline(ax, d, c="C3", l=None): ax.axvline(dt.date.fromisoformat(d), color=c, ls="--", lw=1, label=l)
# Fig 1 controls
fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.4), sharey=True)
for ax, m in zip(axs, ["S:D614G", "S:N501Y", "S:L452R"]):
    c = R["catch_test"][m]; ax.plot(mids, traj(m), color="k", lw=1.2)
    ax.axvline(dt.date.fromisoformat(c["recognition_date"]), color="C0", ls=":", lw=1.2, label="recognition")
    if c["first_flag_weighted"]: flagline(ax, c["first_flag_weighted"], l="first flag")
    ax.set_title(m + (" (caught, +%dd)" % c["lead_days_weighted"] if c["first_flag_weighted"] else " (not flagged)"))
    ax.set_xlim(dt.date(2020,1,1), dt.date(2021,9,30)); ax.tick_params(axis="x", rotation=40)
    ax.legend(fontsize=6, loc="upper left")
axs[0].set_ylabel("weekly share (LAPIS proportion)"); fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig1_control_trajectories.pdf")); fig.savefig(os.path.join(FIG, "fig1_control_trajectories.png"), dpi=200)
# Fig 2 Delta constellation
fig, ax = plt.subplots(figsize=(5, 2.8))
for m in ["S:T478K", "S:P681R", "S:G142D", "S:D950N"]: ax.plot(mids, traj(m), lw=1.2, label=m)
flagline(ax, "2021-05-31", l="flag 2021-05-31"); ax.set_xlim(dt.date(2021,1,1), dt.date(2021,12,31))
ax.set_ylabel("weekly share"); ax.set_xlim(dt.date(2021,1,1), dt.date(2021,9,30)); ax.tick_params(axis="x", rotation=40); ax.legend(fontsize=7); fig.tight_layout()
fig.savefig(os.path.join(FIG, "fig2_delta_constellation.pdf")); fig.savefig(os.path.join(FIG, "fig2_delta_constellation.png"), dpi=200)
# Fig 3 precision bars
nw, ng = R["negative_control_weighted"], R["negative_control_growth_only"]
fig, ax = plt.subplots(figsize=(3.6, 2.6))
ax.bar(["structure-weighted", "growth-only"], [nw["precision"], ng["precision"]], color=["C0", "C7"])
for i, d in enumerate([nw, ng]): ax.text(i, d["precision"] + .01, "%d/%d = %.3f" % (d["tp"], d["n"], d["precision"]), ha="center", fontsize=8)
ax.set_ylim(0, 1); ax.set_ylabel("precision (peak share >= 20% in 26 wk)"); fig.tight_layout()
fig.savefig(os.path.join(FIG, "fig3_precision.pdf")); fig.savefig(os.path.join(FIG, "fig3_precision.png"), dpi=200)
# Fig 4 alerts per scan
fig, ax = plt.subplots(figsize=(5, 2.6))
ax.bar([s["freeze"][:7] for s in R["scan_log"]], [s["n_alerts_weighted"] for s in R["scan_log"]], color="C0", alpha=.6, label="weighted", width=.4, align="edge")
ax.bar([s["freeze"][:7] for s in R["scan_log"]], [s["n_alerts_growth_only"] for s in R["scan_log"]], color="C7", alpha=.6, label="growth-only", width=-.4, align="edge")
ax.tick_params(axis="x", rotation=90, labelsize=6); ax.set_ylabel("alerts per monthly scan"); ax.legend(fontsize=7); fig.tight_layout()
fig.savefig(os.path.join(FIG, "fig4_alerts_per_scan.pdf")); fig.savefig(os.path.join(FIG, "fig4_alerts_per_scan.png"), dpi=200)
# stats
a, b = set(nw["alerts"]), set(ng["alerts"])
tab = [[nw["tp"], nw["n"] - nw["tp"]], [ng["tp"], ng["n"] - ng["tp"]]]
st = {"weighted_n": nw["n"], "weighted_tp": nw["tp"], "growth_n": ng["n"], "growth_tp": ng["tp"],
      "alerts_in_both": len(a & b), "weighted_only": sorted(a - b), "growth_only_only": sorted(b - a),
      "fisher_exact_p_two_sided": fisher_exact(tab)[1],
      "n_S_nonzero_alerts_weighted": sum(1 for v in nw["alerts"].values() if v["S"] > 0)}
json.dump(st, open(os.path.join(RES, "derived_stats.json"), "w"), indent=1); print(json.dumps(st, indent=1))
