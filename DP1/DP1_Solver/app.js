/* app.js — renders the Rotor Support Solver page from DP1 (solver), DP1S (search), DP1_CATALOG and DP1_PRECOMP. */
(function () {
  'use strict';
  const D = window.DP1, SR = window.DP1S, CAT = window.DP1_CATALOG, PRE = window.DP1_PRECOMP;
  const { IN, PROB, PW } = D;

  // ------------------------------------------------------------------ helpers
  const $ = s => document.querySelector(s);
  function h(tag, attrs, ...kids) {
    const e = document.createElement(tag);
    if (attrs) for (const k in attrs) {
      const v = attrs[k]; if (v == null || v === false) continue;
      if (k === 'class') e.className = v; else if (k === 'text') e.textContent = v; else if (k.startsWith('on')) e.addEventListener(k.slice(2), v);
      else if (k === 'style') e.setAttribute('style', v); else e.setAttribute(k, v === true ? '' : v);
    }
    for (const c of kids.flat()) if (c != null && c !== false) e.append(c instanceof Node ? c : document.createTextNode(String(c)));
    return e;
  }
  const SVGNS = 'http://www.w3.org/2000/svg';
  function s(tag, attrs, parent, text) {
    const e = document.createElementNS(SVGNS, tag);
    for (const k in attrs || {}) if (attrs[k] != null) e.setAttribute(k, attrs[k]);
    if (text != null) e.textContent = text;
    if (parent) parent.appendChild(e);
    return e;
  }
  const f = (x, d = 1) => (x == null || !isFinite(x)) ? '—' : Number(x).toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d });
  const f0 = x => f(x, 0), f1 = x => f(x, 1), f2 = x => f(x, 2), f3 = x => f(x, 3);
  const nm = x => f(x / 1000, 1);          // N·mm -> N·m (1 dp)
  const nm2 = x => f(x / 1000, 2);
  const inch = (mm, d = 3) => f(mm / IN, d);
  const money = x => '$' + f(x, 2);
  const vec = (v, d = 1) => '(' + v.map(x => f(x, d)).join(', ') + ')';
  const chip = (ok, t) => h('span', { class: 'chip ' + (ok === true ? 'pass' : ok === false ? 'fail' : ok), text: t || (ok ? 'PASS' : 'FAIL') });
  const frac = x => { const t = [[0.125, '1/8'], [0.1875, '3/16'], [0.25, '1/4'], [0.3125, '5/16'], [0.375, '3/8'], [0.4375, '7/16'], [0.5, '1/2'], [0.5625, '9/16'], [0.625, '5/8'], [0.75, '3/4'], [0.875, '7/8'], [1, '1'], [1.25, '1-1/4'], [1.5, '1-1/2'], [2, '2'], [2.5, '2-1/2'], [3, '3'], [3.5, '3-1/2'], [4, '4'], [5, '5'], [6, '6'], [8, '8']];
    for (const [v, n] of t) if (Math.abs(x - v) < 1e-4) return n; return f(x, 3).replace(/\.?0+$/, ''); };
  const table = (heads, rows, opts = {}) => {
    const thead = h('thead', null, h('tr', null, heads.map(x => h('th', { class: x.num ? 'num' : null, text: (x && typeof x === 'object') ? (x.t ?? '') : x }))));
    const tb = h('tbody');
    rows.forEach((r, i) => { const tr = h('tr', { class: (opts.rowClass && opts.rowClass(i)) || null }); r.forEach((c, j) => tr.append(c instanceof Node ? h('td', { class: heads[j].num ? 'num' : null }, c) : h('td', { class: heads[j].num ? 'num' : null, text: c }))); if (opts.onClick) { tr.classList.add('clickable'); tr.tabIndex = 0; tr.addEventListener('click', () => opts.onClick(i)); tr.addEventListener('keydown', e => { if (e.key === 'Enter') opts.onClick(i); }); } tb.append(tr); });
    return h('div', { class: 'tablewrap' }, h('table', null, thead, tb));
  };
  const eq = lines => h('pre', { class: 'eq', text: lines.join('\n') });
  const head = (no, title, sub) => h('div', { class: 'sheethead' }, h('h2', { text: title }), h('span', { class: 'sheetno', text: no + (sub ? ' · ' + sub : '') }));
  const pinName = p => `${frac(p.d_in)}" × ${f(p.usable_in, 3).replace(/\.?0+$/, '')}" usable ${p.style || 'pin'}`;
  const matName = k => (D.MATERIALS[k] || {}).name || k;
  const drill64 = lo => { const n = Math.floor((lo - 0.010) * 64), g = (a, b) => b ? g(b, a % b) : a, k = g(n, 64); return `${n / k}/${64 / k}`; };

  // ------------------------------------------------------------------ state
  const S = { opts: Object.assign({}, D.DEFAULT_OPTS, { aMin: 300, aMax: 800, aStep: 10, bCap: 4 * IN, topN: 40 }, PRE ? PRE.opts : {}), rows: [], sel: 0, ev: null, perBeam: PRE ? PRE.perBeam : [], stats: PRE ? PRE.stats : null, lists: null };
  function lists() {
    if (!S.lists || S.lists.key !== JSON.stringify([S.opts.bCap, S.opts.kerf, S.opts.float])) {
      S.lists = { key: JSON.stringify([S.opts.bCap, S.opts.kerf, S.opts.float]), beams: SR.beamOptions(CAT), plates: SR.plateOptions(CAT, S.opts), pins: SR.pinOptions(CAT, S.opts) };
    }
    return S.lists;
  }
  function designFromSpec(sp) {
    const L = lists();
    const beam = L.beams.find(b => b.item.pn === sp.beam && b.orient === sp.orient);
    const pl = L.plates.find(p => p.item.pn === sp.plate && p.mode === sp.mode && Math.abs(p.b - sp.b) < 0.05 && (!sp.sheet || (p.sheet && p.sheet.pn === sp.sheet)));
    const pin = L.pins.find(p => p.pn === sp.pin);
    if (!beam || !pl || !pin) return null;
    return SR.makeDesign({ beam, pl, pin, a: sp.a });
  }
  const specOf = r => ({ beam: r.beam.item.pn, orient: r.beam.orient, plate: r.pl.item.pn, mode: r.pl.mode, b: r.pl.b, sheet: r.pl.sheet ? r.pl.sheet.pn : null, pin: r.pin.pn, a: r.a });

  // ------------------------------------------------------------------ charts
  let tipEl = null;
  function lineChart(cfg) {
    // cfg: { title, unit, series: [{name, color, pts: [[x,y]]}], xLabel, xFmt, yFmt, marks: [{x, label}], hlines: [{y, label}], width, height, legend }
    const W = cfg.width || 420, H = cfg.height || 190, m = { l: 52, r: 14, t: 14, b: 30 };
    const xs = cfg.series.flatMap(sr => sr.pts.map(p => p[0])), ys = cfg.series.flatMap(sr => sr.pts.map(p => p[1])).concat((cfg.hlines || []).map(l => l.y));
    let x0 = cfg.xmin ?? Math.min(...xs), x1 = cfg.xmax ?? Math.max(...xs);
    let y0 = Math.min(0, ...ys), y1 = Math.max(0, ...ys); if (cfg.ymin != null) y0 = cfg.ymin; if (cfg.ymax != null) y1 = cfg.ymax;
    if (y1 - y0 < 1e-9) { y1 += 1; y0 -= 1; }
    const nice = (lo, hi, n) => { const span = hi - lo, step0 = span / n, mag = 10 ** Math.floor(Math.log10(step0)), st = [1, 2, 2.5, 5, 10].map(k => k * mag).find(k => span / k <= n) || mag * 10; return { lo: Math.floor(lo / st) * st, hi: Math.ceil(hi / st) * st, st }; };
    const ny = nice(y0, y1, 4); y0 = ny.lo; y1 = ny.hi;
    const X = x => m.l + (x - x0) / (x1 - x0) * (W - m.l - m.r), Y = y => m.t + (y1 - y) / (y1 - y0) * (H - m.t - m.b);
    const wrap = h('div', { class: 'chart' });
    const svg = s('svg', { viewBox: `0 0 ${W} ${H}`, width: '100%', role: 'img', 'aria-label': cfg.title || 'chart' });
    for (let y = y0; y <= y1 + 1e-9; y += ny.st) {
      s('line', { x1: m.l, x2: W - m.r, y1: Y(y), y2: Y(y), stroke: 'var(--rule)', 'stroke-width': Math.abs(y) < 1e-9 ? 1.2 : 1 }, svg);
      s('text', { x: m.l - 6, y: Y(y) + 4, 'text-anchor': 'end', 'font-size': 10, class: 't-mono t-muted' }, svg, (cfg.yFmt || (v => f(v, Math.abs(ny.st) < 1 ? 2 : 0)))(y));
    }
    const nx = nice(x0, x1, cfg.xTicks || 6);
    for (let x = nx.lo; x <= x1 + 1e-9; x += nx.st) { if (x < x0 - 1e-9) continue; s('text', { x: X(x), y: H - m.b + 15, 'text-anchor': 'middle', 'font-size': 10, class: 't-mono t-muted' }, svg, (cfg.xFmt || f0)(x)); }
    if (cfg.xLabel) s('text', { x: W - m.r, y: H - 2, 'text-anchor': 'end', 'font-size': 10, class: 't-muted' }, svg, cfg.xLabel);
    for (const mk of cfg.marks || []) { if (mk.x < x0 || mk.x > x1) continue; s('line', { x1: X(mk.x), x2: X(mk.x), y1: m.t, y2: H - m.b, stroke: 'var(--muted)', 'stroke-width': 1, 'stroke-dasharray': '2 3', opacity: 0.6 }, svg); s('text', { x: X(mk.x) + 3, y: m.t + 9, 'font-size': 9.5, class: 't-muted' }, svg, mk.label); }
    for (const hl of cfg.hlines || []) { s('line', { x1: m.l, x2: W - m.r, y1: Y(hl.y), y2: Y(hl.y), stroke: hl.color || 'var(--fail)', 'stroke-width': 1.2 }, svg); s('text', { x: W - m.r - 2, y: Y(hl.y) - 4, 'text-anchor': 'end', 'font-size': 10, fill: hl.color || 'var(--fail)' }, svg, hl.label); }
    for (const sr of cfg.series) {
      const d = sr.pts.map((p, i) => (i ? 'L' : 'M') + X(p[0]).toFixed(1) + ' ' + Y(p[1]).toFixed(1)).join(' ');
      if (sr.fill) s('path', { d: d + ` L${X(sr.pts[sr.pts.length - 1][0]).toFixed(1)} ${Y(0).toFixed(1)} L${X(sr.pts[0][0]).toFixed(1)} ${Y(0).toFixed(1)} Z`, fill: sr.color, opacity: 0.1, stroke: 'none' }, svg);
      s('path', { d, fill: 'none', stroke: sr.color, 'stroke-width': 2, 'stroke-linejoin': 'round', 'stroke-linecap': 'round', 'stroke-dasharray': sr.dash || null }, svg);
      if (sr.dot) for (const p of sr.dot) s('circle', { cx: X(p[0]), cy: Y(p[1]), r: 4.5, fill: sr.color, stroke: 'var(--sheet)', 'stroke-width': 2 }, svg);
      if (sr.endLabel) { const p = sr.pts[sr.pts.length - 1]; s('text', { x: X(p[0]) - 4, y: Y(p[1]) - 6, 'text-anchor': 'end', 'font-size': 10, class: 't-ink' }, svg, sr.endLabel); }
    }
    // hover crosshair
    const cross = s('line', { y1: m.t, y2: H - m.b, stroke: 'var(--ink-2)', 'stroke-width': 1, visibility: 'hidden' }, svg);
    const hit = s('rect', { x: m.l, y: m.t, width: W - m.l - m.r, height: H - m.t - m.b, fill: 'transparent' }, svg);
    const show = (ev) => {
      const r = svg.getBoundingClientRect(), px = (ev.clientX - r.left) / r.width * W;
      const xv = x0 + (px - m.l) / (W - m.l - m.r) * (x1 - x0);
      cross.setAttribute('x1', px); cross.setAttribute('x2', px); cross.setAttribute('visibility', 'visible');
      if (!tipEl) { tipEl = h('div', { class: 'tip' }); }
      wrap.append(tipEl);
      tipEl.textContent = '';
      tipEl.append(h('div', { class: 'label', text: (cfg.xName || 'x') + ' = ' + (cfg.xFmt || f0)(xv) + (cfg.xUnit || '') }));
      for (const sr of cfg.series) {
        let best = sr.pts[0]; for (const p of sr.pts) if (Math.abs(p[0] - xv) < Math.abs(best[0] - xv)) best = p;
        tipEl.append(h('div', null, h('span', { style: `display:inline-block;width:12px;height:2px;background:${sr.color};vertical-align:middle;margin-right:6px` }), h('b', { text: (cfg.yFmt || (v => f(v, 2)))(best[1]) + ' ' + (cfg.unit || '') }), ' ', h('span', { class: 'small', text: sr.name })));
      }
      const wr = wrap.getBoundingClientRect();
      tipEl.style.left = Math.min(ev.clientX - wr.left + 12, wr.width - 170) + 'px'; tipEl.style.top = (ev.clientY - wr.top + 10) + 'px';
    };
    hit.addEventListener('pointermove', show);
    hit.addEventListener('pointerleave', () => { cross.setAttribute('visibility', 'hidden'); if (tipEl && tipEl.parentNode === wrap) tipEl.remove(); });
    if (cfg.title) wrap.append(h('div', { class: 'label', style: 'margin-bottom:4px', text: cfg.title }));
    if (cfg.legend) wrap.append(h('div', { class: 'legend', style: 'margin-bottom:4px' }, cfg.series.map(sr => h('span', { style: `--k:${sr.color}`, text: sr.name }))));
    wrap.append(svg);
    return wrap;
  }

  // ------------------------------------------------------------------ evaluation & search
  function evaluateSel() {
    const row = S.rows[S.sel];
    const des = row ? designFromSpec(row.spec) : null;
    S.ev = des ? D.evaluate(des, S.opts) : null;
  }
  async function runSearch() {
    const btn = $('#runBtn'), bar = $('#prog > div'), st = $('#searchStatus');
    btn.disabled = true; st.textContent = 'Searching…';
    S.lists = null; const t0 = performance.now();
    const res = await SR.search(CAT, Object.assign({}, S.opts), async (fr, best) => { bar.style.width = (fr * 100).toFixed(0) + '%'; st.textContent = `Searching… ${(fr * 100).toFixed(0)} %` + (best ? ` · best so far ${money(best.cost)}` : ''); await new Promise(r => setTimeout(r, 0)); });
    S.rows = res.final.map(x => ({ spec: specOf(x.r), cost: x.ev.cost.total, defl: x.ev.defl.mag, minFS: x.ev.minFS, gov: x.ev.governing.name, ok: x.ev.ok }))
      .filter(r => r.ok).sort((p, q) => p.cost - q.cost || p.defl - q.defl);
    S.perBeam = summarizePerBeam(res.stats.perBeam); S.stats = { combos: res.stats.combos, cores: res.stats.cores, fails: res.stats.fails, counts: res.counts, seconds: (performance.now() - t0) / 1000 };
    S.sel = 0; bar.style.width = '100%'; btn.disabled = false;
    st.textContent = S.rows.length ? `Done in ${S.stats.seconds.toFixed(1)} s · ${S.rows.length} passing designs kept` : 'No design passes with these settings.';
    evaluateSel(); renderAll(true);
  }
  function summarizePerBeam(pb) {
    return pb.map(p => ({ pn: p.beam.item.pn, orient: p.beam.orient, mat: p.beam.item.mat, lb: p.beam.lbCost, desc: beamDesc(p.beam.item), bestCost: isFinite(p.bestCost) ? p.bestCost : null, minDefl: isFinite(p.minDeflAny) ? p.minDeflAny : null, skipped: p.skipped || null, reasons: Object.entries(p.reason).sort((a, b) => b[1] - a[1]).slice(0, 3).map(x => x[0]) }));
  }
  const beamDesc = it => `${frac(it.dimA_in)}" × ${frac(it.dimB_in)}"${it.kind === 'tube' ? ' × ' + frac(it.t_in) + '" wall tube' : ' solid bar'}, ${matName(it.mat)}`;
  const plateDesc = p => `${frac(p.item.t_in)}" × ${p.item.shape === 'flat_bar' ? frac(p.item.w_in) + '" bar' : 'sheet'}, ${matName(p.item.mat)}`;

  // ------------------------------------------------------------------ sections
  function renderMeta() {
    const m = $('#meta'); m.textContent = '';
    m.append(h('span', { text: `Catalog read from mcmaster.com on ${CAT.meta.date}` }),
      h('span', { text: `${CAT.beams.length} beam stocks · ${CAT.plateStocks.length} plate stocks · ${CAT.pins.length} stainless pins` }),
      h('span', { text: 'Due 16 Oct 2026, 11:59 pm' }));
  }

  function renderAnswer() {
    const el = $('#answer'); el.textContent = '';
    const ev = S.ev;
    el.append(head('Answer', 'Cheapest design that meets every requirement', S.sel === 0 ? 'rank 1 of the search' : `rank ${S.sel + 1} (selected)`));
    if (!ev) { el.append(h('p', { text: 'No passing design with the current solver settings. Relax a setting in the Solver sheet.' })); return; }
    const d = ev.design, c = ev.cost, dv = ev.dv;
    const left = h('div', { class: 'stack' });
    left.append(h('div', { class: 'label', text: 'Procurement cost (McMaster list price)' }), h('div', { class: 'hero', text: money(c.total) }),
      h('div', null, chip(ev.ok, ev.ok ? 'MEETS ALL REQUIREMENTS' : 'FAILS A REQUIREMENT'), ' ', h('span', { class: 'small note', text: S.opts.pinBending ? 'pin bending checked at FS 2' : 'pin bending NOT checked (shear + bearing only)' })));
    const parts = h('div', { class: 'parts' });
    const part = (what, pn, desc, price) => parts.append(h('div', { class: 'part' }, h('div', { class: 'what', text: what }), h('div', null, h('div', { class: 'pn', text: pn }), h('div', { class: 'small note', text: desc })), h('div', { class: 'price', text: money(price) })));
    part('Beam', c.beam.pn, `${beamDesc(d.beam.item)}; ${d.beam.orient}; buy ${c.beam.label || f(c.beam.length_in / 12, 1) + ' ft'}, cut to 1350 mm`, c.beam.price);
    part('Diagonals', c.plate.pn, `${plateDesc(d.plate)}; ${c.plateHow}; buy ${c.plate.label || f(c.plate.length_in / 12, 1) + ' ft'}`, c.plate.price);
    part('Pins ×3', d.pin.pn, `${pinName(d.pin)}, ${d.pin.material}${d.pin.pkg > 1 ? `, pack of ${d.pin.pkg}` : ''}`, c.pinCost);
    if (c.ret) part('Retainers ×3', c.ret.pn, `${c.ret.type}, ${c.ret.material}${c.ret.pkg > 1 ? `, pack of ${c.ret.pkg}` : ''}`, c.retCost);
    if (c.washer) part(`Washers ×${c.washerCount}`, c.washer.pn, `${c.washer.desc}; ${c.washerPerJoint[1]} under the pin head at A and ${c.washerPerJoint[2]} at B, so the plates cannot walk along the pin`, c.washerCost);
    left.append(parts);
    const right = h('div', { class: 'stack' });
    const meter = (label, val, lim, fmtv, lower) => {
      const frac_ = lower ? Math.min(lim / val, 1) : Math.min(val / lim, 1);
      return h('div', { class: 'meter' }, h('div', { class: 'row' }, h('span', { text: label }), h('span', { class: 'mono', text: fmtv })), h('div', { class: 'track' }, h('div', { class: 'fill' + (frac_ > 0.9 ? ' hot' : ''), style: `width:${(frac_ * 100).toFixed(1)}%` })));
    };
    right.append(h('div', { class: 'label', text: 'Margins' }));
    right.append(meter('Rotor-CG deflection (limit 0.70 mm)', ev.defl.mag, 0.7, `${f3(ev.defl.mag)} mm`));
    right.append(meter(`Lowest factor of safety (required 2.0)`, ev.minFS, 2, `${f2(ev.minFS)}`, true));
    right.append(h('p', { class: 'small note' }, 'Smallest margin: ', h('b', { text: ev.governing.name }), ` (FS ${f2(ev.governing.fs)} vs ${f1(ev.governing.FSreq)} required).`));
    right.append(h('dl', { class: 'kv' },
      h('dt', { text: 'Diagonal attaches at' }), h('dd', { text: `x = −${d.a} mm (a = ${d.a} mm from O)` }),
      h('dt', { text: 'Plate size' }), h('dd', { text: `${inch(d.plate.b, 3)} in × ${frac(d.plate.item.t_in)} in × ${inch(dv.Lcut, 2)} in long (×2)` }),
      h('dt', { text: 'Pin holes' }), h('dd', { text: `Ø${f(dv.hole.lo_in, 4)}–${f(dv.hole.hi_in, 4)} in, drill + ream` }),
      h('dt', { text: 'Beam' }), h('dd', { text: `${d.beam.orient}, 1350 mm long` }),
      h('dt', { text: 'Checks' }), h('dd', { text: `${ev.checks.filter(k => k.ok).length} of ${ev.checks.length} pass` })));
    el.append(h('div', { class: 'answer' }, left, right));
  }

  function renderCompliance() {
    const el = $('#compliance'); el.textContent = '';
    const ev = S.ev; if (!ev) return;
    el.append(head('Requirements', 'Compliance with the 13 requirements', 'every row is computed for the selected design'));
    const d = ev.design, dv = ev.dv, c = ev.cost, g = ev.g;
    const byName = re => ev.checks.filter(k => re.test(k.name));
    const allOk = re => byName(re).every(k => k.ok);
    const minFSof = re => Math.min(...byName(re).filter(k => k.fs != null).map(k => k.fs));
    const rows = [
      ['1', 'Flow 2.5 m/s, rotor 500 × 500 mm', `P_fluid = ½ρAV³ = ${f0(PW.P_fluid)} W`, true],
      ['2', '30 % hydraulic at 285 rpm, 82 % electrical', `P_mech = ${f1(PW.P_mech)} W, P_elec = ${f1(PW.P_elec)} W, T = ${f2(PW.T_rotor / 1000)} N·m`, true],
      ['3', 'Beam: one piece of corrosion-resistant McMaster stock, planar top/front/rear, top ⟂ sides', `${c.beam.pn}: ${beamDesc(d.beam.item)} (${d.beam.item.kind === 'tube' ? 'rectangular tube' : 'solid bar'})`, true],
      ['3', 'Diagonals: flat plates cut from one piece of corrosion-resistant McMaster stock', `${c.plate.pn}: two ${inch(dv.Lcut, 2)} in plates, ${c.plateHow}; needs ${f2(c.plateNeedIn)} in of ${f1(c.plate.length_in)} in`, c.ok],
      ['4', 'Sprocket pitch diameters 9.554 in / 3.038 in, generator ≈ 900 rpm', `#40 chain (½ in pitch); generator ${f0(PW.rpm_gen)} rpm; chain tension ${f1(PW.T_chain)} N`, true],
      ['5', 'Drag 560 N in +z', 'applied at the COP, (h/2 + 500) mm below the beam axis', true],
      ['6', 'Rotor turns +y; axis 100 mm from the beam end', 'tight chain span on −z (rear); beam from x = −1300 mm', true],
      ['7', 'No chain preload', 'slack span tension = 0', true],
      ['8', 'Rotor 150 N (CG 350 mm below beam), generator 120 N', 'both in the load table; beam and plate self-weight added', true],
      ['9', 'Identical hand-removable stainless McMaster pins; edge distance ≥ 2 × hole', `${d.pin.pn} (${pinName(d.pin)}); ${c.ret ? 'hairpin-type retainer, no tools' : 'self-retaining quick-release, no tools'}; edge rule: beam ${f1(g.H / 2)} ≥ ${f1(dv.e_req)} mm, plate ${f1(d.plate.b / 2)} ≥ ${f1(dv.e_req)} mm, ends ${dv.e_end} mm`, allOk(/edge|2 d_hole|usable length/i)],
      ['10', 'Brackets ½ in Al (35 ksi); x-torsion carried by the diagonals', `bracket bearing FS ${f2(minFSof(/Bracket bearing/))}; O carries no torque about x`, allOk(/Bracket/)],
      ['11', 'Factor of safety ≥ 2 on material strength', `lowest FS ${f2(ev.minFS)} (${ev.governing.name})`, ev.checks.filter(k => k.kind !== 'geom').every(k => k.ok)],
      ['12', 'Rotor-CG deflection ≤ 0.7 mm, including twist', `|u| = ${f3(ev.defl.mag)} mm (${f0(ev.defl.mag / 0.7 * 100)} % of the limit)`, ev.defl.mag <= 0.7],
      ['13', 'Beam z-width ≥ 4 in', `${inch(g.W, 3)} in`, g.W >= PROB.minWidth - 1e-9],
      ['Fig. 2', 'Diagonal attaches within 800 mm of O; pins on the neutral axis', `a = ${d.a} mm; all holes at y = 0`, d.a <= 800],
    ];
    el.append(table([{ t: 'Req.' }, { t: 'Requirement' }, { t: 'How the design meets it' }, { t: 'Status' }], rows.map(r => [r[0], r[1], r[2], chip(r[3])])));
  }

  function renderSolver(fresh) {
    const el = $('#solver'); el.textContent = '';
    el.append(head('Solver', 'Search every catalog combination', 'branch-and-bound on cost, then full re-check'));
    el.append(h('p', { class: 'note', text: 'For each beam (both orientations with ≥ 4 in width), plate thickness and attachment distance a, the solver solves the statics and the beam deflection exactly, then screens every plate stock (as bought, ripped or cut from sheet) and every pin with its retainer and washers against all checks. The cheapest designs are re-evaluated with the full model shown in sheets A–F. Untick "Require pin bending" to see what a shear-and-bearing-only pin check would allow; the joint-compliance box is a sensitivity study, not part of requirement 12.' }));
    const o = S.opts;
    const num = (id, label, val, step, min, max, unit) => h('label', { class: 'ctl', for: id }, h('span', { class: 'label', text: label + (unit ? ` (${unit})` : '') }), h('input', { id, type: 'number', value: val, step, min, max }));
    const ctl = h('div', { class: 'controls' },
      h('label', { class: 'ctl check', for: 'optBend' }, h('input', { id: 'optBend', type: 'checkbox', checked: o.pinBending }), 'Require pin bending FS ≥ 2'),
      h('label', { class: 'ctl check', for: 'optJoint' }, h('input', { id: 'optJoint', type: 'checkbox', checked: o.jointCompliance }), 'Sensitivity: add pin-joint compliance (Huth)'),
      num('optFloat', 'Bracket clearance at O', o.float, 0.1, 0, 3, 'mm'),
      num('optAmin', 'a min', o.aMin, 10, 300, 800, 'mm'), num('optAmax', 'a max', o.aMax, 10, 300, 800, 'mm'), num('optAstep', 'a step', o.aStep, 5, 2, 50, 'mm'),
      num('optBcap', 'Max plate width', +(o.bCap / IN).toFixed(2), 0.25, 1, 8, 'in'),
      h('button', { id: 'runBtn', onclick: () => { readOpts(); runSearch(); } }, 'Run search'));
    el.append(ctl, h('div', { class: 'progress', id: 'prog' }, h('div', { style: 'width:100%' })), h('div', { class: 'small note', id: 'searchStatus', text: S.stats ? `${S.stats.counts ? S.stats.counts.beams + ' beam orientations × ' + S.stats.counts.plates + ' plate options × ' + S.stats.counts.pins + ' pins × ' + S.stats.counts.as + ' values of a' : ''} · ${f0(S.stats.combos)} combinations screened${S.stats.seconds ? ' in ' + S.stats.seconds.toFixed(1) + ' s' : ''}. Click a row to load that design into every sheet.` : '' }));
    if (!S.rows.length) { el.append(h('p', { text: 'No passing designs.' })); return; }
    const L = lists();
    const rows = S.rows.slice(0, 25).map((r, i) => {
      const sp = r.spec, it = CAT.beams.find(b => b.pn === sp.beam), pl = CAT.plateStocks.find(p => p.pn === sp.plate), pn = CAT.pins.find(p => p.pn === sp.pin);
      return [String(i + 1), money(r.cost), `${sp.beam} · ${beamDesc(it)} · ${sp.orient}`, `${sp.plate} · ${frac(pl.t_in)}" ${pl.shape === 'flat_bar' ? '× ' + frac(pl.w_in) + '"' : 'sheet'} ${matName(pl.mat).split(' ')[0]} (${sp.mode}${sp.mode !== 'bar' ? ', b = ' + inch(sp.b, 2) + '"' : ''})`, `${sp.pin} · ${frac(pn.d_in)}" ${pn.style}`, String(sp.a), f3(r.defl), f2(r.minFS)];
    });
    el.append(table([{ t: '#' }, { t: 'Cost', num: true }, { t: 'Beam' }, { t: 'Plate stock' }, { t: 'Pin' }, { t: 'a (mm)', num: true }, { t: 'CG defl (mm)', num: true }, { t: 'min FS', num: true }], rows,
      { rowClass: i => i === S.sel ? 'sel' : null, onClick: i => { S.sel = i; evaluateSel(); renderAll(); location.hash = 'answer'; } }));
    // why nothing cheaper
    const pb = (S.perBeam || []).filter(p => p.lb != null).sort((a, b) => a.lb - b.lb).slice(0, 14);
    if (pb.length) {
      el.append(h('h3', { text: 'Why the cheaper beams lose' }));
      el.append(h('p', { class: 'note small', text: 'The cheapest beam stocks in the catalog, the best design each one allows, and the checks that most often rejected its combinations.' }));
      el.append(table([{ t: 'Beam stock' }, { t: 'Beam price', num: true }, { t: 'Best passing design', num: true }, { t: 'Lowest CG deflection seen', num: true }, { t: 'Main reasons rejected' }],
        pb.map(p => [`${p.pn} · ${p.desc} · ${p.orient}`, money(p.lb), p.bestCost ? money(p.bestCost) : '—', p.minDefl != null ? f3(p.minDefl) + ' mm' : '—', p.skipped ? 'not searched: cost bound already beaten' : (p.reasons.join('; ') || '—')])));
    }
  }
  function readOpts() {
    const o = S.opts;
    o.pinBending = $('#optBend').checked; o.jointCompliance = $('#optJoint').checked;
    o.float = +$('#optFloat').value; o.aMin = +$('#optAmin').value; o.aMax = +$('#optAmax').value; o.aStep = Math.max(2, +$('#optAstep').value);
    o.bCap = +$('#optBcap').value * IN;
  }

  // ------------------------------------------------------------------ FBD figures
  function arrow(svg, x1, y1, x2, y2, color, label, lx, ly, anchor) {
    const ang = Math.atan2(y2 - y1, x2 - x1), hl = 8;
    s('line', { x1, y1, x2, y2, stroke: color, 'stroke-width': 2 }, svg);
    s('path', { d: `M${x2} ${y2} L${x2 - hl * Math.cos(ang - 0.4)} ${y2 - hl * Math.sin(ang - 0.4)} L${x2 - hl * Math.cos(ang + 0.4)} ${y2 - hl * Math.sin(ang + 0.4)} Z`, fill: color }, svg);
    if (label) s('text', { x: lx ?? x2, y: ly ?? y2, 'font-size': 11, 'text-anchor': anchor || 'start', class: 't-ink' }, svg, label);
  }
  function fbdSide(ev) {
    const g = ev.g, R = ev.R, d = ev.design, H = g.H;
    const W = 980, Hh = 660, sc = 0.52, ox = 760, oy = 300;   // px per mm, origin at O
    const X = x => ox + x * sc, Y = y => oy - y * sc;
    const svg = s('svg', { viewBox: `0 0 ${W} ${Hh}`, width: '100%', style: 'min-width:720px', role: 'img', 'aria-label': 'Side view free-body diagram of the support beam' });
    const ink = 'var(--ink)', mut = 'var(--muted)';
    // structure + brackets
    for (let i = 0; i < 16; i++) s('line', { x1: X(95), y1: Y(-140 + i * 45), x2: X(125), y2: Y(-140 + i * 45 + 30), stroke: mut }, svg);
    s('line', { x1: X(95), y1: Y(-150), x2: X(95), y2: Y(580), stroke: ink, 'stroke-width': 1.5 }, svg);
    s('path', { d: `M${X(95)} ${Y(40)} L${X(-25)} ${Y(25)} L${X(-25)} ${Y(-25)} L${X(95)} ${Y(-40)} Z`, fill: 'none', stroke: mut }, svg);
    s('path', { d: `M${X(95)} ${Y(540)} L${X(-25)} ${Y(525)} L${X(-25)} ${Y(475)} L${X(95)} ${Y(460)} Z`, fill: 'none', stroke: mut }, svg);
    // beam
    s('rect', { x: X(-1300), y: Y(H / 2), width: 1350 * sc, height: H * sc, fill: 'var(--accent-wash)', stroke: ink, 'stroke-width': 1.3 }, svg);
    s('line', { x1: X(-1320), x2: X(70), y1: Y(0), y2: Y(0), stroke: mut, 'stroke-dasharray': '10 4 2 4' }, svg);
    // shaft box, rotor, sprockets, chain, generator
    s('rect', { x: X(-1300), y: Y(H / 2 + 140), width: 200 * sc, height: 140 * sc, fill: 'none', stroke: mut }, svg);
    s('text', { x: X(-1200), y: Y(H / 2 + 60), 'text-anchor': 'middle', 'font-size': 10, class: 't-muted' }, svg, 'shaft box');
    s('line', { x1: X(-1200), x2: X(-1200), y1: Y(H / 2 + 160), y2: Y(g.y_cop - 260), stroke: mut, 'stroke-width': 3 }, svg);
    s('rect', { x: X(-1450), y: Y(g.y_cop + 250), width: 500 * sc, height: 500 * sc, fill: 'none', stroke: mut, 'stroke-dasharray': '4 3' }, svg);
    s('text', { x: X(-1440), y: Y(g.y_cop + 230), 'font-size': 10, class: 't-muted' }, svg, 'rotor 500 × 500');
    s('line', { x1: X(-1200 - PW.R1), x2: X(-1200 + PW.R1), y1: Y(g.y_chain), y2: Y(g.y_chain), stroke: mut, 'stroke-width': 4 }, svg);
    s('line', { x1: X(PROB.x_gen - PW.R2), x2: X(PROB.x_gen + PW.R2), y1: Y(g.y_chain), y2: Y(g.y_chain), stroke: mut, 'stroke-width': 4 }, svg);
    s('line', { x1: X(-1200 + PW.R1), x2: X(PROB.x_gen - PW.R2), y1: Y(g.y_chain), y2: Y(g.y_chain), stroke: mut, 'stroke-dasharray': '3 3' }, svg);
    s('text', { x: X(-700), y: Y(g.y_chain) + 14, 'font-size': 10, class: 't-muted', 'text-anchor': 'middle' }, svg, `chain (internal), tight span ${f1(PW.T_chain)} N on −z`);
    s('rect', { x: X(PROB.x_gen - 60), y: Y(H / 2 + 110), width: 120 * sc, height: 110 * sc, fill: 'none', stroke: mut }, svg);
    s('text', { x: X(PROB.x_gen), y: Y(H / 2 + 125), 'text-anchor': 'middle', 'font-size': 10, class: 't-muted' }, svg, 'generator');
    s('line', { x1: X(PROB.x_gen), x2: X(PROB.x_gen), y1: Y(H / 2), y2: Y(g.y_chain), stroke: mut, 'stroke-width': 2 }, svg);
    // plate
    const a = g.a, ux = g.u[0], uy = g.u[1], bb = d.plate.b, nx = -uy, ny = ux, e = ev.dv.e_end;
    const P = (x, y) => `${X(x)} ${Y(y)}`;
    const p1 = [-a - e * ux + nx * bb / 2, -e * uy + ny * bb / 2], p2 = [e * ux + nx * bb / 2, 500 + e * uy + ny * bb / 2], p3 = [e * ux - nx * bb / 2, 500 + e * uy - ny * bb / 2], p4 = [-a - e * ux - nx * bb / 2, -e * uy - ny * bb / 2];
    s('path', { d: `M${P(...p1)} L${P(...p2)} L${P(...p3)} L${P(...p4)} Z`, fill: 'var(--rule)', stroke: ink, opacity: 0.9 }, svg);
    for (const [x, y, lab] of [[0, 0, 'O'], [-a, 0, 'A'], [0, 500, 'B']]) { s('circle', { cx: X(x), cy: Y(y), r: 5, fill: 'var(--sheet)', stroke: ink, 'stroke-width': 1.5 }, svg); s('text', { x: X(x) - 14, y: Y(y) - 9, 'font-size': 13, 'font-weight': 600, class: 't-ink' }, svg, lab); }
    // loads (red = applied, blue = reactions)
    const ap = 'var(--fail)', re = 'var(--accent)', L = 70;
    arrow(svg, X(-1200), Y(g.y_cg) - L, X(-1200), Y(g.y_cg), ap, `W_rotor ${f0(PROB.W_rotor)} N`, X(-1200) + 8, Y(g.y_cg) - 30);
    s('circle', { cx: X(-1200), cy: Y(g.y_cg), r: 4, fill: ap }, svg); s('text', { x: X(-1200) - 8, y: Y(g.y_cg) + 4, 'text-anchor': 'end', 'font-size': 10, class: 't-muted' }, svg, 'CG');
    s('circle', { cx: X(-1200), cy: Y(g.y_cop), r: 8, fill: 'none', stroke: ap, 'stroke-width': 2 }, svg); s('circle', { cx: X(-1200), cy: Y(g.y_cop), r: 2.5, fill: ap }, svg);
    s('text', { x: X(-1200) + 13, y: Y(g.y_cop) + 4, 'font-size': 11, class: 't-ink' }, svg, `Drag ${PROB.drag} N (+z, out of page) at COP`);
    s('text', { x: X(-1200) + 13, y: Y(g.y_cop) + 20, 'font-size': 11, class: 't-ink' }, svg, `Water torque ${f2(PW.T_rotor / 1000)} N·m about +y`);
    arrow(svg, X(PROB.x_gen), Y(H / 2 + 110) - 50, X(PROB.x_gen), Y(H / 2 + 110), ap, `W_gen ${PROB.W_gen} N`, X(PROB.x_gen) + 6, Y(H / 2 + 110) - 34);
    const xm = (g.x_left + g.x_right) / 2;
    arrow(svg, X(xm), Y(H / 2) - 40, X(xm), Y(H / 2), ap, `W_beam ${f1(ev.AL.Wb)} N (uniform)`, X(xm) - 6, Y(H / 2) - 26, 'end');
    // reactions at A (plate forces on beam), O
    const Af = [R.F_f * ux, R.F_f * uy], Ar = [R.F_r * ux, R.F_r * uy];
    const sA = 0.024;
    arrow(svg, X(-a), Y(0), X(-a) + Ar[0] * sA, Y(0) - Ar[1] * sA, re, `rear plate ${f0(R.F_r)} N`, X(-a) + Ar[0] * sA + 4, Y(0) - Ar[1] * sA);
    arrow(svg, X(-a), Y(0), X(-a) + Af[0] * sA, Y(0) - Af[1] * sA, re, `front plate ${f0(R.F_f)} N`, X(-a) + Af[0] * sA - 4, Y(0) - Af[1] * sA + 14, 'end');
    const Ox = R.Ox_f + R.Ox_r, Oy = R.Oy;
    arrow(svg, X(0) - Math.sign(Ox || 1) * 70, Y(0) + 40, X(0) - 6 * Math.sign(Ox || 1), Y(0) + 40, re, `ΣOx ${f0(Ox)} N`, X(0) - 80, Y(0) + 56);
    arrow(svg, X(0) + 30, Y(0) - Math.sign(Oy) * 60, X(0) + 30, Y(0) - Math.sign(Oy) * 6, re, `Oy ${f0(Oy)} N`, X(0) + 36, Y(0) - Math.sign(Oy) * 40);
    s('text', { x: 16, y: 22, 'font-size': 12, class: 't-ink', 'font-weight': 600 }, svg, 'Side view (x right, y up, z out of the page) — drawn to scale');
    s('text', { x: 16, y: 40, 'font-size': 11, class: 't-muted' }, svg, 'red: applied loads · blue: reactions on the beam (plate forces drawn as their x-y components) · front/rear split in the plan view');
    // dims
    s('text', { x: X(-a / 2), y: Y(0) + 34 + H * sc / 2, 'text-anchor': 'middle', 'font-size': 10, class: 't-mono t-muted' }, svg, `a = ${a} mm`);
    return svg;
  }
  function fbdPlan(ev) {
    const g = ev.g, R = ev.R, d = ev.design;
    const W = 980, Hh = 430, sc = 0.52, zs = 1.25, ox = 760, oz = 215;   // exaggerate z by zs for legibility
    const X = x => ox + x * sc, Z = z => oz - z * sc * zs;
    const svg = s('svg', { viewBox: `0 0 ${W} ${Hh}`, width: '100%', style: 'min-width:640px', role: 'img', 'aria-label': 'Plan view free-body diagram (x-z)' });
    const ink = 'var(--ink)', mut = 'var(--muted)', ap = 'var(--fail)', re = 'var(--accent)';
    s('rect', { x: X(-1300), y: Z(g.W / 2), width: 1350 * sc, height: g.W * sc * zs, fill: 'var(--accent-wash)', stroke: ink }, svg);
    s('rect', { x: X(-g.a), y: Z(g.z_d + d.plate.t / 2), width: g.a * sc, height: d.plate.t * sc * zs, fill: 'var(--rule)', stroke: ink }, svg);
    s('rect', { x: X(-g.a), y: Z(-g.z_d + d.plate.t / 2), width: g.a * sc, height: d.plate.t * sc * zs, fill: 'var(--rule)', stroke: ink }, svg);
    s('rect', { x: X(-25), y: Z(g.z_br + PROB.t_br / 2), width: 120 * sc, height: PROB.t_br * sc * zs, fill: 'none', stroke: mut }, svg);
    s('rect', { x: X(-25), y: Z(-g.z_br + PROB.t_br / 2), width: 120 * sc, height: PROB.t_br * sc * zs, fill: 'none', stroke: mut }, svg);
    s('circle', { cx: X(-1200), cy: Z(0), r: PW.R1 * sc, fill: 'none', stroke: mut }, svg);
    s('circle', { cx: X(PROB.x_gen), cy: Z(0), r: PW.R2 * sc, fill: 'none', stroke: mut }, svg);
    const ch = ev.AL.chain;
    s('line', { x1: X(ch.P1[0]), y1: Z(ch.P1[2]) , x2: X(ch.P2[0]), y2: Z(ch.P2[2]), stroke: ap, 'stroke-width': 1.5, 'stroke-dasharray': '6 3' }, svg);
    s('text', { x: X(-1150), y: Z(-g.W / 2) + 34, 'font-size': 10.5, class: 't-ink' }, svg, `tight chain span ${f1(PW.T_chain)} N on the −z side (internal)`);
    s('text', { x: X(-1295), y: Z(g.W / 2) - 6, 'font-size': 10.5, class: 't-muted' }, svg, 'front (+z)');
    s('text', { x: X(-1295), y: Z(-g.W / 2) + 14, 'font-size': 10.5, class: 't-muted' }, svg, 'rear (−z)');
    arrow(svg, X(-1200), Z(0), X(-1200), Z(0) - 70, ap, `Drag ${PROB.drag} N (+z) at COP, ${f0(-g.y_cop)} mm below axis`, X(-1200) + 8, Z(0) - 74);
    const sx = 0.026;
    const pa = (x, z, Fx, lab, below) => arrow(svg, X(x), Z(z), X(x) + Fx * sx, Z(z), re, lab, X(x) + Fx * sx + (Fx > 0 ? 4 : -4), Z(z) + (below ? 16 : -6), Fx > 0 ? 'start' : 'end');
    pa(-g.a, g.z_d, R.F_f * g.u[0], `front plate x: ${f0(R.F_f * g.u[0])} N`);
    pa(-g.a, -g.z_d, R.F_r * g.u[0], `rear plate x: ${f0(R.F_r * g.u[0])} N`, true);
    pa(0, g.z_br, R.Ox_f, `O front x: ${f0(R.Ox_f)} N`);
    pa(0, -g.z_br, R.Ox_r, `O rear x: ${f0(R.Ox_r)} N`, true);
    arrow(svg, X(40), Z(g.W / 2) - 70, X(40), Z(g.W / 2) - 4, re, `Oz ${f0(R.Oz)} N (front bracket face)`, X(44), Z(g.W / 2) - 74);
    for (const [x, lab] of [[0, 'O'], [-g.a, 'A']]) { s('line', { x1: X(x), x2: X(x), y1: Z(g.z_br + 14), y2: Z(-g.z_br - 14), stroke: ink, 'stroke-width': 2.5 }, svg); s('text', { x: X(x) - 4, y: Z(-g.z_br - 14) + 14, 'font-size': 13, 'font-weight': 600, 'text-anchor': 'end', class: 't-ink' }, svg, lab); }
    s('text', { x: 16, y: 22, 'font-size': 12, class: 't-ink', 'font-weight': 600 }, svg, 'Plan view looking up from below (x right, z up, as Figure 2 bottom view); z scale ×1.25');
    s('text', { x: 16, y: 40, 'font-size': 11, class: 't-muted' }, svg, 'The drag (+z) is reacted by the bracket face at O; its moment about y by the O bracket couple and the plate couple.');
    return svg;
  }
  function fbdEnd(ev) {
    const g = ev.g, R = ev.R, d = ev.design;
    const W = 420, Hh = 520, sc = 0.62, oz = 210, oy = 150;
    const Zx = z => oz + z * sc * 1.0, Y = y => oy - y * sc;    // view from -x (front view): +z to the right
    const svg = s('svg', { viewBox: `0 0 ${W} ${Hh}`, width: '100%', style: 'min-width:300px', role: 'img', 'aria-label': 'End view at A: torsion couple' });
    const ink = 'var(--ink)', mut = 'var(--muted)', ap = 'var(--fail)', re = 'var(--accent)';
    s('rect', { x: Zx(-g.W / 2), y: Y(g.H / 2), width: g.W * sc, height: g.H * sc, fill: 'var(--accent-wash)', stroke: ink }, svg);
    for (const sg of [1, -1]) s('rect', { x: Zx(sg * g.z_d - d.plate.t / 2), y: Y(110), width: d.plate.t * sc, height: 220 * sc, fill: 'var(--rule)', stroke: ink }, svg);
    s('line', { x1: Zx(0), x2: Zx(0), y1: Y(-g.H / 2), y2: Y(g.y_cop), stroke: mut, 'stroke-width': 3 }, svg);
    arrow(svg, Zx(0), Y(g.y_cop), Zx(0) + 80, Y(g.y_cop), ap, `${PROB.drag} N (+z)`, Zx(0) + 84, Y(g.y_cop) + 4);
    s('text', { x: Zx(0) - 8, y: Y(g.y_cop) + 4, 'text-anchor': 'end', 'font-size': 10, class: 't-muted' }, svg, 'COP');
    const sy = 0.02;
    arrow(svg, Zx(g.z_d), Y(0), Zx(g.z_d), Y(0) - R.F_f * g.u[1] * sy, re, `${f0(R.F_f * g.u[1])} N`, Zx(g.z_d) + 6, Y(0) - R.F_f * g.u[1] * sy);
    arrow(svg, Zx(-g.z_d), Y(0), Zx(-g.z_d), Y(0) - R.F_r * g.u[1] * sy, re, `${f0(R.F_r * g.u[1])} N`, Zx(-g.z_d) - 6, Y(0) - R.F_r * g.u[1] * sy, 'end');
    s('text', { x: 14, y: 20, 'font-size': 12, class: 't-ink', 'font-weight': 600 }, svg, 'End view at A, looking along +x');
    s('text', { x: 14, y: 38, 'font-size': 10.5, class: 't-muted' }, svg, `Torque ${nm(Math.abs(R.Mx_plates))} N·m about x = plate y-forces`);
    s('text', { x: 14, y: 53, 'font-size': 10.5, class: 't-muted' }, svg, `× 2 z_d = ${f1(2 * g.z_d)} mm (front: rear on the left)`);
    return svg;
  }

  // ------------------------------------------------------------------ Part A
  function renderA() {
    const el = $('#partA'); el.textContent = ''; const ev = S.ev; if (!ev) return;
    el.append(head('Sheet A', 'Power and external loads', '2 points'));
    const g = ev.g, ch = ev.AL.chain;
    el.append(h('h3', { text: 'A.1 Power' }));
    el.append(eq([
      `A_swept = 0.500 m × 0.500 m = 0.250 m²          ρ_water = 1000 kg/m³ (fresh water)`,
      `P_fluid = ½ ρ A V³ = 0.5 × 1000 × 0.250 × 2.5³  = ${f1(PW.P_fluid)} W     (power carried by the flow through the rotor area)`,
      `P_mech  = η_h P_fluid = 0.30 × ${f1(PW.P_fluid)}         = ${f1(PW.P_mech)} W      (delivered to the rotor shaft)`,
      `P_elec  = η_e P_mech  = 0.82 × ${f1(PW.P_mech)}          = ${f1(PW.P_elec)} W      (delivered by the generator)`,
      ``,
      `ω = 285 × 2π/60 = ${f3(PW.omega)} rad/s          T_rotor = P_mech/ω = ${f2(PW.T_rotor / 1000)} N·m   (water torque on the rotor, +y)`,
      `r_1 = 9.554/2 in = ${f2(PW.R1)} mm   r_2 = 3.038/2 in = ${f2(PW.R2)} mm   (60T and 19T #40 sprockets: p/sin(180°/N) with p = ½ in)`,
      `Chain tension (tight span) F = T_rotor / r_1 = ${f1(PW.T_chain)} N; slack span 0 N (no preload, req 7)`,
      `Generator speed = 285 × 60/19 = ${f0(PW.rpm_gen)} rpm (req 4: "about 900")   chain speed ${f2(PW.v_chain)} m/s`,
      `Centre distance 39.49 in = ${f1(39.49 * IN)} mm → x_gen = −1200 + ${f1(39.49 * IN)} = ${f2(PROB.x_gen)} mm;  L = 2C/p + (N1+N2)/2 + ((N1−N2)/2π)²/(C/p) = ${f2(PW.links)} links → 198`,
      `Tangent skew φ = asin((r_1 − r_2)/C) = ${f2(ch.phi * 180 / Math.PI)}°   → chain force direction (cos φ, 0, sin φ) on the rotor sprocket`,
    ]));
    el.append(h('p', { class: 'note', text: 'Which span is tight: the rotor turns +y (counter-clockwise seen from the top). On its −z side the sprocket rim moves toward −x, pulling the chain from the generator toward the rotor, so the −z (rear) span is tight and the slack +z span carries nothing.' }));
    el.append(h('h3', { text: 'A.2 Free-body diagram of the support beam' }));
    el.append(h('figure', null, h('div', { class: 'fig' }, fbdSide(ev)), h('figcaption', { text: 'System = beam + shaft box + rotor + generator. The chain forces are internal (equal and opposite on one line) but they compress the beam between the sprockets, so they appear in the internal-load diagrams.' })));
    el.append(h('figure', null, h('div', { class: 'fig' }, fbdPlan(ev))));
    el.append(h('div', { class: 'grid2', style: 'grid-template-columns:minmax(0,1fr) minmax(0,1.6fr);align-items:start' }, h('figure', null, h('div', { class: 'fig' }, fbdEnd(ev))),
      h('div', { class: 'stack' }, h('h4', { text: 'Why the plates carry torsion' }), h('p', { class: 'note', text: `The drag acts ${f0(-ev.g.y_cop)} mm below the beam axis, so it twists the beam about x by 560 N × ${f3(-ev.g.y_cop / 1000)} m = ${nm(Math.abs(ev.R.SM[0]))} N·m. Requirement 10 sends all of it to the diagonals: the front and rear plates push and pull with different forces, and the difference of their vertical components times their spacing (2 z_d = ${f1(2 * ev.g.z_d)} mm) balances the torque. That is why one plate is in compression even though the weights alone would put both in tension, and why a wider beam (larger z_d) lowers the plate forces.` }))));
    el.append(h('h3', { text: 'A.3 Load table (Figure 2 frame, origin at pin O on the neutral axis)' }));
    const rows = ev.AL.loads.filter(L => L.key !== 'Ch1' && L.key !== 'Ch2').map(L => [L.name, vec(L.r, 1), vec(L.F, 1), vec(L.C.map(v => v / 1000), 2)]);
    rows.push(['Beam self-weight (resultant of the uniform load)', vec([(g.x_left + g.x_right) / 2, 0, 0], 1), vec([0, -ev.AL.Wb, 0], 1), '(0.00, 0.00, 0.00)']);
    rows.push(['Chain on rotor sprocket (internal)', vec(ch.P1, 1), vec(ch.F1, 1), '(0.00, 0.00, 0.00)']);
    rows.push(['Chain on generator sprocket (internal)', vec(ch.P2, 1), vec(ch.F2, 1), '(0.00, 0.00, 0.00)']);
    el.append(table([{ t: 'Load' }, { t: 'Point r (mm)' }, { t: 'Force F (N)' }, { t: 'Couple M (N·m)' }], rows));
    el.append(eq([
      `Resultant of applied loads:          ΣF = ${vec(ev.R.SF, 1)} N`,
      `Moment of applied loads about O:     ΣM = ${vec(ev.R.SM.map(v => v / 1000), 2)} N·m`,
      `  Mx ≈ −560 N × (h/2 + 500 mm) − weights × 0 → torsion the plates must carry`,
      `  My ≈ 560 N × 1.200 m + T_rotor = ${f1(PROB.drag * 1.2 + PW.T_rotor / 1000)} N·m → shared by the O bracket couple and the plate couple`,
      `  Mz ≈ +(150 × 1.200 + 120 × ${f3(-PROB.x_gen / 1000)} + W_beam × 0.625 + …) N·m (weights hang at negative x) → carried by the plates`,
    ]));
  }

  // ------------------------------------------------------------------ Part B
  function renderB() {
    const el = $('#partB'); el.textContent = ''; const ev = S.ev; if (!ev) return;
    const g = ev.g, R = ev.R, d = ev.design, dv = ev.dv, J = ev.joints;
    el.append(head('Sheet B', 'Reactions and pins', '2 points'));
    el.append(h('h3', { text: 'B.1 Six equilibrium equations, six unknowns' }));
    const s_ = g.u[1], c_ = g.u[0];
    el.append(eq([
      `Unknowns: O_x,front, O_x,rear, O_y (split equally, req 10), O_z (front bracket face), F_front, F_rear (plate axial, + = tension)`,
      `Plate direction u = (B − A)/|B − A| = (${f0(g.a)}, 500, 0)/${f1(g.Lpp)} = (${f3(c_)}, ${f3(s_)}, 0);  z_d = ±${f2(g.z_d)} mm, z_br = ±${f2(g.z_br)} mm`,
      ``,
      `ΣM_x:  −z_d s (F_f − F_r) + ΣM_x,app = 0   →  F_f − F_r = ΣM_x/(z_d s) = ${f0(R.F_f - R.F_r)} N`,
      `ΣM_z:  −a s (F_f + F_r) + ΣM_z,app = 0     →  F_f + F_r = ΣM_z/(a s)   = ${f0(R.F_f + R.F_r)} N`,
      `ΣM_y:  z_br (O_xf − O_xr) + z_d c (F_f − F_r) + ΣM_y,app = 0  →  O_xf − O_xr = ${f0(R.Ox_f - R.Ox_r)} N`,
      `ΣF_x:  O_xf + O_xr + c (F_f + F_r) + ΣF_x,app = 0               →  O_xf + O_xr = ${f0(R.Ox_f + R.Ox_r)} N`,
      `ΣF_y:  O_y + s (F_f + F_r) + ΣF_y,app = 0                       →  O_y = ${f0(R.Oy)} N (${f0(R.Oy / 2)} N per bracket)`,
      `ΣF_z:  O_z + 560 = 0                                            →  O_z = ${f0(R.Oz)} N`,
      ``,
      `F_front = ${f0(R.F_f)} N (${R.F_f < 0 ? 'compression' : 'tension'}),  F_rear = ${f0(R.F_r)} N (${R.F_r < 0 ? 'compression' : 'tension'})`,
      `Moment about y at O: bracket couple ${nm(R.My_bracket)} N·m, plate couple ${nm(R.My_plates)} N·m (plate couple = cot θ × torsion)`,
      `Equilibrium residual of the solved system: ${R.residual.toExponential(1)} (N, N·m)`,
    ]));
    el.append(h('h3', { text: 'B.2 Loads at each side of each pin' }));
    el.append(h('p', { class: 'note small', text: 'Forces that the outer members (brackets at O, plates at A and B) put on the pin, and the forces the pin then puts on the inner members (beam walls at A and O, brackets at B). The inner forces come from the pin’s own equilibrium: the front/rear difference is a couple, and the inner members sit closer to the centre, so they carry larger forces.' }));
    const P = J.P, row = (loc, side, Fo, Fi, extraZ) => [loc, side, f0(Fo[0]), f0(Fo[1]), f0(extraZ || 0), f0(Math.hypot(Fo[0], Fo[1])), f0(Math.hypot(Fi[0], Fi[1]))];
    const rows = [
      row('O (bracket ↔ beam)', 'Front (+z)', [R.Ox_f, R.Oy / 2], J.O.Pi_f, R.Oz), row('O (bracket ↔ beam)', 'Rear (−z)', [R.Ox_r, R.Oy / 2], J.O.Pi_r, 0),
      row('A (plate ↔ beam)', 'Front (+z)', P.Pf_A, J.A.Pi_f), row('A (plate ↔ beam)', 'Rear (−z)', P.Pr_A, J.A.Pi_r),
      row('B (plate ↔ bracket)', 'Front (+z)', P.Pf_B, J.B.Pi_f), row('B (plate ↔ bracket)', 'Rear (−z)', P.Pr_B, J.B.Pi_r),
    ];
    el.append(table([{ t: 'Pin' }, { t: 'Side' }, { t: 'Fx on beam / B-bracket (N)', num: true }, { t: 'Fy (N)', num: true }, { t: 'Fz face contact (N)', num: true }, { t: '|F| outer member (N)', num: true }, { t: '|F| inner member (N)', num: true }], rows));
    el.append(h('p', { class: 'note small', text: 'Sign: forces on the beam at O and A, and on the fixed bracket at B. The z force at O is carried by the beam wall bearing on the front bracket face, not by the pin; the hairpin or ball detents carry no load.' }));
    // pin selection
    el.append(h('h3', { text: 'B.3 Pin selection' }));
    const pin = d.pin;
    el.append(h('dl', { class: 'kv' },
      h('dt', { text: 'Part' }), h('dd', { text: `${pin.pn} — ${pin.family}` }),
      h('dt', { text: 'Size' }), h('dd', { text: `${frac(pin.d_in)} in dia (tol ${pin.tolMinus_in >= 0 ? '+' : ''}${f(pin.tolMinus_in, 3)} / +${f(pin.tolPlus_in, 3)} in), usable length ${pin.usable_in} in` }),
      h('dt', { text: 'Material basis' }), h('dd', { text: `${pin.material}${pin.hardness ? ' (' + pin.hardness + ')' : ''}: design S_y = ${f0(pin.mat.Sy)} MPa, S_u = ${f0(pin.mat.Su)} MPa — ${pin.mat.note}${pin.shearNote ? '; McMaster prints ' + pin.shearNote : ''}` }),
      h('dt', { text: 'Retention' }), h('dd', { text: pin.retention }),
      h('dt', { text: 'Grip and washers' }), h('dd', { text: `O: ${inch(dv.grips.O)} in (beam ${inch(g.W)} in + two ½ in brackets + ${S.opts.float} mm clearance each side); A and B: ${inch(dv.grips.A)} in. Usable ${pin.usable_in} in, so ${dv.wash.perJoint} washer${dv.wash.perJoint === 1 ? '' : 's'} go under the pin head at A and at B${dv.wash.washer ? ' (' + dv.wash.washer.pn + ')' : ''}; worst-case leftover axial play ${f2(dv.playAB)} mm, used as the gap in the A/B pin-bending check. None are needed at O, where the brackets are fixed.` }),
      h('dt', { text: 'Price' }), h('dd', { text: `${money(pin.price)}${pin.pkg > 1 ? ' per pack of ' + pin.pkg : ' each'} → ${money(ev.cost.pinCost)} for 3` })));
    el.append(h('p', { class: 'note', text: 'Each pin is a short beam loaded by bearing in every member it passes through (uniform bearing through each thickness, AFFDL-TR-69-42 §9.4). Between the beam walls (or the B brackets) the pin is unsupported, so it bends; the moment peaks inside the inner member where the shear changes sign.' }));
    const prof = k => J[k].prof ? J[k].prof.map(p => [p.z, p.M / 1000]) : [];
    el.append(h('div', { class: 'grid2' },
      lineChart({ title: 'Pin bending moment |M| along the pin (N·m)', unit: 'N·m', xName: 'z', xUnit: ' mm', legend: true, xLabel: 'z (mm), front at right', series: [{ name: 'pin O', color: 'var(--s1)', pts: prof('O') }, { name: 'pin A', color: 'var(--s2)', pts: prof('A') }, { name: 'pin B', color: 'var(--s3)', pts: prof('B') }], width: 460, height: 210 }),
      h('div', { class: 'stack' }, eq([
        `d = ${f2(dv.d)} mm   A = π(d² − d_b²)/4 = ${f1(dv.Apin)} mm²   Z = π(d⁴ − d_b⁴)/(32 d) = ${f1(dv.Zpin)} mm³${dv.db ? `   (bore d_b = ${f1(dv.db)} mm)` : ''}`,
        `Max |M|: O ${nm2(J.O.Mmax)}, A ${nm2(J.A.Mmax)}, B ${nm2(J.B.Mmax)} N·m`,
        `σ_b = M/Z = ${f1(Math.max(J.O.Mmax, J.A.Mmax, J.B.Mmax) / dv.Zpin)} MPa  vs S_y = ${f0(pin.mat.Sy)} MPa`,
        `Max |V| = ${f0(Math.max(J.O.Vmax, J.A.Vmax, J.B.Vmax))} N   τ_max = k V/A = ${f1(dv.kShear * Math.max(J.O.Vmax, J.A.Vmax, J.B.Vmax) / dv.Apin)} MPa  vs 0.577 S_y = ${f0(0.577 * pin.mat.Sy)} MPa`,
      ]))));
    const pinChecks = ev.checks.filter(k => /Pins|Bracket|bearing|tear-out/i.test(k.group + k.name));
    el.append(checkTable(pinChecks));
    // hole
    el.append(h('h3', { text: 'B.4 Hole diameter and tolerance' }));
    const hl = dv.hole;
    el.append(eq([
      `Pin diameter (McMaster tolerance): ${f(hl.dmin_in, 4)} to ${f(hl.dmax_in, 4)} in`,
      `Holes (8 in our parts: both beam walls at A and at O, both plates at both ends; use the same callout for the 4 bracket holes): Ø${f(hl.lo_in, 4)} / ${f(hl.hi_in, 4)} in  (${f(hl.lo_in * IN, 3)}–${f(hl.hi_in * IN, 3)} mm)`,
      `  minimum hole = largest pin + ${f(hl.cmin_in, 4)} in (about the ANSI B4.1 RC7 minimum clearance for this size)`,
      `  hole tolerance = H8 = +${f(hl.H8_in, 4)} in   → clearance ${f(hl.cmin_in, 4)} to ${f(hl.cmax_in, 4)} in: always positive, so the pin slides in by hand`,
      `Make: drill ${drill64(hl.lo_in)} in (${f(Math.floor((hl.lo_in - 0.010) * 64) / 64, 4)} in, leaves ≈${f(hl.lo_in - Math.floor((hl.lo_in - 0.010) * 64) / 64, 3)} in for the reamer), then machine-ream to Ø${f(hl.lo_in, 4)} +${f(hl.H8_in, 4)}/−0 in.`,
      `Drawing callout: "Ø${f(hl.lo_in, 4)}–${f(hl.hi_in, 4)} THRU, REAM". Sources: ANSI B4.1-1967 (R1987) Table 1 (RC clearance classes), ISO 286-2 grade IT8 (H8); pin diameter tolerance from the McMaster part page.`,
    ]));
    if (ev.slop) el.append(h('div', { class: 'callout' }, h('b', { text: 'Hole clearance is play, not deflection. ' }), `With no flow both plates hang in slight tension; when the flow starts the front plate goes into compression and the rear O bracket force reverses, so the pins cross their hole clearances once. Over all joints that seats the rotor CG about ${f1(ev.slop.atMin.z)}–${f1(ev.slop.atMax.z)} mm from its no-flow position (minimum to maximum clearance). It happens once, at start-up, and is not elastic deflection, so it is reported here and not added to requirement 12; every hand-removable clearance-fit pin joint has it (about 0.6 mm at the CG per 0.001 in of clearance). Reduce it by line-reaming each plate with its mating holes and assembling with the beam pushed against the front (+z, drag-side) O bracket.`));
    el.append(h('div', { class: 'callout info' }, h('b', { text: 'Interface with the fixed structure. ' }), `O brackets: inner faces ${inch(g.W + 2 * S.opts.float, 3)} in apart (beam ${inch(g.W, 3)} in + clearance), holes on the beam neutral axis. B brackets: outer faces ${inch(g.W, 3)} in apart so the plates stay flat in their planes. Same reamed hole callout in the brackets. The plate end at B reaches x ≈ ${f0(dv.e_end * Math.cos(g.theta) + d.plate.b / 2 * Math.sin(g.theta))} mm; if the structure face is closer than that, chamfer that corner (any chamfer that keeps ≥ ${f1(dv.e_req)} mm from the hole centre).`));
  }
  function checkTable(list) {
    return table([{ t: 'Check' }, { t: 'Demand', num: true }, { t: 'Capacity', num: true }, { t: 'FS', num: true }, { t: 'Detail' }, { t: '' }],
      list.map(k => [k.name, `${f(k.demand, k.unit === 'N' ? 0 : 1)} ${k.unit}`, `${f(k.capacity, k.unit === 'N' ? 0 : 1)} ${k.unit}`, k.fs == null ? '—' : f2(k.fs), k.detail || '', chip(k.ok)]));
  }

  // ------------------------------------------------------------------ Part C
  function renderC() {
    const el = $('#partC'); el.textContent = ''; const ev = S.ev; if (!ev) return;
    const d = ev.design, sec = d.beam.sec, g = ev.g, c = ev.cost;
    el.append(head('Sheet C', 'Support beam: strength', '2 points'));
    el.append(h('h3', { text: 'C.1 Stock' }));
    el.append(h('dl', { class: 'kv' },
      h('dt', { text: 'McMaster part' }), h('dd', { text: `${c.beam.pn} (${d.beam.item.family})` }),
      h('dt', { text: 'Section' }), h('dd', { text: `${beamDesc(d.beam.item)}, installed ${d.beam.orient}` }),
      h('dt', { text: 'Length' }), h('dd', { text: `needs 1350 mm = ${f2(c.beamNeedIn)} in (x = −1300 to +50) → shortest stock ${c.beam.label || f1(c.beam.length_in) + ' in'} at ${money(c.beam.price)}` }),
      h('dt', { text: 'Material' }), h('dd', { text: `${d.beam.mat.name}; S_y = ${f0(d.beam.Sy)} MPa (${d.beam.item.yieldNote || 'McMaster printed value'}); E = ${f0(d.beam.mat.E / 1000)} GPa, G = ${f1(d.beam.mat.G / 1000)} GPa` }),
      h('dt', { text: 'Why it qualifies (req 3)' }), h('dd', { text: 'one piece; flat top, front and rear faces; top square to the sides; corrosion-resistant alloy' })));
    el.append(eq([
      `Section (${sec.kind === 'tube' ? `rounded corners r_o = ${f2(sec.ro)} mm, r_i = ${f2(sec.ri)} mm` : 'solid'}):`,
      `A = ${f0(sec.A)} mm²   I_z (vertical bending) = ${f(sec.Iz / 1e6, 3)}×10⁶ mm⁴   I_y (lateral bending) = ${f(sec.Iy / 1e6, 3)}×10⁶ mm⁴`,
      sec.kind === 'tube' ? `Torsion (Bredt–Batho, thin closed section): A_m = (b−t)(h−t) − (4−π) r_m² = ${f0(sec.Am)} mm², p_m = ${f1(sec.pm)} mm,` : `Torsion (Saint-Venant, Roark Table 10.1 case 4): J = b c³[1/3 − 0.21(c/b)(1 − c⁴/12b⁴)]`,
      sec.kind === 'tube' ? `   J = 4 A_m² t / p_m = ${f(sec.J / 1e6, 3)}×10⁶ mm⁴,  τ = T/(2 A_m t) = T × ${f(sec.tauPerT * 1e6, 3)}×10⁻⁶ /mm³` : `   J = ${f(sec.J / 1e6, 3)}×10⁶ mm⁴,  τ_max = T (3b + 1.8c)/(b² c²)`,
      `Self-weight q = ρ g A = ${f(ev.AL.q * 1000, 1)} N/m → ${f1(ev.AL.Wb)} N over 1350 mm;  shear coefficients (Cowper) κ_y = ${f3(sec.kapY)}, κ_z = ${f3(sec.kapZ)}`,
    ]));
    el.append(h('h3', { text: 'C.2 Internal loads along the beam (section cuts, right part acting on left part)' }));
    const dg = D.diagrams(ev, 500);
    const marks = [{ x: PROB.x_rot, label: 'rotor' }, { x: PROB.x_gen, label: 'gen' }, { x: -g.a, label: 'A' }, { x: 0, label: 'O' }];
    const mk = (key, title, unit, scale, color) => lineChart({ title: `${title} (${unit})`, unit, xName: 'x', xUnit: ' mm', series: [{ name: title, color, fill: true, pts: dg.map(p => [p.x, p[key] * scale]) }], marks, width: 400, height: 170, xmin: -1300, xmax: 50, yFmt: v => f(v, 0) });
    el.append(h('div', { class: 'grid3' },
      mk('N', 'Axial force N', 'N', 1, 'var(--s1)'), mk('Vy', 'Shear V_y', 'N', 1, 'var(--s1)'), mk('Vz', 'Shear V_z', 'N', 1, 'var(--s1)'),
      mk('Tx', 'Torque T_x', 'N·m', 1e-3, 'var(--s2)'), mk('My', 'Bending M_y (lateral)', 'N·m', 1e-3, 'var(--s2)'), mk('Mz', 'Bending M_z (vertical)', 'N·m', 1e-3, 'var(--s2)')));
    const pk = ev.peaks, where = x => Math.abs(x - PROB.x_rot) < 1 ? 'at the rotor (x = −1200)' : Math.abs(x + g.a) < 1 ? `at A (x = −${g.a})` : Math.abs(x - PROB.x_gen) < 1 ? 'at the generator' : Math.abs(x) < 1 ? 'at O' : `x = ${f0(x)} mm`;
    el.append(table([{ t: 'Quantity' }, { t: 'Peak', num: true }, { t: 'Where' }, { t: 'What causes it' }], [
      ['Axial force N', `${f0(pk.N.v)} N`, where(pk.N.x), 'chain compression between the sprockets plus the x-components of the plate forces between A and O'],
      ['Bending moment M_y (lateral, about y)', `${nm(pk.My.v)} N·m`, where(pk.My.x), 'drag 560 N × lever arm, reduced to the right of A by the plate couple'],
      ['Bending moment M_z (vertical, about z)', `${nm(pk.Mz.v)} N·m`, where(pk.Mz.x), 'weights hanging off the cantilever from A to the rotor'],
      ['Torque T_x (about x)', `${nm(pk.Tx.v)} N·m`, 'between the rotor and A (zero from A to O)', 'drag 560 N acting (h/2 + 500) mm below the axis; carried only by the plates (req 10)'],
      ['Shear V_y / V_z', `${f0(pk.Vy.v)} / ${f0(pk.Vz.v)} N`, `${where(pk.Vy.x)} / ${where(pk.Vz.x)}`, 'jumps at the load points'],
    ]));
    el.append(h('h3', { text: 'C.3 Stresses (worst corner + peak shear, both combined: conservative)' }));
    const bs = ev.beamStress;
    const pick = []; const want = [[PROB.x_rot, '+', 'just right of the rotor'], [-g.a, '-', 'just left of A (net section)'], [-g.a, '+', 'just right of A'], [PROB.x_gen, '-', 'at the generator'], [0, '-', 'at O (net section)']];
    for (const [x, sd, lab] of want) { const p = bs.pts.find(q => Math.abs(q.x - x) < 1e-6 && (q.side === sd || (sd === '-' && q.side === '-') )) || bs.pts.reduce((a, b) => Math.abs(b.x - x) < Math.abs(a.x - x) ? b : a); pick.push([lab, p]); }
    pick.push(['worst section found', bs.worst]);
    el.append(table([{ t: 'Section' }, { t: 'N/A', num: true }, { t: 'M_z c/I_z', num: true }, { t: 'M_y c/I_y', num: true }, { t: 'τ torsion', num: true }, { t: 'τ shear', num: true }, { t: 'σ_vm (MPa)', num: true }, { t: 'FS', num: true }],
      pick.map(([lab, p]) => [`${lab} (x = ${f0(p.x)})`, f2(p.sigN), f2(p.sigMz), f2(p.sigMy), f2(p.tauT), f2(p.tauV), f2(p.vm), f1(p.fs)])));
    el.append(eq([
      `σ = |N|/A + |M_z|(h/2)/I_z + |M_y|(w/2)/I_y      (all three at the same corner: worst case)`,
      `τ = |T| / (2 A_m t)  [Bredt–Batho]  + |V| Q/(I b)   σ_vm = √(σ² + 3τ²) ≤ S_y/2 = ${f1(d.beam.Sy / 2)} MPa`,
      `At the pin holes the net section is used (the hole removes wall at the neutral axis and the extreme fibres for M_y).`,
    ]));
    el.append(checkTable(ev.checks.filter(k => k.group === 'Beam')));
  }

  // ------------------------------------------------------------------ Part D
  function renderD() {
    const el = $('#partD'); el.textContent = ''; const ev = S.ev; if (!ev) return;
    const d = ev.design, pl = d.plate, g = ev.g, R = ev.R, dv = ev.dv, c = ev.cost, bk = ev.buckling;
    el.append(head('Sheet D', 'Diagonal plates and deflection', '2 points'));
    el.append(h('h3', { text: 'D.1 Stock and cutting' }));
    el.append(h('dl', { class: 'kv' },
      h('dt', { text: 'McMaster part' }), h('dd', { text: `${c.plate.pn} (${pl.item.family})` }),
      h('dt', { text: 'Stock' }), h('dd', { text: `${plateDesc(pl)}; S_y = ${f0(pl.Sy)} MPa; buy ${c.plate.label || f1(c.plate.length_in) + ' in'} at ${money(c.plate.price)}` }),
      h('dt', { text: 'Each plate' }), h('dd', { text: `${inch(pl.b, 3)} in wide × ${frac(pl.item.t_in)} in thick × ${inch(dv.Lcut, 2)} in long (${f1(dv.Lcut)} mm); holes ${f1(g.Lpp)} mm apart, ${dv.e_end} mm from each end` }),
      h('dt', { text: 'Two from one piece' }), h('dd', { text: `${c.plateHow}: needs ${f2(c.plateNeedIn)} in ≤ ${f2(c.plate.length_in)} in available` })));
    el.append(h('h3', { text: 'D.2 Loads in each plate' }));
    const qn = pl.mat.rho * D.GRAV * pl.b * pl.t * Math.cos(g.theta), Msw = qn * g.Lpp ** 2 / 8;
    el.append(table([{ t: 'Plate' }, { t: 'Peak axial (N)', num: true }, { t: 'In-plane bending (N·m)', num: true }, { t: 'Out-of-plane bending', num: true }, { t: 'Torque', num: true }, { t: 'Where' }], [
      ['Front (+z)', `${f0(R.F_f)} (${R.F_f < 0 ? 'C' : 'T'})`, f2(Msw / 1000), '0', '0', 'axial uniform between pins; self-weight bending at mid-length'],
      ['Rear (−z)', `${f0(R.F_r)} (${R.F_r < 0 ? 'C' : 'T'})`, f2(Msw / 1000), '0', '0', 'same'],
    ]));
    el.append(h('p', { class: 'note small', text: 'Each plate is a two-force member: pins carry no moment, and the flat plate carries no z force (O takes the drag). The only bending is its own weight across the span, w L² cos θ / 8. With no flow the front plate is in slight tension; when the flow starts it goes into compression, so buckling governs its thickness.' }));
    el.append(eq([
      `Compression plate: P = ${f0(-bk.Fc)} N, L = ${f1(g.Lpp)} mm pin to pin, K = 1 (pins give no reliable rotational fixity)`,
      `Out of plane: I = b t³/12 = ${f0(pl.b * pl.t ** 3 / 12)} mm⁴, L/k = ${f0(bk.weak.sr)} (${bk.weak.mode}; transition ${f0(bk.weak.sr1)})  P_cr = ${f0(bk.weak.P)} N → FS = ${f2(bk.weak.P / -bk.Fc)}`,
      `In plane:     I = t b³/12 = ${f0(pl.t * pl.b ** 3 / 12)} mm⁴, P_cr = ${f0(bk.strong.P)} N → FS = ${f2(bk.strong.P / -bk.Fc)}`,
      `Imperfect column at 2P with crookedness L/1000: σ = ${f1(ev.checks.find(k => /crookedness/.test(k.name)) ? ev.checks.find(k => /crookedness/.test(k.name)).demand : 0)} MPa ≤ S_y = ${f0(pl.Sy)} MPa`,
    ]));
    el.append(checkTable(ev.checks.filter(k => k.group === 'Diagonals')));
    el.append(h('h3', { text: 'D.3 Plate stretch' }));
    el.append(eq([
      `δ = F L / (E A):   front δ_f = ${f0(R.F_f)} × ${f1(g.Lpp)} / (${f0(pl.mat.E)} × ${f1(pl.b * pl.t)}) = ${f(ev.plateStretch.delta_f, 4)} mm`,
      `                   rear  δ_r = ${f0(R.F_r)} × ${f1(g.Lpp)} / (${f0(pl.mat.E)} × ${f1(pl.b * pl.t)}) = ${f(ev.plateStretch.delta_r, 4)} mm`,
      `Unequal stretch rolls the beam about x: θ_x = (δ_f − δ_r)/(2 z_d sin θ) = ${f(ev.defl.thx_pl * 1e3, 4)} mrad → ${f3(ev.defl.thx_pl * g.y_cg)} mm at the CG (lever ${f1(-g.y_cg)} mm)`,
      `Mean stretch pitches the beam about z: θ_z = (δ_f + δ_r)/(2 a sin θ) = ${f(ev.defl.thz_pl * 1e3, 4)} mrad`,
    ]));
    el.append(h('h3', { text: 'D.4 Rotor-CG deflection' }));
    el.append(h('p', { class: 'note', text: 'O fixes the three translations and the rotation about y (bracket couple); the two plates fix the rotations about x and z. The beam is integrated as an elastic beam from O, then given the rigid rotation that makes the plate ends move exactly by the plate stretches (compatibility). The CG hangs h/2 + 350 mm below the beam axis on the rigid shaft, so every rotation about x is multiplied by that lever.' }));
    el.append(eq([
      `θ_x = θ_y(A) cot θ + (δ_f − δ_r)/(2 z_d sin θ)        θ_z = [u(A) cos θ + v(A) sin θ + (δ_f + δ_r)/2] / (a sin θ)`,
      `u_CG = ( u(x_r) − (θ_z,el + θ_z) y_cg ,  v(x_r) + θ_z x_r ,  w(x_r) + (φ(x_r) − φ(A) + θ_x) y_cg ),  x_r = −1200, y_cg = ${f1(g.y_cg)} mm`,
    ]));
    const comps = ev.defl.comps;
    const items = comps.map(cc => ({ name: cc.name, v: cc.d[2] }));
    el.append(h('div', { class: 'grid2' }, waterfall(items, ev.defl.total[2]), table([{ t: 'Contribution' }, { t: 'dx', num: true }, { t: 'dy', num: true }, { t: 'dz (mm)', num: true }],
      comps.map(cc => [cc.name, f(cc.d[0], 4), f(cc.d[1], 4), f(cc.d[2], 4)]).concat([['Total (vector sum)', f(ev.defl.total[0], 4), f(ev.defl.total[1], 4), f(ev.defl.total[2], 4)], ['Magnitude |u|', '', '', f(ev.defl.mag, 4)]]))));
    el.append(h('p', { class: 'note' }, `|u_CG| = ${f3(ev.defl.mag)} mm ≤ 0.700 mm `, chip(ev.defl.mag <= 0.7), `  — the plate deflection is ${f0(Math.abs((comps.find(k => k.key === 'plate_diff').d[2]) / ev.defl.mag * 100))} % of the total; it does not compromise performance because the total stays within the limit with ${f0((1 - ev.defl.mag / 0.7) * 100)} % margin.`));
    // a-sweep
    el.append(h('h3', { text: 'D.5 Where to attach the diagonal (same parts, a swept)' }));
    const sw = [];
    for (let a = 300; a <= 800; a += 10) { const e2 = D.evaluate(Object.assign({}, d, { a }), S.opts); sw.push({ a, defl: e2.defl.mag, fs: e2.minFS, cost: e2.cost.ok ? e2.cost.total : null, ok: e2.ok }); }
    el.append(h('div', { class: 'grid3' },
      lineChart({ title: 'CG deflection vs a (mm)', unit: 'mm', xName: 'a', xUnit: ' mm', series: [{ name: 'deflection', color: 'var(--s1)', pts: sw.map(p => [p.a, p.defl]), dot: [[d.a, ev.defl.mag]] }], hlines: [{ y: 0.7, label: 'limit 0.7' }], width: 360, height: 180, yFmt: v => f(v, 2) }),
      lineChart({ title: 'Lowest factor of safety vs a', unit: '', xName: 'a', xUnit: ' mm', series: [{ name: 'min FS', color: 'var(--s3)', pts: sw.map(p => [p.a, Math.min(p.fs, 6)]), dot: [[d.a, Math.min(ev.minFS, 6)]] }], hlines: [{ y: 2, label: 'required 2.0' }], width: 360, height: 180, yFmt: v => f(v, 1), ymin: 0 }),
      lineChart({ title: 'Cost vs a (USD)', unit: 'USD', xName: 'a', xUnit: ' mm', series: [{ name: 'cost', color: 'var(--s2)', pts: sw.filter(p => p.cost != null).map(p => [p.a, p.cost]), dot: [[d.a, ev.cost.total]] }], width: 360, height: 180, yFmt: v => '$' + f(v, 0) })));
    const okA = sw.filter(p => p.ok).map(p => p.a);
    el.append(h('p', { class: 'note small', text: okA.length ? `With these parts every requirement is met for a = ${Math.min(...okA)}–${Math.max(...okA)} mm (where the plates still fit the stock). Moving A toward the rotor shortens the twisted length and the lateral cantilever, but lengthens the plates (more stretch, lower buckling load) and eventually needs longer stock.` : 'No value of a passes with these exact parts.' }));
  }
  function waterfall(items, total) {
    const W = 470, rowH = 26, m = { l: 210, r: 60, t: 10 }, Hh = m.t + (items.length + 1) * rowH + 24;
    let cum = 0; const pts = items.map(it => { const s0 = cum; cum += it.v; return { ...it, s0, s1: cum }; });
    const lo = Math.min(0, ...pts.map(p => Math.min(p.s0, p.s1))), hi = Math.max(0.7, ...pts.map(p => Math.max(p.s0, p.s1)));
    const X = v => m.l + (v - lo) / (hi - lo) * (W - m.l - m.r);
    const svg = s('svg', { viewBox: `0 0 ${W} ${Hh}`, width: '100%', role: 'img', 'aria-label': 'Waterfall of z-deflection contributions' });
    s('line', { x1: X(0), x2: X(0), y1: m.t, y2: Hh - 20, stroke: 'var(--muted)' }, svg);
    s('line', { x1: X(0.7), x2: X(0.7), y1: m.t, y2: Hh - 20, stroke: 'var(--fail)', 'stroke-dasharray': '3 3' }, svg);
    s('text', { x: X(0.7), y: Hh - 6, 'text-anchor': 'middle', 'font-size': 10, fill: 'var(--fail)' }, svg, '0.7 mm');
    pts.forEach((p, i) => {
      const y = m.t + i * rowH;
      s('text', { x: m.l - 8, y: y + 16, 'text-anchor': 'end', 'font-size': 10.5, class: 't-ink' }, svg, p.name.length > 34 ? p.name.slice(0, 33) + '…' : p.name);
      const x0 = X(Math.min(p.s0, p.s1)), w = Math.max(Math.abs(X(p.s1) - X(p.s0)), 1);
      s('rect', { x: x0, y: y + 5, width: w, height: 14, rx: 2, fill: p.v >= 0 ? 'var(--s1)' : 'var(--s3)' }, svg);
      s('text', { x: Math.max(X(p.s0), X(p.s1)) + 4, y: y + 16, 'font-size': 10, class: 't-mono t-muted' }, svg, (p.v >= 0 ? '+' : '') + f(p.v, 3));
    });
    const y = m.t + items.length * rowH;
    s('text', { x: m.l - 8, y: y + 16, 'text-anchor': 'end', 'font-size': 11, 'font-weight': 600, class: 't-ink' }, svg, 'Total z');
    s('rect', { x: X(Math.min(0, total)), y: y + 5, width: Math.abs(X(total) - X(0)), height: 14, rx: 2, fill: 'var(--ink-2)' }, svg);
    s('text', { x: X(Math.max(0, total)) + 4, y: y + 16, 'font-size': 10.5, class: 't-mono t-ink' }, svg, f(total, 3) + ' mm');
    return h('figure', null, h('div', { class: 'label', text: 'z-deflection contributions at the CG (mm, signed)' }), svg, h('figcaption', { text: 'Blue adds, green subtracts. The x and y parts are small; see the table.' }));
  }

  // ------------------------------------------------------------------ Part E
  function plateDrawing(ev) {
    const d = ev.design, dv = ev.dv, pl = d.plate, hl = dv.hole;
    const Lin = dv.Lcut / IN, bin = pl.b / IN, tin = pl.item.t_in, ein = dv.e_end / IN, cin = ev.g.Lpp / IN;
    const W = 1000, Hh = 600, ox = 60, oy = 120, sc = Math.min(25.5, (W - ox - 150) / Lin);   // px per inch, fitted to the sheet
    const svg = s('svg', { viewBox: `0 0 ${W} ${Hh}`, width: '100%', style: 'min-width:760px', role: 'img', 'aria-label': 'Fabrication drawing of the diagonal plate' });
    const ink = 'var(--ink)', mut = 'var(--muted)';
    s('rect', { x: 6, y: 6, width: W - 12, height: Hh - 12, fill: 'none', stroke: ink, 'stroke-width': 1.5 }, svg);
    const X = x => ox + x * sc, Y = y => oy + y * sc;
    s('rect', { x: X(0), y: Y(0), width: Lin * sc, height: bin * sc, fill: 'var(--accent-wash)', stroke: ink, 'stroke-width': 1.6 }, svg);
    for (const xh of [ein, ein + cin]) {
      s('circle', { cx: X(xh), cy: Y(bin / 2), r: hl.hi_in / 2 * sc, fill: 'var(--sheet)', stroke: ink, 'stroke-width': 1.4 }, svg);
      s('line', { x1: X(xh) - 14, x2: X(xh) + 14, y1: Y(bin / 2), y2: Y(bin / 2), stroke: mut, 'stroke-dasharray': '6 2 2 2' }, svg);
      s('line', { x1: X(xh), x2: X(xh), y1: Y(bin / 2) - 14, y2: Y(bin / 2) + 14, stroke: mut, 'stroke-dasharray': '6 2 2 2' }, svg);
    }
    s('line', { x1: X(-0.3), x2: X(Lin + 0.3), y1: Y(bin / 2), y2: Y(bin / 2), stroke: mut, 'stroke-dasharray': '14 3 3 3', opacity: 0.6 }, svg);
    const dimH = (x1, x2, y, text) => { s('line', { x1: X(x1), x2: X(x2), y1: y, y2: y, stroke: ink }, svg); for (const [xx, dir] of [[x1, 1], [x2, -1]]) s('path', { d: `M${X(xx)} ${y} l${8 * dir} -3 l0 6 Z`, fill: ink }, svg); s('text', { x: (X(x1) + X(x2)) / 2, y: y - 5, 'text-anchor': 'middle', 'font-size': 12, class: 't-mono t-ink' }, svg, text); };
    const ext = (x, y1, y2) => s('line', { x1: X(x), x2: X(x), y1, y2, stroke: mut, 'stroke-width': 0.8 }, svg);
    ext(0, Y(0) - 4, Y(0) - 64); ext(Lin, Y(0) - 4, Y(0) - 64); ext(ein, Y(bin / 2) - 10, Y(0) - 34); ext(ein + cin, Y(bin / 2) - 10, Y(0) - 34);
    dimH(0, Lin, Y(0) - 58, `${f(Lin, 2)} ±0.03  [${f1(dv.Lcut)} mm]`);
    dimH(ein, ein + cin, Y(0) - 28, `${f(cin, 3)} ±0.005  [${f1(ev.g.Lpp)} mm]  (pin centres)`);
    ext(0, Y(bin) + 4, Y(bin) + 40); ext(ein, Y(bin / 2) + 10, Y(bin) + 40);
    dimH(0, ein, Y(bin) + 34, `${f(ein, 3)} ±0.020`);
    // width dim (vertical)
    const xv = X(Lin) + 40;
    s('line', { x1: X(Lin) + 4, x2: xv + 6, y1: Y(0), y2: Y(0), stroke: mut, 'stroke-width': 0.8 }, svg); s('line', { x1: X(Lin) + 4, x2: xv + 6, y1: Y(bin), y2: Y(bin), stroke: mut, 'stroke-width': 0.8 }, svg);
    s('line', { x1: xv, x2: xv, y1: Y(0), y2: Y(bin), stroke: ink }, svg);
    s('text', { x: xv + 8, y: Y(bin / 2) + 4, 'font-size': 12, class: 't-mono t-ink' }, svg, `${f(bin, 3)} ${pl.mode === 'bar' ? '(stock)' : '±0.03'}`);
    // hole callout
    s('line', { x1: X(ein + cin) - 6, y1: Y(bin / 2) + 8, x2: X(ein + cin) - 50, y2: Y(bin) + 62, stroke: ink }, svg);
    s('text', { x: X(ein + cin) - 54, y: Y(bin) + 70, 'font-size': 12, 'text-anchor': 'end', class: 't-mono t-ink' }, svg, `2× Ø${f(hl.lo_in, 4)}–${f(hl.hi_in, 4)} THRU, REAM`);
    s('text', { x: X(ein + cin) - 54, y: Y(bin) + 86, 'font-size': 11, 'text-anchor': 'end', class: 't-muted' }, svg, `on plate centreline ±0.010; ${frac(d.pin.d_in)} in pin, clearance ${f(hl.cmin_in, 4)}–${f(hl.cmax_in, 4)} in`);
    // edge view (thickness)
    const ey = Y(bin) + 120;
    s('rect', { x: X(0), y: ey, width: Lin * sc, height: Math.max(tin * sc, 4), fill: 'var(--accent-wash)', stroke: ink }, svg);
    s('text', { x: X(0), y: ey + Math.max(tin * sc, 4) + 16, 'font-size': 11, class: 't-ink' }, svg, `Edge view — THK ${f(tin, 3)} (stock${pl.item.thicknessTol ? ', ' + pl.item.thicknessTol : ''})`);
    // notes
    const spec = { ss304: 'ASTM A276/A479', ss316: 'ASTM A276/A479', al6061: 'ASTM B221, T6511', al5052: 'ASTM B209, H32', al6063: 'ASTM B221' }[pl.item.mat] || '';
    const notes = [
      `MATERIAL: ${matName(pl.item.mat)} (${spec}), from McMaster ${ev.cost.plate.pn} (${plateDesc(pl)})`,
      `QTY: 2 (cut both from one piece: ${ev.cost.plateHow})`,
      'UNITS: inch [mm]. UNLESS NOTED: .XX ±0.03, .XXX ±0.010, angles ±1°',
      'Break sharp edges 0.02 max; deburr both sides of each hole. Ream after drilling (clamp both plates and ream together).',
      'Optional corner chamfer at the B end to clear the structure; keep ≥ 2 × hole Ø (1.256) from the hole centre.',
    ];
    notes.forEach((n, i) => s('text', { x: 20, y: Hh - 200 + i * 16, 'font-size': 11, class: 't-ink' }, svg, n));
    // title block
    const tbx = W - 330, tby = Hh - 118;
    s('rect', { x: tbx, y: tby, width: 318, height: 106, fill: 'none', stroke: ink }, svg);
    for (const yy of [26, 52, 78]) s('line', { x1: tbx, x2: tbx + 318, y1: tby + yy, y2: tby + yy, stroke: ink, 'stroke-width': 0.8 }, svg);
    s('line', { x1: tbx + 170, x2: tbx + 170, y1: tby + 26, y2: tby + 106, stroke: ink, 'stroke-width': 0.8 }, svg);
    s('text', { x: tbx + 8, y: tby + 18, 'font-size': 13, 'font-weight': 700, class: 't-ink' }, svg, 'DIAGONAL SUPPORT PLATE');
    s('text', { x: tbx + 8, y: tby + 44, 'font-size': 10.5, class: 't-ink' }, svg, 'PicoPower rotor support');
    s('text', { x: tbx + 178, y: tby + 44, 'font-size': 10.5, class: 't-ink' }, svg, 'DWG DP1-002  REV A');
    s('text', { x: tbx + 8, y: tby + 70, 'font-size': 10.5, class: 't-ink' }, svg, 'ME3180 Fall 2026 DP1');
    s('text', { x: tbx + 178, y: tby + 70, 'font-size': 10.5, class: 't-ink' }, svg, 'SCALE: NTS · SHEET 1/1');
    s('text', { x: tbx + 8, y: tby + 96, 'font-size': 10.5, class: 't-ink' }, svg, 'DRAWN: F. Arevalo');
    s('text', { x: tbx + 178, y: tby + 96, 'font-size': 10.5, class: 't-ink' }, svg, 'DATE: 2026-10-14');
    s('text', { x: 20, y: 30, 'font-size': 13, 'font-weight': 600, class: 't-ink' }, svg, 'Front view');
    // third-angle projection symbol
    const px = tbx - 74, py = tby + 30;
    s('path', { d: `M${px} ${py - 10} L${px + 26} ${py - 16} L${px + 26} ${py + 16} L${px} ${py + 10} Z`, fill: 'none', stroke: ink }, svg);
    s('circle', { cx: px + 50, cy: py, r: 16, fill: 'none', stroke: ink }, svg); s('circle', { cx: px + 50, cy: py, r: 9, fill: 'none', stroke: ink }, svg);
    s('text', { x: px - 2, y: py + 34, 'font-size': 9.5, class: 't-muted' }, svg, 'THIRD ANGLE');
    return svg;
  }
  function renderE() {
    const el = $('#partE'); el.textContent = ''; const ev = S.ev; if (!ev) return;
    const d = ev.design, c = ev.cost;
    el.append(head('Sheet E', 'Diagonal drawing and bill of materials', '1 point'));
    el.append(h('figure', null, h('div', { class: 'fig' }, plateDrawing(ev)), h('figcaption', { text: 'Generated from the selected design. Re-draw it in your CAD package with these dimensions for the submitted drawing (Onshape/SolidWorks drawing with the same views, dimensions, notes and title block).' })));
    el.append(h('h3', { text: 'Bill of materials' }));
    const rows = [
      ['1', 'Support beam stock', c.beam.pn, `${beamDesc(d.beam.item)}, ${c.beam.label || f1(c.beam.length_in) + ' in'} long`, '1', money(c.beam.price), money(c.beam.price)],
      ['2', 'Diagonal plate stock (both plates)', c.plate.pn, `${plateDesc(d.plate)}, ${c.plate.label || f1(c.plate.length_in) + ' in'}`, '1', money(c.plate.price), money(c.plate.price)],
      ['3', 'Pin (O, A, B)', d.pin.pn, `${pinName(d.pin)}, ${d.pin.material}`, String(c.pinPacks * (d.pin.pkg || 1)), money(d.pin.price) + (d.pin.pkg > 1 ? ` / ${d.pin.pkg}` : ''), money(c.pinCost)],
    ];
    if (c.ret) rows.push(['4', 'Pin retainer', c.ret.pn, `${c.ret.type}, ${c.ret.material}`, String(Math.ceil(3 / (c.ret.pkg || 1)) * (c.ret.pkg || 1)), money(c.ret.price) + (c.ret.pkg > 1 ? ` / ${c.ret.pkg}` : ''), money(c.retCost)]);
    if (c.washer) rows.push([String(rows.length + 1), 'Washer (under the pin head at A and B)', c.washer.pn, `${c.washer.desc}; ${c.washerPerJoint[1]} at A, ${c.washerPerJoint[2]} at B`, String(c.washerCount), money(c.washer.price) + (c.washer.pkg > 1 ? ` / ${c.washer.pkg}` : ''), money(c.washerCost)]);
    rows.push(['', 'Total', '', '', '', '', money(c.total)]);
    el.append(table([{ t: 'Item' }, { t: 'Description' }, { t: 'McMaster part' }, { t: 'Spec' }, { t: 'Qty', num: true }, { t: 'Unit price', num: true }, { t: 'Extended', num: true }], rows));
    el.append(h('p', { class: 'note small', text: `Prices are McMaster-Carr list prices read on ${CAT.meta.date}; re-check them on the day you submit. Machining (drilling and reaming 8 holes, 3 saw cuts) is excluded as the problem allows.` }));
  }

  // ------------------------------------------------------------------ Part F
  function renderF() {
    const el = $('#partF'); el.textContent = ''; const ev = S.ev; if (!ev) return;
    const c = ev.cost;
    el.append(head('Sheet F', 'Economy', '1 point'));
    const parts = [['Beam', c.beam.price], ['Plate stock', c.plate.price], ['Pins', c.pinCost], ['Retainers', c.retCost], ['Washers', c.washerCost]].filter(p => p[1] > 0);
    const W = 640, Hh = 56, tot = c.total; let x = 0;
    const svg = s('svg', { viewBox: `0 0 ${W} ${Hh}`, width: '100%', role: 'img', 'aria-label': 'Cost breakdown' });
    const cols = ['var(--s1)', 'var(--s2)', 'var(--s3)', 'var(--s4)', 'var(--s5)'];
    parts.forEach((p, i) => { const w = p[1] / tot * W; s('rect', { x: x + (i ? 1 : 0), y: 4, width: Math.max(w - 2, 1), height: 22, rx: 3, fill: cols[i] }, svg); if (w > 70) s('text', { x: x + 6, y: 46, 'font-size': 11, class: 't-ink' }, svg, `${p[0]} ${money(p[1])}`); x += w; });
    el.append(h('figure', null, h('div', { class: 'label', text: `Where the ${money(tot)} goes` }), svg, h('div', { class: 'legend' }, parts.map((p, i) => h('span', { style: `--k:${cols[i]}`, text: `${p[0]} ${money(p[1])} (${f0(p[1] / tot * 100)} %)` })))));
    const gov = ev.governing;
    el.append(h('p', { class: 'note', text: `What sets the cost: the 0.7 mm deflection limit uses ${f0(ev.defl.mag / 0.7 * 100)} % of its budget and the tightest strength check is "${gov.name}" at FS ${f2(gov.fs)}. A cheaper beam or thinner plates fail one of these; the table in the Solver sheet lists the cheaper beams and why they lose.` }));
    if (S.rows.length > 1) {
      el.append(h('h3', { text: 'Next-cheapest passing alternatives' }));
      el.append(table([{ t: '#' }, { t: 'Cost', num: true }, { t: 'Δ vs best', num: true }, { t: 'Beam' }, { t: 'Plate stock' }, { t: 'Pin' }, { t: 'a', num: true }],
        S.rows.slice(0, 8).map((r, i) => [String(i + 1), money(r.cost), '+' + money(r.cost - S.rows[0].cost), `${r.spec.beam} (${r.spec.orient})`, `${r.spec.plate} ${r.spec.mode}`, r.spec.pin, String(r.spec.a)]), { rowClass: i => i === S.sel ? 'sel' : null, onClick: i => { S.sel = i; evaluateSel(); renderAll(); location.hash = 'answer'; } }));
    }
  }

  // ------------------------------------------------------------------ assumptions & refs
  function renderAssumptions() {
    const el = $('#assumptions'); el.textContent = '';
    el.append(head('§', 'Assumptions and how each was justified'));
    const A = [
      ['Geometry from Figure 2', 'Rotor axis x = −1200 mm; beam from x = −1300 to +50 mm (the bottom-view "50" runs from pin O to the beam end), so the beam is 1350 mm long; B is 500 mm above O; the 50/350/500 mm dimensions are measured from the beam bottom face, so they move with the beam height; 39.49 in is the sprocket centre distance (exactly a 198-link #40 chain), so the generator shaft is at x = −196.95 mm.'],
      ['Chain', 'Tight span on −z (rear) from the rotation direction; tension = T/r₁ = 161.8 N; slack span 0 (no preload, req 7). Applied along the exact tangent line (4.73° skew). The water torque on the rotor is an external load; the chain and the generator torque are internal to the system but load the beam between the sprockets.'],
      ['Supports', 'O: two ½ in aluminium brackets outside the beam walls and one through-pin; reacts F_x, F_y, F_z and a moment about y (bracket couple), but no torque about x (req 10) and none about z (pin axis). F_z (the drag) is carried by the beam wall bearing on the front bracket face, not by the pin. Statically determinate: 6 unknowns, 6 equations.'],
      ['Diagonals', 'Flat plates on the outside of the beam walls at A and outside the B brackets; two-force members in the x-y plane carrying no z force. One through-pin at A and one at B (identical long pins used as two stubs at B would collide in the bracket gap), so three identical pins.'],
      ['Pin model', 'Each pin is a beam through its member stack with uniform bearing in every member (AFFDL-TR-69-42 §9.4, no peaking credit). Inner-member forces follow from the pin’s own equilibrium. At O the gap between bracket and beam is the bracket clearance; at A and B it is the worst-case axial play left after the washers, with all of it on one side. Stresses use the minimum pin diameter. Solid beams (if chosen) use a beam-on-elastic-foundation model (Hetényi).'],
      ['Factor of safety 2', 'On yield for every stress (von Mises, bearing against the weaker of member and pin, tear-out with 0.577 S_y, net section), for pin bending and peak pin shear (4V/3A); on load for plate buckling (Euler/Johnson, K = 1, both planes) and for first yield of the compression plate with an initial crookedness equal to the larger of L/1000 and the bar straightness tolerance (1/8 in per 5 ft).'],
      ['Materials', '18-8 and 316 pins: annealed minimums (S_y 30 ksi) because McMaster prints only hardness; no credit for cold work. 17-4 PH: S_y from the printed hardness (HRC ≥ 28 → H1150, 105 ksi; HRC ≥ 40 → H1025, 145 ksi), otherwise the 75 ksi H1150-M floor. Beam and plate yield: McMaster’s printed value for that family. E and G from ASM/AZoM data with G = E/2(1+ν).'],
      ['Requirement 12 (deflection)', 'Read as elastic deflection with ideal pins, the course convention: beam bending in both planes with Timoshenko shear (Cowper coefficients), twist from A to the rotor (Bredt, rounded corners), axial strain, plate stretch, and the roll caused by the beam’s slope at A, all summed as vectors at the CG. Brackets, shaft box and rotor shaft are rigid (req 10). Hole-clearance play (a one-time seating shift) is computed and reported separately; pin-joint elastic compliance is available as a sensitivity toggle.'],
      ['Tolerances', 'Holes reamed to the pin’s maximum diameter + RC-class minimum clearance, H8 width. Plate end distance includes 1 mm for cut and hole position; plate width checked at the narrowest stock width McMaster allows (−1/8 in hot-rolled stainless, −0.034 in 6061). Washer count uses the thickest washers so the retainer always engages; the leftover play uses the thinnest.'],
      ['Cost', 'Beam: shortest listed stock ≥ 1350 mm. Plates: shortest listed piece from which both plates come out (end to end with ⅛ in kerf, ripped lengthwise from a wider bar, or cut from a sheet). Pins, retainers and washers at pack price. List prices read on mcmaster.com on the catalog date.'],
      ['Corrosion', 'Stainless and aluminium only (galvanized steel excluded: cut ends and holes are bare). Stainless pins in aluminium are a galvanic couple, as the problem’s own aluminium brackets already are; use anti-seize on the pins in service, which also prevents galling.'],
      ['Removal', 'Hand-removable means no hammer, press or pliers: quick-release ball-detent pins or clevis pins with hairpin retainers only (retaining rings and split cotter pins excluded). Unload the joint (lift the rotor out of the flow and support the beam) before pulling a pin.'],
    ];
    el.append(table([{ t: 'Topic' }, { t: 'Assumption and reason' }], A));
  }
  function renderRefs() {
    const el = $('#refs'); el.textContent = '';
    el.append(head('¶', 'References'));
    const R = [
      ['Air Force Flight Dynamics Laboratory, Stress Analysis Manual AFFDL-TR-69-42, Ch. 9 Lug Analysis (pin bending Eq. 9-13, bearing, shear-out)', 'https://engineeringlibrary.org/reference/lug-analysis-air-force-stress-manual'],
      ['P. A. Lagace, MIT 16.20 Unit 12: Torsion of thin closed sections (Bredt–Batho τ = T/2A_m t, J = 4A_m²t/p_m)', 'https://ocw.mit.edu/courses/16-20-structural-mechanics-fall-2002/d01996bd6822461f4dcbdc3fbf2ea16f_unit12.pdf'],
      ['Australian Steel Institute, Design Capacity Tables Vol. 2, Section properties of hollow sections (rounded-corner A_m, p_m, J)', 'https://steel.org.au/getattachment/6661afcc-b964-4773-bda2-230850d06770/Section-properties-for-hollow-sections_bk140.pdf'],
      ['W. C. Young, R. G. Budynas, Roark’s Formulas for Stress and Strain, 7th ed., Table 10.1 (torsion of solid and hollow rectangles); M. Hetényi, Beams on Elastic Foundation, 1946', null],
      ['R. G. Budynas, J. K. Nisbett, Shigley’s Mechanical Engineering Design, 10th ed.: §4-11 to 4-13 columns (Euler/Johnson), Ch. 5 distortion energy, §8-12 shear joints, Table A-9 beam deflections', null],
      ['MechaniCalc, Column buckling (Euler, Johnson, transition slenderness)', 'https://mechanicalc.com/reference/column-buckling'],
      ['G. R. Cowper, The shear coefficient in Timoshenko’s beam theory, J. Appl. Mech. 33 (1966) 335–340', 'https://en.wikipedia.org/wiki/Timoshenko%E2%80%93Ehrenfest_beam_theory'],
      ['ANSI B4.1-1967 (R1987), Preferred Limits and Fits for Cylindrical Parts — RC/LC tables', 'https://fac.ksu.edu.sa/sites/default/files/fits_us_tables_ansi_b4.1-1967_r1987.pdf'],
      ['Aluminum Association, Table 12.1 minimum mechanical properties (6061-T6, 6063 extrusions); AZoM grade 304 and 316 data sheets', 'https://www.aluminum.org/sites/default/files/2022-12/Table_12.1.pdf'],
      ['ASTM A276 (annealed 304/316 bar), ASTM A564 (17-4 PH conditions), ASTM A484 (bar straightness 1/8 in per 5 ft)', 'https://store.astm.org/a0276_a0276m-25.html'],
      ['U.S. Tsubaki, The Complete Guide to Chain (chain length, tension = power/speed)', 'https://tsubaki.ca/wp-content/uploads/the-complete-guide-to-chain-tsubaki-canada.pdf'],
      ['McMaster-Carr product pages for every part in the bill of materials (mcmaster.com/<part number>), read on the catalog date', 'https://www.mcmaster.com/'],
    ];
    el.append(h('ol', { class: 'refs' }, R.map(([t, u]) => h('li', null, t, u ? ' — ' : '', u ? h('a', { href: u, target: '_blank', rel: 'noopener', text: u.replace(/^https?:\/\//, '').slice(0, 70) }) : ''))));
  }

  // ------------------------------------------------------------------ boot
  function renderAll() {
    renderMeta(); renderAnswer(); renderCompliance(); renderSolver(); renderA(); renderB(); renderC(); renderD(); renderE(); renderF(); renderAssumptions(); renderRefs();
  }
  function boot() {
    if (PRE && PRE.rows) S.rows = PRE.rows.slice();
    evaluateSel();
    renderAll();
  }
  boot();
  window.__dp1 = { S, runSearch, evaluateSel, renderAll };
})();
