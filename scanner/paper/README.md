# B16 paper

- paper.tex / make_paper.py - sources (make_paper.py is the active renderer;
  paper.tex kept as the LaTeX draft; sandbox TeX was too minimal, so the sealed
  PDF was rendered with reportlab - Times family, blue page borders).
- paper.pdf - binary; delivered to the Drive science-artifacts folder
  (web-UI push route is text-only). Regenerate: python3 make_paper.py.
