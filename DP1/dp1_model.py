# dp1_model.py -- hand-calculation model for ME3180 DP1 (statics, internal loads, stresses, deflection).
# Edit the inputs block near the top (beam size, plate size, pin, a, x_gen) and run:  python3 dp1_model.py
# Requires numpy. Numbers agree with the Rotor Support Explorer artifact and with dp1_fe_check.py.
#!/usr/bin/env python3
"""
DP1 Microhydro rotor support beam -- independent 3D vector statics analysis.

Frame (Figure 2): origin at beam-to-bracket pin O on the beam neutral axis,
+x along the beam toward the fixed structure, +y up, +z toward the viewer of
the Figure-1 side view ("Front").  Right-handed.

Everything is SI internally (m, N, N*m, Pa); printing converts to mm, N, N*m, MPa.

Sign convention for internal loads: resultant that the part of the beam to the
RIGHT of a cut exerts on the part to the LEFT (N = F_x, Vy = F_y, Vz = F_z,
Tx = M_x, My = M_y, Mz = M_z).  With this convention
    sigma_x = N/A - Mz*y/Iz + My*z/Iy,   d2v/dx2 = +Mz/(E Iz),
    d2w/dx2 = -My/(E Iy),                dphi_x/dx = Tx/(G J).
"""
import math, json, sys
import numpy as np

g   = 9.81
IN  = 0.0254
PSI = 6894.757

# ----------------------------------------------------------------- inputs
# water / rotor
rho_w, v_w, A_swept = 1000.0, 2.5, 0.5 * 0.5
eta_h, eta_e, rpm   = 0.30, 0.82, 285.0
omega   = 2 * math.pi * rpm / 60.0
P_fluid = 0.5 * rho_w * A_swept * v_w ** 3
P_mech  = eta_h * P_fluid
P_elec  = eta_e * P_mech
T_rotor = P_mech / omega                      # water torque on rotor, +y

# sprockets (ANSI #40, 1/2" pitch -> 60T 9.554", 19T 3.038")
N1, N2 = 60, 19
R1 = 9.554 * IN / 2.0
R2 = 3.038 * IN / 2.0
rpm_gen = rpm * N1 / N2

# beam: 304 SS 4x4x1/4 square tube, sharp-corner idealisation
h = w = 4.0 * IN
t = 0.25 * IN
E, G, Sy, rho_s = 193e9, 75e9, 215e6, 8000.0
A_b  = h * w - (h - 2 * t) * (w - 2 * t)
I_y  = (w * h ** 3 - (w - 2 * t) * (h - 2 * t) ** 3) / 12.0
I_z  = (h * w ** 3 - (h - 2 * t) * (w - 2 * t) ** 3) / 12.0
A_m  = (h - t) * (w - t)                      # area enclosed by wall mid-line
p_m  = 2 * ((h - t) + (w - t))                # mid-line perimeter
J    = 4 * A_m ** 2 * t / p_m                 # Bredt (thin-walled closed)
q_beam = rho_s * g * A_b                      # N/m
d_hole = 0.375 * IN
x_left, x_right = -1.300, 0.050               # beam runs -1300 .. +50 mm (Figure 2 bottom view: 50 mm overhang past pin O; edge rule needs >= 2*d_hole)
L_beam = x_right - x_left
W_beam = q_beam * L_beam

# diagonals: 304 SS flat 2" x 1/4"
b_d, t_d = 2.0 * IN, 0.25 * IN
A_d = b_d * t_d
I_d_weak   = b_d * t_d ** 3 / 12.0
I_d_strong = t_d * b_d ** 3 / 12.0
z_d = w / 2 + t_d / 2                         # +/-53.975 mm
Sy_d = 215e6

# brackets 1/2" aluminium, Sy 35 ksi
t_br = 0.5 * IN
Sy_al = 35e3 * PSI
z_br = w / 2 + t_br / 2                       # +/-57.15 mm

# pin 3/8" (assume annealed 18-8/304 class, Sy 215 MPa -- see doubts)
d_pin = d_hole
A_pin = math.pi * d_pin ** 2 / 4
Sy_pin = 215e6

# loads / geometry
D_drag = 560.0
W_rot, W_gen = 150.0, 120.0
x_rot   = -1.200
X_GEN   = -0.196954                           # generator sprocket axis (confirmed 14 Oct 2026; 39.49" centre distance)
y_chain = -(h / 2 + 0.050)
y_cg    = -(h / 2 + 0.350)
y_cop   = -(h / 2 + 0.500)
yB      = 0.500
FS_req  = 2.0
DEFL_LIM = 0.7e-3

# ----------------------------------------------------------------- helpers
def cross(a, b):
    return np.cross(np.asarray(a, float), np.asarray(b, float))

def cumtrapz(y, x):
    out = np.zeros_like(y)
    out[1:] = np.cumsum(0.5 * (y[1:] + y[:-1]) * np.diff(x))
    return out

