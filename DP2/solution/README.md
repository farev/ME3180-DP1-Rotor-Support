# DP2 review record

Status: Rev P3 calculation/drawing package. Shaft McMaster 1346K534 (1566,
Rockwell C25, 1-1/2 x 24 in) with the Piazza-approved Sy = 88 ksi and
Sut = 3.4 HB = 860.2 MPa. Cost rule: full price of the shortest sufficient
stock plus prorated hardware. The catalog-wide search is in ../solver/.

Both yield checks pass: Shigley Kf/Kfs (needs Sy >= 500.9 MPa) and the added
Kt/Kts elastic check (needs Sy >= 591.4 MPa).

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
