global.window = undefined;
const D = require('../dp1-solver.js'), SR = require('../dp1-search.js'), C = require('../dp1-catalog.js'), fs = require('fs');
const pre = eval(fs.readFileSync(__dirname + '/../dp1-results.js', 'utf8').replace('window.DP1_PRECOMP =', '(').replace(/;\s*$/, ')'));
const sp = pre.rows[0].spec, o = Object.assign({}, D.DEFAULT_OPTS, pre.opts);
const B = SR.beamOptions(C), P = SR.plateOptions(C, o), N = SR.pinOptions(C, o);
const ev = D.evaluate(SR.makeDesign({ beam: B.find(b => b.item.pn === sp.beam && b.orient === sp.orient), pl: P.find(p => p.item.pn === sp.plate && p.mode === sp.mode && Math.abs(p.b - sp.b) < .05), pin: N.find(p => p.pn === sp.pin), a: sp.a }), o);
const s = ev.joints.spec.B, W = ev.g.W, t = ev.design.plate.t;
for (const gap of [ev.dv.playAB, 8 * 25.4 - ev.dv.grips.A]) { const j = D.pinJointExact(Object.assign({}, s, { z_o: W / 2 + gap + t / 2 })); console.log('gap', gap.toFixed(1), 'mm  M_B', (j.Mmax / 1000).toFixed(1), 'N·m  FS', (ev.design.pin.mat.Sy / (j.Mmax / ev.dv.Zpin)).toFixed(2)); }
console.log('grips in', (ev.dv.grips.O / 25.4).toFixed(3), (ev.dv.grips.A / 25.4).toFixed(3), 'washers/joint', ev.dv.wash.perJoint);
