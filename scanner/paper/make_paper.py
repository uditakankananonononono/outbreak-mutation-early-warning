#!/usr/bin/env python3
"""Render the B16 paper PDF: Times family, blue page borders (program format)."""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle)

BORDER = colors.Color(30/255, 60/255, 160/255)
doc = SimpleDocTemplate("paper.pdf", pagesize=letter,
                        leftMargin=1*inch, rightMargin=1*inch,
                        topMargin=1*inch, bottomMargin=1*inch,
                        title="The B16 Scanner Module",
                        author="Computational Biology (CBIO) portfolio - project 9, scanner slice")

def border(canvas, doc_):
    canvas.saveState()
    canvas.setStrokeColor(BORDER); canvas.setLineWidth(1.5)
    canvas.rect(0.55*inch, 0.55*inch, letter[0]-1.1*inch, letter[1]-1.1*inch)
    canvas.restoreState()

H = ParagraphStyle("H", fontName="Times-Bold", fontSize=20, leading=24, alignment=1, spaceAfter=6)
SUB = ParagraphStyle("SUB", fontName="Times-Italic", fontSize=11, leading=14, alignment=1, textColor=colors.darkslategray)
H1 = ParagraphStyle("H1", fontName="Times-Bold", fontSize=13, leading=16, spaceBefore=12, spaceAfter=4)
B = ParagraphStyle("B", fontName="Times-Roman", fontSize=11, leading=14.5, alignment=4, spaceAfter=6)
S = []
S.append(Paragraph("The B16 Scanner Module: A Reproducible Structurally-Weighted Early-Warning Scanner for Outbreak Mutations", H))
S.append(Paragraph("Computational Biology (CBIO) portfolio - project 9, scanner slice - 2026-10-10", SUB))
S.append(Spacer(1, 10))
S.append(Paragraph("Abstract", H1))
S.append(Paragraph("We present the B16 scanner module: the detection layer of a structure-weighted outbreak mutation early-warning engine, delivered as a clean, reusable, fully reproducible module. The module scans weekly public genome-submission aggregates and flags mutations whose growth slope is weighted by structural criticality derived entirely from published experimental data (antibody-spike and ACE2-spike contact geometry and SARS-CoV-1 conservation). Gates were locked before any output was computed (builder-reported; the local commit chain is published as evidence in scanner/PROVENANCE.md). On the byte-locked LAPIS snapshot (dataVersion 1790179197), the module reproduces the committed B18 reference engine's weekly alert lists and growth-only alert counts at all 21 monthly freezes (0 mismatches), its structural scores equal the B17 scorer on 22/22 flagged spike substitutions, and its command-line tool rejects malformed input with exit 2. It reproduces the reference's behavior including its failed catch test (1 of 3 controls); it is not a validation of early-warning ability.", B))
S.append(Paragraph("1. Problem and prior art", H1))
S.append(Paragraph("Genomic surveillance needs early warning: flag concerning mutations before they dominate. Four published systems bound the space. VirusWarn ranks variants by mutation-burden keyword rules; FEVER estimates empirical mutational risk from lineage outcomes; CoVerage scores antigenic impact with curated literature weights plus epidemiological dynamics; Nextstrain tracks phylogeny descriptively. None ranks flags by structural criticality derived from validated experimental geometry with a pre-registered frozen-window catch test (prior-art verdict: CROWDED, angle survives, adopted verbatim from the B18 validation slice). The engine's reference implementation was evaluated retrospectively in the B18 slice on this single pinned snapshot. That evaluation's pre-registered catch test FAILED its bar (1 of 3 controls flagged; bar 2 of 3), and structural weighting gave no catch advantage over the growth-only comparator (precision 0.750 vs 0.714, Fisher p = 0.80). This slice delivers the scanner itself as a standalone module and proves it reproduces the reference behavior exactly; it claims no early-warning validation.", B))
S.append(Paragraph("2. Data and discipline", H1))
S.append(Paragraph("All scan inputs come from the LAPIS open v2 instance (cov-spectrum), snapshot 1790179197, byte-locked on 2026-09-23 (weekly amino-acid mutation scans, daily sequence totals, 2019-12-30 to 2021-10-04). The snapshot's staleness is by design: this slice targets the locked estimand (exact reproduction of reference scan behavior on pinned bytes), not live surveillance. Structural ground data are byte-locked PDB complexes (6M0J, 6WPT, 6XDG, 7C2L; extension 6M17, 6XCM, 7C01, 6W41 in the B17 slice) and the SARS-CoV-2/SARS-CoV-1 spike alignment. Gates were locked in scanner/GATES_LOCKED.md before any output; one pre-outcome amendment (GATES_AMENDED_1.md) fixed the reference definition to the amended pipeline actually used by the committed results. The pre-result lock is builder-reported: the local commit chain (gates d591f24 at 2026-10-10T00:21:28+05:30, amendment and module 18b65d1 at 00:22:22, gate run 00:22:36 IST, seal 6aa5f39 at 00:24:44) is published in scanner/PROVENANCE.md; public web-UI commit times reflect file-by-file recreation and are not evidence of the original order.", B))
S.append(Paragraph("3. Module contract", H1))
S.append(Paragraph("Weekly bins (Monday + 7 days). A mutation is a candidate at freeze F if, using only weeks ending on or before F: count in the last 4 weeks is at least 20, proportion at least 0.001, and the slope g of log10((c+0.5)/(t+1)) over the last 6 visible weeks (observed weeks only, at least 4 of 6) is positive. The alert score is A = g x (0.5 + S), where the structural-criticality weight for spike is S = 0.35[epitope] + 0.25[ACE2] + 0.15[cleavage] + 0.15[domain] + 0.10[conserved]; non-spike mutations get S = 0 (documented limitation). Alerts are selected by the frozen per-scan robust z-score rule (Z = 6.6 on A; comparator Z_G = 4.8 on g alone). All constants are the committed frozen ones; nothing was retuned.", B))
S.append(Paragraph("4. Results (verbatim, run once)", H1))
rows = [["Gate", "Verdict", "Key evidence"]]
rows.append(["S1 reproduce-detection", "PASS", "21/21 month-end frozen scans (2020-01-31..2021-09-30): zero mismatches in weighted alert lists and growth-only alert counts vs committed reference outputs"])
rows.append(["S2 scorer agreement", "PASS", "Module S equals B17 base S on 22/22 flagged spike substitutions; 4 flagged deletions (S:E156-, S:F157-, S:K310-, S:Y144-) sit outside B17's substitution-only CLI contract and are scored by the module's locked formula (0.0, 0.0, 0.1, 0.35)"])
rows.append(["S3 CLI contract", "PASS", "scan --freeze 2020-10-31: 407 candidates, alerts led by S:E484K (A = 0.2366); malformed inputs S:501, :N501Y, n501y, S:N501 and a non-ISO date all rejected with exit 2 before acceptance"])
rows.append(["S4 module self-check", "PASS", "Control first-flags agree exactly with the committed catch test: S:D614G unflagged (both), S:N501Y flagged 2020-10-31 (both), S:L452R unflagged (both)"])
t = Table(rows, colWidths=[1.5*inch, 0.7*inch, 4.3*inch])
t.setStyle(TableStyle([
    ("FONTNAME", (0,0), (-1,0), "Times-Bold"), ("FONTNAME", (0,1), (-1,-1), "Times-Roman"),
    ("FONTSIZE", (0,0), (-1,-1), 9), ("GRID", (0,0), (-1,-1), 0.4, colors.gray),
    ("VALIGN", (0,0), (-1,-1), "TOP"), ("BACKGROUND", (0,0), (-1,0), colors.Color(0.92,0.94,1.0)),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.Color(0.97,0.98,1.0)]),
]))
S.append(t)
S.append(Spacer(1, 6))
S.append(Paragraph("Every number above is recorded verbatim in scanner/results/reproduce_gate.json and scanner/results/s2_scorer_agreement.json from a single run; no metric was recomputed selectively.", B))
S.append(Paragraph("5. Honest negatives and limitations", H1))
S.append(Paragraph("Two of three pre-registered controls are never flagged - this is reference behavior, preserved rather than patched, and the B18 slice documents the estimator pivots that led here. The B18 catch test failed its pre-registered bar (1 of 3 controls; bar 2 of 3), and structural weighting showed no catch advantage over the growth-only comparator (precision 0.750 vs 0.714, Fisher p = 0.80); this module reproduces that behavior exactly and makes no early-warning claim. Structural weighting covers spike only; non-spike mutations are ranked by growth alone. The scanner scores a pinned historical snapshot; live deployment would need a fresh data lock and a new catch test, which this slice deliberately does not claim.", B))
S.append(Paragraph("6. The tool", H1))
S.append(Paragraph("scanner/tool/omew_scan.py exposes the frozen scan and the structural scorer behind strict input validation. Together with the B17 scorer it forms the engine's reusable front end: given a freeze date it returns ranked, structure-weighted alerts with every constant visible.", B))
S.append(Paragraph("7. Reproduction", H1))
S.append(Paragraph("python3 scanner/code/reproduce_gate.py over the pinned bytes under validation/data/; byte-locks in scanner/MANIFEST.sha256 and the updated top-level MANIFEST.sha256. Corrections applied after independent audit are recorded in scanner/CORRECTIONS_2026-10-10.md. Category: computational biology (CBIO). All data open; no spending, no restricted access.", B))

import json as _json
log = _json.load(open('../results/scan_log_module.json'))['month_end_schedule']
S.append(Paragraph("Appendix A. Full frozen-scan schedule (verbatim module output)", H1))
arows = [["Freeze", "N weighted alerts", "Weighted alerts (mutation)"]]
for e in log:
    arows.append([e["freeze"], str(e["n_alerts_weighted"]), ", ".join(x[0] for x in e["weighted"]) or "-"])
at = Table(arows, colWidths=[0.9*inch, 1.1*inch, 4.5*inch], repeatRows=1)
at.setStyle(TableStyle([
    ("FONTNAME", (0,0), (-1,0), "Times-Bold"), ("FONTNAME", (0,1), (-1,-1), "Times-Roman"),
    ("FONTSIZE", (0,0), (-1,-1), 8.5), ("GRID", (0,0), (-1,-1), 0.4, colors.gray),
    ("VALIGN", (0,0), (-1,-1), "TOP"), ("BACKGROUND", (0,0), (-1,0), colors.Color(0.92,0.94,1.0)),
]))
S.append(at)

doc.build(S, onFirstPage=border, onLaterPages=border)
print("built")
