# dp1_fe_check.py -- 3-D frame finite-element cross-check of dp1_model.py (12-DOF beam elements + two truss diagonals).
# Run:  python3 dp1_fe_check.py   (requires numpy). Use it to confirm the hand superposition for a new geometry.
#!/usr/bin/env python3
"""
ME3180 DP1 (Fall 2026) - Microhydro rotor support structure.
Independent analysis: 3D linear frame FE (numpy) + hand statics + hand superposition.

Units inside the script: N, mm, MPa (N/mm^2), N*mm.  Reported moments are converted to N*m.
Frame (Figure 2): origin at pin O on the beam neutral axis, +x toward the fixed structure,
+y up, +z toward the viewer of the Figure-1 side view ("Front").

Run:  python3 -I dp1_fe.py [--json]
"""
import json
import math
import sys

import numpy as np

# ----------------------------------------------------------------------------- constants
E = 193000.0        # MPa, 304 stainless
G = 75000.0         # MPa
SY = 215.0          # MPa, 304 yield
SY_AL = 35.0 * 6.894757   # MPa, 6061-ish aluminum bracket, 35 ksi
RHO = 8000e-9       # kg/mm^3
GRAV = 9.81
FS_REQ = 2.0

# beam: 4" x 4" x 1/4" wall 304 square tube (McMaster 89825K48), sharp corners
H = 101.6
T_WALL = 6.35
A_B = H * H - (H - 2 * T_WALL) ** 2
I_B = (H ** 4 - (H - 2 * T_WALL) ** 4) / 12.0          # Iy = Iz
B_MID = H - T_WALL                                       # midline side
A_MID = B_MID ** 2                                       # enclosed midline area
J_B = B_MID ** 3 * T_WALL                                # Bredt (thin closed section)
C_B = H / 2.0
W_BEAM = RHO * A_B * GRAV                                # N/mm self weight
D_HOLE = 9.525
X_LEFT = -1300.0
X_RIGHT = 50.0                                           # Figure 2 bottom view: beam ends 50 mm past pin O (>= 2d edge rule)

# diagonals: 2" x 1/4" 304 flat, front/rear faces of the beam
B_D = 50.8
T_D = 6.35
A_D = B_D * T_D
I_D_WEAK = B_D * T_D ** 3 / 12.0
Z_D = H / 2 + T_D / 2            # 53.975 mm  plate mid-thickness
B_PT = np.array([0.0, 500.0, 0.0])
W_D_PER_MM = RHO * A_D * GRAV    # N/mm of diagonal

# brackets at O, 1/2" aluminum on front/rear faces
T_BR = 12.7
Z_BR = H / 2 + T_BR / 2          # 57.15 mm
Z_WALL = H / 2 - T_WALL / 2      # 47.625 mm, tube wall mid-thickness

# pins (all three) 3/8"
D_PIN = 9.525
A_PIN = math.pi * D_PIN ** 2 / 4
Z_PIN = math.pi * D_PIN ** 3 / 32

# loads / geometry
X_ROTOR = -1200.0
Y_CHAIN = -(H / 2 + 50.0)
Y_CG = -(H / 2 + 350.0)
Y_COP = -(H / 2 + 500.0)
W_ROTOR = 150.0
W_GEN = 120.0
F_DRAG = 560.0
R1 = 9.554 * 25.4 / 2.0          # rotor sprocket pitch radius, mm
R2 = 3.038 * 25.4 / 2.0          # generator sprocket pitch radius, mm

# water
RHO_W = 1000.0
V_W = 2.5
A_SWEPT = 0.5 * 0.5
ETA_H = 0.30
RPM = 285.0
ETA_E = 0.82


# ----------------------------------------------------------------------------- power
def power():
    p_fluid = 0.5 * RHO_W * A_SWEPT * V_W ** 3
    p_mech = ETA_H * p_fluid
    p_elec = ETA_E * p_mech
    omega = RPM * 2 * math.pi / 60.0
    torque_rotor = p_mech / omega                # N*m
    t_chain = torque_rotor / (R1 / 1000.0)       # N (slack side = 0)
    torque_gen = t_chain * R2 / 1000.0
    rpm_gen = RPM * R1 / R2
    return dict(P_fluid_W=p_fluid, P_mech_W=p_mech, P_elec_W=p_elec,
                omega_rad_s=omega, T_rotor_Nm=torque_rotor, chain_tension_N=t_chain,
                T_gen_Nm=torque_gen, rpm_gen=rpm_gen)


PW = power()
T_CHAIN = PW["chain_tension_N"]
T_WATER = PW["T_rotor_Nm"] * 1000.0   # N*mm, +y on the rotor