def chain_geometry(x_gen, mode="exact"):
    """Return chain tension T, tight-side contact points and force vectors.
    mode='exact': force along the exact external tangent between the sprockets.
    mode='xonly': force parallel to x at z = -R (common approximation)."""
    A1 = np.array([x_rot, y_chain, 0.0])
    A2 = np.array([x_gen, y_chain, 0.0])
    C  = float(np.linalg.norm(A2 - A1))
    T  = T_rotor / R1
    # tight side = span where the chain ENTERS the driver (rotor) sprocket.
    tight_s = None
    for s in (+1, -1):
        vel = cross([0.0, omega, 0.0], R1 * np.array([0.0, 0.0, s]))
        if np.dot(vel, A1 - A2) > 0:      # surface moving from gen toward rotor
            tight_s = s
    assert tight_s is not None
    s = tight_s
    phi = math.asin((R1 - R2) / C)        # tangent skew angle
    n_hat = np.array([math.sin(phi), 0.0, s * math.cos(phi)])   # centre -> contact
    u_hat = np.array([math.cos(phi), 0.0, -s * math.sin(phi)])  # P1 -> P2 along chain
    if mode == "exact":
        P1 = A1 + R1 * n_hat
        P2 = A2 + R2 * n_hat
        F1 = T * u_hat
        F2 = -T * u_hat
    else:
        P1 = A1 + np.array([0.0, 0.0, s * R1])
        P2 = A2 + np.array([0.0, 0.0, s * R2])
        F1 = np.array([T, 0.0, 0.0]) * (1.0 if x_gen > x_rot else -1.0)
        F2 = -F1
    # sanity: chain torque on rotor must oppose water torque
    tq = cross(P1 - A1, F1)[1]
    assert tq < 0, "tight side chosen wrongly"
    return dict(T=T, C=C, phi=phi, side=s, P1=P1, P2=P2, F1=F1, F2=F2,
                A1=A1, A2=A2, u=u_hat, n=n_hat)

