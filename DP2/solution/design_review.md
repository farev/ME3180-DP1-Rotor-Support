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

A7. Report both Shigley's Kf/Kfs shaft yield check and a supplemental Kt/Kts local elastic check; the latter is an added criterion, not a PDF requirement. Use modified Goodman fatigue, machined surface factors at machined features and reliability factor 0.814 (99%). Maintained corrosion protection is assumed. A8. Assembly clearances/axial float are allowed; section moments are taken directly from the moment diagram, as in Shigley Example 7-2, with no added moment margin. A9. Specified dimensions and tolerances control the result; a sharper groove invalidates it.

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
| Keyseat upper end | -24.75 | 266.51 | 19.63 |
| Pin hole, upper edge (cantilever envelope) | -176.81 | 180.99 | 19.63 |
| Upper groove | 300.49 | 0 | 0 |

![moments](/Users/fabianarevalo/Documents/Georgia Tech/ME3180/DP2/solution/figures/moments.png)

For a statically consistent diagram within the hub, use -1820 N at y=-160 mm and +2380 N at y=-240 mm. Their sum is 560 N and their moment about y=0 is -280 N m. This avoids pretending the shaft physically extends to the COP. The pin stress check instead uses the larger full-load cantilever envelope at the hole's upper edge. A 10 mm contact band has average bearing pressure at most 2380/(37.9984 x 10)=6.26 MPa; the shaft-hole mean-stress allowance is 12 MPa.


---

# Shaft design | 4. Groove, fatigue and yield method

Use identical 93576A210 single-turn spiral rings. Catalog groove: diameter 1.456 +/-0.004 in and width 0.031 +0.002/-0 in. The design deliberately uses a tighter, shallower interval within those limits: **diameter 1.4590-1.4600 in, radius 0.0098-0.0100 in**. Smalley permits a maximum 0.010 in groove-bottom radius for diameters over 1 in. Its VS-150 dimensions match this catalog ring geometry. [3,8,9]

```text
dmin = 37.0586 mm
tmax = (38.1000 - 37.0586)/2 = 0.5207 mm
a/t = 1.5122; r/t = 0.4780
Kt = 3.50 (upper rounded chart estimate, Fig. A-15-16 [10])
```

Chart factors use the groove-root diameter. Kt relates nominal stress to the theoretical local elastic peak; Kf=1+q(Kt-1) accounts for notch sensitivity in fatigue. Shigley Eq. (7-15) also uses Kf/Kfs for its shaft yield check. Report that check as primary and retain Kt/Kts as a separate elastic check. The PDF does not expressly require the added criterion. [15]

```text
sqrt(a_N) = 0.246 - 0.00308 Sut + 1.51e-5 Sut^2 - 2.67e-8 Sut^3
q = 1 / [1 + sqrt(a_N)/sqrt(r)]
Sut = 124.7615 ksi; r = 0.0098 in
q = 0.69; Kf = 2.72
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
sigma_N = 4 N/(pi d^2); sigma_m = Kt sigma_N + contact allowance
sigma_max,S = sqrt[(Kf sigma_b + sigma_m)^2 + 3(Kfs tau_t)^2]
sigma_max,E = sqrt[(Kt sigma_b + sigma_m)^2 + 3(Kts tau_t)^2]
ny,S = Sy/sigma_max,S; ny,E = Sy/sigma_max,E
1/nf = sigma_a/Se + sigma_mean,eq/Sut; sigma_a = Kf sigma_b
```

Eq. (7-15) itself omits axial force. Both checks here retain the same small Kt-amplified axial stress and contact allowance as an explicit conservative extension. Kfs=Kts at the keyseat and pin hole; groove torque is zero. The fatigue calculation is unchanged: sigma_mean,eq=sqrt[sigma_m^2+3(Kts tau_t)^2].

The keyway model uses deliberately increased factors Kt=3.0 and Kts=4.0, compared with common nominal end-milled-keyseat estimates 2.14 and 3.0. A key-bearing normal-stress allowance is added to the mean stress. The hole uses the net-section coefficients and matching Kt from Table A-16 [10], with hole/shaft=0.16778; bending A=0.73, Kt=2.11; torsion A=0.86, Kts=1.61. The net section is applied once only.


