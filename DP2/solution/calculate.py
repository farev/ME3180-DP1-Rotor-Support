"""DP2 calculation record. Units: N, mm, MPa unless explicitly stated.

This is a PROVISIONAL classroom design, subject to approval of the proposed
shaft property set. Run with Python 3; the calculation itself uses stdlib only.
Every assumed coefficient is exposed below. No optimizer silently changes it.
"""
from pathlib import Path
from math import ceil, pi, sin, cos, radians, sqrt, hypot
import json, csv

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
DATA.mkdir(exist_ok=True)
INCH = 25.4
I = {
    # Rev P3 (10 Nov 2026): McMaster 1346K534, 1566 carbon steel, HRC25, 1-1/2 in x 24 in, OD -0.004/0 in.
    # Sy = 88 ksi approved on Piazza (1566 HRC25, D <= 1.5 in). Sut = 3.4 HB (Shigley Eq. 2-36), HRC25 = HB 253.
    'shaft_part': '1346K534', 'D_nom_mm': 1.5*INCH,
    'D_min_mm': 1.496*INCH, 'length_mm': 554.0,
    'shaft_HB': 253, 'Sut_MPa': 3.4*253, 'Sy_MPa': 88*6.894757293, 'E_MPa': 205000.0,
    'rho_kg_m3': 7850.0, 'g_m_s2': 9.80665,
    'bearing_width_mm': 12.7, 'outer_face_spacing_mm': 300.0,
    'rotor_N': 120.0, 'sprocket_N': 35.0, 'drag_N': 560.0,
    'chain_N': 161.8, 'chain_angle_deg': -4.732,
    'chain_y_mm': -50.0, 'COP_y_mm': -500.0,
    'T_Nmm': 19630.0, 'pin_y_mm': -185.0,  # 35 mm below the hub top; lowest round position whose hole stays in the upper 40 mm
    'groove_D_min_mm': 1.456*INCH,
    'groove_D_max_mm': 1.460*INCH,
    'groove_width_min_mm': .031*INCH,
    'groove_width_max_mm': .033*INCH,
    'groove_r_min_mm': .008*INCH,
    'groove_r_max_mm': .0100*INCH,
    'groove_Kt': 3.6,
    'lower_groove_y_mm': -.4937,
    'upper_groove_y_mm': 300.4937,
    'key_slot_center_y_mm': -36.0,
    # Keyseat per ASME B17.1-1967 (R2013), Class 1 fit, square key up to 1/2 in (Machinery's Handbook 31st ed., Tables 4-5):
    #   width W = 3/8 in +0.002/-0; depth H/2 = 3/16 in at the side wall, shaft keyseat +0.015 deeper / -0 (S +0/-0.015);
    #   floor fillet 1/32 in and key chamfer 3/64 x 45 deg for H/2 over 1/8 to 1/4 in (Table 5).
    # Length (B17.1 gives none): ISO 286 IT14 for 10-18 mm = 0.43 mm. Key length 12.70 h14 (+0/-0.43);
    #   slot end-centre distance 12.70 H14 (+0.43/-0), so the straight walls are never shorter than the key.
    'key_length_mm': .50*INCH,  # key must be longer than it is wide (class rule)
    'key_length_tolerance_mm': .43,        # h14: +0/-0.43
    'key_slot_cc_mm': .50*INCH,            # end-centre distance = straight length
    'key_slot_cc_plus_mm': .43,            # H14: +0.43/-0
    'keyseat_width_mm': .375*INCH, 'keyseat_width_plus_mm': .002*INCH,
    'key_b_min_mm': .372*INCH,
    'key_h_min_mm': .372*INCH,
    'keyseat_depth_side_mm': .1875*INCH, 'keyseat_depth_plus_mm': .015*INCH,
    'key_Sut_MPa': 515.0, 'key_Sy_MPa': .8*515,
    'keyseat_r_mm': INCH/32,               # B17.1 Table 5 fillet
    'key_chamfer_mm': 3*INCH/64,           # B17.1 Table 5 key chamfer
    'pin_d_mm': .25*INCH, 'pin_length_mm': 3.0*INCH,
    'pin_d_max_mm': .2503*INCH,              # McMaster 98380A556: 1/4 in +0.0001/+0.0003 (ASME B18.8.2 standard series)
    'pin_double_shear_lbf': 7200.0,          # McMaster 98380A556: double shear breaking strength
    'pin_shaft_hole_mm': [6.363, 6.378],     # ISO 286 F7 for 6.35 mm (+0.013/+0.028): slip fit in the shaft
    'pin_hub_hole_in': [.2495, .2500],       # ASME B18.8.2 press-fit hole, standard series 1/4 in (steel)
    'screw_Sy_MPa': 205.0, 'screw_d_mm': .25*INCH,
    'screw_Ar_mm2': .0269*INCH**2,          # 1/4-20 UNC minor-diameter area, Shigley Table 8-2
    'screw_pitch_mm': INCH/20,
    'screw_socket_AF_mm': .125*INCH,         # 1/8 in hex socket, ASME B18.3 (Unbrako table)
    'screw_flat_tip_min_mm': .118*INCH,      # flat point diameter C min, ASME B18.3 (Unbrako table)
    'screw_K': .20,                          # Shigley Table 8-15 / Sec. 8-8: K = 0.2 when condition not stated
    'screw_mu': .15,                         # Shigley Table 8-5, steel on steel dry, low end 0.15-0.25
    'screw_preload_scatter': .25,            # Unbrako: induced load may vary +/-25% at a given torque
    'screw_interfaces': 2,                   # screw tip on key, and hub bore on the opposite side of the shaft
    'hardware_n_min': 1.2,
    'reliability_factor': .814,
    'shaft_stock_length_in': 24.0, 'shaft_stock_price_USD': 112.69,  # full price of shortest sufficient stock (Req. 4)
    'ring_pack_price_USD': 10.26, 'ring_pack_quantity': 5,
    'pin_pack_price_USD': 4.69, 'pin_pack_quantity': 1,
    'screw_pack_price_USD': 4.81, 'screw_pack_quantity': 25,
    'key_stock_length_in': 36, 'key_stock_price_USD': 28.32,
    'coating_allowance_USD': 100.0,
}