# ----------------------------------------------------------------- model
def solve(a, x_gen, chain_mode="exact"):
    R = {}
    A_pt = np.array([-a, 0.0, 0.0]); B_pt = np.array([0.0, yB, 0.0])
    L_pp = float(np.linalg.norm(B_pt - A_pt))
    u_AB = (B_pt - A_pt) / L_pp
    theta = math.atan2(yB, a)
    L_cut = L_pp + 4 * d_hole
    W_d = rho_s * g * A_d * L_cut
    ch = chain_geometry(x_gen, chain_mode)
    T = ch["T"]

    # applied loads on the beam system (name, r[m], F[N], C[N m])
    L = []
    L.append(("Rotor weight @CG",              [x_rot, y_cg, 0.0],        [0, -W_rot, 0],   [0, 0, 0]))
    L.append(("Water drag @COP",               [x_rot, y_cop, 0.0],       [0, 0, D_drag],   [0, 0, 0]))
    L.append(("Water torque on rotor (couple)",[x_rot, y_cop, 0.0],       [0, 0, 0],        [0, T_rotor, 0]))
    L.append(("Chain tension on rotor sprocket @P1", ch["P1"].tolist(),   ch["F1"].tolist(),[0, 0, 0]))
    L.append(("Chain tension on gen sprocket @P2",   ch["P2"].tolist(),   ch["F2"].tolist(),[0, 0, 0]))
    L.append(("Generator+sprocket weight",     [x_gen, 0.0, 0.0],         [0, -W_gen, 0],   [0, 0, 0]))
    L.append(("Beam self-weight (resultant of %.1f N/m)" % q_beam,
              [(x_left + x_right) / 2, 0.0, 0.0],                         [0, -W_beam, 0],  [0, 0, 0]))
    L.append(("Front diagonal half-weight @A_f",[-a, 0.0, +z_d],          [0, -W_d / 2, 0], [0, 0, 0]))
    L.append(("Rear diagonal half-weight @A_r", [-a, 0.0, -z_d],          [0, -W_d / 2, 0], [0, 0, 0]))
    loads = [dict(name=n, r=np.array(r, float), F=np.array(F, float), C=np.array(C, float)) for n, r, F, C in L]

    # unknown reactions: Ox_f, Ox_r, Oy (each side, equal), Oz (front plate face), F_f, F_r
    unit = [
        ("Ox_f", [0, 0, +z_br], [1, 0, 0]),
        ("Ox_r", [0, 0, -z_br], [1, 0, 0]),
        ("Oy",   None, None),                     # handled specially (two points)
        ("Oz",   [0, 0, +z_br], [0, 0, 1]),
        ("F_f",  [-a, 0, +z_d], u_AB.tolist()),
        ("F_r",  [-a, 0, -z_d], u_AB.tolist()),
    ]
    Amat = np.zeros((6, 6)); rhs = np.zeros(6)
    for j, (nm, r, F) in enumerate(unit):
        if nm == "Oy":
            for zz in (+z_br, -z_br):
                r_ = np.array([0, 0, zz], float); F_ = np.array([0, 1, 0], float)
                Amat[0:3, j] += F_; Amat[3:6, j] += cross(r_, F_)
        else:
            r_ = np.array(r, float); F_ = np.array(F, float)
            Amat[0:3, j] = F_; Amat[3:6, j] = cross(r_, F_)
    for ld in loads:
        rhs[0:3] -= ld["F"]; rhs[3:6] -= cross(ld["r"], ld["F"]) + ld["C"]
    sol = np.linalg.solve(Amat, rhs)
    Ox_f, Ox_r, Oy, Oz, F_f, F_r = sol
    # applied-load resultants about O
    SF = -rhs[0:3]; SM = -rhs[3:6]

    reactions = [
        dict(name="Bracket front plate on beam @O_f", r=np.array([0, 0, +z_br]), F=np.array([Ox_f, Oy, Oz]), C=np.zeros(3)),
        dict(name="Bracket rear plate on beam @O_r",  r=np.array([0, 0, -z_br]), F=np.array([Ox_r, Oy, 0.0]), C=np.zeros(3)),
        dict(name="Front diagonal on beam @A_f",      r=np.array([-a, 0, +z_d]), F=F_f * u_AB, C=np.zeros(3)),
        dict(name="Rear diagonal on beam @A_r",       r=np.array([-a, 0, -z_d]), F=F_r * u_AB, C=np.zeros(3)),
    ]
    # residual check
    res = np.zeros(6)
    for ld in loads + reactions:
        res[0:3] += ld["F"]; res[3:6] += cross(ld["r"], ld["F"]) + ld["C"]
    assert np.max(np.abs(res)) < 1e-6, res

    # ------------------------------------------------ internal loads on a grid
    allp = loads + reactions
    xs = np.linspace(x_left, x_right, 26381)       # dx = 0.05 mm
    Fint = np.zeros((len(xs), 3)); Mint = np.zeros((len(xs), 3))
    for ld in allp:
        if np.allclose(ld["F"], 0) and np.allclose(ld["C"], 0):
            continue
        if ld["name"].startswith("Beam self-weight"):
            continue
        mask = (ld["r"][0] < xs).astype(float)
        rF = cross(ld["r"], ld["F"])
        Fx, Fy, Fz = ld["F"]
        Fint -= np.outer(mask, ld["F"])
        # (r - rc) x F = r x F - rc x F ; rc x F = (0, -x Fz, x Fy)
        Mint[:, 0] -= mask * (rF[0] + ld["C"][0])
        Mint[:, 1] -= mask * (rF[1] - (-xs * Fz) + ld["C"][1])
        Mint[:, 2] -= mask * (rF[2] - (xs * Fy) + ld["C"][2])
    # distributed self weight from x_left to x
    xe = np.minimum(xs, x_right)
    Wx = q_beam * (xe - x_left)
    xm = 0.5 * (x_left + xe)
    Fint[:, 1] -= -Wx
    Mint[:, 2] -= -(xm - xs) * Wx          # (xm-x,0,0) x (0,-W,0) = (0,0,-(xm-x)W)

    def at(xq):
        i = int(np.argmin(np.abs(xs - xq)))
        return Fint[i].copy(), Mint[i].copy()
    eps = 2e-4
    def peak(col, arr):
        i = int(np.argmax(np.abs(arr[:, col])))
        return float(arr[i, col]), float(xs[i])

    N, Vy, Vz = Fint[:, 0], Fint[:, 1], Fint[:, 2]
    Tx, My, Mz = Mint[:, 0], Mint[:, 1], Mint[:, 2]
    beam_peaks = {}
    for lab, col, arr in (("N", 0, Fint), ("Vy", 1, Fint), ("Vz", 2, Fint), ("Tx", 0, Mint), ("My", 1, Mint), ("Mz", 2, Mint)):
        v, xx = peak(col, arr)
        beam_peaks[lab] = dict(value=v, x_mm=xx * 1e3)

    # ------------------------------------------------ stresses (von Mises at corners)
    corners = [(sy * h / 2, sz * w / 2) for sy in (+1, -1) for sz in (+1, -1)]
    tau_t = Tx / (2 * A_m * t)
    svm_max = np.zeros(len(xs)); corner_id = np.zeros(len(xs), int)
    for k, (yy, zz) in enumerate(corners):
        sx = N / A_b - Mz * yy / I_z + My * zz / I_y
        svm = np.sqrt(sx ** 2 + 3 * tau_t ** 2)
        upd = svm > svm_max
        svm_max[upd] = svm[upd]; corner_id[upd] = k
    # transverse shear (mid-wall, for completeness)
    tau_v = np.sqrt(Vy ** 2 + Vz ** 2) / (2 * h * t)
    tau_mid = np.abs(tau_t) + tau_v
    svm_mid = np.sqrt(3.0) * tau_mid
    def stress_at(xq):
        i = int(np.argmin(np.abs(xs - xq)))
        return dict(x_mm=xs[i] * 1e3, N=N[i], Vy=Vy[i], Vz=Vz[i], Tx=Tx[i], My=My[i], Mz=Mz[i],
                    tau_torsion_MPa=tau_t[i] / 1e6, sigma_vm_MPa=svm_max[i] / 1e6,
                    corner=("y%+d z%+d" % (int(np.sign(corners[corner_id[i]][0])), int(np.sign(corners[corner_id[i]][1])))),
                    FS=Sy / svm_max[i] if svm_max[i] > 0 else float("inf"))
    i_max = int(np.argmax(svm_max))
    beam_stress = dict(
        at_rotor_plus=stress_at(x_rot + eps), at_A_minus=stress_at(-a - eps), at_A_plus=stress_at(-a + eps),
        at_O_minus=stress_at(0 - eps), global_max=stress_at(xs[i_max]),
        max_shear_mid_wall_MPa=float(np.max(tau_mid)) / 1e6, max_vm_mid_wall_MPa=float(np.max(svm_mid)) / 1e6)

    # ------------------------------------------------ deflections
    # (1a) xy bending, rigid supports v(0)=0, v(-a)=0
    kz = Mz / (E * I_z)
    th0 = cumtrapz(kz, xs); v0 = cumtrapz(th0, xs)
    def interp(arr, xq): return float(np.interp(xq, xs, arr))
    # v = v0 + c1 x + c2
    M2 = np.array([[0.0, 1.0], [-a, 1.0]]); b2 = np.array([-interp(v0, 0.0), -interp(v0, -a)])
    c1, c2 = np.linalg.solve(M2, b2)
    v = v0 + c1 * xs + c2; vp = th0 + c1
    # (1b) xz bending, cantilever from rigid bracket: w(0)=0, w'(0)=0
    ky = -My / (E * I_y)
    wp0 = cumtrapz(ky, xs); w0 = cumtrapz(wp0, xs)
    c3 = -interp(wp0, 0.0); c4 = -(interp(w0, 0.0) + c3 * 0.0)
    wdef = w0 + c3 * xs + c4; wp = wp0 + c3
    # (1c) twist, phi_x(-a)=0
    ph0 = cumtrapz(Tx / (G * J), xs); phi_x = ph0 - interp(ph0, -a)
    # axial displacement u(0)=0
    u0 = cumtrapz(N / (E * A_b), xs); u_ax = u0 - interp(u0, 0.0)
    # (2) rigid beam on elastic diagonals (axial springs), O fixed, beta=0
    d_f = F_f * L_pp / (E * A_d); d_r = F_r * L_pp / (E * A_d)
    uA = interp(u_ax, -a)
    s_t, c_t = math.sin(theta), math.cos(theta)
    alpha = (d_f - d_r) / (2 * z_d * s_t)
    gamma = (d_f + d_r + 2 * uA * c_t) / (2 * a * s_t)
    r_cg_rel = np.array([0.0, y_cg, 0.0])       # CG relative to beam axis at x_rot
    r_cg_O   = np.array([x_rot, y_cg, 0.0])
    # elastic contributions at the CG
    u_bend_xy  = np.array([interp(v, x_rot) * 0 + cross([0, 0, interp(vp, x_rot)], r_cg_rel)[0], interp(v, x_rot), 0.0])
    u_bend_xz  = np.array([0.0, 0.0, interp(wdef, x_rot)])
    u_twist    = cross([interp(phi_x, x_rot), 0, 0], r_cg_rel)
    u_axial    = np.array([interp(u_ax, x_rot), 0.0, 0.0])
    u_rigid    = cross([alpha, 0.0, gamma], r_cg_O)
    # kinematic coupling: the beam's rotation about y at A (slope of the xz bending curve) moves the front and
    # rear plate attachment points in opposite x directions; the inclined plates turn that into an extra
    # rigid rotation of the beam about x: theta_x = theta_yA * cos(alpha)/sin(alpha).  (Verified against a 3-D frame FE model.)
    theta_yA  = -interp(wp, -a)
    theta_xc  = theta_yA * u_AB[0] / u_AB[1]
    u_couple  = cross([theta_xc, 0.0, 0.0], r_cg_O)
    u_tot = u_bend_xy + u_bend_xz + u_twist + u_axial + u_rigid + u_couple
    defl = dict(
        bend_xy_mm=u_bend_xy * 1e3, bend_xz_mm=u_bend_xz * 1e3, twist_mm=u_twist * 1e3,
        axial_mm=u_axial * 1e3, rigid_mm=u_rigid * 1e3, couple_mm=u_couple * 1e3, total_mm=u_tot * 1e3,
        total_mag_mm=float(np.linalg.norm(u_tot)) * 1e3,
        twist_angle_rotor_rad=float(interp(phi_x, x_rot)), alpha_rad=alpha, gamma_rad=gamma,
        delta_f_mm=d_f * 1e3, delta_r_mm=d_r * 1e3, w_at_A_mm=interp(wdef, -a) * 1e3,
        slope_y_at_A_rad=interp(wp, -a), v_rotor_mm=interp(v, x_rot), w_rotor_mm=interp(wdef, x_rot) * 1e3)

    # ------------------------------------------------ diagonal + pin checks
    Fd_on_beam_f = F_f * u_AB + np.array([0, -W_d / 2, 0])
    Fd_on_beam_r = F_r * u_AB + np.array([0, -W_d / 2, 0])
    Fd_on_B_f = -F_f * u_AB + np.array([0, -W_d / 2, 0])
    Fd_on_B_r = -F_r * u_AB + np.array([0, -W_d / 2, 0])
    Pcr_weak = math.pi ** 2 * E * I_d_weak / L_pp ** 2
    Pcr_strong = math.pi ** 2 * E * I_d_strong / L_pp ** 2
    q_d = rho_s * g * A_d
    M_sw = q_d * c_t * L_pp ** 2 / 8            # self-weight bending, strong axis, pinned
    def diag_checks(F, label):
        d = {}
        d["axial_N"] = F
        d["net_section_sigma_MPa"] = F / ((b_d - d_hole) * t_d) / 1e6
        d["gross_sigma_MPa"] = F / A_d / 1e6
        d["FS_net_section_yield"] = Sy_d / abs(F / ((b_d - d_hole) * t_d)) if F != 0 else float("inf")
        d["bearing_sigma_MPa"] = abs(F) / (d_pin * t_d) / 1e6
        d["FS_bearing_plate"] = Sy_d / (abs(F) / (d_pin * t_d))
        A_to = 2 * (2 * d_hole - d_hole / 2) * t_d
        d["tearout_tau_MPa"] = abs(F) / A_to / 1e6
        d["FS_tearout"] = 0.577 * Sy_d / (abs(F) / A_to)
        if F < 0:
            d["FS_euler_weak"] = Pcr_weak / abs(F)
            d["FS_euler_strong"] = Pcr_strong / abs(F)
        else:
            d["FS_euler_weak"] = float("inf"); d["FS_euler_strong"] = float("inf")
        d["self_weight_bending_Nm"] = M_sw
        d["sigma_total_with_sw_MPa"] = (abs(F) / A_d + M_sw * (b_d / 2) / I_d_strong) / 1e6
        return d
    diag = dict(front=diag_checks(F_f, "front"), rear=diag_checks(F_r, "rear"),
                Pcr_weak_N=Pcr_weak, Pcr_strong_N=Pcr_strong, L_pp_mm=L_pp * 1e3, L_cut_mm=L_cut * 1e3,
                W_d_each_N=W_d, slenderness_weak=L_pp / (t_d / math.sqrt(12)), theta_deg=math.degrees(theta))

    def pin_checks(F_vec, t_a, Sy_a, t_b, Sy_b, label):
        """F_vec = force transmitted across one shear plane (one side of the pin).
        t_a/Sy_a: outer member (bracket plate or diagonal); t_b/Sy_b: inner member (tube wall or bracket)."""
        Fp = float(np.hypot(F_vec[0], F_vec[1]))   # in-plane (radial) load on pin
        tau = Fp / A_pin
        sb_a = Fp / (d_pin * t_a); sb_b = Fp / (d_pin * t_b)
        arm = t_a / 2 + t_b / 2
        Mb = Fp * arm
        sig_b = 32 * Mb / (math.pi * d_pin ** 3)
        return dict(side_force_N=[float(x) for x in F_vec], radial_N=Fp, axial_z_N=float(F_vec[2]),
                    pin_shear_MPa=tau / 1e6, FS_pin_shear=0.577 * Sy_pin / tau if tau > 0 else float("inf"),
                    bearing_outer_MPa=sb_a / 1e6, FS_bearing_outer=Sy_a / sb_a if sb_a > 0 else float("inf"),
                    bearing_tube_or_bracket_MPa=sb_b / 1e6, FS_bearing_inner=Sy_b / sb_b if sb_b > 0 else float("inf"),
                    pin_bend_arm_mm=arm * 1e3, pin_bend_M_Nm=Mb, pin_bend_sigma_MPa=sig_b / 1e6,
                    FS_pin_bending=Sy_pin / sig_b if sig_b > 0 else float("inf"), label=label)
    pins = dict(
        O_front=pin_checks(np.array([Ox_f, Oy, Oz]), t_br, Sy_al, t, Sy, "bracket Al plate / tube wall"),
        O_rear =pin_checks(np.array([Ox_r, Oy, 0.0]), t_br, Sy_al, t, Sy, "bracket Al plate / tube wall"),
        A_front=pin_checks(Fd_on_beam_f, t_d, Sy_d, t, Sy, "diagonal plate / tube wall"),
        A_rear =pin_checks(Fd_on_beam_r, t_d, Sy_d, t, Sy, "diagonal plate / tube wall"),
        B_front=pin_checks(Fd_on_B_f, t_d, Sy_d, t_br, Sy_al, "diagonal plate / Al bracket"),
        B_rear =pin_checks(Fd_on_B_r, t_d, Sy_d, t_br, Sy_al, "diagonal plate / Al bracket"),
    )

    # moments carried where
    M_y_bracket_couple = z_br * (Ox_f - Ox_r)
    M_y_diag_couple = z_d * (F_f - F_r) * u_AB[0]
    M_x_diag_couple = -z_d * (F_f - F_r) * u_AB[1]

    R.update(dict(
        a_mm=a * 1e3, x_gen_mm=x_gen * 1e3, chain_mode=chain_mode, theta_deg=math.degrees(theta),
        chain=ch, T=T, loads=loads, reactions=reactions, sol=sol, SF_applied=SF, SM_applied_about_O=SM,
        Ox_f=Ox_f, Ox_r=Ox_r, Oy=Oy, Oz=Oz, F_f=F_f, F_r=F_r, u_AB=u_AB,
        Fd_on_beam_f=Fd_on_beam_f, Fd_on_beam_r=Fd_on_beam_r, Fd_on_B_f=Fd_on_B_f, Fd_on_B_r=Fd_on_B_r,
        M_y_bracket_couple=M_y_bracket_couple, M_y_diag_couple=M_y_diag_couple, M_x_diag_couple=M_x_diag_couple,
        xs=xs, Fint=Fint, Mint=Mint, beam_peaks=beam_peaks, beam_stress=beam_stress, defl=defl,
        diag=diag, pins=pins, W_d=W_d, L_pp=L_pp, L_cut=L_cut, at=at, eps=eps))
    return R