# ----------------------------------------------------------------------------- loads
def make_loads(a, x_gen, chain_mode="exact"):
    """Return (point_loads, info).  point_loads = list of dict(name, x, F(3), M(3)) applied
    at the beam neutral axis (x,0,0): statically equivalent loads from the rotor station and
    the generator station, plus diagonal weight at A.  Beam self weight handled separately."""
    C = x_gen - X_ROTOR                         # sprocket center distance
    if chain_mode == "exact":
        sphi = (R1 - R2) / C
        cphi = math.sqrt(1 - sphi ** 2)
        e_t = np.array([cphi, 0.0, sphi])        # tight-side chain direction (rotor -> gen)
        P1 = np.array([X_ROTOR + R1 * sphi, Y_CHAIN, -R1 * cphi])   # tangent pt on rotor sprocket
        P2 = np.array([x_gen + R2 * sphi, Y_CHAIN, -R2 * cphi])     # tangent pt on gen sprocket
    else:  # x-only approximation
        sphi, cphi = 0.0, 1.0
        e_t = np.array([1.0, 0.0, 0.0])
        P1 = np.array([X_ROTOR, Y_CHAIN, -R1])
        P2 = np.array([x_gen, Y_CHAIN, -R2])
    F_c1 = T_CHAIN * e_t          # chain on rotor sprocket (pulls toward generator)
    F_c2 = -T_CHAIN * e_t         # chain on generator sprocket

    # rotor station: rotating assembly (rotor+shaft+sprocket) in equilibrium under water torque,
    # drag, weight, chain, bearing reactions.  Bearings transmit no moment about y.
    axis1 = np.array([X_ROTOR, 0.0, 0.0])
    r_cop = np.array([0.0, Y_COP, 0.0])
    r_cg = np.array([0.0, Y_CG, 0.0])
    F_drag = np.array([0.0, 0.0, F_DRAG])
    F_wr = np.array([0.0, -W_ROTOR, 0.0])
    M1 = np.cross(r_cop, F_drag) + np.cross(r_cg, F_wr) + np.cross(P1 - axis1, F_c1)
    M1 = M1 + np.array([0.0, T_WATER, 0.0])   # water torque cancels chain y-moment on the shaft
    y_residual = M1[1]                        # should be ~0 in exact and x-only
    M1[1] = 0.0                               # bearings pass no y-moment (enforce)
    F1 = F_drag + F_wr + F_c1

    # generator station: housing bolted to beam; stator reaction torque makes the chain force
    # at P2 act on the beam with its full moment about the generator axis point.
    axis2 = np.array([x_gen, 0.0, 0.0])
    F_wg = np.array([0.0, -W_GEN, 0.0])
    M2 = np.cross(P2 - axis2, F_c2)           # includes +T*R2 about y (stator reaction)
    F2 = F_c2 + F_wg

    L_d = math.hypot(a, 500.0)
    L_cut = L_d + 4 * D_HOLE
    W_d = W_D_PER_MM * L_cut                  # per diagonal
    loads = [
        dict(name="rotor station (equiv. at beam axis)", x=X_ROTOR, F=F1, M=M1),
        dict(name="generator station (equiv. at beam axis)", x=x_gen, F=F2, M=M2),
        dict(name="diagonal self-weight, half of each diagonal at A", x=-a,
             F=np.array([0.0, -W_d, 0.0]), M=np.zeros(3)),
    ]
    info = dict(C=C, sphi=sphi, cphi=cphi, phi_deg=math.degrees(math.asin(sphi)), e_t=e_t,
                P1=P1, P2=P2, F_c1=F_c1, F_c2=F_c2, M1=M1, M2=M2, F1=F1, F2=F2,
                y_residual=y_residual, L_d=L_d, L_cut=L_cut, W_d=W_d,
                theta=math.atan2(500.0, a))
    return loads, info


def beam_weight_total():
    L = X_RIGHT - X_LEFT
    return W_BEAM * L, 0.5 * (X_LEFT + X_RIGHT)


# ----------------------------------------------------------------------------- hand statics
def hand_statics(a, x_gen, chain_mode="exact"):
    loads, info = make_loads(a, x_gen, chain_mode)
    th = info["theta"]
    c = np.array([math.cos(th), math.sin(th), 0.0])   # A -> B unit vector (bar axis)
    Wb, xc = beam_weight_total()

    def wrench(point, F, M=None):
        M = np.zeros(3) if M is None else M
        return np.concatenate([F, np.cross(point, F) + M])

    # applied resultant about O
    R_app = np.zeros(6)
    for ld in loads:
        R_app += wrench(np.array([ld["x"], 0.0, 0.0]), ld["F"], ld["M"])
    R_app += wrench(np.array([xc, 0.0, 0.0]), np.array([0.0, -Wb, 0.0]))

    # unknown columns: F_f, F_r, Ox_f, Ox_r, Oy_half(both sides), Oz
    cols = [
        wrench(np.array([-a, 0.0, Z_D]), c),
        wrench(np.array([-a, 0.0, -Z_D]), c),
        wrench(np.array([0.0, 0.0, Z_BR]), np.array([1.0, 0.0, 0.0])),
        wrench(np.array([0.0, 0.0, -Z_BR]), np.array([1.0, 0.0, 0.0])),
        wrench(np.array([0.0, 0.0, Z_BR]), np.array([0.0, 1.0, 0.0]))
        + wrench(np.array([0.0, 0.0, -Z_BR]), np.array([0.0, 1.0, 0.0])),
        wrench(np.zeros(3), np.array([0.0, 0.0, 1.0])),
    ]
    Amat = np.column_stack(cols)
    x = np.linalg.solve(Amat, -R_app)
    F_f, F_r, Ox_f, Ox_r, Oy_h, Oz = x
    res = dict(F_f=F_f, F_r=F_r, Ox_f=Ox_f, Ox_r=Ox_r, Oy_f=Oy_h, Oy_r=Oy_h, Oz=Oz,
               Ox=Ox_f + Ox_r, Oy=2 * Oy_h, My_O=Z_BR * (Ox_f - Ox_r), Mx_O=0.0,
               R_app=R_app, c=c, loads=loads, info=info, Wb=Wb, xc=xc)
    return res


