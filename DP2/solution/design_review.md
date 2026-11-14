# Shaft design | 1. Recommendation and assumptions

**Recommended design, Rev P3.** All checks use one diameter, 1.500 in (38.10 mm), from McMaster 1346K534: a 1566 carbon-steel precision rotary shaft, Rockwell C25, bought as a 24 in stick and cut to 554.0 mm. Estimated assignment cost: **$222.07**, including the full price of the stock and the mandatory $100 non-stainless allowance.

| Property / decision | Basis |
| --- | --- |
| Shaft material | 1566 carbon-steel precision rotary shaft, Rockwell C25; turned, ground and polished; OD 1.496-1.500 in; 24 in stock. [2] |
| Sy = 88 ksi = 606.74 MPa | Approved on Piazza for 1566 at Rockwell C25, shaft diameters up to and including 1.5 in. [7] |
| Sut = 860.20 MPa | Not listed on Piazza. Shigley Eq. (2-36), Sut = 3.4 HB, with HRC25 = HB 253 (ASTM E140): 3.4(253) = 860.20 MPa, the minimum the hardness rule allows. |
| Hardness cap | Rockwell C25 is exactly the Rev2 cap; no strength beyond C25 is claimed. |

## Explicit assumptions

A1. Rev2 governs, with the existing P2 class constraint that the key be longer than it is wide. A2. The 300 mm dimension is between the two outside support/bearing faces. Bearings are each 12.7 mm wide, with radial reactions at their midplanes. A3. Water and chain loads are steady in the stationary frame; shaft bending is fully reversed, torque and weights are steady. The given safety factors cover the specified overload objective; no additional shock multiplier is invented.

A4. Rotor/hub bore contact carries transverse drag and its bending couple. The pin carries torque and the 120 N rotor weight. A snug hub bore and contact bands near the hub ends are assumed. A5. Ambient-temperature, low-speed operation below critical speed; the ring rotational rating must not be exceeded. No required operating speed is supplied. A6. Upper ring/bearing carries all downward thrust; both rings are checked for the entire thrust, including conservative unmachined shaft self-weight.

A7. The shaft yield requirement uses Shigley's Kf/Kfs check, Eq. (7-15). The Kt/Kts local elastic peak is also reported, for information only; it is not a PDF requirement. Use modified Goodman fatigue, machined surface factors at machined features and reliability factor 0.814 (99%). Maintained corrosion protection is assumed. A8. Assembly clearances/axial float are allowed; section moments are taken directly from the moment diagram, as in Shigley Example 7-2, with no added moment margin. A9. Specified dimensions and tolerances control the result; a sharper groove invalidates it.

A10. Price basis follows Rev2 item 4: the full price of the shortest stock of the selected part that is long enough to make the shaft (24 in, $112.69), plus per-item prorated hardware, without tax or freight. Key stock is cut and deburred to length on this material-only basis. Pin is selected to span the 3 in rotor-hub OD for straightforward installation/removal. These assumptions delimit the cost comparison; an absolute global minimum across every possible joint configuration has not been proved.


---

# Shaft design | 2. Bearing reactions

```text
Fx = 161.8 cos(4.732 deg) = 161.2485 N
Fz = +161.8 sin(4.732 deg) = 13.3477 N
yL = 6.35 mm; yU = 293.65 mm; L = 287.30 mm
```

A negative rotation about +y takes +x toward +z under the right-hand convention. Thus the chain z component is positive. Use y = 0 at the lower outside face, y positive upward. Chain station: -50 mm; rotor hub: -150 to -250 mm; rotor CG: -350 mm; water COP: -500 mm.

```text
RUx = Fx(56.35)/287.30
RLx = -Fx - RUx
RUz = [560(506.35) + Fz(56.35)]/287.30
RLz = -560 - Fz - RUz
```

| Bearing | Rx (N) | Rz (N) | Radial resultant (N) |
| --- | --- | --- | --- |
| Upper | 31.63 | 989.59 | 990.09 |
| Lower | -192.88 | -1,562.93 | 1,574.79 |

The x and z force sums and both bearing moment balances close numerically. Wshaft = rho g pi D^2 L/4 = 48.62 N. Total downward thrust = 120 + 35 + Wshaft = 203.62 N. Using the full cylinder slightly overestimates the machined shaft weight.

![load_map](/Users/fabianarevalo/Documents/Georgia Tech/ME3180/DP2/solution/figures/load_map.png)


---

# Shaft design | 3. Moments and critical sections

Above the rotor-hub top, the water load can be represented by a 560 N force at y = -500 mm. Below the sprocket, T = 19.63 N m; above its torque-transfer region, T = 0. A conservative full-torque envelope is used throughout the keyseat. The largest nominal bending occurs at the lower bearing, but the lower retaining-ring groove creates the largest local elastic stress.