def reactions(center_model=False):
    B = I['bearing_width_mm']
    yl,yu = (0,300) if center_model else (B/2,300-B/2)
    fx=I['chain_N']*cos(radians(I['chain_angle_deg']))
    fz=-I['chain_N']*sin(radians(I['chain_angle_deg']))
    ux=fx*(yl-I['chain_y_mm'])/(yu-yl)
    uz=(fz*(yl-I['chain_y_mm'])+I['drag_N']*(yl-I['COP_y_mm']))/(yu-yl)
    return dict(Fx=fx,Fz=fz,yL=yl,yU=yu,span=yu-yl,
                RUx=ux,RUz=uz,RLx=-fx-ux,RLz=-fz-I['drag_N']-uz)

R=reactions()
def bending(y):
    """Resultant bending ABOVE the hub top, obtained from loads below a cut.
    Returns moments about x and z (signs per sum(r cross F))."""
    mx=(I['COP_y_mm']-y)*I['drag_N']; mz=0.0
    if y>=I['chain_y_mm']:
        mx+=(I['chain_y_mm']-y)*R['Fz']
        mz-= (I['chain_y_mm']-y)*R['Fx']
    if y>=R['yL']:
        mx+=(R['yL']-y)*R['RLz']; mz-=(R['yL']-y)*R['RLx']
    if y>=R['yU']:
        mx+=(R['yU']-y)*R['RUz']; mz-=(R['yU']-y)*R['RUx']
    return dict(Mx=mx,Mz=mz,M=hypot(mx,mz))

Wshaft=I['rho_kg_m3']*pi*(I['D_nom_mm']/1000)**2/4*(I['length_mm']/1000)*I['g_m_s2']
N=I['rotor_N']+I['sprocket_N']+Wshaft

def ka(Sut, ground=False):
    # Shigley 11th ed., Table 6-2 (Sut in MPa): ground a = 1.38, b = -0.067; machined a = 3.04, b = -0.217.
    # (The 10th-edition values 1.58/-0.085 and 4.51/-0.265 were used before 12 Nov 2026.)
    return (1.38*Sut**-.067) if ground else (3.04*Sut**-.217)