# ----------------------------------------------------------------------------- hand internal diagrams + superposition
def hand_deflection(a, x_gen, chain_mode="exact", dx=0.5):
    st = hand_statics(a, x_gen, chain_mode)
    info, loads, c = st["info"], st["loads"], st["c"]
    th = info["theta"]
    F_f, F_r = st["F_f"], st["F_r"]
    L_d = info["L_d"]

    # all point wrenches on the beam axis, including diagonal forces (with z-offset moments) and O reactions
    pts = []
    for ld in loads:
        pts.append((ld["x"], ld["F"].copy(), ld["M"].copy()))
    for Fi, zs in ((F_f, Z_D), (F_r, -Z_D)):
        Fv = Fi * c
        pts.append((-a, Fv, np.cross(np.array([0.0, 0.0, zs]), Fv)))
    R_O_F = np.array([st["Ox"], st["Oy"], st["Oz"]])
    R_O_M = np.array([0.0, st["My_O"], 0.0])
    pts.append((0.0, R_O_F, R_O_M))

    xs = np.arange(X_LEFT, X_RIGHT + dx / 2, dx)
    n = len(xs)
    N = np.zeros(n); Vy = np.zeros(n); Vz = np.zeros(n)
    Tx = np.zeros(n); My = np.zeros(n); Mz = np.zeros(n)
    for (xi, F, M) in pts:
        left = xs > xi + 1e-9     # section to the right of the load -> load is on the left part
        N[left] -= F[0]
        Vy[left] -= F[1]
        Vz[left] -= F[2]
        Tx[left] -= M[0]
        My[left] -= M[1] + (xs[left] - xi) * F[2]
        Mz[left] -= M[2] + (xi - xs[left]) * F[1]
    # distributed self weight (downward w per mm from X_LEFT to x)
    s = xs - X_LEFT
    Vy -= -W_BEAM * s              # internal Vy = -sum(Fy on left part) = +w s
    Mz += -W_BEAM * s ** 2 / 2.0   # internal Mz = -int (x'-x)(-w) dx' = -w s^2/2 (hogging)

    def cumtrapz(y):
        out = np.zeros_like(y)
        out[1:] = np.cumsum(0.5 * (y[1:] + y[:-1]) * np.diff(xs))
        return out

    iO = int(np.argmin(np.abs(xs - 0.0)))
    iA = int(np.argmin(np.abs(xs + a)))
    iR = int(np.argmin(np.abs(xs - X_ROTOR)))

    # axial
    u_p = cumtrapz(N / (E * A_B))
    u = u_p - u_p[iO]
    u_xA = u[iA]
    # xy bending: v'' = Mz/EIz ; v(0)=0 ; v(-a) = u_y(A) from bar average stretch
    e_avg = (F_f + F_r) * L_d / (2 * E * A_D)
    u_yA = -(e_avg + u_xA * math.cos(th)) / math.sin(th)
    vp1 = cumtrapz(Mz / (E * I_B))
    vp = cumtrapz(vp1)
    # v = vp + c0 + c1 x
    M2 = np.array([[1.0, 0.0], [1.0, -a]])
    rhs = np.array([-vp[iO], u_yA - vp[iA]])
    c0, c1 = np.linalg.solve(M2, rhs)
    v = vp + c0 + c1 * xs
    v1 = vp1 + c1
    # xz bending: w'' = -My/EIy ; w(0)=0 ; w'(0)=0
    wp1 = cumtrapz(-My / (E * I_B))
    wp = cumtrapz(wp1)
    d1 = -wp1[iO]
    d0 = -wp[iO] - d1 * 0.0
    w = wp + d0 + d1 * xs
    w1 = wp1 + d1
    th_y = -w1
    # torsion: phi' = T/GJ ; phi(-a) = theta_x(A) from bar differential + coupling with theta_y(A)
    th_yA = th_y[iA]
    phi_bar_direct = (F_f - F_r) * L_d / (E * A_D * 2 * Z_D * math.sin(th))
    phi_coupling = th_yA * math.cos(th) / math.sin(th)
    th_xA = phi_bar_direct + phi_coupling
    php = cumtrapz(Tx / (G * J_B))
    phi = php + (th_xA - php[iA])

    th_z = v1
    off = -Y_CG   # 400.8 mm below the axis -> r = (0, Y_CG, 0)
    u_cg = np.array([u[iR] + (-Y_CG) * th_z[iR] * 1.0, v[iR], w[iR] - (-Y_CG) * phi[iR] * 1.0])
    # NOTE: delta = u + theta x r, r=(0,Y_CG,0): (-theta_z*Y_CG, 0, theta_x*Y_CG)
    u_cg = np.array([u[iR] - th_z[iR] * Y_CG, v[iR], w[iR] + phi[iR] * Y_CG])

    v_rigid = u_yA * (X_ROTOR / (-a))
    comps = dict(
        xy_bending_elastic_y=v[iR] - v_rigid,
        xy_rigid_rotation_z_from_diag_strain_y=v_rigid,
        xz_bending_z=w[iR],
        twist_rotor_to_A_z=(phi[iR] - phi[iA]) * Y_CG,
        rigid_rotation_x_from_diag_strain_z=th_xA * Y_CG,
        rigid_rotation_x_direct_bar_strain_z=phi_bar_direct * Y_CG,
        rigid_rotation_x_coupling_theta_y_z=phi_coupling * Y_CG,
        x_from_axial_and_rot_z=u_cg[0],
    )
    out = dict(statics=st, xs=xs, N=N, Vy=Vy, Vz=Vz, Tx=Tx, My=My, Mz=Mz,
               u=u, v=v, w=w, phi=phi, th_y=th_y, th_z=th_z,
               u_xA=u_xA, u_yA=u_yA, th_xA=th_xA, th_yA=th_yA,
               u_cg=u_cg, mag=float(np.linalg.norm(u_cg)), comps=comps,
               dL_f=F_f * L_d / (E * A_D), dL_r=F_r * L_d / (E * A_D))
    return out