# ----------------------------------------------------------------- printing
def fmt_v(v, s=1.0, nd=1):
    return "[" + ", ".join("%.*f" % (nd, x * s) for x in v) + "]"

def print_case(R, full=True):
    a = R["a_mm"]; ch = R["chain"]
    print("=" * 100)
    print("CASE  a = %.0f mm, x_gen = %.3f mm, chain model = %s, theta = %.2f deg" % (a, R["x_gen_mm"], R["chain_mode"], R["theta_deg"]))
    print("=" * 100)
    if full:
        print("Chain: T = %.2f N, centre distance C = %.1f mm, skew phi = %.3f deg, tight side z-sign = %+d (rear)" % (R["T"], ch["C"] * 1e3, math.degrees(ch["phi"]), ch["side"]))
        print("  P1 (rotor contact) mm = %s, F1 N = %s" % (fmt_v(ch["P1"], 1e3, 2), fmt_v(ch["F1"], 1, 2)))
        print("  P2 (gen contact)   mm = %s, F2 N = %s" % (fmt_v(ch["P2"], 1e3, 2), fmt_v(ch["F2"], 1, 2)))
        print("\nLOAD TABLE (applied loads on beam system; point mm, force N, couple N*m):")
        for ld in R["loads"]:
            print("  %-45s r=%s  F=%s  C=%s" % (ld["name"], fmt_v(ld["r"], 1e3, 2), fmt_v(ld["F"], 1, 2), fmt_v(ld["C"], 1, 3)))
        print("  Resultant applied force  N   = %s" % fmt_v(R["SF_applied"], 1, 2))
        print("  Resultant applied moment about O N*m = %s" % fmt_v(R["SM_applied_about_O"], 1, 3))
    print("\nREACTIONS (force ON the beam unless noted):")
    print("  O front plate -> beam : %s N   (z carried by face contact, see assumptions)" % fmt_v(R["reactions"][0]["F"], 1, 1))
    print("  O rear  plate -> beam : %s N" % fmt_v(R["reactions"][1]["F"], 1, 1))
    print("  A front diag  -> beam : %s N   (axial F_f = %+.1f N, %s)" % (fmt_v(R["Fd_on_beam_f"], 1, 1), R["F_f"], "tension" if R["F_f"] > 0 else "COMPRESSION"))
    print("  A rear  diag  -> beam : %s N   (axial F_r = %+.1f N, %s)" % (fmt_v(R["Fd_on_beam_r"], 1, 1), R["F_r"], "tension" if R["F_r"] > 0 else "COMPRESSION"))
    print("  B front diag  -> fixed bracket : %s N" % fmt_v(R["Fd_on_B_f"], 1, 1))
    print("  B rear  diag  -> fixed bracket : %s N" % fmt_v(R["Fd_on_B_r"], 1, 1))
    print("  Bracket couple about y at O (z_br*(Ox_f-Ox_r)) = %.1f N*m ; diagonal couple about y at A = %.1f N*m ; diagonal couple about x at A = %.1f N*m"
          % (R["M_y_bracket_couple"], R["M_y_diag_couple"], R["M_x_diag_couple"]))
    bp = R["beam_peaks"]
    print("\nBEAM PEAKS: " + "; ".join("%s = %.1f %s @ x = %.1f mm" % (k, v["value"], "N" if k in ("N", "Vy", "Vz") else "N*m", v["x_mm"]) for k, v in bp.items()))
    bs = R["beam_stress"]
    print("BEAM STRESS (von Mises at worst corner):")
    for k in ("at_rotor_plus", "at_A_minus", "at_A_plus", "at_O_minus", "global_max"):
        s = bs[k]
        print("  %-14s x=%8.1f mm: N=%7.1f N  Tx=%7.2f  My=%8.2f  Mz=%8.2f N*m  tau_t=%.3f MPa  sigma_vm=%.3f MPa (%s)  FS=%.1f"
              % (k, s["x_mm"], s["N"], s["Tx"], s["My"], s["Mz"], s["tau_torsion_MPa"], s["sigma_vm_MPa"], s["corner"], s["FS"]))
    d = R["defl"]
    print("\nROTOR-CG DEFLECTION (mm, [x,y,z]):")
    print("  beam bending xy          : %s" % fmt_v(d["bend_xy_mm"], 1, 4))
    print("  beam bending xz          : %s   (cantilever from rigid bracket, w(A)=%.4f mm)" % (fmt_v(d["bend_xz_mm"], 1, 4), d["w_at_A_mm"]))
    print("  beam twist rotor->A      : %s   (phi_x = %.3e rad)" % (fmt_v(d["twist_mm"], 1, 4), d["twist_angle_rotor_rad"]))
    print("  beam axial               : %s" % fmt_v(d["axial_mm"], 1, 5))
    print("  rigid body (diag strain) : %s   (alpha=%.3e rad, gamma=%.3e rad; delta_f=%.4f mm, delta_r=%.4f mm)" % (fmt_v(d["rigid_mm"], 1, 4), d["alpha_rad"], d["gamma_rad"], d["delta_f_mm"], d["delta_r_mm"]))
    print("  TOTAL                    : %s   |u| = %.4f mm  (limit 0.7 mm -> %s)" % (fmt_v(d["total_mm"], 1, 4), d["total_mag_mm"], "OK" if d["total_mag_mm"] <= 0.7 else "FAIL"))
    dg = R["diag"]
    print("\nDIAGONALS: L_pp = %.1f mm, L_cut = %.1f mm, W each = %.1f N, Pcr_weak = %.0f N, Pcr_strong = %.0f N, slenderness = %.0f"
          % (dg["L_pp_mm"], dg["L_cut_mm"], dg["W_d_each_N"], dg["Pcr_weak_N"], dg["Pcr_strong_N"], dg["slenderness_weak"]))
    for side in ("front", "rear"):
        c = dg[side]
        print("  %-5s F=%+8.1f N: net-sect sigma=%.2f MPa (FS %.1f) | bearing %.1f MPa (FS %.2f) | tearout %.1f MPa (FS %.2f) | Euler weak FS %.2f"
              % (side, c["axial_N"], c["net_section_sigma_MPa"], c["FS_net_section_yield"], c["bearing_sigma_MPa"], c["FS_bearing_plate"], c["tearout_tau_MPa"], c["FS_tearout"], c["FS_euler_weak"]))
    print("PINS (3/8\" , per side):")
    for k, p in R["pins"].items():
        print("  %-7s radial %7.1f N (z %6.1f): shear %.1f MPa FS %.2f | brg outer(%s) %.1f MPa FS %.2f | brg inner %.1f MPa FS %.2f | bend arm %.2f mm sigma %.0f MPa FS %.2f"
              % (k, p["radial_N"], p["axial_z_N"], p["pin_shear_MPa"], p["FS_pin_shear"], p["label"].split("/")[0].strip(), p["bearing_outer_MPa"], p["FS_bearing_outer"],
                 p["bearing_tube_or_bracket_MPa"], p["FS_bearing_inner"], p["pin_bend_arm_mm"], p["pin_bend_sigma_MPa"], p["FS_pin_bending"]))

