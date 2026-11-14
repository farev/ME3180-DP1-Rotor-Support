const D = require('../dp1-solver.js'), SR = require('../dp1-search.js');
const C = JSON.parse(JSON.stringify(require('../dp1-catalog.js')));
if (!C.retainers.length) C.retainers.push({ pn: 'TEST-HAIRPIN', type: 'hairpin', material: 'stainless', hand: true, price: 1, pkg: 1, pinDmin_in: 0, pinDmax_in: 2 });
(async () => {
  for (const pb of [true, false]) {
    const t0 = Date.now();
    const res = await SR.search(C, { pinBending: pb, topN: 30 });
    console.log(`\n=== pinBending=${pb} ${(Date.now() - t0) / 1000}s combos ${res.stats.combos}`, JSON.stringify(res.stats.fails).slice(0, 400));
    const seen = new Set();
    for (const f of res.final) {
      const ev = f.ev, r = f.r, k = r.beam.item.pn + r.pl.item.pn + r.pin.pn; if (seen.has(k)) continue; seen.add(k);
      console.log(`$${ev.cost.total.toFixed(2)} a=${r.a} ${r.beam.item.pn} ${r.beam.item.mat} ${r.beam.item.dimA_in}x${r.beam.item.dimB_in}x${r.beam.item.t_in} ${r.beam.orient.slice(0, 18)} | ${r.pl.item.pn} ${r.pl.item.mat} ${r.pl.mode} t=${r.pl.item.t_in} b=${(r.pl.b / 25.4).toFixed(2)} | ${r.pin.pn} ${r.pin.matKey} d=${r.pin.d_in} $${r.pin.price} | defl ${ev.defl.mag.toFixed(3)} FS ${ev.minFS.toFixed(2)} ${ev.ok ? '' : 'NOT OK'} | ${ev.governing.name.slice(0, 50)}`);
      if (seen.size >= 10) break;
    }
  }
})();