# ----------------------------------------------------------------------------- FE
def beam_k(L, EA, EIy, EIz, GJ):
    k = np.zeros((12, 12))
    a_ = EA / L
    k[0, 0] = k[6, 6] = a_; k[0, 6] = k[6, 0] = -a_
    tq = GJ / L
    k[3, 3] = k[9, 9] = tq; k[3, 9] = k[9, 3] = -tq
    # bending in xy (v, theta_z) with Iz
    s1, s2, s3, s4 = 12 * EIz / L ** 3, 6 * EIz / L ** 2, 4 * EIz / L, 2 * EIz / L
    k[1, 1] = k[7, 7] = s1; k[1, 7] = k[7, 1] = -s1
    k[1, 5] = k[5, 1] = k[1, 11] = k[11, 1] = s2
    k[7, 5] = k[5, 7] = k[7, 11] = k[11, 7] = -s2
    k[5, 5] = k[11, 11] = s3; k[5, 11] = k[11, 5] = s4
    # bending in xz (w, theta_y) with Iy
    r1, r2, r3, r4 = 12 * EIy / L ** 3, 6 * EIy / L ** 2, 4 * EIy / L, 2 * EIy / L
    k[2, 2] = k[8, 8] = r1; k[2, 8] = k[8, 2] = -r1
    k[2, 4] = k[4, 2] = k[2, 10] = k[10, 2] = -r2
    k[8, 4] = k[4, 8] = k[8, 10] = k[10, 8] = r2
    k[4, 4] = k[10, 10] = r3; k[4, 10] = k[10, 4] = r4
    return k


def skew(r):
    return np.array([[0, -r[2], r[1]], [r[2], 0, -r[0]], [-r[1], r[0], 0]], dtype=float)


