# DP2 Rotor Shaft: solution plan

Problem statement: `Fall2026DP2-RotorShaft-Rev2.pdf` (due 13 Nov 2026, 11:59 pm). Units below: mm, N, MPa, N·m. Shigley = Budynas & Nisbett, *Shigley's Mechanical Engineering Design* (cite your edition's equation/table numbers).

## 0. The five things that drive this design

1. **The shaft is one constant diameter.** It must be a McMaster precision rotary shaft, and the bearing shoulders are in the plates, not on the shaft. The only stress raisers are the two retaining-ring grooves, the keyway and the cross-pin hole. "Designing the shaft" means picking one diameter and one material, then placing those four features.
2. **The drag dominates.** 560 N acting 500 mm below the lower bearing gives about 281 N·m of bending at the lower bearing. The chain adds only about 8 N·m. The torque is small (19.6 N·m).
3. **There is no torque at the lower bearing.** The torque enters at the pin (in the hub, about 170 mm down) and leaves at the key (sprocket, about 50 mm down). Above the sprocket the shaft carries bending only.
4. **The worst point is the lower retaining-ring groove.** It sits just below the lower bearing, which is close to the peak moment, and it has the highest Kt (Shigley Table 7-1 first estimate: Kt = 5.0 in bending). The keyway end (M ≈ 266 N·m, torque present, Kt about 2.1) is a close second. The pin hole (M ≤ 185 N·m) is third.
5. **The bending is fully reversed and the torque is steady.** The loads are fixed in space while the shaft turns, so a point on the surface sees σa = Kf·32M/(πd³) with σm ≈ 0, and τm = Kfs·16T/(πd³) with τa = 0. Use DE-Goodman for fatigue (n ≥ 1.2, infinite life) and the von Mises maximum for first-cycle yield (n ≥ 3.0).

## 1. Geometry read from Figure 2 (datum y = 0 at the lower bearing line, +y up)

| Item | y (mm) | Source |
|---|---|---|
| Upper bearing | +300 | "300" dimension |
| Lower bearing | 0 | datum |
| Chain force F (centre of toothed part of sprocket) | −50 | "50" |
| Top of rotor hub | −150 | "150" |
| Bottom of rotor hub (hub length 100) | −250 | "250", Req. 10 |
| Rotor CG (120 N) | −350 | "350" |
| COP (560 N drag, +z) | −500 | 350 + "150" |

- Sprocket: overall width 1.125 in (28.6), toothed part 0.284 in (7.2) centred on y = −50, hub on the upper side, so it spans about y = −53.6 to −25.0. The keyway can be at most 28.6 long.
- Pin: must sit in the upper 40 mm of the hub (y = −150 to −190). The hub OD at the pin is 2d.
- Shaft ends: top = upper groove plus enough end margin for the ring's thrust load. Bottom: at least y = −250 (through the hub). Length ≈ 300 + 250 + top margin + bearing half-widths, so **about 560 to 575 mm (22 to 23 in)**.

**Open question A: what the "300" spans.** The extension lines appear to sit at the outer faces of the bearing plates, with the bearings flush to those faces. If the 300 is between bearing centres, R_lower ≈ 1520 N. If it is face to face with 1/2 in bearings, the centres are 287.3 apart and R_lower ≈ 1575 N (+4 %). The groove moment barely changes (276 to 280 N·m). Plan: use bearing centres 300 apart, state it, run the other case as a sensitivity check, and ask on Piazza.

## 2. Loads

| Load | Vector (N or N·m) | Point (y) |
|---|---|---|
| Rotor + blade weight | (0, −120, 0) | −350 (axial, carried by the pin) |
| Sprocket weight | (0, −35, 0) | −50 (axial, carried by the set screw/key) |
| Shaft self-weight | (0, −ρ g A L, 0), about 45 to 55 N | distributed |
| Drag | (0, 0, +560) | −500 |
| Water torque | (0, ±19.63, 0) | at the hub, through the pin |
| Chain force | 161.8 (cos 4.732°, 0, +sin 4.732°) = **(161.25, 0, +13.35)** | −50 |
| Chain torque | equal and opposite to the water torque | sprocket, through the key |

Chain sign: a rotation of −4.732° about +y takes x̂ to (cos, 0, +sin), so F_z = +13.35 N. That also adds to the drag, which is the conservative choice. State it.

Axial path: all the weight goes down to the **upper** ring, which bears on the top of the upper bearing. So the upper ring thrust is 155 N + shaft weight ≈ 205 N. The lower ring carries nothing in normal operation. Both rings must be identical (Req.), so size them for about 205 N.

## 3. Shaft calculations (rubric: 4 pts)

### 3.1 Bearing reactions (x and z)
Simply supported shaft with an overhang. Take moments about the lower bearing:

