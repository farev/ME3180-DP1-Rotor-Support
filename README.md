# ME 3180 Design Problem 1: Microhydro Rotor Support

Analysis code and report figures for the rotor support structure (support beam, two diagonal supports and three quick-release pins), Georgia Tech ME 3180, Fall 2026.

Final design: 6061-T6 rectangular tube 6 × 4 × 3/16 in (McMaster 6546K73), two 304 stainless diagonals cut from 1/4 × 5 in bar (8992K61), three 3/4 × 8 in ring-grip quick-release pins (98404A790), diagonal attached at a = 660 mm.

Units inside the code: mm, N, MPa, N·mm. Coordinates follow Figure 2 of the assignment (origin at pin O on the beam neutral axis).

## Report figures and calculations (`FBD_report/`)

| File | Produces / checks |
|---|---|
| `make_fbd_figures.py` | Figure 1(a)–(d) free-body diagrams and Table 1 load table (`fig_fbd_*.png`, `table_fbd_loads.png/.csv`) |
| `pin_reactions.py` | Part B.1 pin loads (Table 2), closed form plus a direct 3-D equilibrium check |
| `beam_internal.py` | Part C internal loads and stresses along the beam (section cuts) |
| `beam_diagrams.py` | Figure 2 internal-load diagrams (`fig_beam_internal_loads.png`) |
| `part_d.py` | Part D diagonal loads, diagonal deflection and the rotor-CG deflection terms of Table 6 |

Run any script with `python3 <script>.py` (needs NumPy and Matplotlib).

## Design search and cross-checks

| File | Purpose |
|---|---|
| `DP1_Solver/` | Full analysis model and cheapest-design search over McMaster stock (`dp1-solver.js`, `dp1-search.js`, catalog in `dp1-catalog.js`); open `index.html` to browse results; `node build_results.js` regenerates them |
| `dp1_model.py` | Independent Python hand-calculation model: statics, internal loads, stresses and deflection |
| `dp1_fe_check.py` | 3-D frame finite-element cross-check of `dp1_model.py` (beam elements plus two truss diagonals) |
| `RotorSupport3D.html` | 3-D model of the final design: every force on the beam, the rotor-CG deflection split into its eight causes with the working, and a live explorer that re-runs `DP1_Solver` (report conventions) for any McMaster beam, diagonal, pin and attachment point a, with price and pass/fail. Self-contained; open in a browser |
| `RotorBeamFBD.html`, `RotorSupportFBDLab.html`, `RotorSupportExplorer.html` | Interactive 3-D free-body diagram and design-exploration tools (open in a browser) |

McMaster prices and properties were read in October 2026 and may have changed.