def solve_fe(a, x_gen, chain_mode="exact", n_el=40):
    loads, info = make_loads(a, x_gen, chain_mode)
    key = [X_LEFT, X_ROTOR, -float(a), float(x_gen), 0.0, X_RIGHT]
    grid = [g for g in np.linspace(X_LEFT, X_RIGHT, n_el + 1)
            if min(abs(g - k) for k in key) > 5.0]
    xs = np.array(sorted(set([float(k) for k in key] + [float(g) for g in grid])))
    n = len(xs)
    ndof = 6 * n
    K = np.zeros((ndof, ndof))
    F = np.zeros(ndof)
    Feq = np.zeros(ndof)   # equivalent nodal loads of distributed weight (for end-force recovery)
    ks = []
    for e in range(n - 1):
        L = xs[e + 1] - xs[e]
        k = beam_k(L, E * A_B, E * I_B, E * I_B, G * J_B)
        ks.append(k)
        d = list(range(6 * e, 6 * e + 12))
        K[np.ix_(d, d)] += k
        q = -W_BEAM
        fe = np.array([0, q * L / 2, 0, 0, 0, q * L ** 2 / 12, 0, q * L / 2, 0, 0, 0, -q * L ** 2 / 12])
        Feq[d] += fe
    F += Feq
    idx = {x: i for i, x in enumerate(xs)}
    iA = int(np.argmin(np.abs(xs + a)))
    iO = int(np.argmin(np.abs(xs)))
    iR = int(np.argmin(np.abs(xs - X_ROTOR)))
    for ld in loads:
        i = int(np.argmin(np.abs(xs - ld["x"])))
        F[6 * i:6 * i + 3] += ld["F"]
        F[6 * i + 3:6 * i + 6] += ld["M"]
    # diagonals: bars from A' = A + (0,0,+-Z_D) (rigid offset, master-slave) to fixed B
    dA = list(range(6 * iA, 6 * iA + 6))
    L_d = info["L_d"]
    th = info["theta"]
    bars = []
    for zs in (+Z_D, -Z_D):
        r = np.array([0.0, 0.0, zs])
        Tr = np.hstack([np.eye(3), -skew(r)])      # u_A' = u_A + theta x r = [I, -skew(r)] [u; theta]
        Ap = np.array([-a, 0.0, zs])
        cvec = (np.array([0.0, 500.0, zs]) - Ap)
        Lb = np.linalg.norm(cvec)
        cvec = cvec / Lb
        kbar = (E * A_D / Lb) * np.outer(cvec, cvec)
        K[np.ix_(dA, dA)] += Tr.T @ kbar @ Tr
        bars.append((Tr, cvec, Lb))
    fixed = [6 * iO + 0, 6 * iO + 1, 6 * iO + 2, 6 * iO + 4]
    free = [i for i in range(ndof) if i not in fixed]
    u = np.zeros(ndof)
    u[free] = np.linalg.solve(K[np.ix_(free, free)], F[free])
    R = K[fixed, :] @ u - F[fixed]       # support forces on the beam: Rx, Ry, Rz, RMy
    Rx, Ry, Rz, RMy = R
    # bar forces (tension +)
    barF = []
    for (Tr, cvec, Lb) in bars:
        dAp = Tr @ u[dA]
        elong = -cvec @ dAp                     # B fixed
        barF.append(E * A_D / Lb * elong)
    F_f, F_r = barF
    # element end forces -> internal resultants (force of right part on left part at the section)
    sec_x, sec = [], []
    for e in range(n - 1):
        d = list(range(6 * e, 6 * e + 12))
        fel = ks[e] @ u[d] - Feq[d]
        sec_x.append(xs[e]); sec.append(-fel[0:6])
        sec_x.append(xs[e + 1]); sec.append(fel[6:12])
    sec_x = np.array(sec_x); sec = np.array(sec)
    uR = u[6 * iR:6 * iR + 6]
    r_cg = np.array([0.0, Y_CG, 0.0])
    u_cg = uR[:3] + np.cross(uR[3:], r_cg)
    uA = u[6 * iA:6 * iA + 6]
    out = dict(xs=xs, u=u, Rx=Rx, Ry=Ry, Rz=Rz, RMy=RMy,
               Ox_f=(Rx + RMy / Z_BR) / 2, Ox_r=(Rx - RMy / Z_BR) / 2, Oy_f=Ry / 2, Oy_r=Ry / 2,
               F_f=F_f, F_r=F_r, sec_x=sec_x, sec=sec, u_cg=u_cg, mag=float(np.linalg.norm(u_cg)),
               uR=uR, uA=uA, info=info, loads=loads, iA=iA, iO=iO, iR=iR)
    # checks: global equilibrium of applied loads vs reactions
    return out


