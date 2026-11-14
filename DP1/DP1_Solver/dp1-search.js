/* dp1-search.js — exhaustive cheapest-design search over a McMaster catalog for ME3180 DP1.
 * Requires dp1-solver.js (window.DP1 or require).  Strategy:
 *   for every beam (both orientations with z-width >= 4 in), every plate thickness, every a on a grid:
 *     two exact structural solutions (plate weight 0 and 100 N) -> every response is linear in plate weight;
 *   for every plate option and every pin (+ retainer) at that (beam, t, a): O(1) screening of all checks and the cost;
 *   branch-and-bound on cost keeps the best N; the best N are then re-evaluated with the full DP1.evaluate().
 */
(function (root) {
  'use strict';
  const DP1 = root.DP1 || (typeof require !== 'undefined' ? require('./dp1-solver.js') : null);
  const { IN, PROB, MATERIALS } = DP1;
  const hyp2 = a => Math.hypot(a[0], a[1]);

  // ---------------------------------------------------------------- catalog -> option lists
  function beamOptions(cat) {
    const out = [];
    for (const it of cat.beams) {
      const mat = MATERIALS[it.mat]; if (!mat) continue;
      const dims = [[it.dimA_in, it.dimB_in], [it.dimB_in, it.dimA_in]];
      const seen = new Set();
      for (const [Wz, Hy] of dims) {
        if (Wz * IN < PROB.minWidth - 1e-6) continue;
        const key = `${Wz}x${Hy}`; if (seen.has(key)) continue; seen.add(key);
        const sec = DP1.beamSection(it.kind, Wz * IN, Hy * IN, (it.t_in || 0) * IN, (it.ro_in || 0) * IN, it.ri_in != null ? it.ri_in * IN : null, mat.nu);
        out.push({ item: it, mat, Sy: it.Sy || mat.Sy, sec, orient: `${Wz}" wide (z) x ${Hy}" tall (y)`, rotated: Wz !== it.dimA_in });
      }
    }
    return out;
  }

  function plateOptions(cat, opts) {
    const kerf = opts.kerf, bCap = opts.bCap, out = [];
    for (const it of cat.plateStocks) {
      const mat = MATERIALS[it.mat]; if (!mat) continue;
      const t = it.t_in * IN, Sy = it.Sy || mat.Sy;
      // stock width tolerance (minus side): McMaster prints up to -1/8 in for hot-rolled stainless bar, -0.034 in for 6061, -1/16 in for 5052;
      // ripped or sheared strips are cut to +/-1/32 in
      const barTol = (it.widthTolMinus_in != null ? it.widthTolMinus_in : (it.mat.startsWith('ss') ? 0.125 : it.mat === 'al6061' ? 0.034 : 0.0625)) * IN, cutTol = IN / 32;
      if (it.shape === 'flat_bar') {
        const W = it.w_in * IN;
        if (W <= bCap + 1e-6) out.push({ item: it, mat, Sy, t, b: W, widthTol: barTol, mode: 'bar', costFor: LcutIn => DP1.cheapestLength(it.offers, 2 * LcutIn + kerf / IN) });
        const bR = Math.min((W - kerf) / 2, bCap);
        if (bR >= 1.0 * IN) out.push({ item: it, mat, Sy, t, b: bR, widthTol: cutTol, mode: 'rip', costFor: LcutIn => DP1.cheapestLength(it.offers, LcutIn) });
      } else {   // sheet / plate pieces: {w_in, l_in, price, pn}
        for (const so of it.sheetOffers || []) {
          const W = so.w_in * IN, L = so.l_in;
          // side-by-side strips (length >= Lcut) or end-to-end (length >= 2 Lcut + kerf)
          const bSide = Math.min((W - kerf) / 2, bCap), bEnd = Math.min(W, bCap);
          if (bSide >= 1.0 * IN) out.push({ item: it, mat, Sy, t, b: bSide, widthTol: cutTol, mode: 'sheet', sheet: so, costFor: LcutIn => (L + 1e-9 >= LcutIn ? { price: so.price, pn: so.pn, length_in: L, label: `${so.w_in} x ${so.l_in} in` } : null), how: 'two strips side by side' });
          if (bEnd > bSide + 1e-6) out.push({ item: it, mat, Sy, t, b: bEnd, widthTol: bEnd < W - 1e-6 ? cutTol : barTol, mode: 'sheet', sheet: so, costFor: LcutIn => (L + 1e-9 >= 2 * LcutIn + kerf / IN ? { price: so.price, pn: so.pn, length_in: L, label: `${so.w_in} x ${so.l_in} in` } : null), how: 'two pieces end to end' });
        }
      }
    }
    return out;
  }

  function pinOptions(cat, opts) {
    const out = [];
    for (const p of cat.pins) {
      const mat = MATERIALS[p.matKey]; if (!mat) continue;
      let ret = null, retCost = 0;
      if (p.needsRetainer) {
        const cands = (cat.retainers || []).filter(r => r.hand && (r.pinDmin_in == null || p.d_in >= r.pinDmin_in - 1e-6) && (r.pinDmax_in == null || p.d_in <= r.pinDmax_in + 1e-6)
          && (r.wire_in == null || p.cotterMax_in == null || r.wire_in <= p.cotterMax_in + 1e-6));
        for (const r of cands) { const c = Math.ceil(3 / (r.pkg || 1)) * r.price; if (!ret || c < retCost) { ret = r; retCost = c; } }
        if (!ret) continue;   // no hand-installable retainer known -> not admissible
      }
      const pinCost = Math.ceil(3 / (p.pkg || 1)) * p.price;
      out.push(Object.assign({}, p, { mat, retainer: ret, cost3: pinCost + retCost, pinCost, retCost, hole: DP1.holeFor(p) }));
    }
    return out.sort((x, y) => x.cost3 - y.cost3);
  }

  // ---------------------------------------------------------------- linear structural context for (beam, t, a)
  const WREF = 100;   // N, reference plate weight for the linear interpolation
  function linCtx(beam, t, a, opts) {
    const c0 = DP1.core(beam, t, a, 0, 13, PROB.overhang, opts.float), c1 = DP1.core(beam, t, a, WREF, 13, PROB.overhang, opts.float);
    const lin = (f) => { const v0 = f(c0), v1 = f(c1); return Wp => v0 + (v1 - v0) * Wp / WREF; };
    const R = {}; for (const k of ['Ox_f', 'Ox_r', 'Oy', 'Oz', 'F_f', 'F_r']) R[k] = lin(c => c.R[k]);
    const A = {}, T = {};
    for (const k of ['u', 'vb', 'vs', 'wb', 'ws', 'wpb', 'phi', 'thz']) { A[k] = lin(c => c.atA[k]); T[k] = lin(c => c.atRot[k]); }
    return { g: c0.g, R, A, T, c0, c1, t };
  }
  // Fast-accept bound on the beam von Mises stress (plate weights 0..WPMAX, net section of the largest admissible hole); a combination
  // that fails the bound is re-checked exactly before it is rejected.
  const WPMAX = 400;
  function beamStressBound(beam, ctx, dhMax, opts) {
    const cMax = DP1.core(beam, ctx.t, ctx.g.a, WPMAX, 13, PROB.overhang, opts.float);
    return Math.max(DP1.beamStress(beam, ctx.c0.g, ctx.c0.internal, dhMax).worst.vm, DP1.beamStress(beam, cMax.g, cMax.internal, dhMax).worst.vm);
  }

  // ---------------------------------------------------------------- O(1) screening of one combination (same checks as DP1.evaluate)
  const FAIL = {};
  function screen(beam, ctx, pl, pin, opts, sbound) {
    const g = ctx.g, a = g.a, sec = beam.sec;
    const design = { beam, plate: pl, pin, a };
    const dv = DP1.derive(design, opts);
    // cheap geometric and cost pre-checks
    if (dv.e_req > PROB.overhang) return { fail: 'beam end distance' };
    if (sec.H / 2 < dv.e_req) return { fail: 'beam edge distance' };
    if (dv.bMin < 2 * dv.e_req) return { fail: 'plate edge distance' };
    if (dv.usable < Math.max(dv.grips.O, dv.grips.A) - 1e-6) return { fail: 'pin too short' };
    const LcutIn = dv.Lcut / IN;
    const pOffer = pl.costFor(LcutIn); if (!pOffer) return { fail: 'plate stock too short' };
    const bOffer = DP1.cheapestLength(beam.item.offers, (dv.overhang - PROB.x_left) / IN); if (!bOffer) return { fail: 'beam stock too short' };
    const washerCost = dv.wash.cost;
    const cost = bOffer.price + pOffer.price + pin.cost3 + washerCost;
    if (cost >= opts._cutoff) return { fail: 'cost', cost };
    const Wp = dv.Wp;
    const R = {}; for (const k in ctx.R) R[k] = ctx.R[k](Wp);
    // deflection
    const Ap = pl.b * pl.t, Ep = pl.mat.E;
    const df = R.F_f * g.Lpp / (Ep * Ap), dr = R.F_r * g.Lpp / (Ep * Ap);
    const atA = {}, atR = {}; for (const k in ctx.A) { atA[k] = ctx.A[k](Wp); atR[k] = ctx.T[k](Wp); }
    const defl = DP1.cgFromVals(g, atA, atR, df, dr);
    if (defl.mag > PROB.deflLimit) return { fail: 'deflection', defl: defl.mag, cost };
    if (beam.Sy / sbound < PROB.FS) {
      const cc = DP1.core(beam, pl.t, a, Wp, dv.dh, PROB.overhang, opts.float);
      if (beam.Sy / DP1.beamStress(beam, cc.g, cc.internal, dv.dh).worst.vm < PROB.FS) return { fail: 'beam stress' };
    }
    let failName = null;
    const add = (group, name, demand, capacity, unit, FSreq, detail, kind) => {
      const ok = kind === 'geom' ? demand <= capacity + 1e-9 : capacity / demand >= FSreq - 1e-9;
      if (!ok) { failName = group + ': ' + name.replace(/\(.*$/, '').trim(); throw FAIL; }
      return true;
    };
    const env = { beam, plate: pl, pin, a, g, R, Wp, dv, opts };
    try { DP1.memberChecks(env, add); } catch (e) { if (e === FAIL) return { fail: failName }; throw e; }
    return { ok: true, cost, defl: defl.mag, bOffer, pOffer, Wp, Lcut: dv.Lcut, washerCost };
  }

  // ---------------------------------------------------------------- the search
  async function search(cat, opts, progress) {
    opts = Object.assign({}, DP1.DEFAULT_OPTS, { aMin: 300, aMax: 800, aStep: 10, bCap: 4 * IN, topN: 40 }, opts || {});
    const beams = beamOptions(cat), plates = plateOptions(cat, opts), pins = pinOptions(cat, opts);
    const thick = [...new Set(plates.map(p => p.t))].sort((x, y) => x - y);
    const dhMax = Math.max(...pins.map(p => DP1.holeFor(p).d_mm));
    const minPin = pins.length ? pins[0].cost3 : 0;
    // cheapest plate cost over all options for the shortest plates (lower bound)
    const minPlate = Math.min(...plates.map(p => { const o = p.costFor(Math.hypot(opts.aMin, 500) / IN); return o ? o.price : Infinity; }));
    beams.forEach(b => { b.lbCost = (() => { let best = Infinity; for (const o of b.item.offers) if (o.length_in * IN >= 1300 + 10 && o.price < best) best = o.price; return best; })(); });
    beams.sort((x, y) => x.lbCost - y.lbCost);
    const best = [];                 // top-N feasible (sorted by cost)
    opts._cutoff = Infinity;
    const stats = { combos: 0, cores: 0, fails: {}, perBeam: [] };
    const as = []; for (let a = opts.aMin; a <= opts.aMax + 1e-9; a += opts.aStep) as.push(a);
    let done = 0;
    const keyOf = r => `${r.beam.item.pn}|${r.beam.orient}|${r.pl.item.pn}|${r.pl.mode}|${r.pl.b.toFixed(1)}|${r.pin.pn}`;
    for (const beam of beams) {
      const pb = { beam, bestCost: Infinity, bestDefl: Infinity, minDeflAny: Infinity, reason: {} };
      stats.perBeam.push(pb);
      if (beam.lbCost + minPlate + minPin >= opts._cutoff) { pb.skipped = 'cost bound'; done++; continue; }
      const sec = beam.sec;
      // pins that fit this beam at all (grip at O, beam-height edge rule, 50 mm beam end)
      const pinsB = pins.filter(p => { const dh = p.hole.d_mm; return 2 * dh <= sec.H / 2 + 1e-9 && 2 * dh <= PROB.overhang + 1e-9 && p.usable_in * IN >= sec.W + 2 * PROB.t_br + 2 * opts.float - 1e-6; });
      if (!pinsB.length) { pb.reason['no pin fits this beam (grip or edge distance)'] = 1; done++; continue; }
      const dhB = Math.max(...pinsB.map(p => p.hole.d_mm));
      for (const t of thick) {
        const pinsBT = pinsB.filter(p => p.usable_in * IN >= sec.W + 2 * t + 2 * opts.float - 1e-6);
        if (!pinsBT.length) continue;
        const pls = plates.filter(p => Math.abs(p.t - t) < 1e-9).map(pl => ({ pl, pins: pinsBT.filter(p => pl.b - (pl.widthTol || 0) >= 4 * p.hole.d_mm - 1e-9) })).filter(x => x.pins.length);
        if (!pls.length) continue;
        for (const a of as) {
          const ctx = linCtx(beam, t, a, opts); stats.cores += 2;
          let sb = null;
          for (const { pl, pins: pp } of pls) {
            const plLBo = pl.costFor(ctx.g.Lpp / IN); const plLB = plLBo ? plLBo.price : 0;   // plate cost never drops as the cut length grows
            for (const pin of pp) {
              stats.combos++;
              if (beam.lbCost + plLB + pin.cost3 >= opts._cutoff) break;     // valid lower bound: pins sorted by cost3; washers >= 0
              if (sb === null) sb = beamStressBound(beam, ctx, dhB, opts);
              const r = screen(beam, ctx, pl, pin, opts, sb);
              if (r.defl !== undefined) pb.minDeflAny = Math.min(pb.minDeflAny, r.defl);
              if (!r.ok) { stats.fails[r.fail] = (stats.fails[r.fail] || 0) + 1; pb.reason[r.fail] = (pb.reason[r.fail] || 0) + 1; if (r.fail === 'deflection' && r.defl > PROB.deflLimit + 0.003) break; continue; }
              const rec = { beam, pl, pin, a, cost: r.cost, defl: r.defl, bOffer: r.bOffer, pOffer: r.pOffer };
              const k = keyOf(rec);
              const ex = best.find(x => x.key === k);
              if (ex) { if (rec.cost < ex.cost - 1e-9 || (Math.abs(rec.cost - ex.cost) < 1e-9 && rec.defl < ex.defl)) Object.assign(ex, rec); }
              else { rec.key = k; best.push(rec); }
              best.sort((x, y) => x.cost - y.cost || x.defl - y.defl);
              if (best.length > opts.topN) best.length = opts.topN;
              if (best.length === opts.topN) opts._cutoff = best[best.length - 1].cost + 1e-6;
              if (r.cost < pb.bestCost) { pb.bestCost = r.cost; pb.bestDefl = r.defl; }
            }
          }
        }
      }
      done++;
      if (progress && done % 4 === 0) { await progress(done / beams.length, best[0]); }
    }
    // full re-evaluation of the shortlist
    const final = [];
    for (const r of best) {
      const design = makeDesign(r);
      const ev = DP1.evaluate(design, opts);
      final.push({ r, design, ev });
    }
    return { best, final, stats, opts, counts: { beams: beams.length, plates: plates.length, pins: pins.length, thick: thick.length, as: as.length } };
  }

  function makeDesign(r) {
    return {
      beam: { item: r.beam.item, sec: r.beam.sec, mat: r.beam.mat, Sy: r.beam.Sy, orient: r.beam.orient },
      plate: { item: r.pl.item, t: r.pl.t, b: r.pl.b, widthTol: r.pl.widthTol, mat: r.pl.mat, Sy: r.pl.Sy, mode: r.pl.mode, offer: r.pl.mode === 'sheet' ? r.pOffer : null, how: r.pl.how, costFor: r.pl.costFor },
      pin: r.pin, a: r.a,
    };
  }

  // refine a around a given design (finer step) and return the cheapest/most robust a
  function refineA(r, opts, step) {
    const out = [];
    for (let a = Math.max(opts.aMin || 300, r.a - 20); a <= Math.min(PROB.aMax, r.a + 20) + 1e-9; a += (step || 2)) {
      const ev = DP1.evaluate(Object.assign(makeDesign(r), { a }), opts);
      out.push({ a, ev });
    }
    return out;
  }

  const API = { beamOptions, plateOptions, pinOptions, linCtx, screen, search, makeDesign, refineA };
  if (typeof module !== 'undefined' && module.exports) module.exports = API; else root.DP1S = API;
})(typeof window !== 'undefined' ? window : globalThis);
