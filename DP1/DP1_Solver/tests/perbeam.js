const D = require('../dp1-solver.js'), SR = require('../dp1-search.js');
const C = JSON.parse(JSON.stringify(require('../dp1-catalog.js')));
if (!C.retainers.length) C.retainers.push({ pn: 'TEST-HAIRPIN', type: 'hairpin', material: 'stainless', hand: true, price: 1, pkg: 1, pinDmin_in: 0, pinDmax_in: 2 });
(async () => {
  const res = await SR.search(C, { pinBending: true, topN: 30 });
  const ev = res.final[0].ev;
  for (const c of ev.defl.comps) console.log(c.key.padEnd(11), c.d.map(v => v.toFixed(4)).join(', '));
  console.log('|u|', ev.defl.mag.toFixed(4));
  const pb = res.stats.perBeam.sort((a, b) => a.beam.lbCost - b.beam.lbCost);
  for (const p of pb.slice(0, 45)) console.log(p.beam.item.pn.padEnd(10), p.beam.item.mat, `${p.beam.item.dimA_in}x${p.beam.item.dimB_in}x${p.beam.item.t_in}`.padEnd(14), p.beam.orient.slice(0, 22).padEnd(22), '$' + p.beam.lbCost, 'minDefl', isFinite(p.minDeflAny) ? p.minDeflAny.toFixed(3) : '-', 'best', isFinite(p.bestCost) ? p.bestCost.toFixed(0) : '-', p.skipped || JSON.stringify(p.reason).slice(0, 120));
})();
