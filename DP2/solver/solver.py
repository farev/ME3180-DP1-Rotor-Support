"""DP2 shaft solver: every McMaster precision rotary shaft x every stainless ring that fits it.

Same physics as ../solution/calculate.py (loads, moments, Marin factors, Neuber q, Goodman,
Shigley Eq. 7-15 yield and the stricter Kt elastic check), generalised to any diameter.
Units: N, mm, MPa. Stdlib only.

Cost rule (Req. 4, user's reading, 10 Nov 2026): full price of the shortest stock of the
part that is long enough for the shaft, + $100 if the shaft is not stainless, + hardware.

Run:  python3 solver.py            ranked table + data/results.csv
      python3 solver.py --check    regression against calculate.py's 1.500 in design
"""
from math import pi, sin, cos, radians, sqrt, hypot, ceil
from pathlib import Path
import csv, json, sys, bisect

HERE = Path(__file__).resolve().parent
DATA = HERE / 'data'
INCH = 25.4

# ---------------- loads (identical to calculate.py) ----------------
L = dict(rotor_N=120.0, sprocket_N=35.0, drag_N=560.0, chain_N=161.8, chain_deg=-4.732,
         chain_y=-50.0, COP_y=-500.0, T=19630.0, pin_y=-185.0, bearing_w=12.7,
         face=300.0, rho=7850.0, g=9.80665, shaft_bottom=-250.5)
fx = L['chain_N']*cos(radians(L['chain_deg']))
fz = -L['chain_N']*sin(radians(L['chain_deg']))
yL, yU = L['bearing_w']/2, L['face']-L['bearing_w']/2
RUx = fx*(yL-L['chain_y'])/(yU-yL)
RUz = (fz*(yL-L['chain_y'])+L['drag_N']*(yL-L['COP_y']))/(yU-yL)
RLx, RLz = -fx-RUx, -fz-L['drag_N']-RUz

def bending(y):
    mx = (L['COP_y']-y)*L['drag_N']; mz = 0.0
    if y >= L['chain_y']: mx += (L['chain_y']-y)*fz; mz -= (L['chain_y']-y)*fx
    if y >= yL: mx += (yL-y)*RLz; mz -= (yL-y)*RLx
    if y >= yU: mx += (yU-y)*RUz; mz -= (yU-y)*RUx
    return hypot(mx, mz)

# ---------------- Shigley factors ----------------
REL = 0.814                     # ke, 99 % reliability (Table 6-4)
KT_DECIMALS = 1                 # chart Kt read to one decimal, as Shigley Ex. 7-2 does (3.58 -> 3.6 at the 1.5 in groove)
GROOVE_R_IN = 0.008             # drawing callout R 0.008-0.010 in; worst case is the small end
GROOVE_ROOT = 'nominal'         # root at catalog nominal (Rev P3 callout 1.456-1.460 in for the 1.5 in ring)
PIN_EXTRA = 0.0                 # P2 added a 12 MPa hub-contact mean stress at the pin hole; dropped (no physical basis)
KA = {'ground': (1.38, -.067), 'machined': (3.04, -.217)}   # Shigley 11th ed., Table 6-2, Sut in MPa
def ka(Sut, ground=False):
    a, b = KA['ground' if ground else 'machined']; return a*Sut**b
def kb(d): return 1.24*d**-.107 if d <= 51 else 1.51*d**-.157
Q_MODE = 'groove'   # 'groove': q at ring grooves only (design); 'none': Kf = Kt everywhere; 'all': q at every notch
def q_bend(Sut, r):
    """Shigley 11th Eqs. (6-33) and (6-35), bending/axial, Sut in kpsi, r in inches."""
    if Q_MODE == 'none': return 1.0
    k = Sut/6.894757293; a = .246-.00308*k+.0000151*k**2-2.67e-8*k**3
    return 1/(1+a/sqrt(r/INCH))
