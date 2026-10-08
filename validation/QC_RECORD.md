# QC record - B18 validation closeout (2026-10-08)

Checker: closeout agent, independent of the builder. Base: main 51d9d70.

1. Reproduction: `python3 validation/code/run_validation.py` over byte-locked validation/data/raw. Output validation_results.json compared with the committed copy via `cmp`: byte-identical. Runtime about 1 s. PASS.
2. Pivot chain present in git history: 209667f (locked gates), 55bd7e1 (original failure), 47f1a7f + 04d9280 (pivot 1 + failure), b08e624 (pivot 2 gates), 51d9d70 (results). Gates for each pivot are committed before its run. PASS.
3. Catch-test FAIL (1/3 vs bar 2/3) stated plainly in VALIDATION_REPORT.md and paper. PASS.
4. Claims cross-checked against results JSON: N501Y first flag 2020-10-31, lead 48 d; D614G, L452R never flagged; weighted 24/32 = 0.750; growth-only 30/42 = 0.714; Delta constellation T478K, P681R, G142D, D950N all flagged 2021-05-31. PASS.
5. Added analysis (not in locked protocol, descriptive only): overlap of alert sets (31 shared) and Fisher exact test (p = 0.796), in results/derived_stats.json. Protocol constants and detection rules untouched.
6. Figures inspected as images (fig1, fig2, fig3, fig4, and the paper page layout contact sheet). Paper compiled with pdflatex (Times via mathptmx/Nimbus Roman).
7. Caveats recorded, not fixed: pivot 2 diagnosis used a negative-window slope (forking paths); only 3 controls; D614G already near 90% share at first usable scan; paper is 10 pages, shorter than the 17-21 page target (no padding added).
8. Prior-art citations copied from GATES_LOCKED.md, not re-verified.