def kb(d):
    return 1.24*d**-.107 if d<=51 else 1.51*d**-.157
def q_bending(Sut,r_mm):
    ksi=Sut/6.894757293
    sqrta=.246-.00308*ksi+.0000151*ksi**2-2.67e-8*ksi**3
    return 1/(1+sqrta/sqrt(r_mm/INCH))
Se=.5*I['Sut_MPa']*ka(I['Sut_MPa'])*kb(I['D_nom_mm'])*I['reliability_factor']
q=q_bending(I['Sut_MPa'],I['groove_r_min_mm'])

def stress(name,d,M,T,Kt,Kts,Kf=None,At_b=1,At_t=1,mean_extra=0,ground=False,Kfs=None):
    if Kf is None: Kf=Kt
    if Kfs is None: Kfs=Kts
    sb=32*M/(pi*d**3*At_b)
    st=16*T/(pi*d**3*At_t)
    sn=4*N/(pi*d*d)
    # Colocated positive mean normal stress is a conservative bound.
    sa=Kf*sb
    sm=Kt*sn+mean_extra
    tm=Kts*st
    vm=sqrt((Kt*sb+sm)**2+3*tm**2)
    # Shigley Eq. (7-15) uses Kf/Kfs for peak bending/torsion.
    # The published equation neglects axial force. Retain the existing Kt*sn
    # stress in both checks, explicitly, as a conservative extension.
    vm_shigley=sqrt((Kf*sb+sm)**2+3*(Kfs*st)**2)
    seqm=sqrt(sm**2+3*tm**2)
    se=.5*I['Sut_MPa']*ka(I['Sut_MPa'],ground)*kb(I['D_nom_mm'])*I['reliability_factor']
    nf=1/(sa/se+seqm/I['Sut_MPa']) if sa+seqm else float('inf')
    return dict(name=name,d_mm=d,M_Nm=M/1000,T_Nm=T/1000,Kt=Kt,Kts=Kts,Kf=Kf,Kfs=Kfs,
                nominal_bending_MPa=sb,alternating_MPa=sa,mean_eq_MPa=seqm,
                peak_von_Mises_MPa=vm,Se_MPa=se,ny=I['Sy_MPa']/vm,nf=nf,
                minimum_Sy_for_n3_MPa=3*vm,
                shigley_max_equivalent_MPa=vm_shigley,ny_shigley=I['Sy_MPa']/vm_shigley,
                minimum_Sy_shigley_for_n3_MPa=3*vm_shigley,
                elastic_peak_von_Mises_MPa=vm,ny_elastic=I['Sy_MPa']/vm,
                minimum_Sy_elastic_for_n3_MPa=3*vm,
                passes_yield_shigley=I['Sy_MPa']/vm_shigley>=3,
                passes_yield_elastic=I['Sy_MPa']/vm>=3)

def peterson_keyseat(r_over_d):
    """End-milled keyseat, Pilkey (Peterson's SCF, 2nd ed., Sec. 5.2) curve fits, 0.005 <= r/d <= 0.07.
    Bending Kt (Fessler et al. 1969), torsion Kts (Okubo et al. 1968)."""
    assert .005<=r_over_d<=.07
    u=.1/r_over_d
    return 1.426+.1643*u-.0019*u*u, 1.953+.1434*u-.0021*u*u
keyseat_r_over_d=I['keyseat_r_mm']/I['D_min_mm']
keyseat_Kt_exact,keyseat_Kts_exact=peterson_keyseat(keyseat_r_over_d)
I['keyway_Kt_b']=round(keyseat_Kt_exact,2); I['keyway_Kts']=round(keyseat_Kts_exact,2)