def q_shear(Sut, r):
    """Shigley 11th Eqs. (6-33) and (6-36), torsion, Sut in kpsi (no +20 kpsi shift in this edition)."""
    if Q_MODE == 'none': return 1.0
    k = Sut/6.894757293; a = .190-2.51e-3*k+1.35e-5*k**2-2.67e-8*k**3
    return 1/(1+a/sqrt(r/INCH))

FIG = {float(k): v for k, v in json.load(open(DATA/'fig_a15_16.json')).items()}
def kt_groove(at, rt):
    """Fig. A-15-16, digitized for 1.0 <= a/t <= 3.0; linear in a/t along a curve, linear in r/t between curves."""
    if not 1.0 <= at <= 3.0: raise ValueError(f'a/t {at:.2f} outside digitized range 1-3')
    def on(c):
        pts = FIG[c]; xs = [p[0] for p in pts]
        if at < xs[0] or at > xs[-1]: return None
        i = max(1, bisect.bisect_left(xs, at)); (x0, y0), (x1, y1) = pts[i-1], pts[i]
        return y0+(y1-y0)*(at-x0)/(x1-x0)
    cs = sorted(c for c in FIG if on(c) is not None)
    if rt <= cs[0]: raise ValueError(f'r/t {rt:.3f} sharper than charted')
    if rt >= cs[-1]: return on(cs[-1])            # blunter than the last curve: conservative
    for c0, c1 in zip(cs, cs[1:]):
        if c0 <= rt <= c1: return on(c0)+(on(c1)-on(c0))*(rt-c0)/(c1-c0)

# Table A-16, solid bar (d/D = 0): a/D -> (A, Kt) bending, (A, Kts) torsion
A16B = [(.05,.88,2.42),(.075,.86,2.35),(.10,.83,2.27),(.125,.80,2.20),(.15,.76,2.15),(.175,.72,2.10),
        (.20,.68,2.07),(.225,.65,2.04),(.25,.61,2.00),(.275,.58,1.97),(.30,.54,1.94)]
A16T = [(.05,.92,1.77),(.10,.92,1.68),(.125,.89,1.64),(.15,.87,1.62),(.175,.85,1.60),(.20,.83,1.58),
        (.25,.79,1.54),(.30,.74,1.51)]
def lerp_tab(tab, x):
    for (x0,*a),(x1,*b) in zip(tab, tab[1:]):
        if x0 <= x <= x1: return [u+(v-u)*(x-x0)/(x1-x0) for u, v in zip(a, b)]
    raise ValueError('a/D outside Table A-16')

# Table 7-6 square keys: shaft over..to (in) -> width (in)
KEYS = [(7/8, 1.25, .25), (1.25, 1.375, .3125), (1.375, 1.75, .375), (1.75, 2.25, .5), (2.25, 2.75, .625)]
def key_width(D_in):
    for lo, hi, w in KEYS:
        if lo < D_in <= hi + 1e-9: return w
    raise ValueError('no key size')

# Hardness -> Brinell (ASTM E140 approximate); HRC25 cap = HB 253 (Req. 5)
HB = {'HB197':197,'HB190':190,'HRC25':253,'HRC28':271,'HRC14':197,'HRB95':210,'HRB90':185,
      'HRB89':180,'HRB85':162,'HRB83':156,'HRB80':146}

