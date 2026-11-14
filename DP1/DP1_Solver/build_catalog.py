#!/usr/bin/env python3
"""build_catalog.py — merge the McMaster sweeps into dp1-catalog.js (solver schema).

Inputs (JSON files in a work directory):
  old_catalog.json            8 Oct 2026 sweep (tubes, flat bars 1-3 in wide)     -> beams, plateStocks
  wf_result.json              14 Oct 2026 workflow result {catalog: {clevis, qrpins, retainers, bars, sheets}}
Usage: python3 build_catalog.py <workdir> <out.js>
"""
import json, re, sys, math
from fractions import Fraction

LBF = 4.448222

def num(x):
    if x is None: return None
    if isinstance(x, (int, float)): return float(x)
    s = str(x).strip().replace('"', '').replace('in', '').strip()
    try:
        if ' ' in s:
            a, b = s.split(' ', 1); return float(a) + float(Fraction(b))
        if '-' in s and '/' in s and not s.startswith('-'):
            a, b = s.split('-', 1); return float(a) + float(Fraction(b))
        return float(Fraction(s))
    except Exception:
        return None

def mat_key(m):
    m = (m or '').lower()
    if '17-4' in m: return 'ss174'
    if '316' in m: return 'ss316'
    if '18-8' in m or '304' in m or '303' in m or '302' in m: return 'ss188'
    if '6061' in m: return 'al6061'
    if '6063' in m: return 'al6063'
    if '5052' in m: return 'al5052'
    if 'stainless' in m: return 'ss188'
    return None

def stock_mat(m):
    m = (m or '').lower()
    if '316' in m: return 'ss316'
    if '304' in m or '18-8' in m: return 'ss304'
    if '6061' in m: return 'al6061'
    if '6063' in m: return 'al6063'
    if '5052' in m: return 'al5052'
    return None

def pin_strength_key(row):
    """17-4 PH: condition from printed hardness (conservative mapping)."""
    txt = ' '.join(str(row.get(k) or '') for k in ('material', 'hardness_or_condition', 'tensile_or_yield', 'notes'))
    k = mat_key(row.get('material'))
    if k != 'ss174': return k
    m = re.search(r'H\s?(900|925|1025|1075|1100|1150)', txt)
    if m:
        c = int(m.group(1)); return 'ss174_h900' if c <= 925 else ('ss174_h1025' if c <= 1075 else 'ss174_h1150')
    m = re.search(r'Rockwell C\s?(\d{2})', txt) or re.search(r'HRC\s?(\d{2})', txt)
    if m:
        hrc = int(m.group(1))
        if hrc >= 40: return 'ss174_h1025'      # HRC 40 is the H900 minimum; credit only the next-lower condition (H1025)
        if hrc >= 28: return 'ss174_h1150'      # HRC 28 is the H1150 minimum hardness (ASTM A564)
    return 'ss174_floor'                        # no condition, or an implausible Rockwell B print: H1150-M floor

def tol(s):
    if not s: return (-0.005, 0.0)
    v = re.findall(r'[-+]?\d*\.\d+|[-+]?\d+', s.replace('"', ''))
    if len(v) >= 2:
        a, b = float(v[0]), float(v[1]); return (min(a, b), max(a, b))
    return (-0.005, 0.0)

def cotter_max(s):
    m = re.search(r'(\d+/\d+|\d*\.\d+)"?\s*(?:max|maximum)?', s or '')
    mm = re.search(r'cotter[^0-9]*?(\d+/\d+|\d*\.\d+)', (s or '').lower())
    return num(mm.group(1)) if mm else None

