# DP2 review record

Status: Rev P3 calculation/drawing package. Shaft McMaster 1346K534 (1566,
Rockwell C25, 1-1/2 x 24 in) with the Piazza-approved Sy = 88 ksi and
Sut = 3.4 HB = 860.2 MPa. Cost rule: full price of the shortest sufficient
stock plus prorated hardware. The catalog-wide search is in ../solver/.

Groove callout: root 1.456-1.460 in, radius 0.008-0.010 in (worst corner Kt 3.6).
The lower ring groove governs: ny 3.92 (Shigley Eq. 7-15, needs Sy >= 464.8 MPa)
and nf 1.34 (surface factor from Shigley 11th ed. Table 6-2, corrected 12 Nov; the
10th-edition coefficients gave 1.43). Keyseat to ASME B17.1 (Peterson Kt 2.17): ny 5.61, nf 1.89. Key
12.70 h14, set screw 0.24 N m (sized from the 35 N sprocket weight), pin checked
against McMaster's 7200 lbf double-shear rating at y = -185 mm. The Kt/Kts
elastic peak at the groove is reported for information only (n = 2.97).
Drawing tolerances are still being converted to standards.

NOTE (12 Nov): the PROVISIONAL PDFs in ../../output/pdf and design_review.md were built before the
surface-factor correction and still show nf 1.43/2.02/2.28. The VibeWrite report is the current text.
Report figures: ../FBD_report/ (fig_fbd_views, fig_shaft_layout, fig_internal_loads). Onshape source: cad/dp2_shaft.fs.

Files:
- `calculate.py`: auditable assumptions, equations, equilibrium/criterion checks.
- `data/results.json`, `data/shaft_sections.csv`, `data/bom.csv`: full-precision results.
- `sources/catalog_observations.csv`: dated part/length/price comparisons.
- `design_review.md`: editable report trace.
- `piazza_property_request.md`: note that the approved list covers this shaft.
- `build_report.py`: plots and vector drawing/PDF/DXF generation.
- `cad/DP2_shaft_P3.dxf`: editable 2-D drawing, paper geometry in millimeters.
- `../../output/pdf/DP2_design_review_PROVISIONAL.pdf`: assembled report and drawing.
- `../../output/pdf/DP2_shaft_drawing_PROVISIONAL.pdf`: separate shaft-only drawing.

Reproduce calculations with `python3 calculate.py`. To rebuild the report use a
Python environment with numpy, matplotlib, reportlab and pypdf, then execute
`python3 build_report.py`. The report builder imports the calculation module,
regenerates the results and checks all numerical acceptance criteria.

The original assignment, prior plan and earlier figures were not modified.