KSI = 6.894757293
SUT_MODE = 'hardness'          # 'hardness': Sut = 3.4 HB (Eq. 2-36); 'marks': 703 MPa for 1045 HB197
def props(sh):
    """Piazza-approved yield strengths (instructor post, 10 Nov 2026); Sut from hardness, HRC25 cap."""
    hb = HB.get(sh['hardness'])
    if hb is None: return None
    Sut = 3.4*min(hb, 253)
    st, h, D = sh['steel'], sh['hardness'], sh['D_in']
    Sy = None
    if st == '1045' and h == 'HB197': Sy = 75*KSI
    elif st == '1045' and h == 'HB190' and D <= 2.0: Sy = 75*KSI
    elif st == '1566' and h == 'HRC25': Sy = (88 if D <= 1.5 else 82)*KSI
    elif st == 'alloy' and h == 'HRC28': Sy = (120 if D <= 1.0 else 110)*KSI
    if st == '1045' and h == 'HB197' and SUT_MODE == 'marks': Sut = 703.0
    src = (f'Sy {Sy:.1f} MPa approved on Piazza; ' if Sy else 'no approved Sy; ') + f'Sut {Sut:.1f} MPa'
    return dict(Sut=Sut, Sy=Sy, src=src)

def evaluate(sh, ring, keyseat='harsh', kt_override=None, pin_d_in=None):
    P = props(sh)
    D = sh['D_in']*INCH; Dmin = (sh['D_in']-sh['od_tol_in'])*INCH
    out = dict(part=sh['part'], steel=sh['steel'], D_in=sh['D_in'], len_in=sh['len_in'],
               price=sh['price_USD'], ring=ring['part'], ring_type=ring['type'], notes=[])
    Sut = P['Sut']; Sy = P['Sy']
    # groove: worst case of the drawing callout (root at catalog nominal, smallest root radius)
    tol = ring['groove_tol_plus_in']
    root_in = ring['groove_in'] + (tol-0.001 if (tol and GROOVE_ROOT == 'shallow') else 0.0)
    root = root_in*INCH; t = (D-root)/2; a = ring['width_in']*INCH; r = GROOVE_R_IN*INCH
    at, rt = a/t, r/t
    Ktc = kt_groove(at, rt); Kt = kt_override or round(Ktc, KT_DECIMALS)
    q = q_bend(Sut, r); Kfg = 1+q*(Kt-1)
    yg = -(0.1+a/2)
    length = -L['shaft_bottom'] + L['face'] + 0.1 + a + .002*INCH + 2.562
    N = L['rotor_N']+L['sprocket_N']+L['rho']*L['g']*pi*(D/1000)**2/4*(length/1000)
    Se_m = .5*Sut*ka(Sut)*kb(D)*REL; Se_g = .5*Sut*ka(Sut, True)*kb(D)*REL

    def sec(name, d, M, T, Kt, Kts, Kf=None, Kfs=None, Ab=1, At=1, extra=0, ground=False):
        Kf = Kt if Kf is None else Kf; Kfs = Kts if Kfs is None else Kfs
        sb = 32*M/(pi*d**3*Ab); st = 16*T/(pi*d**3*At); sn = 4*N/(pi*d*d)
        sa = Kf*sb; sm = Kt*sn+extra; tm = Kts*st
        strict = sqrt((Kt*sb+sm)**2+3*tm**2); e715 = sqrt((Kf*sb+sm)**2+3*(Kfs*st)**2)
        se = Se_g if ground else Se_m
        nf = 1/(sa/se+sqrt(sm**2+3*tm**2)/Sut)
        return dict(name=name, M=M/1000, Kt=Kt, Kf=Kf, nf=nf, s_strict=strict, s_715=e715,
                    ny_strict=Sy/strict if Sy else None, ny_715=Sy/e715 if Sy else None)

    S = [sec('groove', root, bending(yg), 0, Kt, 0, Kf=Kfg)]
    # keyseat
    w = key_width(sh['D_in']); Lk = w+.125                       # key longer than wide (class rule)
    keyF = 2*L['T']/Dmin
    if keyseat == 'harsh':   # P2 geometry, kept for the --check regression
        slot = Lk*INCH+9.75; yk = -36+(slot+.05)/2
        eng = (w-.003)*INCH-(w/2+.001)*INCH; Lmin = Lk*INCH-.05
    else:                    # ASME B17.1 Class 1 keyseat + ISO 286 IT14 lengths (as in calculate.py)
        it14 = .43 if Lk*INCH <= 18 else .52
        slot = Lk*INCH+it14+(w+.002)*INCH; yk = -36+slot/2          # end-centre distance H14, width +0.002 in
        fil, chm = ((1/32, 3/64) if w/2 <= .25 else (1/16, 5/64))  # B17.1 Table 5 fillet, key chamfer (in)
        eng = (min((w-.003)-(w/2+.015), w/2)-chm)*INCH; Lmin = Lk*INCH-it14
    p_key = keyF/(eng*Lmin); tau_key = keyF/((w-.003)*INCH*Lmin)
    if keyseat == 'harsh':     # P2 model, kept for the --check regression only
        S.append(sec('keyseat', Dmin, bending(yk), L['T'], 3.0, 4.0, extra=p_key))
    elif keyseat == 'peterson':  # design: floor R = 0.02d -0.002 in, Pilkey Sec. 5.2 fits, Kf = Kt (q = 1), no key pressure
        rd = fil*INCH/Dmin; u = .1/rd
        S.append(sec('keyseat', Dmin, bending(yk), L['T'], round(1.426+.1643*u-.0019*u*u, 2), round(1.953+.1434*u-.0021*u*u, 2)))
    else:   # Shigley Table 7-1 end-mill keyseat, r/d = 0.02, with notch sensitivity
        rk = .02*Dmin
        S.append(sec('keyseat', Dmin, bending(yk), L['T'], 2.14, 3.0, Kf=1+q_bend(Sut,rk)*1.14, Kfs=1+q_shear(Sut,rk)*2.0))
    # pin and pin hole: smallest 416 pin that passes, hub OD = 2D so pin length >= 2D
    # Design: 1/4 in 416 dowel (McMaster 98380A556/560), checked against its 7200 lbf double-shear rating.
    pin_opts = [pin_d_in] if pin_d_in else [.25]
    for pd in pin_opts:
        pdm = pd*INCH
        hole = (pd+.001)*INCH if keyseat == 'harsh' else 6.378   # P2 hole / ISO 286 F7 upper limit
        pinR = hypot(L['T']/Dmin, L['rotor_N']/2)
        ny_pin = 7200*4.448221615/(2*pinR)
        Ab, Ktb = lerp_tab(A16B, hole/Dmin); At_, Ktt = lerp_tab(A16T, hole/Dmin)
        qa = Q_MODE == 'all'
        ph = sec('pin hole', Dmin, L['drag_N']*(500+L['pin_y']+hole/2), L['T'], Ktb, Ktt, Ab=Ab, At=At_, extra=PIN_EXTRA,
                 Kf=1+q_bend(Sut, hole/2)*(Ktb-1) if qa else None, Kfs=1+q_shear(Sut, hole/2)*(Ktt-1) if qa else None)
        if ny_pin >= 1.2: break
    S.append(ph)
    S.append(sec('plain at bearing', Dmin, bending(yL), 0, 1, 1, ground=True))

    out.update(Sut=Sut, Sy=Sy, prop_src=P['src'], a_t=at, r_t=rt, Kt_chart=Ktc, Kt=Kt, Kf_groove=Kfg,
               root_in=root_in, length_mm=length, key_w_in=w, key_L_in=Lk, pin_d_in=pd, pin_len_min_in=2*sh['D_in'],
               ny_pin=ny_pin, n_key_shear=412/(sqrt(3)*tau_key), n_key_bearing=412/p_key,
               ring_capacity_ratio=ring['thrust_lbf']*4.448221615/N, sections=S)
    out['nf_min'] = min(s['nf'] for s in S); out['nf_at'] = min(S, key=lambda s: s['nf'])['name']
    out['Sy_req_715'] = 3*max(s['s_715'] for s in S); out['Sy_req_strict'] = 3*max(s['s_strict'] for s in S)
    out['ny_715'] = Sy/max(s['s_715'] for s in S) if Sy else None
    out['ny_strict'] = Sy/max(s['s_strict'] for s in S) if Sy else None
    if sh['len_in']*INCH < length: out['notes'].append('stock too short')
    # cost
    ring_each = ring['pack_price_USD']/ring['pack_qty']
    # 416 dowel pins read 10 Nov 2026: 98380A556 1/4 x 3 in $4.69, 98380A560 1/4 x 3-1/2 in $9.46
    if pd == .25 and 2*sh['D_in'] <= 3.0: pin_cost, out['pin_part'] = 4.69, '98380A556'
    elif pd == .25 and 2*sh['D_in'] <= 3.5: pin_cost, out['pin_part'] = 9.46, '98380A560'
    else:
        pin_cost, out['pin_part'] = 10.00, '?'
        out['notes'].append(f'pin {pd} x >= {2*sh["D_in"]:.3f} in: price assumed $10.00')
    key_cost = 28.32/36*Lk
    if w != .375: out['notes'].append(f'{w} in key stock price assumed = 3/8 stock $/in')
    out['cost'] = sh['price_USD']+(0 if sh['stainless'] else 100)+2*ring_each+pin_cost+4.81/25+key_cost
    hw_ok = min(out['ny_pin'], out['n_key_shear'], out['n_key_bearing'], out['ring_capacity_ratio']) >= 1.2
    out['passes_fatigue'] = out['nf_min'] >= 1.2
    out['passes_yield_715'] = None if Sy is None else out['ny_715'] >= 3
    out['passes_yield_strict'] = None if Sy is None else out['ny_strict'] >= 3
    out['hardware_ok'] = hw_ok and 'stock too short' not in out['notes']
    return out