```text
For -150 <= y < -50: |Mx| = 560(y+500); Mz = 0
For -50 <= y <= yL:
  |Mx| = 560(y+500) + Fz(y+50)
  |Mz| = Fx(y+50)
M = sqrt(Mx^2 + Mz^2)  [N mm]
```

| Section | y (mm) | M (N m) | T (N m) |
| --- | --- | --- | --- |
| Lower bearing center | 6.35 | 284.45 | 0 |
| Lower groove center | -0.49 | 280.50 | 0 |
| Keyseat upper end | -24.65 | 266.57 | 19.63 |
| Pin hole, upper edge (cantilever envelope) | -181.81 | 178.19 | 19.63 |
| Upper groove | 300.49 | 0 | 0 |

![moments](/Users/fabianarevalo/Documents/Georgia Tech/ME3180/DP2/solution/figures/moments.png)

For a statically consistent diagram within the hub, use -1820 N at y=-160 mm and +2380 N at y=-240 mm. Their sum is 560 N and their moment about y=0 is -280 N m. This avoids pretending the shaft physically extends to the COP. The pin stress check instead uses the larger full-load cantilever envelope at the hole's upper edge. A 10 mm contact band has average bearing pressure at most 2380/(37.9984 x 10)=6.26 MPa. That is a radial compressive stress, so, as in Shigley, it is not added to the axial shaft stresses.


---

# Shaft design | 4. Groove, fatigue and yield method

Use identical 93576A210 single-turn spiral rings. Catalog groove: diameter 1.456 +/-0.004 in and width 0.031 +0.002/-0 in. The drawing uses the shallower half of that range: **diameter 1.4560-1.4600 in, radius 0.008-0.010 in**. Both are ordinary CNC lathe limits: a 0.2 or 0.25 mm (0.008 or 0.0098 in) corner-radius grooving insert sets the radius, and standard gauges inspect it. Smalley permits a maximum 0.010 in groove-bottom radius for diameters over 1 in. The calculation takes the worst corner of the callout: deepest root 1.456 in with the smallest radius 0.008 in. Its VS-150 dimensions match this catalog ring geometry. [3,8,9]

```text
dmin = 1.456 in = 36.9824 mm; r = 0.008 in = 0.2032 mm; a = 0.031 in = 0.7874 mm
tmax = (38.1000 - 36.9824)/2 = 0.5588 mm
a/t = 1.4091; r/t = 0.3636
Fig. A-15-16 [10]: r/t = 0.20 curve 4.23, r/t = 0.40 curve 3.43
Kt = 4.23 + (3.43 - 4.23)(0.364 - 0.20)/(0.40 - 0.20) = 3.58
Kt = 3.6 (chart reading to one decimal, as in Shigley Example 7-2)
```

Chart factors use the groove-root diameter. Kt relates nominal stress to the theoretical local elastic peak; Kf=1+q(Kt-1) accounts for notch sensitivity in fatigue. Shigley Eq. (7-15) also uses Kf/Kfs for its shaft yield check. That check is the yield requirement here. The Kt/Kts elastic peak is reported alongside for information; the PDF does not require it. [15]

```text
sqrt(a_N) = 0.246 - 0.00308 Sut + 1.51e-5 Sut^2 - 2.67e-8 Sut^3
q = 1 / [1 + sqrt(a_N)/sqrt(r)]
Sut = 124.7615 ksi; r = 0.008 in (smallest allowed)
q = 0.67; Kf = 2.73
```

```text
Se' = 0.5 Sut
ka = 4.51 Sut^(-0.265) [Sut in MPa, machined]
kb = 1.24 D^(-0.107) [D in mm]
kc = kd = 1; ke = 0.814; miscellaneous = 1
Se = 0.5(860.20)(0.75)(0.84)(0.814) = 221.29 MPa
```

Using the full nominal diameter in kb is slightly conservative relative to the smaller groove root. Plain stock alone uses a ground-surface factor. Fatigue at the keyseat and transverse hole conservatively takes Kf=Kt, avoiding notch-sensitivity credit at those features.

```text
sigma_b = 32 M/(pi d^3); tau_t = 16 T/(pi d^3)
sigma_N = 4 N/(pi d^2); sigma_m = Kt sigma_N
sigma_max,S = sqrt[(Kf sigma_b + sigma_m)^2 + 3(Kfs tau_t)^2]
sigma_max,E = sqrt[(Kt sigma_b + sigma_m)^2 + 3(Kts tau_t)^2]
ny,S = Sy/sigma_max,S; ny,E = Sy/sigma_max,E
1/nf = sigma_a/Se + sigma_mean,eq/Sut; sigma_a = Kf sigma_b
```

Eq. (7-15) itself omits axial force. Both checks here retain the same small Kt-amplified axial stress as an explicit conservative extension. Kfs=Kts at the keyseat and pin hole; groove torque is zero. The fatigue calculation is unchanged: sigma_mean,eq=sqrt[sigma_m^2+3(Kts tau_t)^2].