---

# Shaft design | 5. Both yield checks and sensitivity

```text
Groove: sigma_b = 32(280498)/(pi x 37.0586^3) = 56.139 MPa
Retained axial term sigma_m = 0.661 MPa; T = 0
Shigley: sigma_max,S = 2.71965 sigma_b + sigma_m = 153.339
  ny,S = 606.74/153.339 = 3.9569
Elastic: sigma_max,E = 3.5 sigma_b + sigma_m = 197.146
  ny,E = 606.74/197.146 = 3.0776
```

| Location | ny Shigley | ny elastic | nf |
| --- | --- | --- | --- |
| Lower retaining-ring groove | 3.96 | 3.08 | 1.45 |
| Keyseat upper end (envelope) | 3.63 | 3.63 | 1.44 |
| Transverse pin hole (envelope) | 5.53 | 5.53 | 2.20 |
| Plain lower bearing section | 11.45 | 11.45 | 4.95 |
| Upper retaining-ring groove | 918.28 | 918.28 | 1,301.89 |

| Required Sy for ny=3 (MPa) | Shigley Kf/Kfs | Elastic Kt/Kts |
| --- | --- | --- |
| Lower groove | 460.02 | 591.44 |
| Keyseat | 500.93 | 500.93 |
| Governing shaft requirement | 500.93 | 591.44 |

**The keyseat controls Shigley yielding and fatigue; the lower groove controls the supplemental elastic check.** Its Kf=Kt=3.0 and Kfs=Kts=4.0 make the keyseat result identical in both yield methods. The shaft needs Sy >= 500.93 MPa under the Shigley method and Sy >= 591.44 MPa under the added elastic check; the approved 606.74 MPa satisfies both. These thresholds hold Sut=860.20 MPa and all geometry/contact assumptions fixed.

| Sensitivity | Result / implication |
| --- | --- |
| Sy = 82 ksi = 565.4 MPa (1566 value for D > 1.5 in) | Shigley minimum ny=3.39 (passes); elastic groove ny=2.87 (fails added check). Not applicable: D = 1.500 in is within the 88 ksi range. |
| Notch sensitivity q at the groove | q = 0.69. Fatigue and Shigley yield still pass up to q = 0.91 (Kf = 3.28). With Kf = Kt everywhere, groove nf falls below 1.2. |
| Use unrestricted catalog root tolerance | The root may shrink to 1.452 in, and the notch factor changes. Do not use the current safety factor. |
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

The earlier proposal (Marks handbook averages Sut=703, Sy=598 MPa for 1045) is superseded: the approved 1045 value is 517 MPa. At 517 MPa the previous 1045 design passes the Shigley check (3.11) but not the added elastic check (2.62), and it is sold only as a 120 in stick. The selected 1566 shaft has the same 1.500 in geometry and passes both checks.

## Hardware properties are separate assumptions

For the 18-8 key and screw, use the annealed 304-class baseline Sut=515 MPa and Sy=205 MPa published by ATI for its flat products [12] as a conservative classroom assumption, not a fastener certification. Only the key receives the PDF exception Sy=0.8Sut=412 MPa. For the HRC36 minimum 416 pin, use Sy=760 MPa from Swiss Steel's lower-hardness condition-T range [11]. The pin calculation explicitly identifies this as a typical-property assumption. Ring capacity comes directly from the selected supplier rating.


---

# Shaft design | 7. Cost search and selection

Every McMaster precision rotary shaft from 1-1/4 to 3 in and 30 to 50 mm was read from the catalog on 10 Nov 2026, with the shortest stock at least 21.8 in long. Each was paired with every stainless retaining ring sold for its diameter and run through the same equations as this report (DP2/solver/solver.py; its regression check reproduces this calculation). Groove Kt comes from Fig. A-15-16, digitized, times 1.06, the same rounding used here (3.31 to 3.5). Cost = full stock price + $100 if not stainless + hardware.