keyF=2*I['T_Nmm']/I['D_min_mm']
# Key bearing height: the smaller of the hub and shaft contact heights, less the key chamfer.
# Shaft side: side-wall depth (min 3/16 in) less chamfer; hub side: key height above the deepest keyseat, less chamfer.
keyEng=min(I['key_h_min_mm']-(I['keyseat_depth_side_mm']+I['keyseat_depth_plus_mm']),I['keyseat_depth_side_mm'])-I['key_chamfer_mm']
keyLmin=I['key_length_mm']-I['key_length_tolerance_mm']
slot_overall_max=I['key_slot_cc_mm']+I['key_slot_cc_plus_mm']+I['keyseat_width_mm']+I['keyseat_width_plus_mm']
slot_overall_nom=I['key_slot_cc_mm']+I['keyseat_width_mm']
keyTau=keyF/(I['key_b_min_mm']*keyLmin)
keyBearing=keyF/(keyEng*keyLmin)
keyY=I['key_slot_center_y_mm']+slot_overall_max/2  # upper end of the longest, widest slot
keyM=bending(keyY)['M']
hole=I['pin_shaft_hole_mm'][1]   # largest shaft hole (F7 upper limit)
ratio=hole/I['D_min_mm']
def lerp(x,xs,ys):
    for a,b,c,d in zip(xs,xs[1:],ys,ys[1:]):
        if a<=x<=b: return c+(d-c)*(x-a)/(b-a)
    raise ValueError('outside table')
Ab=lerp(ratio,[.15,.175,.2],[.76,.72,.68])
Ktb=lerp(ratio,[.15,.175,.2],[2.15,2.10,2.07])
At=lerp(ratio,[.15,.175,.2],[.87,.85,.83])
Ktt=lerp(ratio,[.15,.175,.2],[1.62,1.60,1.58])
pinM=I['drag_N']*(500+I['pin_y_mm']+hole/2)
sections=[
    stress('Lower retaining-ring groove',I['groove_D_min_mm'],bending(I['lower_groove_y_mm'])['M'],0,I['groove_Kt'],0,1+q*(I['groove_Kt']-1)),
    stress('Keyseat upper end (envelope)',I['D_min_mm'],keyM,I['T_Nmm'],I['keyway_Kt_b'],I['keyway_Kts']),
    stress('Transverse pin hole (envelope)',I['D_min_mm'],pinM,I['T_Nmm'],Ktb,Ktt,At_b=Ab,At_t=At),
    stress('Plain lower bearing section',I['D_min_mm'],bending(R['yL'])['M'],0,1,1,ground=True),
    stress('Upper retaining-ring groove',I['groove_D_min_mm'],0,0,I['groove_Kt'],0,1+q*(I['groove_Kt']-1)),
]

# Cost screen of simple fractional cut lengths; keep slot clearance and key center.
key_trials=[]
for length_in in [.125,.1875,.25,.5]:
    length_mm=length_in*INCH
    trial_slot_mm=length_mm+I['key_slot_cc_plus_mm']+I['keyseat_width_mm']+I['keyseat_width_plus_mm']
    moment=bending(-36+trial_slot_mm/2)['M']
    trial=stress('Key length trial',I['D_min_mm'],moment,I['T_Nmm'],I['keyway_Kt_b'],I['keyway_Kts'])
    key_trials.append(dict(length_in=length_in,shaft_nf=trial['nf'],shaft_ny=trial['ny'],shaft_ny_shigley=trial['ny_shigley'],
                           allocated_key_cost_USD=28.32/36*length_in))

# Pin: two shear planes, torque and axial load in orthogonal directions.
pinR=hypot(I['T_Nmm']/I['D_min_mm'],I['rotor_N']/2)
pinRating=I['pin_double_shear_lbf']*4.448221615
pinLoad=2*pinR                     # total load across the two shear planes
pinClear=[I['pin_shaft_hole_mm'][0]-I['pin_d_max_mm'],I['pin_shaft_hole_mm'][1]-.2501*INCH]
pinInterf=[.2501*INCH-I['pin_hub_hole_in'][1]*INCH,I['pin_d_max_mm']-I['pin_hub_hole_in'][0]*INCH]

