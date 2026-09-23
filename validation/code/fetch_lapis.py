#!/usr/bin/env python3
"""Fetch weekly amino-acid mutation scan + daily totals from LAPIS open v2 (cov-spectrum).
Raw JSON responses are stored verbatim in data/raw for sha256 byte-locking."""
import json, os, subprocess, sys, datetime as dt

BASE = "https://lapis.cov-spectrum.org/open/v2"
RAW = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(RAW, exist_ok=True)

def weeks(start="2019-12-30", end="2021-09-27"):
    d = dt.date.fromisoformat(start); e = dt.date.fromisoformat(end)
    while d < e:
        yield d.isoformat(), (d + dt.timedelta(days=7)).isoformat()
        d += dt.timedelta(days=7)

def curl(url, out):
    for attempt in range(4):
        r = subprocess.run(["curl", "-s", "-m", "90", url, "-o", out])
        if r.returncode == 0:
            try:
                d = json.load(open(out))
                if "data" in d: return True
            except Exception: pass
    return False

if __name__ == "__main__":
    jobs = []
    for a, b in weeks():
        jobs.append((f"{BASE}/sample/aminoAcidMutations?dateFrom={a}&dateTo={b}&minProportion=0.001&limit=10000",
                     os.path.join(RAW, f"aaMut_{a}_{b}.json")))
    jobs.append((f"{BASE}/sample/aggregated?dateFrom=2019-12-30&dateTo=2021-10-04&fields=date&limit=100000",
                 os.path.join(RAW, "totals_by_date_2019-12-30_2021-10-04.json")))
    todo = [(u, o) for u, o in jobs if not os.path.exists(o)]
    print(f"{len(todo)} fetches to do of {len(jobs)}")
    # parallel via xargs for speed
    lst = os.path.join(RAW, "_fetch_list.tsv")
    with open(lst, "w") as f:
        for u, o in todo: f.write(f"{u}\t{o}\n")
    r = subprocess.run(["bash", "-c",
        "cat %s | xargs -P8 -L1 bash -c 'curl -s -m 90 \"$0\" -o \"$1\" || echo FAIL $1' " % lst])
    # verify + retry serially
    bad = []
    for u, o in jobs:
        ok = False
        if os.path.exists(o):
            try: ok = "data" in json.load(open(o))
            except Exception: ok = False
        if not ok: bad.append((u, o))
    for u, o in bad:
        print("retry", o); curl(u, o)
    still = [(u,o) for u,o in bad if not os.path.exists(o) or "data" not in json.load(open(o))]
    print("done. failed:", len(still))
    # record data versions
    vers = {}
    for u, o in jobs:
        try:
            d = json.load(open(o)); vers[os.path.basename(o)] = d.get("info",{}).get("dataVersion")
        except Exception as e: vers[os.path.basename(o)] = f"ERROR {e}"
    json.dump(vers, open(os.path.join(RAW, "data_versions.json"), "w"), indent=1)
    print("data versions:", set(v for v in vers.values() if v and not v.startswith("ERROR")))
