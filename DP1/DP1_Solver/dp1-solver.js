/* dp1-solver.js — ME3180 DP1 (Fall 2026) microhydro rotor support: analysis + cheapest-design search.
 *
 * Units inside: mm, N, MPa (= N/mm^2), N·mm.  Angles in rad.  Prices in USD.
 * Frame (Figure 2): origin at pin O on the beam neutral axis, +x along the beam toward the fixed structure,
 * +y up, +z toward the viewer of the Figure-1 side view ("Front").  Right-handed.
 *
 * Internal-load sign convention: resultant that the part of the beam to the RIGHT of a cut exerts on the part
 * to the LEFT (N = Fx, Vy = Fy, Vz = Fz, Tx = Mx, My, Mz about the section centroid).  Then
 *   v'' = Mz/(E Iz),  w'' = -My/(E Iy),  phi_x' = Tx/(G J),  u' = N/(E A),  shear slopes  Vy/(G Asy), Vz/(G Asz).
 *
 * Works in a browser (window.DP1) and in Node (module.exports).
 */
(function (root) {
  'use strict';

  const IN = 25.4;                 // mm per inch
  const PSI = 6.894757e-3;         // MPa per psi
  const KSI = 6.894757;            // MPa per ksi
  const GRAV = 9.81;               // m/s^2
  const LBF = 4.448222;            // N per lbf

  // ------------------------------------------------------------------ problem data (from the DP1 statement)
  const PROB = {
    rho_w: 1000, v_w: 2.5, rotorH: 0.5, rotorW: 0.5,        // req 1
    eta_h: 0.30, eta_e: 0.82, rpm: 285,                     // req 2
    PD1_in: 9.554, PD2_in: 3.038, N1: 60, N2: 19,           // req 4, Fig. 2
    drag: 560,                                              // req 5, +z
    W_rotor: 150, W_gen: 120,                               // req 8
    x_rot: -1200, x_left: -1300,                            // Fig. 2, req 6 (axis 100 mm from left end)
    cg_below: 350, cop_below: 500, chain_below: 50,         // Fig. 2 (below the beam's bottom face)
    yB: 500,                                                // Fig. 2: B is 500 mm above O
    C_in: 39.49,                                            // Fig. 2 bottom view: sprocket centre distance
    t_br: 0.5 * IN, Sy_br: 35 * KSI,                        // req 10: 1/2 in aluminium brackets, 35 ksi
    FS: 2.0, deflLimit: 0.7, aMax: 800, minWidth: 4 * IN,   // req 11, 12, Fig. 2, req 13
    overhang: 50,                                           // Fig. 2 bottom view: beam right end is 50 mm past pin O (beam 1350 mm long)
    cutTol: 1.0,                                            // mm: saw-cut length + hole-position tolerance allowed for in the plate end distance
  };
  PROB.x_gen = PROB.x_rot + PROB.C_in * IN;                 // -196.95 mm

  // ------------------------------------------------------------------ materials (defaults; catalog items may override Sy)
  // E, G in MPa; rho in kg/mm^3; Sy/Su minimums in MPa.  G = E / (2(1+nu)).
  const MATERIALS = {
    ss304:  { name: '304/304L stainless steel', E: 193000, nu: 0.29, rho: 8.00e-6, Sy: 205, Su: 515, note: 'ASTM A276/A240 annealed minimums (Sy 30 ksi, Su 75 ksi)' },
    ss316:  { name: '316/316L stainless steel', E: 193000, nu: 0.29, rho: 8.00e-6, Sy: 205, Su: 515, note: 'ASTM A276/A240 annealed minimums' },
    al6061: { name: '6061-T6 aluminum', E: 68900, nu: 0.33, rho: 2.70e-6, Sy: 241.3, Su: 290, note: 'McMaster prints 35 ksi yield (ASTM B221 min for T6 extrusions)' },
    al6063: { name: '6063 aluminum', E: 68900, nu: 0.33, rho: 2.70e-6, Sy: 110.3, Su: 152, note: 'McMaster prints 16 ksi yield (T52)' },
    al5052: { name: '5052-H32 aluminum', E: 70300, nu: 0.33, rho: 2.68e-6, Sy: 193, Su: 228, note: 'ASTM B209 H32 min Sy 23 ksi; typical 28 ksi' },
    ss188:  { name: '18-8 stainless steel (pin)', E: 193000, nu: 0.29, rho: 8.00e-6, Sy: 205, Su: 515, note: 'annealed 302/304 minimum, ASTM A276/A580 (30 / 75 ksi); McMaster prints only a minimum hardness, so no cold-work credit is taken' },
    ss174_floor: { name: '17-4 PH stainless, condition not printed', E: 196500, nu: 0.27, rho: 7.75e-6, Sy: 517, Su: 793, note: 'H1150-M floor (75 / 115 ksi, ASTM A564), used when McMaster gives no condition or hardness' },
    ss174_h1150: { name: '17-4 PH stainless, H1150', E: 196500, nu: 0.27, rho: 7.75e-6, Sy: 724, Su: 931, note: 'ASTM A564 H1150 minimums (105 / 135 ksi)' },
    ss174_h1025: { name: '17-4 PH stainless, H1025', E: 196500, nu: 0.27, rho: 7.75e-6, Sy: 1000, Su: 1069, note: 'ASTM A564 H1025 minimums (145 / 155 ksi)' },
    ss174_h900:  { name: '17-4 PH stainless, H900', E: 196500, nu: 0.27, rho: 7.75e-6, Sy: 1172, Su: 1310, note: 'ASTM A564 H900 minimums (170 / 190 ksi)' },
  };
  for (const k in MATERIALS) { const m = MATERIALS[k]; m.G = m.E / (2 * (1 + m.nu)); }

  // ------------------------------------------------------------------ small vector helpers
  const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
  const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
  const scl = (a, s) => [a[0] * s, a[1] * s, a[2] * s];
  const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  const norm = a => Math.hypot(a[0], a[1], a[2]);
  const hyp2 = a => Math.hypot(a[0], a[1]);

  function solveLinear(A, b) {           // Gaussian elimination with partial pivoting (small systems)
    const n = b.length, M = A.map((r, i) => [...r, b[i]]);
    for (let c = 0; c < n; c++) {
      let p = c; for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[p][c])) p = r;
      [M[c], M[p]] = [M[p], M[c]];
      for (let r = 0; r < n; r++) if (r !== c) { const f = M[r][c] / M[c][c]; for (let k = c; k <= n; k++) M[r][k] -= f * M[c][k]; }
    }
    return M.map((r, i) => r[n] / r[i]);
  }

  // ------------------------------------------------------------------ power and chain (Part A)
  function powerAndChain() {
    const A = PROB.rotorH * PROB.rotorW;                         // m^2, swept (projected) area
    const P_fluid = 0.5 * PROB.rho_w * A * PROB.v_w ** 3;         // W
    const P_mech = PROB.eta_h * P_fluid;
    const P_elec = PROB.eta_e * P_mech;
    const omega = PROB.rpm * 2 * Math.PI / 60;                   // rad/s
    const T_rotor = P_mech / omega * 1000;                       // N·mm, water torque on rotor about +y
    const R1 = PROB.PD1_in * IN / 2, R2 = PROB.PD2_in * IN / 2;  // mm
    const T_chain = T_rotor / R1;                                // N, tight side (slack side 0, req 7)
    const rpm_gen = PROB.rpm * PROB.N1 / PROB.N2;
    // chain length check for the 39.49 in centre distance (#40, 1/2 in pitch)
    const Cp = PROB.C_in / 0.5;
    const links = 2 * Cp + (PROB.N1 + PROB.N2) / 2 + ((PROB.N1 - PROB.N2) / (2 * Math.PI)) ** 2 / Cp;
    const v_chain = omega * R1 / 1000;                           // m/s
    return { A, P_fluid, P_mech, P_elec, omega, T_rotor, R1, R2, T_chain, rpm_gen, links, v_chain, T_gen: T_chain * R2 };
  }
  const PW = powerAndChain();

  // Tight span: rotor turns +y (CCW from the top) and drives a sprocket at larger x.  On the z<0 side the rotor-sprocket
  // surface moves toward -x, i.e. it pulls the chain from the generator toward the rotor -> that span is tight.
  function chainGeometry(yChain) {
    const C = PROB.x_gen - PROB.x_rot;
    const s = -1;                                                // tight span on -z (rear)
    const sphi = (PW.R1 - PW.R2) / C, cphi = Math.sqrt(1 - sphi * sphi);
    const n = [sphi, 0, s * cphi];                               // centre -> tangent point (both sprockets)
    const u = [cphi, 0, -s * sphi];                              // along the tight span, rotor -> generator
    const P1 = [PROB.x_rot + PW.R1 * n[0], yChain, PW.R1 * n[2]];
    const P2 = [PROB.x_gen + PW.R2 * n[0], yChain, PW.R2 * n[2]];
    const F1 = scl(u, PW.T_chain);                               // chain on rotor sprocket (toward generator)
    const F2 = scl(u, -PW.T_chain);                              // chain on generator sprocket
    const torqueOnRotor = cross(sub(P1, [PROB.x_rot, yChain, 0]), F1)[1];   // must be -T_rotor
    return { C, s, sphi, cphi, phi: Math.asin(sphi), n, u, P1, P2, F1, F2, torqueOnRotor };
  }

  // ------------------------------------------------------------------ sections
  // Rounded-rectangle helpers (outer b x h, corner radius r): area and second moment about the axis parallel to b.
  function rrArea(b, h, r) { return b * h - (4 - Math.PI) * r * r; }
  function rrI(b, h, r) {             // about centroidal axis parallel to b (extent h)
    const y0 = h / 2 - r;
    const Idef = y0 * y0 * (1 - Math.PI / 4) * r * r + 2 * y0 * r ** 3 / 6 + (1 / 3 - Math.PI / 16) * r ** 4;
    return b * h ** 3 / 12 - 4 * Idef;
  }
  // Beam section. W = z-width (horizontal, >= 4 in), H = y-height.  kind 'tube' (wall t, outer corner radius ro) or 'solid'.
  // Cowper (1966) shear coefficient for a thin box: shear parallel to h, flanges b (Timoshenko beam).
  function cowperBox(h, b, nu) {
    const m = b / h, n = b / h;
    return 10 * (1 + nu) * (1 + 3 * m) ** 2 / ((12 + 72 * m + 150 * m * m + 90 * m ** 3) + nu * (11 + 66 * m + 135 * m * m + 90 * m ** 3) + 10 * n * n * ((3 + nu) * m + 3 * m * m));
  }
  function beamSection(kind, W, H, t, ro, ri_, nu) {
    nu = nu || 0.3;
    const s = { kind, W, H, t: t || 0, ro: ro || 0 };
    if (kind === 'tube') {
      const ri = ri_ != null ? ri_ : Math.max(s.ro - t, 0); s.ri = ri;
      s.A = rrArea(W, H, s.ro) - rrArea(W - 2 * t, H - 2 * t, ri);
      s.Iz = rrI(W, H, s.ro) - rrI(W - 2 * t, H - 2 * t, ri);           // vertical (x-y) bending
      s.Iy = rrI(H, W, s.ro) - rrI(H - 2 * t, W - 2 * t, ri);           // lateral (x-z) bending
      const rm = (s.ro + ri) / 2 > t / 2 ? (s.ro + ri) / 2 : 0; s.rm = rm;
      s.Am = (W - t) * (H - t) - (4 - Math.PI) * rm * rm;               // area enclosed by wall mid-line
      s.pm = 2 * (W - t) + 2 * (H - t) - (8 - 2 * Math.PI) * rm;        // mid-line perimeter
      s.J = 4 * s.Am * s.Am * t / s.pm;                                 // Bredt-Batho, uniform wall
      s.tauPerT = 1 / (2 * s.Am * t);                                   // tau = T/(2 Am t)
      s.kapY = cowperBox(H, W, nu); s.kapZ = cowperBox(W, H, nu);         // Cowper shear coefficients
      s.Asy = s.kapY * s.A; s.Asz = s.kapZ * s.A;                       // stiffness shear areas
      s.Qy = (W * H * H / 8 - (W - 2 * t) * (H - 2 * t) ** 2 / 8);      // first moment for Vy at the NA (sharp)
      s.Qz = (H * W * W / 8 - (H - 2 * t) * (W - 2 * t) ** 2 / 8);
      s.bWebY = 2 * t; s.bWebZ = 2 * t;
      s.tBearing = t;                                                   // pin bears on one wall per side
    } else {
      s.A = W * H; s.Iz = W * H ** 3 / 12; s.Iy = H * W ** 3 / 12;
      const b = Math.max(W, H), c = Math.min(W, H);
      s.J = b * c ** 3 * (1 / 3 - 0.21 * (c / b) * (1 - c ** 4 / (12 * b ** 4)));   // Roark Table 10.1 case 4
      s.tauPerT = (3 * b + 1.8 * c) / (b * b * c * c);                              // Roark Table 10.1 case 4
      s.kapY = s.kapZ = 10 * (1 + nu) / (12 + 11 * nu); s.Asy = s.kapY * s.A; s.Asz = s.kapZ * s.A;
      s.Qy = W * H * H / 8; s.Qz = H * W * W / 8; s.bWebY = W; s.bWebZ = H;
      s.tBearing = W;
    }
    return s;
  }
  // Net section through the pin hole (hole along z at y = 0, diameter dh).
  function netSection(sec, dh) {
    const n = Object.assign({}, sec);
    if (sec.kind === 'tube') {
      const t = sec.t, zc = sec.W / 2 - t / 2;
      n.A = sec.A - 2 * dh * t;
      n.Iz = sec.Iz - 2 * t * dh ** 3 / 12;
      n.Iy = sec.Iy - 2 * (dh * t ** 3 / 12 + dh * t * zc * zc);
    } else {
      n.A = sec.A - dh * sec.W; n.Iz = sec.Iz - sec.W * dh ** 3 / 12; n.Iy = sec.Iy - dh * sec.W ** 3 / 12;
    }
    return n;
  }

  // ------------------------------------------------------------------ geometry for one configuration
  function geometry(beam, plateT, a, dh, overhang, fl) {
    const H = beam.sec.H, W = beam.sec.W;
    fl = fl || 0;                                    // assembly float between an outer member and the beam/bracket face
    const g = {
      a, H, W, dh, overhang, fl,
      x_left: PROB.x_left, x_right: overhang, Lbeam: overhang - PROB.x_left,
      y_cg: -(H / 2 + PROB.cg_below), y_cop: -(H / 2 + PROB.cop_below), y_chain: -(H / 2 + PROB.chain_below),
      z_br: W / 2 + fl + PROB.t_br / 2,              // bracket mid-plane at O (brackets outside the beam walls)
      z_d: W / 2 + plateT / 2,                       // plate mid-plane: plates bear on the outside of the beam walls
      z_w: beam.sec.kind === 'tube' ? W / 2 - beam.sec.t / 2 : null,   // tube wall mid-plane
      z_bB: W / 2 - PROB.t_br / 2,                   // B-bracket mid-plane (brackets inboard of the plates)
      theta: Math.atan2(PROB.yB, a), Lpp: Math.hypot(a, PROB.yB),
    };
    g.u = [Math.cos(g.theta), Math.sin(g.theta), 0];   // unit vector A -> B
    g.A_f = [-a, 0, g.z_d]; g.A_r = [-a, 0, -g.z_d];
    g.B_f = [0, PROB.yB, g.z_d]; g.B_r = [0, PROB.yB, -g.z_d];
    return g;
  }

  // ------------------------------------------------------------------ applied loads on the beam system
  // Each: name, r (application point), F, C (couple), xt (x where it is transmitted into the beam axis), group.
  function appliedLoads(g, beamMat, beamSec, Wp_each) {
    const ch = chainGeometry(g.y_chain);
    const q = beamMat.rho * GRAV * beamSec.A;      // N/mm self weight
    const L = [
      { key: 'Wrot', name: 'Rotor assembly weight (at CG)', r: [PROB.x_rot, g.y_cg, 0], F: [0, -PROB.W_rotor, 0], C: [0, 0, 0], xt: PROB.x_rot },
      { key: 'D', name: 'Water drag on rotor (at COP)', r: [PROB.x_rot, g.y_cop, 0], F: [0, 0, PROB.drag], C: [0, 0, 0], xt: PROB.x_rot },
      { key: 'Tw', name: 'Water torque on rotor (couple)', r: [PROB.x_rot, g.y_cop, 0], F: [0, 0, 0], C: [0, PW.T_rotor, 0], xt: PROB.x_rot },
      { key: 'Ch1', name: 'Chain tight span on rotor sprocket', r: ch.P1, F: ch.F1, C: [0, 0, 0], xt: PROB.x_rot },
      { key: 'Ch2', name: 'Chain tight span on generator sprocket', r: ch.P2, F: ch.F2, C: [0, 0, 0], xt: PROB.x_gen },
      { key: 'Wgen', name: 'Generator + sprocket weight', r: [PROB.x_gen, g.H / 2, 0], F: [0, -PROB.W_gen, 0], C: [0, 0, 0], xt: PROB.x_gen },
      { key: 'Wpf', name: 'Front plate half-weight (at A)', r: g.A_f, F: [0, -Wp_each / 2, 0], C: [0, 0, 0], xt: -g.a },
      { key: 'Wpr', name: 'Rear plate half-weight (at A)', r: g.A_r, F: [0, -Wp_each / 2, 0], C: [0, 0, 0], xt: -g.a },
    ];
    const Wb = q * g.Lbeam, xc = (g.x_left + g.x_right) / 2;
    return { loads: L, q, Wb, xc, chain: ch };
  }

  // ------------------------------------------------------------------ statics (6 unknowns)
  // unknowns: Ox_f, Ox_r, Oy (total; half per bracket, req 10), Oz (front bracket face), F_f, F_r (plate axial, + tension)
  function statics(g, AL) {
    const cols = [];
    const wrench = (r, F) => [...F, ...cross(r, F)];
    cols.push(wrench([0, 0, g.z_br], [1, 0, 0]));
    cols.push(wrench([0, 0, -g.z_br], [1, 0, 0]));
    { const w1 = wrench([0, 0, g.z_br], [0, 0.5, 0]), w2 = wrench([0, 0, -g.z_br], [0, 0.5, 0]); cols.push(w1.map((v, i) => v + w2[i])); }
    cols.push(wrench([0, 0, PROB.minWidth / 2], [0, 0, 1]));          // z contact force at O (no moment arm in x,y)
    cols.push(wrench(g.A_f, g.u));
    cols.push(wrench(g.A_r, g.u));
    const Am = [0, 1, 2, 3, 4, 5].map(i => cols.map(c => c[i]));
    let SF = [0, 0, 0], SM = [0, 0, 0];
    for (const L of AL.loads) { SF = add(SF, L.F); SM = add(SM, add(cross(L.r, L.F), L.C)); }
    SF = add(SF, [0, -AL.Wb, 0]); SM = add(SM, cross([AL.xc, 0, 0], [0, -AL.Wb, 0]));
    const x = solveLinear(Am, [...SF, ...SM].map(v => -v));
    const [Ox_f, Ox_r, Oy, Oz, F_f, F_r] = x;
    const R = {
      Ox_f, Ox_r, Oy, Oz, F_f, F_r, SF, SM,
      O_f: [Ox_f, Oy / 2, Oz], O_r: [Ox_r, Oy / 2, 0],
      A_f: add(scl(g.u, F_f), [0, 0, 0]), A_r: add(scl(g.u, F_r), [0, 0, 0]),
    };
    // residual check
    let rF = [...SF], rM = [...SM];
    const reac = [[[0, 0, g.z_br], R.O_f], [[0, 0, -g.z_br], R.O_r], [g.A_f, R.A_f], [g.A_r, R.A_r]];
    for (const [r, F] of reac) { rF = add(rF, F); rM = add(rM, cross(r, F)); }
    R.residual = Math.max(...rF.map(Math.abs), ...rM.map(v => Math.abs(v) / 1000));
    R.My_bracket = g.z_br * (Ox_f - Ox_r);          // couple about y carried at O by the bracket pair
    R.My_plates = g.z_d * (F_f - F_r) * g.u[0];      // couple about y carried by the plate pair at A
    R.Mx_plates = -g.z_d * (F_f - F_r) * g.u[1];     // couple about x carried by the plate pair at A
    return R;
  }

  // ------------------------------------------------------------------ internal loads at a cut
  // side: '+' = limit from the right of x (loads AT x belong to the left part), '-' = limit from the left.
  function makeInternal(g, AL, R) {
    const pts = AL.loads.map(L => ({ r: L.r, F: L.F, C: L.C, xt: L.xt }));
    pts.push({ r: [0, 0, g.z_br], F: R.O_f, C: [0, 0, 0], xt: 0 });
    pts.push({ r: [0, 0, -g.z_br], F: R.O_r, C: [0, 0, 0], xt: 0 });
    pts.push({ r: g.A_f, F: R.A_f, C: [0, 0, 0], xt: -g.a });
    pts.push({ r: g.A_r, F: R.A_r, C: [0, 0, 0], xt: -g.a });
    const q = AL.q, xL = g.x_left, xR = g.x_right;
    return function internal(x, side) {
      let F = [0, 0, 0], M = [0, 0, 0];
      for (const p of pts) {
        if (p.xt < x || (p.xt === x && side === '+')) {
          F = add(F, p.F);
          M = add(M, add(cross([p.r[0] - x, p.r[1], p.r[2]], p.F), p.C));
        }
      }
      const l = Math.min(Math.max(x, xL), xR) - xL;   // self weight of the left part
      F = add(F, [0, -q * l, 0]);
      M = add(M, [0, 0, q * l * l / 2 + q * l * Math.max(x - xR, 0)]);
      return { N: -F[0], Vy: -F[1], Vz: -F[2], Tx: -M[0], My: -M[1], Mz: -M[2] };
    };
  }

  // ------------------------------------------------------------------ elastic beam relative to an O-clamped frame
  // Integrates from x = 0 toward x_rot through breakpoints; Simpson with 5 nodes per segment is exact for the
  // piecewise-quadratic moments / piecewise-linear shears produced by point loads plus uniform self-weight.
  function beamElastic(g, beam, internal) {
    const sec = beam.sec, m = beam.mat;
    const EIz = m.E * sec.Iz, EIy = m.E * sec.Iy, GJ = m.G * sec.J, EA = m.E * sec.A;
    const GAy = m.G * sec.Asy, GAz = m.G * sec.Asz;
    const bps = [0, PROB.x_gen, -g.a, PROB.x_rot].filter((v, i, arr) => arr.indexOf(v) === i).sort((p, q) => q - p);
    // state at x=0 (clamped frame)
    let st = { x: 0, thz: 0, wpb: 0, phi: 0, u: 0, vb: 0, vs: 0, wb: 0, ws: 0 };
    const at = { '0': Object.assign({}, st) };
    for (let k = 0; k < bps.length - 1; k++) {
      const xb = bps[k], xa = bps[k + 1], h = (xb - xa) / 4;
      const P = [0, 1, 2, 3, 4].map(i => xa + i * h);
      const IL = P.map((x, i) => internal(x, i === 0 ? '+' : (i === 4 ? '-' : '+')));
      const kz = IL.map(l => l.Mz / EIz), ky = IL.map(l => -l.My / EIy), kt = IL.map(l => l.Tx / GJ), ka = IL.map(l => l.N / EA);
      const gy = IL.map(l => l.Vy / GAy), gz = IL.map(l => l.Vz / GAz);
      const simp = (f, i0, i1, i2, hh) => hh / 3 * (f[i0] + 4 * f[i1] + f[i2]);
      // rotations at P4 (= st), P2, P0
      const thz4 = st.thz, thz2 = thz4 - simp(kz, 2, 3, 4, h), thz0 = thz4 - simp(kz, 0, 2, 4, 2 * h);
      const wp4 = st.wpb, wp2 = wp4 - simp(ky, 2, 3, 4, h), wp0 = wp4 - simp(ky, 0, 2, 4, 2 * h);
      const phi0 = st.phi - simp(kt, 0, 2, 4, 2 * h);
      const u0 = st.u - simp(ka, 0, 2, 4, 2 * h);
      const vb0 = st.vb - (2 * h) / 3 * (thz0 + 4 * thz2 + thz4);
      const wb0 = st.wb - (2 * h) / 3 * (wp0 + 4 * wp2 + wp4);
      const vs0 = st.vs - simp(gy, 0, 2, 4, 2 * h), ws0 = st.ws - simp(gz, 0, 2, 4, 2 * h);
      st = { x: xa, thz: thz0, wpb: wp0, phi: phi0, u: u0, vb: vb0, vs: vs0, wb: wb0, ws: ws0 };
      at[String(xa)] = Object.assign({}, st);
    }
    return { at, EIz, EIy, GJ, EA };
  }

  // ------------------------------------------------------------------ core structural analysis for one (beam, a, plate thickness, plate weight)
  function core(beam, plateT, a, Wp_each, dh, overhang, fl) {
    const g = geometry(beam, plateT, a, dh, overhang, fl);
    const AL = appliedLoads(g, beam.mat, beam.sec, Wp_each);
    const R = statics(g, AL);
    const internal = makeInternal(g, AL, R);
    const el = beamElastic(g, beam, internal);
    const A = el.at[String(-a)], Rt = el.at[String(PROB.x_rot)];
    return { g, AL, R, internal, el, atA: A, atRot: Rt };
  }

  // ------------------------------------------------------------------ deflection of the rotor CG (compatibility with the plates)
  // delta_f, delta_r = plate elongations (+ = longer).  Rigid rotation of the beam about O: (thx, 0, thz).
  //   thx = thy(A) cot(theta) - phi(A) + (delta_f - delta_r) / (2 z_d sin(theta))   (phi(A): twist of A relative to O, ~0)
  //   thz = [u(A) cos(theta) + v(A) sin(theta) + (delta_f + delta_r)/2] / (a sin(theta))
  // u_CG = ( u(xr) - (thz_el(xr) + thz) y_cg ,  v(xr) + thz x_r ,  w(xr) + (phi(xr) + thx) y_cg )
  function cgDeflection(c, delta_f, delta_r) { return cgFromVals(c.g, c.atA, c.atRot, delta_f, delta_r); }
  function cgFromVals(g, atA, atRot, delta_f, delta_r) {
    const s = Math.sin(g.theta), co = Math.cos(g.theta), cot = co / s;
    const y = g.y_cg, xr = PROB.x_rot, a = g.a;
    const thyA = -atA.wpb;                                // section rotation about +y at A (bending only)
    const vA = atA.vb + atA.vs, uA = atA.u;
    const thx_cpl = thyA * cot;
    const thx_pl = (delta_f - delta_r) / (2 * g.z_d * s);
    const thz_bend = atA.vb * s / (a * s), thz_shear = atA.vs * s / (a * s), thz_ax = uA * co / (a * s);
    const thz_pl = (delta_f + delta_r) / 2 / (a * s);
    const comps = [
      { key: 'bend_xy', name: 'Beam bending in x-y (vertical), supports O and A', d: [-(atRot.thz + thz_bend) * y, atRot.vb + thz_bend * xr, 0] },
      { key: 'bend_xz', name: 'Beam bending in x-z (lateral), clamped at O', d: [0, 0, atRot.wb] },
      { key: 'couple', name: 'Roll from beam slope about y at A (plates re-align)', d: [0, 0, thx_cpl * y] },
      { key: 'twist', name: 'Beam twist between A and the rotor', d: [0, 0, (atRot.phi - atA.phi) * y] },
      { key: 'plate_diff', name: 'Roll from unequal plate stretch (front vs rear)', d: [0, 0, thx_pl * y] },
      { key: 'plate_mean', name: 'Pitch from mean plate stretch', d: [-thz_pl * y, thz_pl * xr, 0] },
      { key: 'shear', name: 'Beam shear deformation (Timoshenko)', d: [-thz_shear * y, atRot.vs + thz_shear * xr, atRot.ws] },
      { key: 'axial', name: 'Beam axial strain', d: [atRot.u - thz_ax * y, thz_ax * xr, 0] },
    ];
    const tot = [0, 1, 2].map(i => comps.reduce((S, cc) => S + cc.d[i], 0));
    return { comps, total: tot, mag: norm(tot), thx: thx_cpl + thx_pl - atA.phi, thz: thz_bend + thz_shear + thz_ax + thz_pl, thyA, thx_cpl, thx_pl, thz_pl, delta_f, delta_r };
  }

  // ------------------------------------------------------------------ pin joint: the pin as a beam through its member stack
  // Stack (z from + to -): outer front [t_o] | float g | inner front [t_i] | hollow | inner rear [t_i] | float g | outer rear [t_o]
  //   or (solid beam):     outer front [t_o] | float g | solid inner [w] | float g | outer rear [t_o]
  // Po_f, Po_r = in-plane forces (x, y) that the OUTER members put on the pin (front at +z_o, rear at -z_o).
  // Inner-member forces follow from the pin's own equilibrium (sum of forces and of moments about its centre):
  //   P_if + P_ir = -(P_of + P_or),   z_i (P_if - P_ir) = -z_o (P_of - P_or).
  // Bearing is uniform through each member's thickness (AFFDL-TR-69-42 Eq. 9-13 basis, no peaking credit).
  // Solid inner member: each face is a semi-infinite beam on an elastic foundation (Hetényi 1946), k = kFactor * E_member.
  // Exact piecewise integration; returns max |V|, max |M| (vector magnitudes) and, if asked, a profile for plotting.
  function pinJointExact(spec, wantProfile) {
    const { Po_f, Po_r, t_o, z_o, inner } = spec;
    const S = [-(Po_f[0] + Po_r[0]), -(Po_f[1] + Po_r[1])];
    const D = [Po_f[0] - Po_r[0], Po_f[1] - Po_r[1]];
    const zInO = z_o - t_o / 2;
    let Pi_f, Pi_r, qEdge = null;
    if (inner.kind === 'solid') {
      const beta = Math.pow(inner.k / (4 * inner.EIpin), 0.25);
      const gap = Math.max(zInO - inner.w / 2, 0);
      const side = (P) => {
        const Pm = hyp2(P), M0 = Pm * (t_o / 2 + gap);
        let mx = M0; const NS = 90, prof = [];
        for (let i = 0; i <= NS; i++) { const x = (Math.PI / beta) * i / NS, e = Math.exp(-beta * x);
          const m = e * (M0 * (Math.cos(beta * x) + Math.sin(beta * x)) + (Pm / beta) * Math.sin(beta * x)); if (m > mx) mx = m; prof.push({ x, m }); }
        return { M: mx, q0: 2 * beta * (Pm + beta * M0), V: Pm, prof };
      };
      const sf = side(Po_f), sr = side(Po_r);
      Pi_f = [-Po_f[0], -Po_f[1]]; Pi_r = [-Po_r[0], -Po_r[1]]; qEdge = Math.max(sf.q0, sr.q0);
      const out = { Pi_f, Pi_r, Vmax: Math.max(sf.V, sr.V), Mmax: Math.max(sf.M, sr.M), qEdge, endV: 0, endM: 0, beta, okLen: beta * inner.w / 2 >= Math.PI, model: 'BOEF' };
      if (wantProfile) {
        out.prof = [];
        for (const p of sf.prof) out.prof.push({ z: inner.w / 2 - p.x, V: null, M: Math.abs(p.m) });
        for (const p of sr.prof.slice().reverse()) out.prof.push({ z: -inner.w / 2 + p.x, V: null, M: Math.abs(p.m) });
      }
      return out;
    }
    const k = z_o / inner.z_i;
    Pi_f = [(S[0] - k * D[0]) / 2, (S[1] - k * D[1]) / 2];
    Pi_r = [(S[0] + k * D[0]) / 2, (S[1] + k * D[1]) / 2];
    const zTopI = inner.z_i + inner.t_i / 2, zBotI = inner.z_i - inner.t_i / 2;
    const uni = (P, t) => [P[0] / t, P[1] / t];
    const pieces = [{ L: t_o, q: uni(Po_f, t_o), tag: 'outer front' }];
    if (zInO - zTopI > 1e-9) pieces.push({ L: zInO - zTopI, q: [0, 0], tag: 'float' });
    pieces.push({ L: inner.t_i, q: uni(Pi_f, inner.t_i), tag: 'inner front' });
    pieces.push({ L: 2 * zBotI, q: [0, 0], tag: 'hollow' });
    pieces.push({ L: inner.t_i, q: uni(Pi_r, inner.t_i), tag: 'inner rear' });
    if (zInO - zTopI > 1e-9) pieces.push({ L: zInO - zTopI, q: [0, 0], tag: 'float' });
    pieces.push({ L: t_o, q: uni(Po_r, t_o), tag: 'outer rear' });
    let V = [0, 0], M = [0, 0], Vmax = 0, Mmax = 0, z = z_o + t_o / 2, zM = z;
    const prof = wantProfile ? [{ z, V: 0, M: 0 }] : null;
    for (const pc of pieces) {
      const L = pc.L, q = pc.q, NS = 24;
      for (let i = 1; i <= NS; i++) {
        const s = L * i / NS;
        const Vs = [V[0] + q[0] * s, V[1] + q[1] * s];
        const Ms = [M[0] + V[0] * s + q[0] * s * s / 2, M[1] + V[1] * s + q[1] * s * s / 2];
        const vv = hyp2(Vs), mm = hyp2(Ms);
        if (vv > Vmax) Vmax = vv; if (mm > Mmax) { Mmax = mm; zM = z - s; }
        if (prof) prof.push({ z: z - s, V: vv, M: mm });
      }
      M = [M[0] + V[0] * L + q[0] * L * L / 2, M[1] + V[1] * L + q[1] * L * L / 2];
      V = [V[0] + q[0] * L, V[1] + q[1] * L];
      z -= L;
    }
    return { Pi_f, Pi_r, Vmax, Mmax, zM, qEdge, endV: hyp2(V), endM: hyp2(M), prof, model: 'uniform bearing' };
  }

  // ------------------------------------------------------------------ joint flexibility (optional sensitivity; Huth 1986 single-shear form)
  function huthC(t1, E1, t2, E2, d, Ef) {
    const a = 2 / 3, b = 3.0, n = 1;
    return Math.pow((t1 + t2) / (2 * d), a) * (b / n) * (1 / (t1 * E1) + 1 / (n * t2 * E2) + 1 / (2 * t1 * Ef) + 1 / (2 * n * t2 * Ef));
  }

  // ------------------------------------------------------------------ hole size and tolerance (hand-removable clearance fit)
  // Hole_min = d_pin,max + c_min (c_min about the ANSI B4.1 RC7 minimum: 0.0020 in for 0.40-0.71 in, 0.0025 in for 0.71-1.19 in,
  // 0.0016 in for 0.24-0.40 in); hole tolerance H8 (+0.0009 / +0.0010 / +0.0012 in).  Drilled undersize, then reamed.
  function holeFor(pin) {
    const dmax = pin.d_in + (pin.tolPlus_in || 0);
    const dmin = pin.d_in + (pin.tolMinus_in || 0);
    const band = pin.d_in <= 0.40 ? { c: 0.0016, h: 0.0009 } : pin.d_in <= 0.71 ? { c: 0.0020, h: 0.0010 } : { c: 0.0025, h: 0.0012 };
    const lo = Math.ceil((dmax + band.c) * 10000 - 1e-6) / 10000, hi = +(lo + band.h).toFixed(4);
    return { lo_in: lo, hi_in: hi, d_mm: hi * IN, nominal_in: pin.d_in, dmax_in: dmax, dmin_in: dmin,
      cmin_in: +(lo - dmax).toFixed(4), cmax_in: +(hi - dmin).toFixed(4), H8_in: band.h };
  }

  // ------------------------------------------------------------------ derived geometry of a design (hole, edge distances, cut length, grips)
  function derive(design, opts) {
    const { beam, plate, pin, a } = design;
    const hole = holeFor(pin), dh = hole.d_mm, d = pin.d_in * IN;
    const dMin = (pin.d_in + (pin.tolMinus_in || 0)) * IN;  // stresses use the smallest pin the tolerance allows
    const e_req = 2 * dh;                                   // req 9
    const overhang = PROB.overhang;                         // beam end past O (mm), fixed by Fig. 2
    const e_end = Math.ceil(e_req + PROB.cutTol);           // plate end distance: 2 d_hole + saw-cut/hole-position tolerance
    const bMin = plate.b - (plate.widthTol != null ? plate.widthTol : 0);   // narrowest plate the stock tolerance allows
    const Lpp = Math.hypot(a, PROB.yB), Lcut = Lpp + 2 * e_end;
    const Wp = plate.mat.rho * GRAV * plate.b * plate.t * Lcut;
    // Grips.  O: the fixed brackets are spaced W + 2 fl (fl = bracket clearance).  A and B: the plates sit on the beam wall /
    // B-bracket faces, so the nominal stack is W + 2 t.  Extra pin length at A and B is filled with stainless washers under
    // the pin head (fitted until one more would stop the retainer engaging); what is left is axial play, and that play can
    // open up entirely between one plate and the face it bears on, so it is the float used in the A and B pin-bending checks.
    const fl = opts.float;
    const grips = { O: beam.sec.W + 2 * PROB.t_br + 2 * fl, A: beam.sec.W + 2 * plate.t };
    grips.B = grips.A;
    const usable = pin.usable_in * IN;
    const wash = washerPlan(pin, usable - grips.A);
    const playAB = wash.play;                               // worst-case residual axial play at A and B (mm)
    const db = pin.bore_in != null ? pin.bore_in * IN : (pin.hollow ? 0.5 * dMin : 0);
    const Apin = Math.PI * (dMin * dMin - db * db) / 4, Zpin = Math.PI * (dMin ** 4 - db ** 4) / (32 * dMin);
    const ri = db / 2, ro = dMin / 2, kShear = (4 / 3) * (ro * ro + ro * ri + ri * ri) / (ro * ro + ri * ri);   // tau_max = k V / A
    return { hole, dh, d, dMin, e_req, overhang, e_end, bMin, Lpp, Lcut, Wp, grips, usable, wash, playAB, db, Apin, Zpin, kShear };
  }

  // Washer plan for the extra pin length at A and B (same at both): choose the cheapest stainless washer and the largest count that
  // still lets the retainer engage with the thickest washers of the lot; report the worst residual play (thinnest washers).
  function washerPlan(pin, extra) {
    const none = { count: 0, perJoint: 0, cost: 0, washer: null, play: Math.max(extra, 0) };
    if (extra <= 0.5) return none;
    const list = pin.washers || (pin.washer ? [pin.washer] : []);
    let best = null;
    for (const w of list) {
      const tMax = (w.t_max_in || w.t_in * 1.09) * IN, tMin = (w.t_min_in || w.t_in * 0.91) * IN;   // McMaster: 0.078 in nominal is 0.071-0.085 in
      const n = Math.max(0, Math.floor((extra - 0.25) / tMax));
      const play = extra - n * tMin, count = 2 * n;
      const cost = count ? Math.ceil(count / (w.pkg || 1)) * w.price : 0;
      const cand = { count, perJoint: n, cost, washer: count ? w : null, play, tMin, tMax };
      if (!best || cand.play < best.play - 0.3 || (Math.abs(cand.play - best.play) <= 0.3 && cand.cost < best.cost)) best = cand;
    }
    return best || none;
  }

  // ------------------------------------------------------------------ the shared check set (used by evaluate and by the search screen)
  // env: { beam, plate, pin, a, g, R, Wp, dv (derive), opts }.  add(...) records a check; in screening mode it throws on failure.
  function memberChecks(env, add) {
    const { beam, plate, pin, g, R, Wp, dv, opts } = env;
    const FS = PROB.FS, sec = beam.sec, d = dv.d, dh = dv.dh;
    const Sy_b = beam.Sy, Sy_p = plate.Sy, Sy_pin = pin.mat.Sy;
    // ---- geometry / requirement checks (cheap first)
    add('Geometry', 'Beam z-width >= 4 in (req 13)', PROB.minWidth, sec.W + 1e-9, 'mm', null, `W = ${(sec.W / IN).toFixed(3)} in`, 'geom');
    add('Geometry', 'Beam: hole centre to top/bottom faces >= 2 d_hole (req 9; pin on the neutral axis)', dv.e_req, sec.H / 2, 'mm', null, `H/2 = ${(sec.H / 2).toFixed(1)} mm, 2 d_hole = ${dv.e_req.toFixed(1)} mm`, 'geom');
    add('Geometry', 'Beam end (50 mm past O, Fig. 2) >= 2 d_hole from the O hole (req 9)', dv.e_req, PROB.overhang, 'mm', null, `2 d_hole = ${dv.e_req.toFixed(1)} mm`, 'geom');
    add('Geometry', 'Plate: hole centre to both long edges >= 2 d_hole at the narrowest stock width (req 9)', 2 * dv.e_req, dv.bMin, 'mm', null, `b = ${plate.b.toFixed(1)} mm nominal, ${dv.bMin.toFixed(1)} mm minimum`, 'geom');
    add('Geometry', 'Plate: hole centre to plate end >= 2 d_hole after cut tolerance (req 9)', dv.e_req, dv.e_end - PROB.cutTol, 'mm', null, `end distance ${dv.e_end} mm − ${PROB.cutTol} mm tolerance`, 'geom');
    add('Geometry', 'Diagonal attaches within 800 mm of O', g.a, PROB.aMax, 'mm', null, `a = ${g.a} mm`, 'geom');
    add('Geometry', 'Pin usable length spans every stack (O: W + 2 t_br + 2 clearance; A, B: W + 2 t + washers)', Math.max(dv.grips.O, dv.grips.A + dv.wash.perJoint * (dv.wash.tMax || 0)), dv.usable, 'mm', null,
      `grip O ${(dv.grips.O / IN).toFixed(3)} in, A/B ${(dv.grips.A / IN).toFixed(3)} in + ${dv.wash.perJoint} washers, usable ${(pin.usable_in).toFixed(3)} in`, 'geom');
    // ---- plate (diagonal) forces at the pins
    const u = g.u, Ap = plate.b * plate.t, Ep = plate.mat.E, Lpp = g.Lpp;
    const Pf_A = [u[0] * R.F_f, u[1] * R.F_f - Wp / 2], Pr_A = [u[0] * R.F_r, u[1] * R.F_r - Wp / 2];
    const Pf_B = [-u[0] * R.F_f, -u[1] * R.F_f - Wp / 2], Pr_B = [-u[0] * R.F_r, -u[1] * R.F_r - Wp / 2];
    const Fpin = Math.max(hyp2(Pf_A), hyp2(Pr_A), hyp2(Pf_B), hyp2(Pr_B));
    const Fmax = Math.max(Math.abs(R.F_f), Math.abs(R.F_r));
    const SyBrgP = Math.min(Sy_p, Sy_pin);
    add('Diagonals', 'Plate axial stress, gross section', Fmax / Ap, Sy_p, 'MPa', FS, `sigma = F/(b t) = ${Fmax.toFixed(0)}/${Ap.toFixed(0)}`);
    add('Diagonals', 'Plate net section at the pin hole', Fpin / ((plate.b - dh) * plate.t), Sy_p, 'MPa', FS, `sigma = F/((b - d_h) t), F = ${Fpin.toFixed(0)} N`);
    add('Diagonals', 'Plate bearing at the pin hole', Fpin / (d * plate.t), SyBrgP, 'MPa', FS, 'sigma_br = F/(d t) vs min(S_y plate, S_y pin)');
    add('Diagonals', 'Plate tear-out toward its end (two shear planes)', Fpin / (2 * plate.t * (dv.e_end - dh / 2)), 0.577 * Sy_p, 'MPa', FS, `tau = F/(2 t (e - d_h/2)), e = ${dv.e_end} mm`);
    const Fc = Math.min(R.F_f, R.F_r);
    const Iw = plate.b * plate.t ** 3 / 12, Is = plate.t * plate.b ** 3 / 12;
    const crit = I => { const k = Math.sqrt(I / Ap), sr = Lpp / k, sr1 = Math.sqrt(2 * Math.PI ** 2 * Ep / Sy_p);
      return sr >= sr1 ? { P: Math.PI ** 2 * Ep * I / Lpp ** 2, mode: 'Euler', sr, sr1 } : { P: Ap * (Sy_p - (Sy_p * sr / (2 * Math.PI)) ** 2 / Ep), mode: 'Johnson', sr, sr1 }; };
    const bw = crit(Iw), bs = crit(Is);
    let Msw = 0, amp = 1;
    if (Fc < 0) {
      add('Diagonals', `Compression plate buckling out of plane (${bw.mode}, pinned-pinned, L/k = ${bw.sr.toFixed(0)})`, -Fc, bw.P, 'N', FS, `P_cr = pi^2 E I/L^2 = ${bw.P.toFixed(0)} N, I = b t^3/12`);
      add('Diagonals', `Compression plate buckling in plane (${bs.mode})`, -Fc, bs.P, 'N', FS, `P_cr = ${bs.P.toFixed(0)} N`);
      const qn = plate.mat.rho * GRAV * Ap * Math.cos(g.theta);
      Msw = qn * Lpp * Lpp / 8; amp = 1 / Math.max(1 - (-Fc) / bs.P, 1e-6);
      add('Diagonals', 'Compression plate: axial + amplified self-weight bending', -Fc / Ap + Msw * amp * (plate.b / 2) / Is, Sy_p, 'MPa', FS, `M_sw = q L^2/8 = ${(Msw / 1000).toFixed(2)} N·m, x ${amp.toFixed(3)}`);
      // Imperfect column: initial crookedness e0 = max(L/1000, bar straightness 1/8 in per 5 ft prorated to L — ASTM A484 / printed by
      // McMaster for 316 bar).  Load factor lambda to first yield: lambda P/A + lambda P e0/(1 - lambda P/Pcr)/S_weak + amplified
      // self-weight bending = S_y.  Require lambda >= 2 (the FS applied to the load, as for buckling).
      const e0 = Math.max(Lpp / 1000, 0.125 * IN * Lpp / (60 * IN)), P1 = -Fc;
      const sigAt = lam => { const rW = lam * P1 / bw.P, rS = lam * P1 / bs.P; if (rW >= 1 || rS >= 1) return Infinity;
        return lam * P1 / Ap + lam * P1 * e0 / (1 - rW) * (plate.t / 2) / Iw + Msw * (1 + 0.028 * rS) / (1 - rS) * (plate.b / 2) / Is; };
      let lo = 0, hi = Math.min(bw.P, bs.P) / P1;
      for (let it = 0; it < 60; it++) { const mid = (lo + hi) / 2; if (sigAt(mid) < Sy_p) lo = mid; else hi = mid; }
      const nP = FS * P1, rW = nP / bw.P, sigImp = sigAt(FS);
      add('Diagonals', `Compression plate with initial crookedness: load factor to first yield (e0 = ${e0.toFixed(2)} mm)`, P1, lo * P1, 'N', FS,
        `lambda = ${lo.toFixed(2)}; at 2P the stress is ${isFinite(sigImp) ? sigImp.toFixed(0) : '∞'} MPa vs S_y ${Sy_p.toFixed(0)} MPa`);
      env.imperfect = { nP, e0, rW, sigImp };
    }
    // ---- pins (pin as a beam through each stack)
    const innerBeam = sec.kind === 'tube' ? { kind: 'walls', z_i: g.z_w, t_i: sec.t }
      : { kind: 'solid', w: sec.W, k: opts.kFactor * beam.mat.E, EIpin: pin.mat.E * Math.PI * (dv.dMin ** 4 - dv.db ** 4) / 64 };
    const specO = { Po_f: [R.Ox_f, R.Oy / 2], Po_r: [R.Ox_r, R.Oy / 2], t_o: PROB.t_br, z_o: g.z_br, inner: innerBeam };
    const zAB = sec.W / 2 + dv.playAB + plate.t / 2;      // plate mid-plane with all residual play on this side (worst for pin bending)
    const specA = { Po_f: Pf_A, Po_r: Pr_A, t_o: plate.t, z_o: zAB, inner: innerBeam };
    const specB = { Po_f: Pf_B, Po_r: Pr_B, t_o: plate.t, z_o: zAB, inner: { kind: 'walls', z_i: g.z_bB, t_i: PROB.t_br } };
    const jO = pinJointExact(specO, env.profiles), jA = pinJointExact(specA, env.profiles), jB = pinJointExact(specB, env.profiles);
    env.joints = { O: jO, A: jA, B: jB, spec: { O: specO, A: specA, B: specB }, P: { Pf_A, Pr_A, Pf_B, Pr_B } };
    const Vmax = Math.max(jO.Vmax, jA.Vmax, jB.Vmax), Mmax = Math.max(jO.Mmax, jA.Mmax, jB.Mmax);
    const wj = jO.Mmax >= jA.Mmax && jO.Mmax >= jB.Mmax ? 'O' : (jA.Mmax >= jB.Mmax ? 'A' : 'B');
    add('Pins', 'Pin shear, worst shear plane (peak tau = k V/A)', dv.kShear * Vmax / dv.Apin, 0.577 * Sy_pin, 'MPa', FS, `V = ${Vmax.toFixed(0)} N, k = ${dv.kShear.toFixed(3)}, S_sy = 0.577 S_y`);
    if (pin.shearRating_N) add('Pins', 'Pin shear vs McMaster breaking strength (per shear plane, scaled by S_y/S_u)', Vmax, pin.shearRating_N / 2 * (Sy_pin / pin.mat.Su), 'N', FS, `printed ${pin.shearNote || 'breaking strength'} is an ultimate load`);
    if (opts.pinBending) add('Pins', `Pin bending, worst joint ${wj} (uniform bearing; play ${opts.float} mm at O, ${dv.playAB.toFixed(2)} mm at A/B)`, Mmax / dv.Zpin, Sy_pin, 'MPa', FS, `M = ${(Mmax / 1000).toFixed(2)} N·m, sigma = M/Z at the minimum pin diameter ${dv.dMin.toFixed(2)} mm`);
    // ---- beam at the pin holes (inner members of the A and O pins)
    const SyBrgB = Math.min(Sy_b, Sy_pin);
    for (const [J, lab] of [[jA, 'A'], [jO, 'O']]) {
      if (sec.kind === 'tube') {
        const Fi = Math.max(hyp2(J.Pi_f), hyp2(J.Pi_r));
        add('Beam', `Beam wall bearing at ${lab} (pin on one wall, F = ${Fi.toFixed(0)} N)`, Fi / (d * sec.t), SyBrgB, 'MPa', FS, 'sigma_br = F_i/(d t_wall); F_i from pin equilibrium');
      } else {
        add('Beam', `Solid beam peak bearing at ${lab} (elastic-foundation peak)`, J.qEdge / d, SyBrgB, 'MPa', FS, 'q0 = 2 beta (P + beta M0); sigma = q0/d');
      }
      const tt = sec.kind === 'tube' ? sec.t : sec.W;
      const tearForces = sec.kind === 'tube' ? [J.Pi_f, J.Pi_r] : [[J.Pi_f[0] + J.Pi_r[0], J.Pi_f[1] + J.Pi_r[1]]];
      for (const Pi of tearForces) {
        const P = [-Pi[0], -Pi[1]], Fm = hyp2(P); if (Fm < 1e-9) continue;
        let e = Infinity;
        if (lab === 'O' && P[0] / Fm > 1e-9) e = Math.min(e, dv.overhang / (P[0] / Fm));
        if (Math.abs(P[1] / Fm) > 1e-9) e = Math.min(e, (sec.H / 2) / Math.abs(P[1] / Fm));
        if (!isFinite(e) || e > 4 * sec.H) continue;      // load points along the beam, away from any nearby free edge
        add('Beam', `Beam tear-out at ${lab} toward the nearest free edge (e = ${e.toFixed(1)} mm)`, Fm / (2 * tt * Math.max(e - dh / 2, 1e-6)), 0.577 * Sy_b, 'MPa', FS, 'tau = F/(2 t (e - d_h/2))');
      }
    }
    // ---- brackets (1/2 in Al): outer members at O, inner members at B
    const FbrO = Math.max(hyp2(specO.Po_f), hyp2(specO.Po_r)), FbrB = Math.max(hyp2(jB.Pi_f), hyp2(jB.Pi_r));
    const SyBr = Math.min(PROB.Sy_br, Sy_pin);
    add('Brackets', 'Bracket bearing at O (1/2 in Al, S_y 35 ksi)', FbrO / (d * PROB.t_br), SyBr, 'MPa', FS, `F = ${FbrO.toFixed(0)} N`);
    add('Brackets', 'Bracket bearing at B (brackets are the inner members of pin B)', FbrB / (d * PROB.t_br), SyBr, 'MPa', FS, `F = ${FbrB.toFixed(0)} N`);
    env.buckling = { weak: bw, strong: bs, Fc, Msw, amp };
    return env;
  }

  // ------------------------------------------------------------------ beam stress scan
  function beamStress(beam, g, internal, dh) {
    const sec = beam.sec, net = netSection(sec, dh), pts = [];
    const bp = [PROB.x_left, PROB.x_rot, PROB.x_gen, -g.a, 0, g.x_right].sort((p, q) => p - q);
    let worst = null;
    for (let i = 0; i < bp.length - 1; i++) for (let k = 0; k <= 8; k++) {
      const x = bp[i] + (bp[i + 1] - bp[i]) * k / 8, side = k === 8 ? '-' : '+';
      const IL = internal(x, side);
      const isHole = Math.abs(x) < 1e-9 || Math.abs(x + g.a) < 1e-9;
      const S = isHole ? net : sec;
      const sigN = Math.abs(IL.N) / S.A, sigMz = Math.abs(IL.Mz) * (sec.H / 2) / S.Iz, sigMy = Math.abs(IL.My) * (sec.W / 2) / S.Iy;
      const sig = sigN + sigMz + sigMy;
      const tauT = Math.abs(IL.Tx) * sec.tauPerT;
      const tauV = Math.abs(IL.Vy) * sec.Qy / (sec.Iz * sec.bWebY) + Math.abs(IL.Vz) * sec.Qz / (sec.Iy * sec.bWebZ);
      const vm = Math.sqrt(sig * sig + 3 * (tauT + tauV) ** 2);
      const r = { x, side, isHole, IL, sigN, sigMz, sigMy, sig, tauT, tauV, vm, fs: beam.Sy / vm };
      pts.push(r); if (!worst || vm > worst.vm) worst = r;
    }
    return { pts, worst, net };
  }

  // ------------------------------------------------------------------ full evaluation of one design
  const DEFAULT_OPTS = { pinBending: true, jointCompliance: false, kerf: 0.125 * IN, float: 0.5, kFactor: 0.5 };
  function evaluate(design, opts) {
    opts = Object.assign({}, DEFAULT_OPTS, opts || {});
    const { beam, plate, pin, a } = design;
    const FS = PROB.FS;
    const dv = derive(design, opts);
    const c = core(beam, plate.t, a, dv.Wp, dv.dh, dv.overhang, opts.float);
    const { g, AL, R, internal } = c;
    const out = { design, opts, dv, g, AL, R, c, checks: [] };
    const add = (group, name, demand, capacity, unit, FSreq, detail, kind) => {
      const fs = kind === 'geom' ? null : (demand > 0 ? capacity / demand : Infinity);
      const ok = kind === 'geom' ? demand <= capacity + 1e-9 : fs >= FSreq - 1e-9;
      out.checks.push({ group, name, demand, capacity, unit, fs, FSreq, ok, detail, kind: kind || 'fs' });
      return ok;
    };
    // plate stretch and deflection
    const Ep = plate.mat.E, Ap = plate.b * plate.t;
    let delta_f = R.F_f * g.Lpp / (Ep * Ap), delta_r = R.F_r * g.Lpp / (Ep * Ap);
    const env = { beam, plate, pin, a, g, R, Wp: dv.Wp, dv, opts, profiles: true };
    memberChecks(env, add);
    out.joints = env.joints; out.buckling = env.buckling;
    let defl = cgDeflection(c, delta_f, delta_r);
    if (opts.jointCompliance) {
      const d = dv.d, Ef = pin.mat.E, tIn = beam.sec.kind === 'tube' ? beam.sec.t : beam.sec.W / 2;
      const cA = huthC(plate.t, Ep, tIn, beam.mat.E, d, Ef), cB = huthC(plate.t, Ep, PROB.t_br, 68900, d, Ef), cO = huthC(PROB.t_br, 68900, tIn, beam.mat.E, d, Ef);
      delta_f += R.F_f * (cA + cB); delta_r += R.F_r * (cA + cB);
      defl = cgDeflection(c, delta_f, delta_r);
      const sf = cO * R.Ox_f, sr = cO * R.Ox_r, thyO = -(sf - sr) / (2 * g.z_br);
      const cot = Math.cos(g.theta) / Math.sin(g.theta), sn = Math.sin(g.theta), cs = Math.cos(g.theta);
      const dO = [-(sf + sr) / 2, -cO * R.Oy / 2, 0];                 // beam moves opposite to the support force (spring)
      const dthz = -(dO[0] * cs + dO[1] * sn) / (g.a * sn);           // the plates re-pitch the beam to stay compatible
      defl.comps.push({ key: 'joint', name: 'Pin-joint compliance at O (Huth estimate)', d: [dO[0] - dthz * g.y_cg, dO[1] + dthz * PROB.x_rot, -thyO * PROB.x_rot + thyO * cot * g.y_cg] });
      defl.total = [0, 1, 2].map(i => defl.comps.reduce((S, cc) => S + cc.d[i], 0)); defl.mag = norm(defl.total);
      out.jointC = { cA, cB, cO, thyO };
    }
    out.plateStretch = { delta_f, delta_r };
    // Hole-clearance play (rigid seating shift, not elastic deflection; reported, not part of req 12).  When the flow starts the front
    // plate reverses from tension to compression (both its joints take up plate-hole + member-hole clearance, 4c in all) and the rear
    // O bracket force reverses (2c), so the beam rolls about x and yaws about y.
    {
      const s_ = Math.sin(g.theta);
      const slop = c => { const thx = 4 * c / (2 * g.z_d * s_), thy = 2 * c / (2 * g.z_br); return { thx, thy, z: thx * Math.abs(g.y_cg) + thy * Math.abs(PROB.x_rot) }; };
      out.slop = { cmin: dv.hole.cmin_in * IN, cmax: dv.hole.cmax_in * IN, atMin: slop(dv.hole.cmin_in * IN), atMax: slop(dv.hole.cmax_in * IN) };
    }
    out.defl = defl;
    add('Deflection', 'Rotor-CG deflection magnitude (req 12)', defl.mag, PROB.deflLimit, 'mm', null, 'vector sum of all elastic contributions', 'geom');
    // beam stress
    const bsr = beamStress(beam, g, internal, dv.dh);
    out.beamStress = bsr;
    add('Beam', 'Beam von Mises stress, worst section (axial + biaxial bending + torsion + shear)', bsr.worst.vm, beam.Sy, 'MPa', FS,
      `x = ${bsr.worst.x.toFixed(0)} mm (${bsr.worst.isHole ? 'net section at pin hole' : 'gross section'}); peak normal and peak shear combined (conservative)`);
    // peaks of internal loads
    const peaks = {};
    for (const key of ['N', 'Vy', 'Vz', 'Tx', 'My', 'Mz']) {
      let best = { v: 0, x: 0 };
      for (const r of bsr.pts) if (Math.abs(r.IL[key]) > Math.abs(best.v) + 1e-9) best = { v: r.IL[key], x: r.x, side: r.side };
      peaks[key] = best;
    }
    out.peaks = peaks;
    out.cost = costOf(design, out, opts);
    out.ok = out.checks.every(k => k.ok) && out.cost.ok;
    const fsChecks = out.checks.filter(k => k.kind !== 'geom');
    // lowest factor of safety among the FS-2 checks; governing = the check with the smallest margin fs/FSreq
    out.minFS = Math.min(...fsChecks.filter(k => k.FSreq === PROB.FS).map(k => k.fs));
    out.governing = fsChecks.reduce((p, q) => (q.fs / q.FSreq < p.fs / p.FSreq ? q : p));
    out.margin = out.governing.fs / out.governing.FSreq;
    return out;
  }

  // ------------------------------------------------------------------ cost
  function cheapestLength(offers, needIn) {   // the problem prices the SHORTEST offered piece that is long enough (ties: lower price)
    let best = null;
    for (const o of offers || []) if (o.length_in + 1e-9 >= needIn && (!best || o.length_in < best.length_in - 1e-9 || (Math.abs(o.length_in - best.length_in) < 1e-9 && o.price < best.price))) best = o;
    return best;
  }
  function costOf(design, out, opts) {
    const kerfIn = opts.kerf / IN, dv = out.dv;
    const beamNeed = out.g.Lbeam / IN;
    const bOffer = cheapestLength(design.beam.item.offers, beamNeed);
    const pl = design.plate, plItem = pl.item, LcutIn = dv.Lcut / IN;
    let pOffer = null, plateHow = '', plateNeedIn = LcutIn;
    if (pl.mode === 'bar') { plateNeedIn = 2 * LcutIn + kerfIn; pOffer = cheapestLength(plItem.offers, plateNeedIn); plateHow = `two ${LcutIn.toFixed(2)} in pieces cut end to end (+${kerfIn} in saw kerf)`; }
    else if (pl.mode === 'rip') { pOffer = cheapestLength(plItem.offers, LcutIn); plateHow = `ripped lengthwise into two ${(pl.b / IN).toFixed(3)} in strips, each ${LcutIn.toFixed(2)} in long`; }
    else if (pl.mode === 'sheet') { pOffer = pl.costFor(LcutIn); plateHow = `${pl.how} from one ${pOffer ? pOffer.label : ''} piece`; }
    const pin = design.pin, nPins = 3;
    const pinPacks = Math.ceil(nPins / (pin.pkg || 1)), pinCost = pinPacks * pin.price;
    let retCost = 0, ret = pin.retainer || null;
    if (ret) retCost = Math.ceil(nPins / (ret.pkg || 1)) * ret.price;
    const wc = dv.wash;
    const washer = wc.washer, washerCount = wc.count, washerCost = wc.cost, washerPerJoint = [0, wc.perJoint, wc.perJoint];
    const ok = !!bOffer && !!pOffer;
    const total = (bOffer ? bOffer.price : NaN) + (pOffer ? pOffer.price : NaN) + pinCost + retCost + washerCost;
    return { ok, total, beam: bOffer, beamNeedIn: beamNeed, plate: pOffer, plateHow, plateNeedIn, pinCost, pinPacks, retCost, ret, washer, washerCount, washerCost, washerPerJoint };
  }

  // ------------------------------------------------------------------ fine internal-load diagrams (for plots)
  function diagrams(res, n) {
    n = n || 400;
    const { g } = res, internal = res.c.internal;
    const xs = [];
    const bps = [g.x_left, PROB.x_rot, PROB.x_gen, -g.a, 0, g.x_right].sort((p, q) => p - q);
    for (let i = 0; i < bps.length - 1; i++) {
      const m = Math.max(4, Math.round(n * (bps[i + 1] - bps[i]) / (g.x_right - g.x_left)));
      for (let k = 0; k <= m; k++) xs.push([bps[i] + (bps[i + 1] - bps[i]) * k / m, k === m ? '-' : '+']);
    }
    return xs.map(([x, side]) => Object.assign({ x }, internal(x, side)));
  }

  // ------------------------------------------------------------------ exports
  const API = { IN, PSI, KSI, LBF, GRAV, PROB, PW, MATERIALS, DEFAULT_OPTS, chainGeometry, beamSection, netSection, geometry, appliedLoads, statics,
    makeInternal, beamElastic, core, cowperBox, cgDeflection, cgFromVals, pinJointExact, huthC, holeFor, derive, washerPlan, memberChecks, beamStress, evaluate, costOf, cheapestLength, diagrams,
    vec: { add, sub, scl, dot, cross, norm } };
  if (typeof module !== 'undefined' && module.exports) module.exports = API;
  else root.DP1 = API;
})(typeof window !== 'undefined' ? window : globalThis);