# Set screw: smallest clamp that holds the sprocket axially with n = 1.2, then the torque that guarantees it
# at the low end of the +/-25% preload scatter, then the screw stresses at the high end.
screwFreq=I['hardware_n_min']*I['sprocket_N']/(I['screw_interfaces']*I['screw_mu'])
screwTreq=I['screw_K']*screwFreq*I['screw_d_mm']                      # N mm, Shigley Eq. (8-27)
screwT=ceil(screwTreq/(1-I['screw_preload_scatter'])/10)*10              # specified torque, rounded up to 0.01 N m
Fmin=screwT/(I['screw_K']*I['screw_d_mm'])*(1-I['screw_preload_scatter'])
Fmax=screwT/(I['screw_K']*I['screw_d_mm'])*(1+I['screw_preload_scatter'])
dr=sqrt(4*I['screw_Ar_mm2']/pi); af=I['screw_socket_AF_mm']; pt=I['screw_pitch_mm']
# Section through the hex socket (full F and T): root circle less the hexagon.
Ahex=sqrt(3)/2*af**2; Jhex=5*sqrt(3)/8*(af/sqrt(3))**4
Aroot=I['screw_Ar_mm2']-Ahex
Jroot=pi*dr**4/32-Jhex
sc=Fmax/Aroot
tc=screwT*dr/2/Jroot
screwVM=hypot(sc,sqrt(3)*tc)
# Thread root, Shigley Sec. 8-2 (Eq. 8-12 set): first thread carries 0.38F and 0.38T, n_t = 1.
sx=6*.38*Fmax/(pi*dr*pt); sy=-4*Fmax/(pi*dr**2); tyz=16*screwT/(pi*dr**3); tzx=4*.38*screwT/(pi*dr**2*pt)
threadVM=sqrt(.5*((sx-sy)**2+sy**2+sx**2)+3*(tyz**2+tzx**2))
tipArea=pi*I['screw_flat_tip_min_mm']**2/4

ringCapacity=4950*4.448221615
edge=303.5-(300.1+I['groove_width_max_mm'])
# Capacity based on minimal groove depth and full allowable root radius.
depth_min=(I['D_min_mm']-I['groove_D_max_mm'])/2
flat_contact=max(0,depth_min-I['groove_r_max_mm'])
grooveArea=pi*I['groove_D_min_mm']*flat_contact
edgeShearArea=pi*I['groove_D_min_mm']*edge
edgeBendSigma=6*N*depth_min/(pi*I['groove_D_min_mm']*edge**2)

bom=[
 dict(item='1566 precision rotary shaft, 1-1/2 x 24 in',part='1346K534',quantity='1 (cut to 554 mm)',cost=I['shaft_stock_price_USD']),
 dict(item='18-8 single-turn spiral rings',part='93576A210',quantity='2',cost=2*10.26/5),
 dict(item='416 dowel pin, 1/4 x 3 in',part='98380A556',quantity='1',cost=4.69),
 dict(item='18-8 flat-tip set screw, 1/4-20 x 1/4 in',part='94355A533',quantity='1',cost=4.81/25),
 dict(item='18-8 key stock, 3/8 square; cut 1/2 in',part='92530A319',quantity='0.50 in of 36 in',cost=28.32/36*.50),
 dict(item='Required coating/inspection allowance',part='Assignment item 5',quantity='1',cost=100.0),
]

