const D = require('../dp1-solver.js');
const spec = { Po_f: [-3500, 0], Po_r: [4500, 0], t_o: 9.525, z_o: 55.5625, inner: { kind: 'walls', z_i: 47.625, t_i: 6.35 } };
const a = D.pinJointExact(spec), b = D.pinJoint(spec, 4000);
console.log('exact', a.Pi_f, a.Pi_r, a.Vmax.toFixed(1), (a.Mmax/1000).toFixed(3), 'end', a.endV.toFixed(6), a.endM.toFixed(6));
console.log('numeric', b.Vmax.toFixed(1), (b.Mmax/1000).toFixed(3));
// closed form uniform bearing per side: M = Fo to/2 + Fo^2 ti/(2 Fi)
const Fo=4500, Fi=Math.abs(a.Pi_r[0]); console.log('closed rear', ((Fo*9.525/2 + Fo*Fo*6.35/(2*Fi))/1000).toFixed(3));
const s2 = { Po_f: [-3500, 200], Po_r: [4500, -300], t_o: 12.7, z_o: 57.15, inner: { kind: 'solid', w: 101.6 } };
const c = D.pinJointExact(s2), e = D.pinJoint(s2, 4000);
console.log('solid exact', c.Vmax.toFixed(1), (c.Mmax/1000).toFixed(3), c.endV.toExponential(2), c.endM.toExponential(2), ' numeric', e.Vmax.toFixed(1), (e.Mmax/1000).toFixed(3));
