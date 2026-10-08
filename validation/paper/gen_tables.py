import json,os
H=os.path.dirname(os.path.abspath(__file__));R=json.load(open(H+"/../results/validation_results.json"))
def esc(s): return s.replace("_","\\_").replace("&","\\&")
o=[]
for key,name in(("negative_control_weighted","tab_alerts_weighted"),("negative_control_growth_only","tab_alerts_growth")):
    rows=["\\begin{longtable}{lrrrrrc}","\\toprule Mutation & Flag & $g$ & $S$ & $A$ & Peak 26wk & TP\\\\\\midrule","\\endhead"]
    for m,v in R[key]["alerts"].items():
        rows.append("%s & %s & %.3f & %.2f & %.3f & %.3f & %s\\\\"%(esc(m),v["flag"],v["g"],v["S"],v["A"],v["peak26wk"],"yes" if v["tp"] else "no"))
    rows+=["\\bottomrule","\\end{longtable}"]
    open(H+"/"+name+".tex","w").write("\n".join(rows))
rows=["\\begin{longtable}{lrr}","\\toprule Freeze & Weighted alerts & Growth-only alerts\\\\\\midrule","\\endhead"]
for s in R["scan_log"]: rows.append("%s & %d & %d\\\\"%(s["freeze"],s["n_alerts_weighted"],s["n_alerts_growth_only"]))
rows+=["\\bottomrule","\\end{longtable}"];open(H+"/tab_scanlog.tex","w").write("\n".join(rows))