def main(wd, out):
    old = json.load(open(f'{wd}/old_catalog.json'))
    wf = json.load(open(f'{wd}/wf_result.json'))
    cat = wf.get('catalog', wf)
    C = {'meta': {'date': '14 Oct 2026', 'notes': []}, 'beams': [], 'plateStocks': [], 'pins': [], 'retainers': [], 'washers': []}
    ft = lambda k: float(k.split()[0]) * 12
    # ---- beams: tubes from the 8 Oct sweep
    for b in old['beams']:
        t = b['t_in']
        # corners: welded stainless tube (ASTM A554) r_o ~ 2t, r_i ~ t; McMaster prints 'Outside Square, Inside Square' for the
        # multipurpose 6061 tubes (6546K73 page, 14 Oct) and the 6063 architectural tubes are near-sharp
        ro, ri = (2 * t, t) if b['mat'].startswith('ss') else (0, 0)
        C['beams'].append({'pn': b['pn'], 'family': b['family'], 'mat': b['mat'], 'kind': 'tube', 'dimA_in': b['A_in'], 'dimB_in': b['B_in'], 't_in': t,
                           'ro_in': ro, 'ri_in': ri, 'Sy': b.get('yield_mpa'), 'yieldNote': b.get('yield'), 'url': b.get('url'), 'read': '8 Oct 2026',
                           'offers': [{'length_in': ft(k), 'price': v, 'pn': (b.get('pn_by_length') or {}).get(k) or b['pn'], 'label': k} for k, v in b['lengths'].items()]})
    # ---- flat bars from the 8 Oct sweep
    seen = set()
    for b in old['bars']:
        key = (b['mat'], b['t_in'], b['b_in'], b['family'])
        seen.add(key)
        C['plateStocks'].append({'pn': b['pn'], 'family': b['family'], 'mat': b['mat'], 'shape': 'flat_bar', 't_in': b['t_in'], 'w_in': b['b_in'], 'Sy': b.get('yield_mpa'),
                                 'yieldNote': b.get('yield'), 'url': b.get('url'), 'read': '8 Oct 2026',
                                 'offers': [{'length_in': ft(k), 'price': v, 'pn': (b.get('pn_by_length') or {}).get(k) or b['pn'], 'label': k} for k, v in b['lengths'].items()]})
    # ---- new stock (bars, solid beam bars, sheets) from 14 Oct
    PSI = 6.894757e-3
    for src in ('bars', 'sheets'):
        for it in (cat.get(src) or {}).get('items', []):
            mk = stock_mat(it.get('material'))
            if not mk: continue
            Sy = it['yield_psi'] * PSI if it.get('yield_psi') else None
            offers = [{'length_in': o['length_in'], 'price': o['price_usd'], 'pn': o['pn'], 'label': o['length_label']} for o in it.get('offers', []) if o.get('price_usd')]
            if not offers: continue
            shape = it['shape']
            if shape in ('rect_bar_solid', 'square_bar_solid') and max(it['width_in'], it['thickness_in']) >= 4 - 1e-6 and min(it['width_in'], it['thickness_in']) >= 1.5 - 1e-6:
                C['beams'].append({'pn': offers[0]['pn'], 'family': it['family'], 'mat': mk, 'kind': 'solid', 'dimA_in': max(it['width_in'], it['thickness_in']), 'dimB_in': min(it['width_in'], it['thickness_in']),
                                   't_in': 0, 'Sy': Sy, 'yieldNote': it.get('yield_note'), 'url': it['url'], 'read': '14 Oct 2026', 'offers': offers, 'lengthTol': it.get('length_tolerance')})
            if shape in ('flat_bar', 'rect_bar_solid') and it['thickness_in'] <= 1.0 + 1e-6:
                C['plateStocks'].append({'pn': offers[0]['pn'], 'family': it['family'], 'mat': mk, 'shape': 'flat_bar', 't_in': it['thickness_in'], 'w_in': it['width_in'], 'Sy': Sy,
                                         'yieldNote': it.get('yield_note'), 'url': it['url'], 'read': '14 Oct 2026', 'offers': offers, 'lengthTol': it.get('length_tolerance'), 'thicknessTol': it.get('thickness_tolerance')})
            if shape in ('sheet', 'plate'):
                C['plateStocks'].append({'pn': offers[0]['pn'], 'family': it['family'], 'mat': mk, 'shape': 'sheet', 't_in': it['thickness_in'], 'w_in': it['width_in'], 'Sy': Sy,
                                         'yieldNote': it.get('yield_note'), 'url': it['url'], 'read': '14 Oct 2026', 'thicknessTol': it.get('thickness_tolerance'),
                                         'sheetOffers': [{'w_in': it['width_in'], 'l_in': o['length_in'], 'price': o['price'], 'pn': o['pn'], 'label': f"{it['width_in']:g} x {o['length_in']:g} in"} for o in offers]})
    # dedupe plate stocks by (mat, t, w, shape, first pn)
    ded = {}
    for p in C['plateStocks']:
        k = (p['mat'], round(p['t_in'], 4), round(p['w_in'], 4), p['shape'], p['pn'])
        if k not in ded: ded[k] = p; continue
        q = ded[k]
        if p['shape'] == 'flat_bar':     # merge stock lengths seen in different passes; newer reading wins per length
            byLen = {round(o['length_in'], 2): (o, q['read']) for o in q['offers']}
            for o in p['offers']:
                L = round(o['length_in'], 2)
                if L not in byLen or p['read'] >= byLen[L][1]: byLen[L] = (o, p['read'])
            q['offers'] = [v[0] for v in sorted(byLen.values(), key=lambda v: v[0]['length_in'])]
            if p['read'] > q['read']: q['read'] = p['read']; q['Sy'] = p['Sy'] or q['Sy']; q['url'] = p['url']
            if p.get('thicknessTol'): q['thicknessTol'] = p['thicknessTol']
        elif p['read'] > q['read']: ded[k] = p
    C['plateStocks'] = list(ded.values())
    # ---- pins
    for src in ('clevis', 'qrpins'):
        for r in (cat.get(src) or {}).get('pins', []):
            mk = pin_strength_key(r)
            if not mk or r.get('usable_len_in') is None or r.get('price_usd') is None: continue
            lo, hi = tol(r.get('dia_tolerance'))
            if not r.get('dia_tolerance') and r['pn'].startswith(('98404A', '98470A', '94975A', '98405A')): lo, hi = (-0.003, 0.0)   # printed for 98404A530/650/790
            isQR = src == 'qrpins' or 'quick' in (r.get('family') or '').lower() or 'ball' in (r.get('style') or '').lower()
            ret = (r.get('retention') or '').lower(); fam = (r.get('family') or '').lower() + ' ' + (r.get('style') or '').lower()
            if 'retaining ring' in ret or 'retaining ring' in fam or 'headless' in fam:
                C['meta']['notes'].append(f"excluded {r['pn']}: needs retaining-ring pliers or two retainers (not hand-removable / headless)"); continue
            hand_incl = bool(re.search(r'includes? (a )?(reusable )?hairpin|hairpin cotter pin \+ lanyard|linch pin|toggle|wire retainer|locking retainer', ret))
            needs = (not isQR) and not hand_incl
            shear = r.get('shear_strength_lbf')
            note = (r.get('shear_strength_note') or '').lower()
            shearN = shear * LBF if shear and 'double' in note else (shear * 2 * LBF if shear and 'single' in note else (shear * LBF if shear else None))
            C['pins'].append({'pn': r['pn'], 'family': r['family'], 'style': r.get('style') or ('quick-release' if isQR else 'clevis'), 'material': r['material'],
                              'hardness': r.get('hardness_or_condition'), 'matKey': mk, 'd_in': r['d_in'], 'usable_in': r['usable_len_in'], 'overall_in': r.get('overall_len_in'),
                              'price': r['price_usd'], 'pkg': r.get('pkg_qty') or 1, 'tolMinus_in': lo, 'tolPlus_in': hi, 'needsRetainer': needs,
                              'hollow': bool(isQR and re.search(r'(?<!non)locking', fam)),   # push-button locking pins have a plunger bore; ring-grip ball-detent pins are solid
                              'cotterMax_in': cotter_max(r.get('retention')), 'shearRating_N': shearN, 'shearNote': (f"{shear:,.0f} lbf " + ('double-shear' if 'double' in note else 'single-shear') + ' breaking strength') if shear else None, 'retention': r.get('retention'), 'url': r.get('url'), 'read': '14 Oct 2026'})
    # ---- retainers + washers
    for r in (cat.get('retainers') or {}).get('retainers', []):
        if 'split ring' in (r.get('type') or '').lower(): continue      # lanyard key ring, not a cross-hole retainer
        C['retainers'].append({'pn': r['pn'], 'type': r['type'], 'material': r['material'], 'fits': r['fits'], 'wire_in': r.get('wire_dia_in'), 'pinDmin_in': r.get('for_pin_dia_min_in'),
                               'pinDmax_in': r.get('for_pin_dia_max_in'), 'holeDia_in': r.get('for_hole_dia_in'), 'price': r['price_usd'], 'pkg': r.get('pkg_qty') or 1,
                               'hand': bool(r.get('hand_install')) and 'stainless' in (r.get('material') or '').lower(), 'url': r.get('url'), 'read': '14 Oct 2026'})
    for w in (cat.get('retainers') or {}).get('washers', []):
        TW = {'92141A056': (0.102, 0.116)}   # thickness range read on the part page (14 Oct)
        tr = TW.get(w['pn'])
        C['washers'].append({'pn': w['pn'], 'desc': w['desc'], 'for_dia_in': w['for_dia_in'], 't_in': w.get('thickness_in') or 0.0625, 't_min_in': tr[0] if tr else None, 't_max_in': tr[1] if tr else None, 'od_in': w.get('od_in'),
                             'material': w['material'], 'price': w['price_usd'], 'pkg': w.get('pkg_qty') or 1, 'url': w.get('url')})
    # attach cheapest washer per pin diameter
    for p in C['pins']:
        ws = [w for w in C['washers'] if abs(w['for_dia_in'] - p['d_in']) < 1e-6 and 'stainless' in (w['material'] or '').lower()]
        if ws: p['washers'] = ws; p['washer'] = min(ws, key=lambda w: w['price'])
    js = '/* dp1-catalog.js — McMaster-Carr parts (generated by build_catalog.py) */\n(function(){var C=' + json.dumps(C) + \
         ';if(typeof module!=="undefined"&&module.exports)module.exports=C;else window.DP1_CATALOG=C;})();\n'
    open(out, 'w').write(js)
    print({k: len(v) for k, v in C.items() if isinstance(v, list)})

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
