#!/usr/bin/env python3
"""Run the pre-registered validation exactly as locked in GATES_LOCKED.md.
No threshold choices happen here; constants come from results/calibration.json."""
import json, os, sys, datetime as dt
sys.path.insert(0, os.path.dirname(__file__))
from engine_fast import FastEngine as Engine

RES = os.path.join(os.path.dirname(__file__), "..", "results")
cal = json.load(open(os.path.join(RES, "calibration.json")))
G_MIN, THETA, THETA_G = cal["G_MIN"], cal["THETA"], cal["THETA_G"]

e = Engine()

def month_ends():
    out = []
    y, m = 2020, 1
    while (y, m) <= (2021, 9):
        nm_y, nm_m = (y + 1, 1) if m == 12 else (y, m + 1)
        out.append(dt.date(nm_y, nm_m, 1) - dt.timedelta(days=1))
        y, m = nm_y, nm_m
    return out

FREEZES = month_ends()
CONTROLS = {"S:D614G": "2020-04-30", "S:N501Y": "2020-12-18", "S:L452R": "2021-01-17"}

# --- positive control: catch test (structurally-weighted) and comparator (growth-only)
first_flag, first_flag_g = {}, {}
scan_log = []
for f in FREEZES:
    alerts = e.scan(f, g_min=G_MIN, theta=THETA)
    alerts_g = [r for r in e.scan(f, g_min=THETA_G)]  # growth-only comparator
    scan_log.append({"freeze": str(f),
                     "n_alerts_weighted": len(alerts),
                     "weighted": [(r["mutation"], round(r["g"],4), round(r["S"],3), round(r["A"],4)) for r in alerts],
                     "n_alerts_growth_only": len(alerts_g)})
    for r in alerts:
        first_flag.setdefault(r["mutation"], str(f))
    for r in alerts_g:
        first_flag_g.setdefault(r["mutation"], str(f))

catch = {}
for mut, recog in CONTROLS.items():
    ff = first_flag.get(mut); ffg = first_flag_g.get(mut)
    rd = dt.date.fromisoformat(recog)
    catch[mut] = {
        "recognition_date": recog,
        "first_flag_weighted": ff,
        "lead_days_weighted": (rd - dt.date.fromisoformat(ff)).days if ff else None,
        "flagged_before_recognition_weighted": bool(ff and dt.date.fromisoformat(ff) < rd),
        "first_flag_growth_only": ffg,
        "lead_days_growth_only": (rd - dt.date.fromisoformat(ffg)).days if ffg else None,
        "flagged_before_recognition_growth_only": bool(ffg and dt.date.fromisoformat(ffg) < rd),
    }

# --- negative control window: dedup alerts, TP if reaches >=20% global within 26 wks
NEG = [dt.date(2021,5,31), dt.date(2021,6,30), dt.date(2021,7,31), dt.date(2021,8,31)]

def peak_share_within(mut, flag_date, weeks=26):
    return e.weekly_share(mut, flag_date, weeks)

def neg_run(theta_mode):
    seen = {}
    for f in NEG:
        if theta_mode == "weighted":
            alerts = e.scan(f, g_min=G_MIN, theta=THETA)
        else:
            alerts = [r for r in e.scan(f, g_min=THETA_G)]
        for r in alerts:
            if r["mutation"] not in seen:
                peak = peak_share_within(r["mutation"], f)
                seen[r["mutation"]] = {"flag": str(f), "g": round(r["g"],4),
                                       "S": round(r["S"],3), "A": round(r["A"],4),
                                       "peak26wk": round(peak,4), "tp": peak >= 0.20}
    tp = sum(1 for v in seen.values() if v["tp"])
    return {"alerts": seen, "n": len(seen), "tp": tp,
            "precision": (tp/len(seen)) if seen else None}

neg_w = neg_run("weighted")
neg_g = neg_run("growth")

out = {"constants": cal, "catch_test": catch, "scan_log": scan_log,
       "negative_control_weighted": neg_w, "negative_control_growth_only": neg_g,
       "pass_bar": ">=2 controls flagged before recognition",
       "controls_passed_weighted": sum(1 for v in catch.values() if v["flagged_before_recognition_weighted"]),
       "controls_passed_growth_only": sum(1 for v in catch.values() if v["flagged_before_recognition_growth_only"])}
json.dump(out, open(os.path.join(RES, "validation_results.json"), "w"), indent=1)

print("=== CATCH TEST (weighted) ===")
for m, v in catch.items(): print(m, json.dumps(v))
print("controls passed weighted:", out["controls_passed_weighted"], "growth-only:", out["controls_passed_growth_only"])
print("=== NEGATIVE CONTROL ===")
print("weighted:", neg_w["n"], "alerts,", neg_w["tp"], "TP, precision", neg_w["precision"])
for k, v in neg_w["alerts"].items(): print("  ", k, v)
print("growth-only:", neg_g["n"], "alerts,", neg_g["tp"], "TP, precision", neg_g["precision"])
for k, v in neg_g["alerts"].items(): print("  ", k, v)
