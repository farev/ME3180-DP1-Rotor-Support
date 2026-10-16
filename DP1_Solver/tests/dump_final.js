// dump the selected design (rank i of dp1-results.js) for independent verification: design inputs and solver outputs, separately
global.window = undefined;
const D = require('../dp1-solver.js'), SR = require('../dp1-search.js'), C = require('../dp1-catalog.js');
const fs = require('fs'), out = process.argv[3];
const pre = eval(fs.readFileSync(__dirname + '/../dp1-results.js', 'utf8').replace('window.DP1_PRECOMP =', '(').replace(/;\s*$/, ')'));
const i = +(process.argv[2] || 0), sp = pre.rows[i].spec, opts = Object.assign({}, D.DEFAULT_OPTS, pre.opts);
const beams = SR.beamOptions(C), plates = SR.plateOptions(C, opts), pins = SR.pinOptions(C, opts);
const beam = beams.find(b => b.item.pn === sp.beam && b.orient === sp.orient), pl = plates.find(p => p.item.pn === sp.plate && p.mode === sp.mode && Math.abs(p.b - sp.b) < 0.05), pin = pins.find(p => p.pn === sp.pin);
const ev = D.evaluate(SR.makeDesign({ beam, pl, pin, a: sp.a }), opts);
const s = beam.sec;
const design = {
  note: 'Inputs only. Units mm, N, MPa unless stated. Frame: origin at pin O on the beam neutral axis, +x toward the structure, +y up, +z toward the viewer (front).',
  beam: { mcmaster: sp.beam, kind: s.kind, W_z_mm: s.W, H_y_mm: s.H, wall_mm: s.t, corner_ro_mm: s.ro, corner_ri_mm: s.ri, material: beam.mat.name, E: beam.mat.E, G: +beam.mat.G.toFixed(0), nu: beam.mat.nu, density_kg_m3: beam.mat.rho * 1e9, Sy: beam.Sy, x_from: -1300, x_to: 50 },
  plates: { mcmaster: sp.plate, width_b_mm: pl.b, thickness_mm: pl.t, material: pl.mat.name, E: pl.mat.E, density_kg_m3: pl.mat.rho * 1e9, Sy: pl.Sy, a_mm: sp.a, A: [-sp.a, 0], B: [0, 500], end_distance_mm: ev.dv.e_end, cut_length_mm: ev.dv.Lcut },
  pin: { mcmaster: sp.pin, d_mm: pin.d_in * 25.4, solid: !pin.hollow, material: pin.material, Sy_basis: pin.mat.Sy, hole_mm: [ev.dv.hole.lo_in * 25.4, ev.dv.hole.hi_in * 25.4], usable_in: pin.usable_in },
  stacks: { float_g_mm: opts.float, bracket_t_mm: 12.7, bracket_Sy: D.PROB.Sy_br, O: 'bracket | beam wall | hollow | beam wall | bracket (brackets outside the beam walls)', A: 'plate | beam wall | hollow | beam wall | plate', B: 'plate | bracket | gap | bracket | plate (B brackets inboard of the plates, outer faces at z = +/-W/2)', z_plate_mid: ev.g.z_d, z_bracketO_mid: ev.g.z_br, z_wall_mid: ev.g.z_w, z_bracketB_mid: ev.g.z_bB },
  loads: { drag_N: 560, drag_at: 'x=-1200, y=-(H/2+500), z=0, +z', rotor_W_N: 150, cg_at: 'x=-1200, y=-(H/2+350)', gen_W_N: 120, gen_x: D.PROB.x_gen, chain: 'tight span on -z, tension = T/r1 along the exact external tangent between pitch circles 9.554 in and 3.038 in, plane y=-(H/2+50); slack 0', water_torque_Nm: D.PW.T_rotor / 1000, self_weights: 'beam uniform over -1300..+50; each plate weight split half to each end' },
  supports: 'O: Ox_front, Ox_rear at z=+/-z_bracketO_mid, Oy equal per side (no torsion at O, req 10), Oz on the front bracket face (no moment arm). Plates: two-force members A->B. O fixes ux,uy,uz and rotation about y; plates fix rotations about x and z.',
  checks_required: 'FS 2 on yield for stresses, bearing (vs min of member and pin Sy), tear-out (0.577 Sy), pin bending (pin as a beam through the stack, uniform bearing in each member, float g between outer member and inner face), pin peak shear 4V/3A, plate buckling on load (K=1), CG deflection <= 0.7 mm (elastic).',
};
const numbers = {
  reactions: { Ox_f: ev.R.Ox_f, Ox_r: ev.R.Ox_r, Oy_total: ev.R.Oy, Oz: ev.R.Oz, F_front: ev.R.F_f, F_rear: ev.R.F_r },
  pin_inner_forces: { O: [ev.joints.O.Pi_f, ev.joints.O.Pi_r], A: [ev.joints.A.Pi_f, ev.joints.A.Pi_r], B: [ev.joints.B.Pi_f, ev.joints.B.Pi_r] },
  pin_Mmax_Nm: { O: ev.joints.O.Mmax / 1000, A: ev.joints.A.Mmax / 1000, B: ev.joints.B.Mmax / 1000 }, pin_Vmax_N: { O: ev.joints.O.Vmax, A: ev.joints.A.Vmax, B: ev.joints.B.Vmax },
  peaks: Object.fromEntries(Object.entries(ev.peaks).map(([k, v]) => [k, { value: ['Tx', 'My', 'Mz'].includes(k) ? v.v / 1000 : v.v, x: v.x }])),
  beam_section: { A: s.A, Iz: s.Iz, Iy: s.Iy, J: s.J, Am: s.Am, kapY: s.kapY, kapZ: s.kapZ },
  buckling: { Pcr_weak: ev.buckling.weak.P, Fc: ev.buckling.Fc },
  deflection_components_mm: Object.fromEntries(ev.defl.comps.map(c => [c.key, c.d])), deflection_total_mm: ev.defl.total, deflection_mag_mm: ev.defl.mag,
  plate_stretch_mm: ev.plateStretch, checks: ev.checks.map(c => ({ name: c.name, demand: c.demand, capacity: c.capacity, fs: c.fs, ok: c.ok })),
  cost: { total: ev.cost.total, beam: ev.cost.beam, plate: ev.cost.plate, pinCost: ev.cost.pinCost, retainer: ev.cost.ret, retCost: ev.cost.retCost, washer: ev.cost.washer, washerCount: ev.cost.washerCount, washerCost: ev.cost.washerCost },
};
fs.mkdirSync(out, { recursive: true });
fs.writeFileSync(out + '/final_design.json', JSON.stringify(design, null, 1));
fs.writeFileSync(out + '/final_numbers.json', JSON.stringify(numbers, null, 1));
console.log('written', out, 'cost', ev.cost.total.toFixed(2));