O=dict(inputs=I,reactions_N=R,
       shaft_weight_N=Wshaft,total_thrust_N=N,
       groove=dict(t_max_mm=(I['D_nom_mm']-I['groove_D_min_mm'])/2,
                   r_over_t=I['groove_r_min_mm']/((I['D_nom_mm']-I['groove_D_min_mm'])/2),
                   a_over_t=I['groove_width_min_mm']/((I['D_nom_mm']-I['groove_D_min_mm'])/2),
                   q=q,Kf=1+q*(I['groove_Kt']-1),ka=ka(I['Sut_MPa']),kb=kb(I['D_nom_mm']),Se_MPa=Se),
       sections=sections,
       yield_check_conventions=dict(
           primary='Shigley Eq. (7-15): Kf/Kfs bending/torsion; retained Kt axial stress explicitly added.',
           supplemental='Theoretical local elastic check: Kt/Kts. This is an added criterion, not a PDF requirement.',
           legacy_fields='ny, peak_von_Mises_MPa and minimum_Sy_for_n3_MPa retain their original Kt elastic meanings.',
           minimum_Sy_shigley_MPa=max(s['minimum_Sy_shigley_for_n3_MPa'] for s in sections),
           minimum_Sy_elastic_MPa=max(s['minimum_Sy_elastic_for_n3_MPa'] for s in sections)),
       key_length_trials=key_trials,
       key=dict(F_N=keyF,tau_MPa=keyTau,bearing_MPa=keyBearing,n_shear=I['key_Sy_MPa']/(sqrt(3)*keyTau),n_bearing=I['key_Sy_MPa']/keyBearing,engagement_mm=keyEng),
       pin=dict(R_per_plane_N=pinR,double_shear_load_N=pinLoad,rating_N=pinRating,n_rating=pinRating/pinLoad,shaft_clearance_mm=pinClear,hub_interference_mm=pinInterf),
       screw=dict(F_req_N=screwFreq,T_req_Nmm=screwTreq,T_spec_Nmm=screwT,Fmin_N=Fmin,Fmax_N=Fmax,axial_hold_N=I['screw_interfaces']*I['screw_mu']*Fmin,n_slip=I['screw_interfaces']*I['screw_mu']*Fmin/I['sprocket_N'],dr_mm=dr,Aroot_mm2=Aroot,Jroot_mm4=Jroot,compression_MPa=sc,torsion_MPa=tc,vm_MPa=screwVM,n_y=I['screw_Sy_MPa']/screwVM,thread=dict(sx=sx,sy=sy,tyz=tyz,tzx=tzx,vm=threadVM),n_thread=I['screw_Sy_MPa']/threadVM,tip_MPa=Fmax/tipArea,n_tip=I['screw_Sy_MPa']/(Fmax/tipArea)),
       ring=dict(catalog_thrust_N=ringCapacity,capacity_ratio=ringCapacity/N,edge_margin_mm=edge,depth_min_mm=depth_min,flat_contact_mm=flat_contact,n_groove_bearing=I['Sy_MPa']/(N/grooveArea),n_edge_shear=I['Sy_MPa']/sqrt(3)/(N/edgeShearArea),n_edge_bending=I['Sy_MPa']/edgeBendSigma),
       bom=bom,total_cost_USD=sum(row['cost'] for row in bom))

assert abs(R['RUx']+R['RLx']+R['Fx'])<1e-9
assert abs(R['RUz']+R['RLz']+R['Fz']+I['drag_N'])<1e-9
assert abs(R['RUx']*R['span']-R['Fx']*(R['yL']+50))<1e-8
assert bending(301)['M']<1e-7
assert 1.452*INCH<=I['groove_D_min_mm']<=I['groove_D_max_mm']<=1.460*INCH+1e-9
assert I['groove_r_max_mm']<=.01*INCH
assert I['key_chamfer_mm']>I['keyseat_r_mm']
assert I['key_slot_cc_mm']>=I['key_length_mm']  # min straight length (H14 lower limit) >= max key (h14 upper limit)
for s in sections:
    assert s['ny_shigley']>=3,(s['name'],'Shigley yield',s['ny_shigley'])
    assert s['shigley_max_equivalent_MPa']<=s['elastic_peak_von_Mises_MPa']+1e-10
    if s['Kf']==s['Kt'] and s['Kfs']==s['Kts']:
        assert abs(s['ny_shigley']-s['ny_elastic'])<1e-10
    assert s['nf']>=1.2,(s['name'],'fatigue',s['nf'])
assert min(O['screw']['n_y'],O['screw']['n_slip'],O['pin']['n_rating'])>=1.2-1e-9
assert min(O['key']['n_shear'],O['key']['n_bearing'],O['screw']['n_thread'],
           O['screw']['n_tip'],O['ring']['capacity_ratio'],
           O['ring']['n_groove_bearing'],O['ring']['n_edge_shear'],O['ring']['n_edge_bending'])>=1.2

(DATA/'results.json').write_text(json.dumps(O,indent=2)+'\n')
for filename,rows in [('shaft_sections.csv',sections),('bom.csv',bom)]:
    with (DATA/filename).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print(json.dumps(O,indent=2))
