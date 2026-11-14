// TEST ONLY: adapts the 8 Oct catalog (RotorSupportExplorer) to the solver schema; adds a placeholder retainer.
const fs = require('fs');
const old = JSON.parse(fs.readFileSync(process.argv[2] || '/private/tmp/claude-501/-Users-fabianarevalo-Documents-Georgia-Tech-ME3180/83138c4c-6c70-40a7-b213-174996793466/scratchpad/old_catalog.json'));
const ftIn = k => parseFloat(k) * 12;
const tol = s => { const m = (s || '').match(/(-?[\d.]+)"?\s*to\s*(-?[\d.]+)/); return m ? [parseFloat(m[1]), parseFloat(m[2])] : [-0.005, 0]; };
module.exports = {
  beams: old.beams.map(b => ({ pn: b.pn, family: b.family, mat: b.mat, kind: b.kind, dimA_in: b.A_in, dimB_in: b.B_in, t_in: b.t_in, ro_in: 0, Sy: b.yield_mpa || null,
    offers: Object.entries(b.lengths).map(([k, v]) => ({ length_in: ftIn(k), price: v, pn: (b.pn_by_length || {})[k] || b.pn, label: k })) })),
  plateStocks: old.bars.map(b => ({ pn: b.pn, family: b.family, mat: b.mat, shape: 'flat_bar', t_in: b.t_in, w_in: b.b_in, Sy: b.yield_mpa,
    offers: Object.entries(b.lengths).map(([k, v]) => ({ length_in: ftIn(k), price: v, pn: (b.pn_by_length || {})[k] || b.pn, label: k })) })),
  pins: old.pins.map(p => { const [lo, hi] = tol(p.tol); return { pn: p.pn, family: 'Clevis pins', style: 'clevis', matKey: p.mat, d_in: p.d_in, usable_in: p.usable_in, price: p.price, pkg: p.pack, tolMinus_in: lo, tolPlus_in: hi, needsRetainer: true, cotterMax_in: 0.125 }; }),
  retainers: [{ pn: 'TEST-RETAINER', type: 'hairpin', hand: true, price: 1.0, pkg: 1, pinDmin_in: 0, pinDmax_in: 2 }],
};
