const D = require('../dp1-solver.js');
const IN = D.IN;
D.MATERIALS.ss304.G = 75000;  // match dp1_model.py
const mat = D.MATERIALS.ss304;
const beam = { sec: D.beamSection('tube', 4*IN, 4*IN, 0.25*IN, 0), mat, Sy: 215 };
const a = 500, tD = 0.25*IN, bD = 2*IN, dh = 0.375*IN;
const Lpp = Math.hypot(a, 500), Lcut = Lpp + 4*dh;
const Wp = 8000*9.81*1e-9 * bD*tD*Lcut;
const c = D.core(beam, tD, a, Wp, dh, 50);
console.log('x_gen', D.PROB.x_gen.toFixed(2), 'Wp', Wp.toFixed(2));
const R = c.R;
console.log('O_f', R.O_f.map(v=>v.toFixed(1)), 'O_r', R.O_r.map(v=>v.toFixed(1)), 'F_f', R.F_f.toFixed(1), 'F_r', R.F_r.toFixed(1), 'resid', R.residual.toExponential(2));
console.log('My_bracket', (R.My_bracket/1000).toFixed(1), 'My_plates', (R.My_plates/1000).toFixed(1), 'Mx_plates', (R.Mx_plates/1000).toFixed(1));
const E = mat.E, Ap = bD*tD;
const df = R.F_f*Lpp/(E*Ap), dr = R.F_r*Lpp/(E*Ap);
const d = D.cgDeflection(c, df, dr);
for (const k of d.comps) console.log(k.key.padEnd(11), k.d.map(v=>v.toFixed(4)).join(', '));
console.log('TOTAL', d.total.map(v=>v.toFixed(4)), '|u|', d.mag.toFixed(4));
console.log('atA', c.atA, 'atRot', c.atRot);