| Shaft (stock) | Stock price | Total | Result |
| --- | --- | --- | --- |
| 1045, 1-7/16 in, 4138N22 (24 in) | $55.85 | $168.39 | Fails fatigue at the deeper groove (nf 1.06) |
| 1566, 1-1/4 in, 1346K45 (24 in) | $62.74 | $171.48 | Fails fatigue (nf 0.81) |
| 1045, 35 mm, 4138N66 (1000 mm) | $80.56 | $194.08 | Fails fatigue (nf 0.79) |
| 1045, 1-11/16 in, 4138N27 (24 in) | $76.03 | $202.18 | Passes Shigley (ny 3.87, nf 1.37); fails added elastic check (2.69) |
| <b>1566, 1-1/2 in, 1346K534 (24 in)</b> | <b>$112.69</b> | <b>$222.07</b> | <b>Selected: passes both yield checks and fatigue</b> |
| 1045, 1-15/16 in, 4138N33 (24 in) | $97.65 | $306.55 | Passes; heavy-duty rings $49.11 each |
| 1045, 1-1/2 in, 4138N14 (120 in only) | $306.52 | $415.90 | Passes Shigley only at Sy = 517 MPa |

Excluded without a stress check: keyed shafts (the full-length keyway, or the 4 in and 14 in end keyways on 24 in stock, run through the bearing seats and ring grooves); D-profile shafts (full-length flat); nitride-coated shafts (only the HRC60 case hardness is listed, so no property set can meet item 5); chrome-plated shafts (excluded by Rev2). Plain stainless stops at 1-1/4 in and fails fatigue by a wide margin.

## What the cost claim means

**1346K534 is the lowest-cost McMaster rotary shaft found that passes fatigue, the Shigley yield check and the added Kt elastic check.** 4138N27 is $20.11 cheaper but passes only the Shigley check and needs a 15-7 PH ring with a deeper groove. The selected shaft keeps the 1-1/2 in rings, key and pin, and has the larger margin on notch sensitivity (passes up to q = 0.91 against the calculated 0.69).


---

# Connection hardware | 1. Rectangular key

**18-8 stainless straight key, 3/8 x 3/8 in cross section, cut 1/2 in long.** Specify cut length 12.70 +/-0.05 mm; the key is longer than it is wide, as required. A square is the standard equal-sided rectangular cross section for this shaft size. Cut from 36 in stock 92530A319; width and height tolerance -0.003/0 in. Use the assignment-only relation Sy=0.8 Sut, with proposed Sut=515 MPa for 18-8 stainless: Sy=412 MPa. [6,12]

The sprocket has 28.575 mm overall width and 7.2136 mm tooth thickness. Put the tooth midplane at y=-50 mm and the hub above it: hub extent -46.3932 to -25.0318 mm. The key at y=-36.0 mm fits entirely within the un-toothed hub. Hub OD=2D=76.2 mm. Center the set screw over the key within +/-0.10 mm; the 12.7 mm key fully covers its flat tip. The 22.45 mm slot runs from y=-47.25 to -24.75 mm, ending 0.28 mm above the sprocket face; the shaft keyseat may extend past the hub.

Mill a closed slot 22.45 +/-0.05 mm long and 9.525 +0.0254/-0 mm wide, with semicircular ends. Its minimum straight length is 22.40-9.5504=12.8496 mm, exceeding the key maximum 12.75 mm. Seat depth is 4.7625 +/-0.0254 mm. Deburr the key and clear the keyseat floor corners without removing the working side faces.

```text
Ft = 2T/Dmin = 2(19630)/37.9984 = 1033.201 N
bmin = hmin = 0.372 in = 9.4488 mm
Lmin = 12.650 mm
Minimum hub engagement = hmin - depthmax = 4.6609 mm
tau = Ft/(bmin Lmin) = 8.644 MPa
p = Ft/(engagement x Lmin) = 17.524 MPa
n_shear = Sy/(sqrt(3) tau) = 27.52
n_bearing = Sy/p = 23.51
```

Both exceed 1.2. Mating shaft/hub yield strengths are higher than the key value. Maximum screw preload produces less than 14 MPa average compression over the key footprint. The shaft-fatigue check includes the key bearing pressure as a mean-stress allowance. No credit is taken for the closed slot resisting axial slip.