# ----------------------------------------------------------------------------- strength checks
def strength(a, fe, hd):
    info = fe["info"]
    th = info["theta"]
    c = np.array([math.cos(th), math.sin(th), 0.0])
    F_f, F_r = fe["F_f"], fe["F_r"]
    W_d = info["W_d"]
    sec_x, sec = fe["sec_x"], fe["sec"]

    def beam_vm_at(x):
        i = np.where(np.abs(sec_x - x) < 1e-6)[0]
        if len(i) == 0:
            i = [int(np.argmin(np.abs(sec_x - x)))]
        best = None
        for j in i:
            N, Vy, Vz, Tx, My, Mz = sec[j]
            sig = abs(N) / A_B + abs(My) * C_B / I_B + abs(Mz) * C_B / I_B
            tau_t = abs(Tx) / (2 * A_MID * T_WALL)
            tau_v = (abs(Vy) + abs(Vz)) / (2 * H * T_WALL)   # crude, conservative add
            tau = tau_t + tau_v
            vm = math.sqrt(sig ** 2 + 3 * tau ** 2)
            cand = dict(x=float(sec_x[j]), N=float(N), Vy=float(Vy), Vz=float(Vz), Tx_Nm=float(Tx) / 1000,
                        My_Nm=float(My) / 1000, Mz_Nm=float(Mz) / 1000, sigma_axial=abs(N) / A_B,
                        sigma_bend_My=abs(My) * C_B / I_B, sigma_bend_Mz=abs(Mz) * C_B / I_B,
                        tau_torsion=tau_t, tau_shear_est=tau_v, sigma_vm=vm, FS=SY / vm if vm > 0 else 1e9)
            if best is None or vm > best["sigma_vm"]:
                best = cand
        return best

    beam = {}
    for lab, x in (("x=-1200 (rotor)", X_ROTOR), ("x=-a (diagonal pin A)", -a), ("x=0 (pin O)", 0.0)):
        beam[lab] = beam_vm_at(x)
    # global worst
    worst = None
    for x in np.unique(sec_x):
        cand = beam_vm_at(x)
        if worst is None or cand["sigma_vm"] > worst["sigma_vm"]:
            worst = cand
    beam["global worst"] = worst

    # diagonals
    L_d = info["L_d"]
    P_cr = math.pi ** 2 * E * I_D_WEAK / L_d ** 2
    F_comp = min(F_f, F_r, 0.0)
    F_tens = max(F_f, F_r, 0.0)
    A_net = (B_D - D_HOLE) * T_D
    sig_net = F_tens / A_net
    sig_bear_plate = max(abs(F_f), abs(F_r)) / (D_HOLE * T_D)
    e_edge = 2 * D_HOLE
    A_tear = 2 * (e_edge - D_HOLE / 2) * T_D
    tau_tear = max(abs(F_f), abs(F_r)) / A_tear
    diag = dict(
        F_front_N=F_f, F_rear_N=F_r, L_pin_to_pin_mm=L_d, L_cut_mm=info["L_cut"],
        slenderness_L_over_r=L_d / (T_D / math.sqrt(12)),
        P_cr_euler_weak_axis_N=P_cr, FS_buckling=(P_cr / abs(F_comp)) if F_comp < 0 else 1e9,
        sigma_net_tension_MPa=sig_net, FS_net_tension=SY / sig_net if sig_net > 0 else 1e9,
        sigma_bearing_plate_MPa=sig_bear_plate, FS_bearing_plate=SY / sig_bear_plate,
        tau_tearout_MPa=tau_tear, FS_tearout=0.577 * SY / tau_tear,
        tau_pin_double_shear_note="plate is in single shear against the adjacent tube wall; see pins",
        dL_front_mm=hd["dL_f"], dL_rear_mm=hd["dL_r"],
    )

    # pin side forces (vector transmitted through each side)
    O_f = np.array([fe["Ox_f"], fe["Oy_f"], fe["Rz"]])    # z-force assigned to front side (assumption)
    O_r = np.array([fe["Ox_r"], fe["Oy_r"], 0.0])
    A_f = F_f * c + np.array([0.0, -W_d / 2, 0.0])
    A_r = F_r * c + np.array([0.0, -W_d / 2, 0.0])
    B_f = -F_f * c + np.array([0.0, -W_d / 2, 0.0])
    B_r = -F_r * c + np.array([0.0, -W_d / 2, 0.0])

    def pin_checks(name, Ff, Fr, z_plate, t_plate, plate_sy, has_tube):
        # in-plane (shear) components perpendicular to pin axis z
        Vf = math.hypot(Ff[0], Ff[1]); Vr = math.hypot(Fr[0], Fr[1])
        out = dict(front_force_on_beam_or_bracket_N=[float(v) for v in Ff],
                   rear_force_N=[float(v) for v in Fr],
                   front_shear_N=Vf, rear_shear_N=Vr,
                   tau_pin_front_MPa=Vf / A_PIN, tau_pin_rear_MPa=Vr / A_PIN,
                   FS_pin_shear=0.577 * SY / (max(Vf, Vr) / A_PIN),
                   pin_axial_N=float(abs(Ff[2]) + abs(Fr[2])),
                   sigma_bearing_plate_MPa=max(Vf, Vr) / (D_HOLE * t_plate),
                   FS_bearing_plate=plate_sy / (max(Vf, Vr) / (D_HOLE * t_plate)))
        if has_tube:
            # pin as beam: plate loads at +-z_plate, wall reactions at +-Z_WALL (point loads, in-plane vectors)
            zp, zw = z_plate, Z_WALL
            Ff2 = np.array(Ff[:2]); Fr2 = np.array(Fr[:2])
            W_f = -(Ff2 * (zp + zw) + Fr2 * (zw - zp)) / (2 * zw)
            W_r = -(Ff2 + Fr2) - W_f
            Wf, Wr = np.linalg.norm(W_f), np.linalg.norm(W_r)
            V_mid = np.linalg.norm(Ff2 + W_f)       # shear in the hollow span
            lever = t_plate / 2 + T_WALL / 2
            M_pin = max(Vf, Vr) * lever
            out.update(wall_reaction_front_N=Wf, wall_reaction_rear_N=Wr,
                       pin_shear_in_hollow_span_N=V_mid,
                       sigma_bearing_tube_wall_MPa=max(Wf, Wr) / (D_HOLE * T_WALL),
                       FS_bearing_tube_wall=SY / (max(Wf, Wr) / (D_HOLE * T_WALL)),
                       pin_bending_lever_mm=lever, M_pin_Nm=M_pin / 1000,
                       sigma_pin_bending_MPa=M_pin / Z_PIN, FS_pin_bending=SY / (M_pin / Z_PIN))
        else:
            lever = t_plate / 2 + T_D / 2
            M_pin = max(Vf, Vr) * lever
            out.update(pin_bending_lever_mm=lever, M_pin_Nm=M_pin / 1000,
                       sigma_pin_bending_MPa=M_pin / Z_PIN, FS_pin_bending=SY / (M_pin / Z_PIN),
                       sigma_bearing_diag_plate_MPa=max(Vf, Vr) / (D_HOLE * T_D),
                       FS_bearing_diag_plate=SY / (max(Vf, Vr) / (D_HOLE * T_D)))
        return out

    pins = dict(
        O=pin_checks("O", O_f, O_r, Z_BR, T_BR, SY_AL, True),
        A=pin_checks("A", A_f, A_r, Z_D, T_D, SY, True),
        B=pin_checks("B", B_f, B_r, Z_D, T_BR, SY_AL, False),
    )
    return dict(beam=beam, diagonals=diag, pins=pins,
                pin_forces=dict(O_front=O_f, O_rear=O_r, A_front=A_f, A_rear=A_r, B_front=B_f, B_rear=B_r))


