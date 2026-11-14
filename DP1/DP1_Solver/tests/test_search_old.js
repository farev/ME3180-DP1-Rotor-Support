const S = require('../dp1-search.js'), D = require('../dp1-solver.js');
const cat = require('./old_catalog_adapter.js');
(async () => {
  for (const pb of [true, false]) {
    const t0 = Date.now();
    const res = await S.search(cat, { pinBending: pb, topN: 15 });
    console.log(`\n=== pinBending=${pb}  ${(Date.now()-t0)/1000}s  combos ${res.stats.combos} cores ${res.stats.cores}`, res.counts);
    console.log('fails', res.stats.fails);
    for (const f of res.final.slice(0, 12)) {
      const ev = f.ev, r = f.r;
      console.log(`$${ev.cost.total.toFixed(2)} a=${r.a} beam ${r.beam.item.pn} ${r.beam.orient} | plate ${r.pl.item.pn} ${r.pl.mode} t=${(r.pl.t/25.4).toFixed(3)} b=${(r.pl.b/25.4).toFixed(2)} | pin ${r.pin.pn} d=${r.pin.d_in} | defl ${ev.defl.mag.toFixed(3)} ok=${ev.ok} minFS ${ev.minFS.toFixed(2)} gov: ${ev.governing.name}`);
      if (!ev.ok) console.log('   FAILED:', ev.checks.filter(c => !c.ok).map(c => c.name + ' ' + (c.fs ?? c.demand)).join('; '), ev.cost.ok);
    }
  }
})();
