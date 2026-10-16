// node make_dxf.js [rank] : writes diagonal_plate.dxf (inches, R12) for the selected design so it can be imported into CAD
global.window = undefined;
const D = require('./dp1-solver.js'), SR = require('./dp1-search.js'), C = require('./dp1-catalog.js'), fs = require('fs');
const pre = eval(fs.readFileSync(__dirname + '/dp1-results.js', 'utf8').replace('window.DP1_PRECOMP =', '(').replace(/;\s*$/, ')'));
const sp = pre.rows[+(process.argv[2] || 0)].spec, opts = Object.assign({}, D.DEFAULT_OPTS, pre.opts);
const beams = SR.beamOptions(C), plates = SR.plateOptions(C, opts), pins = SR.pinOptions(C, opts);
const ev = D.evaluate(SR.makeDesign({ beam: beams.find(b => b.item.pn === sp.beam && b.orient === sp.orient), pl: plates.find(p => p.item.pn === sp.plate && p.mode === sp.mode && Math.abs(p.b - sp.b) < 0.05), pin: pins.find(p => p.pn === sp.pin), a: sp.a }), opts);
const IN = 25.4, L = ev.dv.Lcut / IN, b = ev.design.plate.b / IN, e = ev.dv.e_end / IN, c = ev.g.Lpp / IN, r = (ev.dv.hole.lo_in + ev.dv.hole.hi_in) / 4;
const ent = [];
const line = (x1, y1, x2, y2) => ent.push(['0', 'LINE', '8', 'OUTLINE', '10', x1, '20', y1, '30', 0, '11', x2, '21', y2, '31', 0]);
const circ = (x, y, rr) => ent.push(['0', 'CIRCLE', '8', 'HOLES', '10', x, '20', y, '30', 0, '40', rr]);
line(0, 0, L, 0); line(L, 0, L, b); line(L, b, 0, b); line(0, b, 0, 0);
circ(e, b / 2, r); circ(e + c, b / 2, r);
const out = ['0', 'SECTION', '2', 'HEADER', '9', '$INSUNITS', '70', 1, '0', 'ENDSEC', '0', 'SECTION', '2', 'ENTITIES', ...ent.flat(), '0', 'ENDSEC', '0', 'EOF'].map(v => typeof v === 'number' ? v.toFixed(5) : v).join('\n');
fs.writeFileSync(__dirname + '/diagonal_plate.dxf', out + '\n');
console.log(`diagonal_plate.dxf: ${L.toFixed(3)} x ${b.toFixed(3)} in, holes Ø${(2 * r).toFixed(4)} at ${e.toFixed(3)} and ${(e + c).toFixed(3)} in from the left end; thickness ${ev.design.plate.item.t_in} in`);