- z: R_Uz = (560·500 + 13.35·50)/300 = **+935.6 N**, R_Lz = −(560 + 13.35) − 935.6 = **−1508.9 N**
- x: R_Ux = 161.25·50/300 = **+26.9 N**, R_Lx = −161.25 − 26.9 = **−188.1 N**
- Resultants: lower ≈ 1520 N, upper ≈ 936 N. The axial reaction (≈ 205 N) is at the upper ring/bearing.

(Python check, centre-to-centre reading. The face-to-face reading gives lower (−192.9, −1562.9) and upper (31.6, 989.6).)

### 3.2 Where the highest stress is (layout and geometry)
Draw V and M in both the xy and zy planes, combine as M = √(Mx² + Mz²), and draw the torque diagram (nonzero only from the pin to the key). Then go through each candidate section with its own M, T and Kt:

| Section | y | M (N·m) | T (N·m) | Raiser |
|---|---|---|---|---|
| Lower ring groove | ≈ −8 | ≈ 276 | 0 | ring groove, Kt ≈ 5 / Kts ≈ 3 (Table 7-1), or Peterson flat-bottom groove chart with the ring's actual groove r/d, t/r |
| Top of keyway (sled-runner or end-mill end) | ≈ −25 | ≈ 266 | ~0 to 19.6 | keyway, Kt 2.14 / Kts 3.0 end-milled, or 1.7 sled-runner |
| Bottom of keyway | ≈ −54 | ≈ 250 | 19.6 | keyway |
| Pin hole | ≈ −170 | ≤ 185 (conservative: all hub moment taken at the bottom of the hub) | 19.6 | transverse hole, Shigley Fig. A-15-10 (bending), A-15-11 (torsion) with net-section nominal stress |
| Upper ring groove | ≈ +308 | ≈ 0 | 0 | axial only |

Expected answer: **the lower ring groove**. Argue it from the numbers: the highest M times the highest Kt, even though T = 0 there. Taking the full torque at the keyway is conservative.

### 3.3 Total moment and torque at the critical section(s)
Report Mx, Mz, the resultant M and T at the groove and at the keyway (and at the pin hole for completeness).

### 3.4 Design the shaft
1. **Material properties.** Sut comes from the McMaster hardness, capped at HRC 25 (≈ HB 253 → Sut ≈ 3.4·HB ≈ 860 MPa, Shigley Eq. 2-17). **Sy must be a Piazza-approved set**: check Piazza for sets already approved for the shaft family you choose, or post a proposal (Sut must match or exceed the hardness-based value). Candidates: 440C or 416 stainless (no $100 coating penalty), 1566/1045/52100 steel (+$100). No chrome-plated shafts.
2. **Endurance limit.** S'e = 0.5 Sut (≤ 700 MPa). Marin factors: ka (ground surface, a = 1.58, b = −0.085), kb (size, 1.24 d^−0.107), kc = 1 (bending), kd = 1, ke (state the reliability you choose, e.g. 0.814 for 99 %, or 1), kf = 1.
3. **Notch sensitivity.** q and qs from Shigley Figs. 6-20/6-21 at the real notch radius (ring groove root radius from the ring catalogue; keyway r/d ≈ 0.02). Kf = 1 + q(Kt − 1).
4. **Fatigue.** DE-Goodman (Shigley Eq. 7-7/7-8) with σa = Kf·32M/(πd³), τm = Kfs·16T/(πd³) and the small axial σm from the weight: n_f ≥ 1.2.
5. **Yield.** σ'max = √[(σa + σm)² + 3(τa + τm)²] with Kf applied (Shigley Eq. 7-15): n_y = Sy/σ'max ≥ 3.0. *Decision needed:* Shigley Ch. 7 applies Kf here, and that is the conservative choice. Some instructors drop Kt for static loading of ductile parts. Use Kf unless the course says otherwise.
6. **First estimate.** Kf ≈ 4, Se ≈ 320 MPa → d ≈ 35 mm from fatigue. Yield FS 3 with Sy ≈ 650 → d ≈ 37.5 mm. **Expect 1.375 to 1.5 in (35 to 38 mm).** Then iterate with the real Kt, q and kb for each McMaster diameter.
7. **Optional good practice (not required):** slope at the bearings and the deflection at the sprocket. Mention them if the margin is fine.
8. **Cost.** Shaft cost = shaft length × lowest $/length for that part family (usually the longest stock), plus $100 if not stainless. Compare across the diameters and materials that pass.

## 4. Connection hardware (rubric: 4 pts, all FS ≥ 1.2)