# ----------------------------------------------------------------------------- peaks
def peaks(fe):
    sec_x, sec = fe["sec_x"], fe["sec"]
    names = ["N", "Vy", "Vz", "Tx", "My", "Mz"]
    out = {}
    for k, nm in enumerate(names):
        j = int(np.argmax(np.abs(sec[:, k])))
        val = float(sec[j, k])
        out[nm] = dict(value=(val / 1000 if k >= 3 else val), unit=("N*m" if k >= 3 else "N"),
                       x_mm=float(sec_x[j]))
    return out


# ----------------------------------------------------------------------------- driver
def fmt(v):
    return float(np.round(v, 4))


def run_case(a, x_gen, chain_mode="exact"):
    fe = solve_fe(a, x_gen, chain_mode)
    hd = hand_deflection(a, x_gen, chain_mode)
    st = hd["statics"]
    s = strength(a, fe, hd)
    return fe, hd, st, s


def main():
    a0, xg0 = 500.0, -196.954                  # x_gen confirmed 14 Oct 2026
    fe, hd, st, s = run_case(a0, xg0)
    info = fe["info"]

    def vec(v, scale=1.0):
        return [fmt(x * scale) for x in v]

    print("=== POWER ===")
    for k, v in PW.items():
        print(f"  {k}: {v:.4f}")
    print(f"  chain geometry: C={info['C']:.1f} mm, phi={info['phi_deg']:.3f} deg, tight side at z<0 (rear)")
    print(f"  P1={vec(info['P1'])}, P2={vec(info['P2'])}")
    print(f"  rotor station F={vec(info['F1'])} N, M={vec(info['M1'],1e-3)} N*m (y residual {info['y_residual']:.3e})")
    print(f"  gen station   F={vec(info['F2'])} N, M={vec(info['M2'],1e-3)} N*m")
    print(f"  beam weight {st['Wb']:.2f} N at x={st['xc']:.2f};  diag weight each {info['W_d']:.2f} N, L_cut {info['L_cut']:.1f} mm")
    print(f"  applied resultant about O: F={vec(st['R_app'][:3])} N, M={vec(st['R_app'][3:],1e-3)} N*m")

    print("\n=== REACTIONS (hand statics vs FE) ===")
    for k in ("F_f", "F_r", "Ox_f", "Ox_r", "Oy_f", "Oy_r"):
        print(f"  {k:5s} hand {st[k]:10.2f}   FE {fe[k]:10.2f}")
    print(f"  Oz    hand {st['Oz']:10.2f}   FE {fe['Rz']:10.2f}")
    print(f"  My_O  hand {st['My_O']/1000:10.3f}   FE {fe['RMy']/1000:10.3f} N*m")

    print("\n=== CG DEFLECTION (mm) ===")
    print(f"  FE   u_cg = {vec(fe['u_cg'])}  |u| = {fe['mag']:.4f}")
    print(f"  hand u_cg = {vec(hd['u_cg'])}  |u| = {hd['mag']:.4f}")
    for k, v in hd["comps"].items():
        print(f"    {k:45s} {v:9.4f}")
    print(f"  theta_x(A)={hd['th_xA']:.3e}, theta_y(A)={hd['th_yA']:.3e}, u_y(A)={hd['u_yA']:.4f}, u_x(A)={hd['u_xA']:.4f}")
    print(f"  FE node A: {vec(fe['uA'])}")
    print(f"  FE node rotor: {vec(fe['uR'])}")
    print(f"  diag stretch: front {hd['dL_f']:.4f} mm, rear {hd['dL_r']:.4f} mm")

    print("\n=== BEAM PEAKS (FE) ===")
    for k, v in peaks(fe).items():
        print(f"  {k}: {v['value']:.3f} {v['unit']} at x={v['x_mm']:.1f}")

    print("\n=== STRENGTH ===")
    print(json.dumps(s["beam"], indent=1, default=float))
    print(json.dumps(s["diagonals"], indent=1, default=float))
    print(json.dumps(s["pins"], indent=1, default=float))

    print("\n=== CHAIN APPROX COMPARISON ===")
    for mode in ("exact", "xonly"):
        ld, inf = make_loads(a0, xg0, mode)
        # net My about O from chain-related terms only (rotor chain force at axis w/o y-moment; gen full)
        Fc1 = inf["F_c1"]; Fc2 = inf["F_c2"]
        My_rotor = np.cross(np.array([X_ROTOR, 0, 0]), Fc1)[1]
        My_gen = (np.cross(np.array([xg0, 0, 0]), Fc2) + inf["M2"] - np.cross(np.array([0, Y_CHAIN, 0]) * 0, Fc2))[1]
        My_gen_force = np.cross(np.array([xg0, 0, 0]), Fc2)[1]
        My_gen_couple = inf["M2"][1]
        fe_m = solve_fe(a0, xg0, mode)
        print(f"  {mode}: chain dir={vec(inf['e_t'])}, My about O from rotor chain force {My_rotor/1000:.3f}, "
              f"gen chain force {My_gen_force/1000:.3f}, gen stator couple {My_gen_couple/1000:.3f}, "
              f"sum {(My_rotor+My_gen_force+My_gen_couple)/1000:.3f} N*m ; FE RMy_O={fe_m['RMy']/1000:.3f}, "
              f"Ox_f={fe_m['Ox_f']:.1f}, Ox_r={fe_m['Ox_r']:.1f}, F_f={fe_m['F_f']:.1f}, F_r={fe_m['F_r']:.1f}, |u_cg|={fe_m['mag']:.4f}")

    print("\n=== a SWEEP ===")
    for a in (300, 400, 500, 600, 700, 800):
        fe_a, hd_a, st_a, s_a = run_case(float(a), xg0)
        p = s_a["pins"]
        print(f"  a={a}: F_f={fe_a['F_f']:8.1f} F_r={fe_a['F_r']:8.1f} Ox_f={fe_a['Ox_f']:8.1f} Ox_r={fe_a['Ox_r']:8.1f} "
              f"Oy={fe_a['Ry']:7.1f} |u_cg| FE={fe_a['mag']:.4f} hand={hd_a['mag']:.4f} "
              f"comps: xy={hd_a['comps']['xy_bending_elastic_y']+hd_a['comps']['xy_rigid_rotation_z_from_diag_strain_y']:.4f} "
              f"xz={hd_a['comps']['xz_bending_z']:.4f} twist={hd_a['comps']['twist_rotor_to_A_z']:.4f} "
              f"rigid_x={hd_a['comps']['rigid_rotation_x_from_diag_strain_z']:.4f} "
              f"FS_buck={s_a['diagonals']['FS_buckling']:.2f} FS_pinshear={min(p['O']['FS_pin_shear'],p['A']['FS_pin_shear'],p['B']['FS_pin_shear']):.2f} "
              f"FS_pinbend={min(p['O']['FS_pin_bending'],p['A']['FS_pin_bending'],p['B']['FS_pin_bending']):.2f}")

    print("\n=== superseded x_gen = -50 reading (comparison only) ===")
    fe2, hd2, st2, s2 = run_case(a0, -50.0)
    print(f"  F_f={fe2['F_f']:.1f} F_r={fe2['F_r']:.1f} Ox_f={fe2['Ox_f']:.1f} Ox_r={fe2['Ox_r']:.1f} Oy={fe2['Ry']:.1f} Oz={fe2['Rz']:.1f} "
          f"My_O={fe2['RMy']/1000:.3f} |u_cg| FE={fe2['mag']:.4f} hand={hd2['mag']:.4f} phi={fe2['info']['phi_deg']:.3f} deg "
          f"T_chain z-comp={fe2['info']['F_c1'][2]:.2f} N")

    if "--json" in sys.argv:
        dump = dict(power=PW, primary=dict(fe=dict(F_f=fe["F_f"], F_r=fe["F_r"], Ox_f=fe["Ox_f"], Ox_r=fe["Ox_r"],
                                                   Oy_f=fe["Oy_f"], Oy_r=fe["Oy_r"], Oz=fe["Rz"], My_O=fe["RMy"] / 1000,
                                                   u_cg=list(fe["u_cg"]), mag=fe["mag"]),
                                           hand=dict(F_f=st["F_f"], F_r=st["F_r"], Ox_f=st["Ox_f"], Ox_r=st["Ox_r"],
                                                     Oy_f=st["Oy_f"], Oy_r=st["Oy_r"], Oz=st["Oz"], My_O=st["My_O"] / 1000,
                                                     u_cg=list(hd["u_cg"]), mag=hd["mag"], comps=hd["comps"]),
                                           peaks=peaks(fe), strength=s))
        print(json.dumps(dump, indent=1, default=float))


if __name__ == "__main__":
    main()
