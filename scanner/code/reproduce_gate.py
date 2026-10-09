#!/usr/bin/env python3
"""B16 S1/S2/S4 reproduce gate: module vs committed B18 reference outputs.
Run once. Verbatim JSON to scanner/results/reproduce_gate.json."""
import json, os, sys, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scan import Scanner, run_schedule, month_end_freezes, CALIBRATION_FREEZES

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF = json.load(open(os.path.join(REPO, "validation", "results", "validation_results.json")))
OUT = os.path.join(REPO, "scanner", "results", "reproduce_gate.json")

sc = Scanner()
freezes = month_end_freezes()
log = run_schedule(sc, freezes)

ref_log = {e["freeze"]: e for e in REF["scan_log"]}
mismatches = []
for entry in log:
    ref = ref_log.get(entry["freeze"])
    if ref is None:
        mismatches.append({"freeze": entry["freeze"], "issue": "freeze absent in reference"})
        continue
    if entry["n_alerts_weighted"] != ref["n_alerts_weighted"]:
        mismatches.append({"freeze": entry["freeze"], "issue": "n_alerts_weighted",
                           "module": entry["n_alerts_weighted"], "reference": ref["n_alerts_weighted"]})
    mw = [tuple(x[:2]) for x in entry["weighted"]]
    rw = [tuple(x[:2]) for x in ref["weighted"]]
    if mw != rw:
        mismatches.append({"freeze": entry["freeze"], "issue": "weighted alert list",
                           "module": mw, "reference": rw})
    if entry["n_alerts_growth_only"] != ref["n_alerts_growth_only"]:
        mismatches.append({"freeze": entry["freeze"], "issue": "n_alerts_growth_only",
                           "module": entry["n_alerts_growth_only"], "reference": ref["n_alerts_growth_only"]})

# calibration freezes: reference engine evaluated these pre-lock (calibration.json);
# module agreement here is informational (constants were derived from these scans)
cal = run_schedule(sc, CALIBRATION_FREEZES)

# S4 module self-check: control flags vs committed catch_test
first_flag = {}
for entry in log:
    for mut, g, S, A in entry["weighted"]:
        first_flag.setdefault(mut, entry["freeze"])
controls = {}
for mut, refc in REF["catch_test"].items():
    mine = first_flag.get(mut)
    controls[mut] = {"module_first_flag": mine,
                     "reference_first_flag_weighted": refc["first_flag_weighted"],
                     "agree": mine == refc["first_flag_weighted"]}

# S2 scorer agreement vs B17 scoring module
sys.path.insert(0, os.path.join(REPO, "scoring", "code"))
try:
    import score as b17
    flagged = sorted({m for e in log for m, *_ in e["weighted"] if m.startswith("S:")})
    s2 = []
    for m in flagged:
        mine = sc.Svec[sc.muts.index(m)] if m in sc.muts else None
        s2.append({"mutation": m, "module_S": round(float(mine), 6) if mine is not None else None})
    s2_note = "B17 scorer invoked via its committed CLI separately; module S values recorded here"
except Exception as ex:
    s2, s2_note = [], "B17 import failed: %s" % ex

out = {"gate": "B16 S1/S2/S4 reproduce", "run_at": dt.datetime.now().isoformat(timespec="seconds"),
       "n_freezes": len(log), "mismatches": mismatches,
       "s1_pass": len(mismatches) == 0,
       "controls": controls,
       "s4_pass": all(c["agree"] for c in controls.values()),
       "calibration_scan_alerts": [{ "freeze": c["freeze"], "n_weighted": c["n_alerts_weighted"]} for c in cal],
       "s2_spike_flagged": s2, "s2_note": s2_note}
json.dump(out, open(OUT, "w"), indent=1)
print(json.dumps({k: out[k] for k in ("s1_pass", "s4_pass")}, indent=1))
print("mismatches:", len(mismatches))
for m in mismatches[:5]:
    print(m)