### 4.1 Key (stainless, Sy = 0.8 Sut per Req. 7)
- Standard square key for d (Shigley Table 7-6 / ANSI B17.1; for example 3/8 in for d = 1.375 to 1.75 in). McMaster stainless key stock (303/316, read Sut).
- F = T/(d/2) ≈ 19.63/(0.0175) ≈ 1.1 kN.
- Shear: τ = F/(w l) ≤ Ssy/1.2 with Ssy = 0.577 Sy.
- Bearing: σ = F/(l h/2) ≤ Sy/1.2.
- Length l ≤ 28.6 mm (sprocket width). The sprocket is at least as strong as the key (Req. 9), so the key governs.
- Pro-rated cost per key (a key-stock piece cut to length, or a precut key).

### 4.2 Set screw (stainless, presses on the key)
- Axial load to hold is the sprocket weight (35 N) plus any axial bump. Required holding force ≥ 1.2 × 35 N.
- Holding power from Shigley Table 7-4 (socket set screws, seating torque → holding force). Choose the cup point.
- Geometry: it threads through the sprocket hub wall over the key. Hub OD = 2d, so the wall is d/2 minus the keyseat depth in the hub. Length must reach the key top without protruding. Rule of thumb: dia ≈ d/4.
- McMaster 18-8 or 316 stainless set screws; pro-rate the pack price.

### 4.3 Pin (416 stainless, through the hub and shaft)
- Carries the torque (19.63 N·m) and the rotor weight (120 N axial). The drag and its moment go into the hub bore as bearing pressure; state that assumption.
- Double shear at the shaft surface: shear force per plane from the torque F_T = T/d, plus 60 N per plane from the axial weight (perpendicular). τ = √(F_T² + 60²)/(π dp²/4).
- Bearing on the shaft (linearly varying pressure, T = σ dp d²/6), bearing on the hub wall (wall = d/2), and net-section effect on the shaft (already in the pin-hole fatigue check of 3.2).
- Properties: McMaster's listed double-shear strength or 416 SS Sut/Sy for the listed hardness. Pin length = hub OD = 2d. Hole within the upper 40 mm of the hub, with edge distance ≥ about 1.5 dp to the hub top.
- Choose the pin type (press-fit dowel versus slip fit + retention) and give the hole tolerance on the drawing.

### 4.4 Retaining rings (two identical, stainless external rings)
- Thrust ≈ 205 N × 1.2 against McMaster's listed thrust capacity (check both the ring and the groove/shaft-material limit, as the ring supplier gives them).
- Groove dimensions and tolerances (groove dia, width, depth) from the McMaster/ring datasheet go to the drawing and into the groove Kt.
- Top end margin ≥ about 3 × groove depth (supplier rule), which sets the shaft length above the upper groove.
- Lower ring goes just outside the lower bearing (bearing width ≤ 12.7). That fixes the critical-section location y_groove.

## 5. Drawing and BOM (rubric: 1 pt)
- **Drawing (separate PDF, shop-ready):** overall length (± tolerance), stock diameter (callout to the McMaster tolerance), two ring grooves (location, dia, width, tolerances), keyway (width, depth, length, position, ANSI B17.1 tolerances, sled-runner or end-mill end), cross hole (dia + fit tolerance, location, perpendicular through centre), chamfers on both ends, material and McMaster P/N, the coating note if not stainless, title block, units, scale.
- **BOM:** shaft (P/N, length used, $ prorated), key, set screw, pin, 2× ring, all with McMaster P/N and per-item cost. These also go into the Canvas quiz.

## 6. Economy (rubric: 1 pt)
Points come from cost relative to the nominal design (≤ 25 % over for full credit). Most of the cost is the shaft, so: the smallest passing diameter, preferably stainless (no $100), and the cheapest $/in stock. The hardware is a few dollars. Plan a small solver (like DP1_Solver) that sweeps every McMaster precision-shaft diameter × material with an approved property set, applies the groove/keyway/pin checks, and ranks by cost.

## 7. Report layout (grader requirement)
Each rubric section on **consecutive pages**: (1) shaft calcs: reactions, critical location, M & T, shaft design; (2) hardware: key, set screw, pin, rings; (3) drawing + BOM; (4) cost summary. Show formula → substitution → result for every number, with Shigley citations and defined symbols.

## 8. To do / decisions before calculating
- [ ] Check Piazza and Canvas for clarifications and for **approved rotary-shaft property sets**. Propose one if none fit the chosen shaft.
- [ ] Settle open question A (what the 300 spans) and the chain z-sign (+13.35 assumed).
- [ ] Decide on Kf in the yield check (planned: yes, per Shigley Ch. 7).
- [ ] Gather McMaster data: precision rotary shafts (diameters, lengths, $, hardness, material, no chrome); stainless key stock; stainless set screws; 416 SS pins (shear strength, sizes); stainless external retaining rings (groove specs, thrust capacity).
- [ ] Build the solver and checks, then write the report.