The keyseat follows ASME B17.1 (Class 1 fit, Machinery's Handbook Tables 4-5 [18]): width 3/8 in +0.002/-0, depth 3/16 in at the side wall with the shaft keyseat up to 0.015 in deeper, floor fillet 1/32 in and key chamfer 3/64 in for a keyseat depth over 1/8 to 1/4 in. Kt and Kts come from Peterson's end-milled keyseat curve fits (Pilkey, Sec. 5.2 [16]), valid for 0.005 <= r/d <= 0.07 [17], at the B17.1 fillet: r/d = (25.4/32)/37.9984 = 0.0209, u = 0.1/(r/d) = 4.787; Kt = 1.426 + 0.1643u - 0.0019u^2 = 2.17; Kts = 1.953 + 0.1434u - 0.0021u^2 = 2.59. At r/d = 0.02 the same fits give 2.20 and 2.62, close to Shigley's 2.14 (Table 7-1) and his 2.62 for torsion without the key. No notch-sensitivity credit is taken at the keyseat (Kf = Kt), because Peterson's q data were not verified for notches deeper than four radii. The hole uses the net-section coefficients and matching Kt from Table A-16 [10], with hole/shaft=0.16785; bending A=0.73, Kt=2.11; torsion A=0.86, Kts=1.61. The net section is applied once only.


---

# Shaft design | 5. Yield checks and sensitivity

```text
Groove: sigma_b = 32(280498)/(pi x 36.9824^3) = 56.486 MPa
Retained axial term sigma_m = 0.682 MPa; T = 0
Shigley: sigma_max,S = 2.73074 sigma_b + sigma_m = 154.933
  ny,S = 606.74/154.933 = 3.9161
Elastic (informational): sigma_max,E = 3.6 sigma_b + sigma_m = 204.034
  ny,E = 606.74/204.034 = 2.9737
```

| Location | ny Shigley | ny elastic | nf |
| --- | --- | --- | --- |
| Lower retaining-ring groove | 3.92 | 2.97 | 1.43 |
| Keyseat upper end (envelope) | 5.61 | 5.61 | 2.02 |
| Transverse pin hole (envelope) | 6.31 | 6.31 | 2.28 |
| Plain lower bearing section | 11.45 | 11.45 | 4.95 |
| Upper retaining-ring groove | 889.10 | 889.10 | 1,260.52 |

| Required Sy for ny=3 (MPa) | Shigley Kf/Kfs | Elastic Kt/Kts (informational) |
| --- | --- | --- |
| Lower groove | 464.80 | 612.10 |
| Keyseat | 324.27 | 324.27 |
| Governing shaft requirement | 464.80 | 612.10 |

**The lower ring groove controls both Shigley yielding and fatigue.** The keyseat follows with ny = 5.61 and nf = 2.02; its Kf = Kt makes its two yield results identical. The shaft needs Sy >= 464.80 MPa under the Shigley method, and the approved 606.74 MPa satisfies it. The informational elastic peak at the worst-case groove would need Sy >= 612.10 MPa for a factor of 3; it gives 2.97, so the local peak stays well below yield. These thresholds hold Sut=860.20 MPa and all geometry/contact assumptions fixed.

| Sensitivity | Result / implication |
| --- | --- |
| Sy = 82 ksi = 565.4 MPa (1566 value for D > 1.5 in) | Shigley minimum ny=5.23 (passes); elastic groove ny=2.77 (informational). Not applicable: D = 1.500 in is within the 88 ksi range. |
| Notch sensitivity q at the groove | q = 0.67. Fatigue still passes up to q = 0.87 (Kf = 3.26), and Shigley yield up to Kf = 3.57. With Kf = Kt everywhere, groove nf falls below 1.2. |
| Use unrestricted catalog root tolerance | The catalog allows a root down to 1.452 in; the drawing stops at 1.456 in. A deeper root raises Kt; do not use the current safety factors. |
| Use an unspecified sharp root | Kt may be substantially higher. The drawing specifies a MINIMUM radius. |

If the approved set changes, rerun the calculations. A lower Sy does not automatically require a larger shaft: first compare it with the threshold for the chosen method. A change in Sut also changes endurance strength and notch sensitivity. No heat treatment has been added to the manufacturing plan.


---

# Shaft design | 6. Approved shaft properties

Rev2 allows only shaft properties approved on Piazza. The instructor posted the approved yield strengths below (10 Nov 2026). No tensile strengths were listed, so each Sut here is the hardness-based minimum required by item 5, Shigley Eq. (2-36): Sut = 3.4 HB, with Rockwell values converted by ASTM E140 and capped at HRC25 (HB 253).

| Approved material (Piazza) | Sy (ksi / MPa) | Sut = 3.4 HB (MPa) | McMaster use |
| --- | --- | --- | --- |
| 1045, Brinell 197 | 75 / 517.1 | 669.8 | 4138N plain rotary shafts |
| 1045, Brinell 190, D <= 2 in | 75 / 517.1 | 646.0 | 6117K partially keyed shafts |
| <b>1566, Rockwell C25, D <= 1.5 in</b> | <b>88 / 606.7</b> | <b>860.2</b> | <b>1346K plain rotary shafts (selected 1346K534)</b> |
| 1566, Rockwell C25, D > 1.5 in | 82 / 565.4 | 860.2 | - |
| 4140, Rockwell C28, D <= 1 in / larger | 120 / 827.4; 110 / 758.4 | 860.2 (HRC25 cap) | 2672N high-strength alloy shafts |

The earlier proposal (Marks handbook averages Sut=703, Sy=598 MPa for 1045) is superseded: the approved 1045 value is 517 MPa. At 517 MPa and Sut = 669.8 MPa the previous 1045 design passes the Shigley yield check (3.11), and fatigue (1.30) with the standard keyseat, but it is sold only as a 120 in stick ($306.52). The selected 1566 shaft has the same 1.500 in geometry and passes yield (3.92) and fatigue (1.43).

## Hardware properties are separate assumptions

For the 18-8 key and screw, use the annealed 304-class baseline Sut=515 MPa and Sy=205 MPa published by ATI for its flat products [12] as a conservative classroom assumption, not a fastener certification. Only the key receives the PDF exception Sy=0.8Sut=412 MPa. The 416 pin is checked against McMaster's rated double-shear breaking strength, so no unapproved pin property is used. Ring capacity comes directly from the selected supplier rating.


---

# Shaft design | 7. Cost search and selection

Every McMaster precision rotary shaft from 1-1/4 to 3 in and 30 to 50 mm was read from the catalog on 10 Nov 2026, with the shortest stock at least 21.8 in long. Each was paired with every stainless retaining ring sold for its diameter and run through the same equations as this report (DP2/solver/solver.py; its regression check reproduces this calculation). Groove Kt comes from Fig. A-15-16, digitized, read to one decimal as in Shigley Example 7-2 (3.58 to 3.6 here). Every groove is evaluated at the catalog-nominal root with the 0.008 in minimum radius. Cost = full stock price + $100 if not stainless + hardware.

| Shaft (stock) | Stock price | Total | Result |
| --- | --- | --- | --- |
| 1045, 1-7/16 in, 4138N22 (24 in) | $55.85 | $168.39 | Fails fatigue at the deeper groove (nf 1.10) |
| 1566, 1-1/4 in, 1346K45 (24 in) | $62.74 | $171.48 | Fails fatigue (nf 0.83) |
| 1045, 35 mm, 4138N66 (1000 mm) | $80.56 | $194.08 | Fails fatigue (nf 0.82) |
| 1045, 1-11/16 in, 4138N27 (24 in) | $76.03 | $202.18 | Passes: Shigley yield 3.91, fatigue 1.38 (groove Kt 4.5, 15-7 PH ring) |
| <b>1566, 1-1/2 in, 1346K534 (24 in)</b> | <b>$112.69</b> | <b>$222.07</b> | <b>Selected: Shigley yield 3.92, fatigue 1.43 (groove Kt 3.6)</b> |
| 1045, 1-15/16 in, 4138N33 (24 in) | $97.65 | $306.55 | Passes; heavy-duty rings $49.11 each |
| 1045, 1-1/2 in, 4138N14 (120 in only) | $306.52 | $415.90 | Passes (yield 3.63, nf 1.30); only sold 120 in long |

Excluded without a stress check: keyed shafts (the full-length keyway, or the 4 in and 14 in end keyways on 24 in stock, run through the bearing seats and ring grooves); D-profile shafts (full-length flat); nitride-coated shafts (only the HRC60 case hardness is listed, so no property set can meet item 5); chrome-plated shafts (excluded by Rev2). Plain stainless stops at 1-1/4 in and fails fatigue by a wide margin.

## What the cost claim means

**4138N27 ($202.18) is the lowest-cost McMaster rotary shaft found that meets every requirement; 1346K534 ($222.07) is selected.** Both pass fatigue and the Shigley yield check. 1346K534 costs $19.89 more for a slightly larger fatigue margin (1.43 against 1.38) and a milder groove (Kt 3.6 against 4.5); yield margins are about equal (3.91 against 3.92). It also keeps the standard 1-1/2 in key, pin and 18-8 spiral rings, where 4138N27 needs a 15-7 PH ring with a deeper groove. The groove still passes fatigue up to q = 0.87, against the calculated 0.67.


---

# Connection hardware | 1. Rectangular key

**18-8 stainless straight key, 3/8 x 3/8 in cross section, cut 1/2 in long.** Specify cut length 12.70 h14 (+0/-0.43 mm, ISO 286); the key is longer than it is wide, as required. A square is the standard equal-sided rectangular cross section for this shaft size. Cut from 36 in stock 92530A319; width and height tolerance -0.003/0 in. Use the assignment-only relation Sy=0.8 Sut, with proposed Sut=515 MPa for 18-8 stainless: Sy=412 MPa. [6,12]

The sprocket has 28.575 mm overall width and 7.2136 mm tooth thickness. Put the tooth midplane at y=-50 mm and the hub above it: hub extent -46.3932 to -25.0318 mm. The key at y=-36.0 mm fits entirely within the un-toothed hub. Hub OD=2D=76.2 mm. Center the set screw over the key within +/-0.10 mm; the 12.7 mm key fully covers its flat tip. The 22.225 mm nominal slot runs from y=-47.11 to -24.89 mm (up to -24.65 at its longest and widest), ending at most 0.38 mm above the sprocket face; the shaft keyseat may extend past the hub.

Mill a closed slot with semicircular ends to ASME B17.1 Class 1: width 9.525 +0.051/-0 mm (3/8 in +0.002/-0) and depth 3/16 in at the side wall, dimensioned as S = D - Y - H/2 = 1.5000 - 0.0238 - 0.1875 = 1.2887 in (32.733 mm) +0.000/-0.015 in, where Y = [D - sqrt(D^2 - W^2)]/2 is the chordal height. Floor corners R 1/32 in from a corner-radius end mill (B17.1 Table 5). B17.1 gives no length tolerance, so the length follows ISO 286 IT14 (0.43 mm for 10-18 mm): key 12.70 h14 (+0/-0.43) and slot end-centre distance 12.70 H14 (+0.43/-0). The straight walls of the slot equal the end-centre distance, so the slot is never shorter than the key, with no added padding; overall slot length is 12.70 + 9.525 = 22.225 mm nominal. McMaster key stock has square edges (catalog drawing), so chamfer the four long edges of the cut key 3/64 in x 45 deg (B17.1 Table 5), larger than the 1/32 in fillet so the key seats flat.

```text
Ft = 2T/Dmin = 2(19630)/37.9984 = 1033.201 N
bmin = hmin = 0.372 in = 9.4488 mm
Lmin = 12.270 mm
Bearing height = min(hmin - depth_side,max, depth_side,min) - chamfer
  = min(9.4488 - (4.7625 + 0.3810), 4.7625) - 1.1906 = 3.1147 mm
tau = Ft/(bmin Lmin) = 8.912 MPa
p = Ft/(engagement x Lmin) = 27.035 MPa
n_shear = Sy/(sqrt(3) tau) = 26.69
n_bearing = Sy/p = 15.24
```

Both exceed 1.2. Mating shaft/hub yield strengths are higher than the key value. Maximum screw preload produces less than 14 MPa average compression over the key footprint. No credit is taken for the closed slot resisting axial slip.

## Key cost

```text
Ckey = ($28.32 / 36 in)(0.50 in) = $0.3933
```

For comparison, 12 in undersized 18-8 stock costs $10.49, and a precut 1 in key costs $14.38/5=$2.876 each. The cut stock is less expensive. Saw kerf/deburring are not charged under the stated material-only assumption; the nominal design cost used for grading is not supplied.

Cut-length trials with correspondingly shortened slots give shaft fatigue factors 2.042 at 1/8 in, 2.038 at 3/16 in, 2.035 at 1/4 in, 2.021 at 1/2 in. Keys shorter than their 3/8 in width are excluded by the course rule that a key must be longer than it is wide; 1/2 in is the shortest common fraction that satisfies it.


---

# Connection hardware | 2. Set screw

**McMaster 94355A533: 18-8 stainless, flat tip, 1/4-20 UNC-3A, 1/4 in long, 1/8 in hex drive, ASME B18.3, Rockwell B80.** It threads radially through the sprocket hub at the key centre and presses on the flat top of the key. McMaster lists no tightening torque for it, so the torque is set by what the screw must hold. [5]

**Load.** The key sits in a closed keyseat, so the slot ends hold it axially and the key carries the torque. The screw only keeps the sprocket from sliding down the shaft under its weight, W_s = 35 N. The screw presses the key with F; the reaction presses the hub bore on the opposite side of the shaft with the same F, so two contacts resist sliding: holding force = 2 mu F. Friction mu = 0.15, the low end of Shigley Table 8-5 for dry steel on steel (Shigley 11th ed.).

```text
F_req = n W_s/(2 mu) = 1.2(35)/(2 x 0.15) = 140.0 N
T_req = K F_req d = 0.2(140.0)(6.35) = 177.8 N mm   (Shigley Eq. 8-27, K = 0.2, Table 8-15)
Preload scatter at a given torque: +/-25% (Unbrako [20])
T_spec = T_req/0.75 = 237.1 N mm, specified as 0.24 N m
F = T_spec/(K d) x (1 -/+ 0.25) = 141.7 to 236.2 N
n_slip = 2(0.15)(141.7)/35 = 1.215 >= 1.2
```

**Screw strength** at the high end, F = 236.22 N with T = 0.24 N m, using S_y = 205 MPa (ATI 304 annealed [12]), the 1/4-20 root area A_r = 0.0269 in^2 (Shigley Table 8-2) and the ASME B18.3 1/8 in hex socket and 0.118 in minimum flat-point diameter (Unbrako [20]). Section through the socket, full F and T:

```text
dr = sqrt(4 A_r/pi) = 4.701 mm; A = A_r - (sqrt(3)/2)AF^2 = 8.625 mm^2
J = pi dr^4/32 - (5 sqrt(3)/8)(AF/sqrt(3))^4 = 35.713 mm^4
sigma = F/A = 27.39 MPa; tau = T dr/(2J) = 15.80 MPa
sigma' = sqrt(sigma^2 + 3 tau^2) = 38.71 MPa; n_y = 205/sigma' = 5.30
```

Thread root, Shigley Sec. 8-2 stress element (Eq. 8-12 set) with the first thread carrying 0.38F and 0.38T, n_t = 1, p = 1.27 mm:

```text
sigma_x = 6(0.38F)/(pi dr p) = 28.72; sigma_y = -4F/(pi dr^2) = -13.61
tau_yz = 16T/(pi dr^3) = 11.77; tau_zx = 4(0.38T)/(pi dr^2 p) = 4.14 MPa
sigma' (Eq. 5-14) = 43.22 MPa; n = 205/sigma' = 4.74
Flat tip on key: p = F/(pi 3.00^2/4) = 33.48 MPa; n_tip = 205/p = 6.12
```

Every screw check exceeds 1.2; the thread root governs at 4.74. The specified torque is 3% of Unbrako's 70 in lbf seating torque for 1/4 in stainless set screws, so the shallow socket of this 1/4 in long screw is not a concern. At the key centre the flat tip sits about 14.9 mm below the hub OD; the screw top is recessed about 8.5 mm and remains accessible with a long hex key.

```text
Cscrew = $4.81/25 = $0.1924
```


---

# Connection hardware | 3. Rotor pin

**McMaster 98380A556: 416 stainless dowel pin, 1/4 in diameter x 3 in long** (ASME B18.8.2 standard series, diameter +0.0001/+0.0003 in, HRC 36 minimum, double shear breaking strength 7200 lbf). Its length spans the rotor hub OD = 2D = 3 in. Rev2 item 5 allows only Piazza-approved material properties and none is listed for the pin, so the pin is checked against McMaster's rated strength rather than an assumed yield strength. [4]

**Location.** Rev2 item 10 leaves the hub's upper 40 mm for the pin, y = -150 to -190 mm. The shaft moment at the hole, 560(500 + y), falls as the pin moves down, so the pin sits as low as a round number allows with the whole hole in that zone: y = -185 mm, 35 mm below the hub top (hole edges at -181.81 and -188.19 mm; centre 65.50 mm from the bottom end of the shaft).

**Fits.** Shaft hole 6.35 F7 (ISO 286: +0.013/+0.028 mm, 6.363-6.378 mm), a slip fit with 0.0054-0.0255 mm clearance, so the press fit puts no hoop stress at the shaft's transverse notch. Hub holes 0.2495-0.2500 in, the ASME B18.8.2 press-fit hole for standard-series 1/4 in pins in steel [21], giving 0.0025-0.0203 mm interference in both hub walls.

```text
Ft per shear plane = T/Dmin = 19630/37.9984 = 516.6 N
Fa per plane = W_r/2 = 120/2 = 60 N
R = sqrt(Ft^2 + Fa^2) = 520.1 N per plane
Double-shear load = 2R = 1040.1 N
Rated double shear breaking strength = 7200 lbf = 32027 N
n = 32027/1040.1 = 30.8 >= 1.2
```

The rating is a breaking load, so this factor is against fracture, which is the only pin strength McMaster publishes. The hub is at least as strong as the pin (Rev2 item 10), so hub bearing does not govern; the shaft side of the hole is checked as the Table A-16 pin-hole section in Part 4.

```text
Cpin = $4.69 each
```


---

# Connection hardware | 4. Retaining rings

**Two identical McMaster 93576A210 rings:** 18-8 stainless, one turn, for 1.500 in shafts, thickness 0.025 +/-0.002 in. Catalog thrust rating 4950 lbf. Both are checked against the full downward thrust 203.62 N, even though the upper ring carries the normal gravity load. [3]

```text
Catalog capacity = 4950(4.44822) = 22,018.70 N
Catalog allowable-load ratio = capacity / thrust = 108.13
```

Do not infer the ring material's yield strength from the thrust rating. Smalley lists its corresponding geometric VS-150 ring shear rating with a built-in factor of 3 and groove rating separately. The McMaster stainless rating is used as the supplier's allowable capacity; the large load ratio exceeds the required 1.2 without needing to reinterpret it as a coupon yield strength. [8]

## Groove wall and end-margin checks

```text
Minimum groove depth = (37.9984 - 37.0840)/2 = 0.4572 mm
Usable flat radial contact after radius = depthmin - 0.254 = 0.2032 mm
Acontact = pi droot x usable_contact
n_groove_bearing = Sy Acontact / thrust = 70.35
Minimum nominal top end margin = 2.5618 mm
3 x maximum groove depth = 1.6764 mm
```

Allowing the stated 0.10 mm end-length and 0.05 mm groove-location tolerances still leaves more than 2.41 mm end margin, exceeding 3t=1.5621 mm. The lower groove is far from either shaft end. An end-lip shear check and an annular cantilever-lip bending check give factors greater than 500 and 700 respectively; therefore the end material is adequate. [9]

```text
Aedge = pi droot e
tau_edge = thrust/Aedge
sigma_edge,b = 6 thrust depth/(pi droot e^2)
```

## Bearing interface and axial freedom

The ring must contact the rotating bearing inner race, with clearance to stationary housing and outer race. Corresponding ring radial width is 0.088 +/-0.004 in. Using maximum groove depth, a 0.50 mm maximum inner-race chamfer remains below the approximately 0.60 mm geometric recommendation 0.375(b-depth). Specify this requirement to the bearing designer. Bearing faces must be perpendicular to the shaft; eccentric ring loading is not assumed.

The drawing's groove widths allow axial clearance. At nominal ring thickness, the full 300 mm outside-face bearing stack has roughly 0.50 mm total axial freedom when the rings bear against their loaded groove walls. Ring, groove and position tolerances produce a small range around this value; no preload is imposed. Bearing-stack tolerance must be coordinated before release. A 0.5 mm shift of the drag line changes the section moments by 560(0.5) = 0.28 N m, about 0.1%, which the safety factors cover. Low-speed operation is assumed; Smalley lists 5900 rpm for this geometry, but final bearing/speed selection is outside Rev2's supplied data.

```text
Crings = 2($10.26/5) = $4.1040
```


---

# Drawing and bill of materials

The separate shaft-only drawing is **DP2_shaft_drawing_PROVISIONAL.pdf**; its editable 2-D source is **DP2_shaft_P3.dxf**. In the assembled packet, the drawing immediately follows this bill of materials, keeping the required section consecutive. Only the shaft is drawn, as required. The geometry is dimensioned for review/quotation, with release conditional on the stated interface assumptions.

| Item / McMaster part | Quantity and prorating | Cost ($) |
| --- | --- | --- |
| 1566 precision rotary shaft, 1-1/2 x 24 in<br/><b>1346K534</b> | 1 (cut to 554 mm) | 112.69 |
| 18-8 single-turn spiral rings<br/><b>93576A210</b> | 2 | 4.10 |
| 416 dowel pin, 1/4 x 3 in<br/><b>98380A556</b> | 1 | 4.69 |
| 18-8 flat-tip set screw, 1/4-20 x 1/4 in<br/><b>94355A533</b> | 1 | 0.19 |
| 18-8 key stock, 3/8 square; cut 1/2 in<br/><b>92530A319</b> | 0.50 in of 36 in | 0.39 |
| Required coating/inspection allowance<br/><b>Assignment item 5</b> | 1 | 100.00 |

```text
Shaft length = 554/25.4 = 21.8110 in, cut from 24 in stock
Cshaft = full price of 1346K534 (shortest stock long enough) = $112.69
Total before rounding = $222.069733
Machining charge for shaft grooves, hole, keyway = $0 by Rev2
```

The displayed total is rounded only after summing unrounded line values. The shaft is charged at the full stock price; hardware is prorated per item, so buying whole packages costs more. Freight, tax and unlisted fabrication charges are not estimated. No purchase has been made.

## Requirement audit

| Rev2 requirement | Evidence / status |
| --- | --- |
| Shaft yielding >=3.0 | Shigley minimum 3.916 (keyseat), at the requirement method; informational elastic peak minimum 2.974 (groove). At the approved Sy=606.74 MPa. |
| Infinite-life fatigue >=1.2 | Minimum 1.433, at the lower ring groove (deepest root, smallest radius). |
| Hardware >=1.2 | Key 15.24 (bearing); set screw slip 1.21, strength 4.74; pin 30.8 (against McMaster's double-shear rating); rings >1.2. |
| Eligible material and source | 1566 precision rotary shaft (HRC25, within the cap); stainless key/screw/rings; 416 pin; all McMaster part numbers. |
| No chrome; coating allowance | Uncoated selected shaft; $100 added. |
| Approved shaft material properties | Sy = 88 ksi from the Piazza-approved list (1566, HRC25, D <= 1.5 in); Sut from Eq. (2-36). |
| Separate CAD PDF / assembled drawing | Provided; no hardware drawings. |
| Nominal-cost score thresholds | Cannot determine: nominal design cost is not supplied. |


---

# Review record | Sources

[1] Assignment: Fall2026DP2-RotorShaft-Rev2.pdf, supplied local file; requirements and dimensions.

[2] Selected shaft: [https://www.mcmaster.com/1346K534/](https://www.mcmaster.com/1346K534/)

[3] Retaining rings: [https://www.mcmaster.com/93576A210/](https://www.mcmaster.com/93576A210/)

[4] 416 pin family: [https://www.mcmaster.com/98380A556/](https://www.mcmaster.com/98380A556/)

[5] Set screw: [https://www.mcmaster.com/94355A533/](https://www.mcmaster.com/94355A533/)

[6] Key stock: [https://www.mcmaster.com/92530A319/](https://www.mcmaster.com/92530A319/)

[7] Approved shaft properties: Instructor post on the course Piazza, 10 Nov 2026 (approved yield strengths for DP2 shaft materials).

[8] Corresponding spiral ring geometry: [https://www.smalley.com/ring/vs-150](https://www.smalley.com/ring/vs-150)

[9] Groove radii, edge margins, contact geometry: [https://www.smalley.com/engineering-support/ring-design](https://www.smalley.com/engineering-support/ring-design)

[10] Shigley 8th ed., Tables A-15 and A-16 (original excerpt): [https://disbasicoupiita.wordpress.com/wp-content/uploads/2013/03/factor-concentracion-esfuerzos.pdf](https://disbasicoupiita.wordpress.com/wp-content/uploads/2013/03/factor-concentracion-esfuerzos.pdf)

[11] Not cited in Rev P3 (former 416 pin property source; the pin is now checked against the McMaster rating): Swiss Steel 416 data sheet

[12] ATI 304 flat-product baseline; assumed for 18-8 hardware: [https://www.atimaterials.com/Products/ati-304](https://www.atimaterials.com/Products/ati-304)

[13] Alternative condition warning: [https://www.pmtsco.com/1040-45-turned-polished](https://www.pmtsco.com/1040-45-turned-polished)

[14] 1045 size-dependent cold-drawn properties, section 4.3: [https://www.wakefieldmetals.co.nz/wp-content/uploads/2019/11/steelTechnicalData.pdf](https://www.wakefieldmetals.co.nz/wp-content/uploads/2019/11/steelTechnicalData.pdf)

[15] Shigley 10th ed., Sec.3-13, Eq.(3-48); Sec.7-4, Eqs.(7-15)-(7-16), p.362: [https://www.mechfamily-ju.com/storage/images/files/file_1731443577xeDvd.pdf](https://www.mechfamily-ju.com/storage/images/files/file_1731443577xeDvd.pdf)

[16] Keyseat Kt/Kts fits from Pilkey, Peterson's Stress Concentration Factors, 2nd ed., Sec. 5.2, as reproduced (with ASME B17.1 chamfer guidance) in Szatmary, ASEE 2023 paper 39427: [https://nemo.asee.org/public/conferences/327/papers/39427/download](https://nemo.asee.org/public/conferences/327/papers/39427/download)

[17] Validity 0.005 <= r/d <= 0.07 for the keyseat fit; Jordaan, R&D J. SAIMechE 41 (2025): [https://scielo.org.za/pdf/rd/v41/01.pdf](https://scielo.org.za/pdf/rd/v41/01.pdf)

[18] ASME B17.1-1967 (R2013) Tables 4 (Class 1 fit) and 5 (fillet and chamfer), as reproduced in Machinery's Handbook 31st ed., pp. 2555-2556: [https://online.flippingbook.com/view/954046886/1233/](https://online.flippingbook.com/view/954046886/1233/)

[19] ISO 286-1 standard tolerance grade IT14 (0.43 mm for 10-18 mm): ISO 286-1:2010, Table 1

[20] Unbrako Socket Products Engineering Guide: socket set screw dimensions (ASME B18.3), seating torques, +/-25% preload note: [https://www.unbrako.com/images/downloads/engguide.pdf](https://www.unbrako.com/images/downloads/engguide.pdf)

[21] ASME B18.8.2 press-fit hole sizes for hardened ground machine dowel pins (standard series): [https://www.engineersedge.com/hardware/press_fit_holes_dowel_pins_15885.htm](https://www.engineersedge.com/hardware/press_fit_holes_dowel_pins_15885.htm)

Catalog prices were read live in the McMaster browser on 2026-11-08/10. Sources [13] and [14] are kept from the earlier 1045 property review.