## Key cost

```text
Ckey = ($28.32 / 36 in)(0.50 in) = $0.3933
```

For comparison, 12 in undersized 18-8 stock costs $10.49, and a precut 1 in key costs $14.38/5=$2.876 each. The cut stock is less expensive. Saw kerf/deburring are not charged under the stated material-only assumption; the nominal design cost used for grading is not supplied.

Cut-length trials with correspondingly shortened slots give shaft fatigue factors 1.336 at 1/8 in, 1.385 at 3/16 in, 1.408 at 1/4 in, 1.436 at 1/2 in. Keys shorter than their 3/8 in width are excluded by the course rule that a key must be longer than it is wide; 1/2 in is the shortest common fraction that satisfies it.


---

# Connection hardware | 2. Set screw

**McMaster 94355A533: 18-8 stainless, flat tip, 1/4-20 UNC, 1/4 in long, 1/8 in hex drive.** The 6.35 mm length is recessed in the 19.05 mm radial hub wall and provides at least 4.5 mm of full engaged thread after runouts. Tap at the key center. The flat tip is suitable for the flat key surface and avoids relying on uncontrolled cup-point penetration. [5]

Assume friction coefficient mu >=0.10 at both the screw/key and key/shaft interfaces, and nut factor K=0.15-0.25. These are assembly assumptions, not catalog guarantees. Tighten to 0.75 +/-0.02 N m. The key and sprocket are both retained through the friction path; capacities at the two series interfaces are not added.

```text
Fmin = Tmin/(Kmax d) = 0.73/(0.25 x 0.00635) = 459.84 N
Fmax = Tmax/(Kmin d) = 0.77/(0.15 x 0.00635) = 808.40 N
Fhold = mu Fmin = 45.98 N
n_slip = Fhold/35 = 1.314 >=1.2
```

For a conservative elastic screening check use Sy=205 MPa for 18-8, root diameter 4.57 mm, and the full 1/8 in hex socket area removed at the critical section. A circumscribed circular socket is removed for the polar-moment estimate. The full installation torque is conservatively applied at this reduced section. The root/tip dimensions are conservative assumptions compatible with the specified standard; verify the supplier drawing before fabrication.

```text
A = pi dr^2/4 - (sqrt(3)/2) AF^2 = 7.673 mm^2
J = pi[dr^4 - (2AF/sqrt(3))^4]/32 = 25.086 mm^4
sigma = Fmax/A = 105.36 MPa
tau = Tmax dr/(2J) = 70.14 MPa
sigma_VM = sqrt(sigma^2+3 tau^2) = 160.80 MPa
ny = 205/sigma_VM = 1.275
```

```text
Thread shear area = 0.5 pi(5.4)(4.5) = 38.17 mm^2
n_thread = (205/sqrt(3))/(Fmax/Athread) = 5.59
Using flat-tip diameter >=3.5 mm: n_tip = 2.44
```

The screw checks exceed 1.2, including installation stress and axial slip. Minimum hub yield is the key yield, 412 MPa, so internal-thread shear is less critical. At the key center the flat tip sits about 14.4 mm below the hub OD; the screw top is recessed about 8.0 mm and remains accessible with a long hex key. Assumed clean contacts must be preserved; lubrication or water ingress that lowers mu invalidates the slip result.

```text
Cscrew = $4.81/25 = $0.1924
```


---

# Connection hardware | 3. Rotor pin

**McMaster 98380A556: 416 stainless dowel pin, 1/4 in diameter x 3 in long.** Nominal length spans the rotor hub OD=2D=3 in. Diameter is +0.0001/+0.0003 in; minimum hardness HRC36; rated double-shear breaking load 7200 lbf. Proposed yield value: 760 MPa, the lower end of Swiss Steel's typical condition-T range (HRC27-31), used conservatively for the harder catalog pin. This is an explicit material assumption, not a supplier-certified yield minimum. The shaft HRC25 cap does not apply to the pin. [4,11]