EXCLUDE = {'nitride': 'core strength/hardness not rated; only the HRC60 case is listed, so no property set can meet Req. 5',
           'd-profile': 'full-length flat runs through both bearing seats and ring grooves',
           'fully-keyed': 'full-length keyway runs through both bearing seats and ring grooves',
           'partially-keyed': '4 in and 14 in end keyways on 24 in stock reach the bearing seats/grooves'}

def load():
    num = lambda r, ks: {**r, **{k: float(r[k]) if r[k] else 0.0 for k in ks}}
    shafts = [num(r, ['D_in','len_in','price_USD','od_tol_in']) | {'stainless': r['stainless']=='1'}
              for r in csv.DictReader(open(DATA/'shafts.csv'))]
    rings = [num(r, ['D_in','groove_in','groove_tol_plus_in','width_in','thrust_lbf','pack_price_USD','pack_qty'])
             for r in csv.DictReader(open(DATA/'rings.csv'))]
    return shafts, rings

def run(keyseat='harsh'):
    shafts, rings = load(); rows = []; excluded = []
    for sh in shafts:
        if sh['shape'] in EXCLUDE: excluded.append((sh, EXCLUDE[sh['shape']])); continue
        if props(sh) is None: excluded.append((sh, 'no hardness to base a property set on')); continue
        fits = [r for r in rings if abs(r['D_in']-sh['D_in']) < 1e-4]
        if not fits: excluded.append((sh, 'no stainless retaining ring for this diameter')); continue
        for rg in fits:
            try: rows.append(evaluate(sh, rg, keyseat))
            except ValueError as e: excluded.append((sh, f'{rg["part"]}: {e}'))
    return rows, excluded