def main():
    print("POWER: P_fluid = %.1f W, P_mech = %.1f W, P_elec = %.1f W, omega = %.3f rad/s, T_rotor = %.3f N*m, chain T = %.2f N, gen rpm = %.1f, gen torque = %.3f N*m"
          % (P_fluid, P_mech, P_elec, omega, T_rotor, T_rotor / R1, rpm_gen, T_rotor * R2 / R1))
    print("SECTION: A = %.1f mm2, I = %.4e mm4, J = %.4e mm4, A_m = %.1f mm2, q_beam = %.2f N/m, W_beam = %.1f N (L = %.2f mm)"
          % (A_b * 1e6, I_y * 1e12, J * 1e12, A_m * 1e6, q_beam, W_beam, L_beam * 1e3))
    print("Diagonal: A_d = %.1f mm2, I_weak = %.1f mm4, I_strong = %.0f mm4 ; R1 = %.3f mm, R2 = %.3f mm" % (A_d * 1e6, I_d_weak * 1e12, I_d_strong * 1e12, R1 * 1e3, R2 * 1e3))

    R0 = solve(0.500, X_GEN, "exact")
    print_case(R0, full=True)

    # internal load distribution printout (coarse)
    print("\nINTERNAL LOAD DISTRIBUTION (right-on-left), x in mm:")
    print("   x(mm)      N(N)    Vy(N)    Vz(N)   Tx(Nm)   My(Nm)   Mz(Nm)")
    for xq in [-1300, -1250, -1200.2, -1199.8, -1100, -1000, -900, -800, -700, -600, -500.2, -499.8, -400, -300, -200, -100, -50.2, -49.8, -25, -0.2, 0.2, 19]:
        F, M = R0["at"](xq / 1e3)
        print("  %7.1f  %8.1f %8.1f %8.1f %8.2f %8.2f %8.2f" % (xq, F[0], F[1], F[2], M[0], M[1], M[2]))

    # chain approximation comparison
    Rx = solve(0.500, X_GEN, "xonly")
    print("\nCHAIN MODEL COMPARISON (net applied moment about y on beam, N*m):")
    print("  exact tangent : My_applied(about O) = %.3f  (of which drag %.3f, chain+torque %.3f)" % (R0["SM_applied_about_O"][1], -x_rot * D_drag, R0["SM_applied_about_O"][1] + x_rot * D_drag))
    print("  x-only        : My_applied(about O) = %.3f  (chain+torque %.3f)" % (Rx["SM_applied_about_O"][1], Rx["SM_applied_about_O"][1] + x_rot * D_drag))
    print("  R1*T = %.3f, R2*T = %.3f, (R1-R2)*T = %.3f" % (R1 * R0["T"], R2 * R0["T"], (R1 - R2) * R0["T"]))
    print("  x-only reactions: Ox_f=%.1f Ox_r=%.1f  vs exact Ox_f=%.1f Ox_r=%.1f ; F_f %.1f/%.1f F_r %.1f/%.1f" % (Rx["Ox_f"], Rx["Ox_r"], R0["Ox_f"], R0["Ox_r"], Rx["F_f"], R0["F_f"], Rx["F_r"], R0["F_r"]))

    # a sweep
    print("\nA-SWEEP (exact chain, x_gen = %.3f mm):" % (X_GEN * 1e3))
    print("   a    F_f      F_r     Ox_f     Ox_r    Oy    |My|max  |Tx|max  |Mz|max  svm_max  ux     uy     uz    |u|   FS_euler FS_pinbend(min) FS_pinshear(min)")
    sweep = []
    for a_mm in (300, 400, 500, 600, 700, 800):
        Rs = solve(a_mm / 1e3, X_GEN, "exact")
        d = Rs["defl"]; bp = Rs["beam_peaks"]
        fs_pb = min(p["FS_pin_bending"] for p in Rs["pins"].values())
        fs_ps = min(p["FS_pin_shear"] for p in Rs["pins"].values())
        fs_eu = min(Rs["diag"]["front"]["FS_euler_weak"], Rs["diag"]["rear"]["FS_euler_weak"])
        print("  %3d %8.1f %8.1f %8.1f %8.1f %6.1f %8.1f %8.1f %8.1f %7.2f %6.3f %6.3f %6.3f %6.3f %7.2f %8.2f %8.2f"
              % (a_mm, Rs["F_f"], Rs["F_r"], Rs["Ox_f"], Rs["Ox_r"], Rs["Oy"], abs(bp["My"]["value"]), abs(bp["Tx"]["value"]), abs(bp["Mz"]["value"]),
                 Rs["beam_stress"]["global_max"]["sigma_vm_MPa"], d["total_mm"][0], d["total_mm"][1], d["total_mm"][2], d["total_mag_mm"], fs_eu, fs_pb, fs_ps))
        sweep.append(Rs)
    for Rs in sweep:
        d = Rs["defl"]
        print("  a=%3.0f: bend_xy %s bend_xz %s twist %s rigid %s total %s |u|=%.3f" % (Rs["a_mm"], fmt_v(d["bend_xy_mm"], 1, 3), fmt_v(d["bend_xz_mm"], 1, 3), fmt_v(d["twist_mm"], 1, 3), fmt_v(d["rigid_mm"], 1, 3), fmt_v(d["total_mm"], 1, 3), d["total_mag_mm"]))

    # superseded generator reading (x_gen = -50 mm), kept for comparison only
    Ra = solve(0.500, -0.050, "exact")
    print("\nSUPERSEDED x_gen = -50 mm reading (comparison only):")
    print_case(Ra, full=False)

    # dump JSON
    def jsonable(R):
        d = R["defl"]
        return dict(a_mm=R["a_mm"], x_gen_mm=R["x_gen_mm"], chain_mode=R["chain_mode"], T_chain_N=R["T"],
                    reactions=dict(O_front=R["reactions"][0]["F"].tolist(), O_rear=R["reactions"][1]["F"].tolist(),
                                   A_front_diag_on_beam=R["Fd_on_beam_f"].tolist(), A_rear_diag_on_beam=R["Fd_on_beam_r"].tolist(),
                                   B_front_diag_on_bracket=R["Fd_on_B_f"].tolist(), B_rear_diag_on_bracket=R["Fd_on_B_r"].tolist(),
                                   F_f=R["F_f"], F_r=R["F_r"], My_bracket_couple=R["M_y_bracket_couple"], My_diag_couple=R["M_y_diag_couple"], Mx_diag_couple=R["M_x_diag_couple"]),
                    beam_peaks=R["beam_peaks"], beam_stress={k: v for k, v in R["beam_stress"].items()},
                    deflection={k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in d.items()},
                    diag=R["diag"], pins=R["pins"], applied_resultant_F=R["SF_applied"].tolist(), applied_resultant_M_about_O=R["SM_applied_about_O"].tolist())
    out = dict(primary=jsonable(R0), xonly=jsonable(Rx), alt_xgen=jsonable(Ra), sweep=[jsonable(x) for x in sweep],
               power=dict(P_fluid_W=P_fluid, P_mech_W=P_mech, P_elec_W=P_elec, omega_rad_s=omega, T_rotor_Nm=T_rotor, T_chain_N=T_rotor / R1, rpm_gen=rpm_gen, T_gen_Nm=T_rotor * R2 / R1),
               section=dict(A_mm2=A_b * 1e6, I_mm4=I_y * 1e12, J_mm4=J * 1e12, q_beam_N_m=q_beam, W_beam_N=W_beam, L_beam_mm=L_beam * 1e3))
    with open(sys.argv[1] if len(sys.argv) > 1 else "/dev/null", "w") as f:
        json.dump(out, f, indent=1, default=float)

if __name__ == "__main__":
    main()