Place the pin at y=-180 mm, 30 mm below the hub top and within the allowed upper 40 mm. Shaft hole: 6.363-6.375 mm, giving clearance to the 6.35254-6.35762 mm pin. Retain the pin by a measured 0.00254-0.00508 mm diametral interference in one hub wall only; the opposite wall is clearance-fit. This avoids press-fit hoop stress at the shaft's transverse fatigue notch. The hub is assumed at least as strong as the pin, per Rev2.

```text
Ft per shear plane = T/Dmin = 516.601 N
Fa per plane = 120/2 = 60 N
R = sqrt(Ft^2 + Fa^2) = 520.073 N
tau = R/(pi dp^2/4) = 16.422 MPa
Conservative pin bending bound: Mp = R D/2 = 9907.397 N mm
sigma_b = 32 Mp/(pi dp^3) = 394.129 MPa
sigma_VM = 395.154 MPa; ny = 1.923
```

The pin is checked for bending as well as double shear. The D/2 lever-arm bound exceeds the normal distributed-contact lever arm. Using at least 10 mm of full-diameter engagement per hub wall (19.05 mm nominal wall, with generous allowance for pin-end relief), bearing pressure is 8.19 MPa and bearing safety factor is 92.79. A 3/16 in pin would have about 933 MPa bending stress under the same bound and fails the adopted yield criterion.

```text
Interference-fit estimate: p approximately E(delta/d)/2
At delta = 0.00254-0.00508 mm, d=6.35 mm, E=205000 MPa:
  p approximately 41-82 MPa; use pmax=85 MPa.
Bound combined bending/fit normal stress by sigma_b + 2pmax.
VM with fit = 564.85 MPa; ny with fit = 1.35
```

With mu=0.10, pmin=40 MPa and 10 mm engagement, the conservative axial pin-retention force is mu p pi dp Le=797.96 N, far above the pin's own weight. Pin length tolerance/end relief must leave the stated engagement; center it during installation. The 7200 lbf catalog breaking-load ratio is 30.79; this is an additional ultimate check and is not mislabeled as yield safety factor.

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
n_groove_bearing = Sy Acontact / thrust = 70.49
Minimum nominal top end margin = 2.5618 mm
3 x maximum groove depth = 1.5621 mm
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
| Shaft yielding >=3.0 | Shigley minimum 3.634 (keyseat); supplemental elastic minimum 3.078 (groove), at the approved Sy=606.74 MPa. |
| Infinite-life fatigue >=1.2 | Minimum 1.436, at the conservative keyseat envelope. |
| Hardware >=1.2 | Key >23; screw minimum 1.275; pin 1.347 including fit bound; rings >1.2. |
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

[11] 416 typical heat-treated strengths, p.2: [https://swisssteel-group.com/content-media/documents/Data-Sheets/Swiss-Steel-USA-Canada/Stainless-Steel/SwissSteel_416__Stainless__4-21.pdf](https://swisssteel-group.com/content-media/documents/Data-Sheets/Swiss-Steel-USA-Canada/Stainless-Steel/SwissSteel_416__Stainless__4-21.pdf)

[12] ATI 304 flat-product baseline; assumed for 18-8 hardware: [https://www.atimaterials.com/Products/ati-304](https://www.atimaterials.com/Products/ati-304)

[13] Alternative condition warning: [https://www.pmtsco.com/1040-45-turned-polished](https://www.pmtsco.com/1040-45-turned-polished)

[14] 1045 size-dependent cold-drawn properties, section 4.3: [https://www.wakefieldmetals.co.nz/wp-content/uploads/2019/11/steelTechnicalData.pdf](https://www.wakefieldmetals.co.nz/wp-content/uploads/2019/11/steelTechnicalData.pdf)

[15] Shigley 10th ed., Sec.3-13, Eq.(3-48); Sec.7-4, Eqs.(7-15)-(7-16), p.362: [https://www.mechfamily-ju.com/storage/images/files/file_1731443577xeDvd.pdf](https://www.mechfamily-ju.com/storage/images/files/file_1731443577xeDvd.pdf)

Catalog prices were read live in the McMaster browser on 2026-11-08/10. Sources [13] and [14] are kept from the earlier 1045 property review.