def verdict(o):
    if not o['hardware_ok']: return 'FAIL hardware/length'
    if not o['passes_fatigue']: return f"FAIL fatigue ({o['nf_at']})"
    if o['Sy'] is None: return f"needs Sy >= {o['Sy_req_715']:.0f} (Eq 7-15)"
    if not o['passes_yield_715']: return 'FAIL yield'
    return 'PASS' + ('' if o['passes_yield_strict'] else ' (Eq 7-15 only)')

if __name__ == '__main__':
    if '--check' in sys.argv:
        shafts, rings = load()
        sh = next(s for s in shafts if s['part']=='4138N14'); rg = next(r for r in rings if r['part']=='93576A210')
        props = lambda _s: dict(Sut=703.0, Sy=598.0, src='P2 proposal')
        GROOVE_R_IN, GROOVE_ROOT = 0.0098, 'shallow'   # P2 drawing groove
        PIN_EXTRA = 12.0
        KA.update(ground=(1.58, -.085), machined=(4.51, -.265))   # P2 used the 10th-edition surface factors
        L['pin_y'] = -180.0
        o = evaluate(sh, rg, kt_override=3.5, pin_d_in=.25)
        ref = {'groove': (1.3309, 3.0333, 4.1576), 'keyseat': (1.2404, 3.5947, 3.5947),
               'pin hole': (1.8998, 5.4742, 5.4742), 'plain at bearing': (4.1309, 11.3305, 11.3305)}
        for s in o['sections']:
            nf, nys, ny7 = ref[s['name']]
            print(f"{s['name']:17} nf {s['nf']:.4f} (calc {nf})  ny strict {s['ny_strict']:.4f} ({nys})  ny 7-15 {s['ny_715']:.4f} ({ny7})")
            assert abs(s['nf']-nf) < 2e-3 and abs(s['ny_strict']-nys) < 5e-3 and abs(s['ny_715']-ny7) < 5e-3
        print(f"chart Kt at this groove: {o['Kt_chart']:.3f} (P2 design used 3.5)")
        print('regression OK'); sys.exit()
    model = 'table71' if '--table71' in sys.argv else ('harsh' if '--harsh' in sys.argv else 'peterson')
    if '--marks-sut' in sys.argv: SUT_MODE = 'marks'
    if '--kf-eq-kt' in sys.argv: Q_MODE = 'none'
    if '--q-all' in sys.argv: Q_MODE, model = 'all', 'table71'
    print(f'Notch sensitivity: {Q_MODE}')
    rows, excluded = run(model)
    rows.sort(key=lambda o: o['cost'])
    print(f'Keyseat model: {model}.  Cost = full stock price + $100 if not stainless + hardware.\n')
    print(f"{'cost':>8} {'shaft':9} {'steel':10} {'D in':>6} {'stock':>6} {'ring':10} {'Kt':>5} {'nf':>5} {'at':9} {'ny715':>6} {'nyKt':>6} {'Sy req':>6}  verdict")
    for o in rows:
        f = lambda v: f'{v:6.2f}' if v is not None else '     -'
        print(f"{o['cost']:8.2f} {o['part']:9} {o['steel'][:10]:10} {o['D_in']:6.4f} {o['len_in']:6.1f} {o['ring']:10} {o['Kt']:5.2f} "
              f"{o['nf_min']:5.2f} {o['nf_at'][:9]:9} {f(o['ny_715'])} {f(o['ny_strict'])} {o['Sy_req_715']:6.0f}  {verdict(o)}")
    print('\nExcluded:')
    for sh, why in excluded: print(f"  {sh['part']:9} {sh['steel'][:12]:12} {sh['D_in']:.4f} in ${sh['price_USD']:.2f}: {why}")
    with open(DATA/f'results_{model}_q-{Q_MODE}.csv', 'w', newline='') as fh:
        keys = ['cost','part','steel','D_in','len_in','price','ring','ring_type','Kt_chart','Kt','a_t','r_t','nf_min','nf_at',
                'ny_715','ny_strict','Sy_req_715','Sy_req_strict','Sut','Sy','key_w_in','pin_d_in','ny_pin','ring_capacity_ratio','notes']
        w = csv.DictWriter(fh, fieldnames=keys+['verdict'], extrasaction='ignore'); w.writeheader()
        for o in rows: w.writerow({**o, 'notes': '; '.join(o['notes']), 'verdict': verdict(o)})
