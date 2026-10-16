"""Part D: diagonal loads, plate deflections and rotor-CG deflection by hand formulas (superposition).

Checks against the numerical integration in beam_internal.py and the DP1_Solver model.  mm, N, MPa.
"""
import numpy as np
from pin_reactions import IN, h, w, t_wall, t_p, b_p, a, xg, tau, T, P1, u, W_b, W_p, z_p, P_f, P_r, s, c
from beam_internal import internal, A, Iz, Iy, Am

E, G = 68900.0, 68900.0 / (2 * 1.33)          # 6061-T6
L = np.hypot(a, 500)                          # pin-to-pin length of a diagonal
Ap, Iweak, Istrong = b_p * t_p, b_p * t_p**3 / 12, t_p * b_p**3 / 12
y_cg, x_r, L_oh = -(h / 2 + 350), 1200.0, 1200.0 - a
q = W_b / 1350
Tc = T * u                                    # chain force on the rotor sprocket (x, 0, z)

# ---------- D.2 diagonal loads
dN = W_p / 2 * s
M_sw = W_p * c * L / 8
print(f"L = {L:.1f}, A_p = {Ap:.1f}, I_weak = {Iweak:.0f}, I_strong = {Istrong:.0f}")
print(f"front: N = {P_f - dN:.0f} (A end) .. {P_f + dN:.0f} (B end); rear: {P_r - dN:.0f} (A) .. {P_r + dN:.0f} (B); M_sw = {M_sw:.0f} N mm")
Pcr = np.pi**2 * E * Iweak / L**2
print(f"Euler weak axis: L/k = {L / (t_p / np.sqrt(12)):.0f}, Pcr = {Pcr:.0f}, n = {Pcr / abs(P_f - dN):.2f}")
print(f"rear net section: {abs(P_r + dN) / ((b_p - 0.7531 * IN) * t_p):.2f} MPa, gross+bending {abs(P_r + dN) / Ap + M_sw / (t_p * b_p**2 / 6):.2f}")

# ---------- D.3 plate stretch -> roll and pitch of the beam about O
d_f, d_r = P_f * L / (Ap * E), P_r * L / (Ap * E)
th_x_pl = (d_f - d_r) / (2 * z_p * s)
th_z_pl = (d_f + d_r) / 2 / (a * s)
print(f"delta_f = {d_f:.5f}, delta_r = {d_r:.5f} mm; roll {th_x_pl:.4e} -> CG z {th_x_pl * y_cg:.4f}; pitch {th_z_pl:.3e} -> CG y {th_z_pl * x_r:.4f}, x {th_z_pl * abs(y_cg):.4f}")

# ---------- D.4 beam contributions
# lateral (x-z) bending: cantilever clamped about y at O, length 1200
EIy, EIz = E * Iy, E * Iz
M_A = z_p * c * (P_r - P_f)                         # y-couple the plates put on the beam at A
def tipP(P, aP): return P * aP**2 * (3 * x_r - aP) / (6 * EIy)          # point load at aP from O, deflection at 1200
def tipM(M, aM): return M * aM * (x_r - aM / 2) / EIy                  # couple at aM from O
def slopeP_at(P, aP, xq): return P * (aP * xq - xq**2 / 2) / EIy if xq <= aP else P * aP**2 / (2 * EIy)
gen_My = -(np.cross(np.array([3.2, -100.8, -38.5]), -Tc))[1]            # not used (see below)
r2 = np.array([xg + 0.0, 0, 0])
# y-moment of the generator-side chain force about the beam axis at xg
P2 = np.array([xg - 3.2 * 0 + 3.2, -100.8, -38.5])
from pin_reactions import P2 as P2e
Mg = np.cross(np.array(P2e) - np.array([xg, 0, 0]), -Tc)[1]
Mr = np.cross(np.array(P1) - np.array([-1200, 0, 0]), Tc)[1] + tau        # net y-couple at the rotor (water torque + chain)
w_drag = tipP(560, x_r); w_MA = tipM(M_A, a); w_cz = tipP(Tc[2], x_r) - tipP(Tc[2], -xg)
w_Mr = Mr * x_r**2 / (2 * EIy); w_Mg = tipM(Mg, -xg)
w_lat = w_drag - w_MA + w_cz + w_Mr + w_Mg
print(f"M_A = {M_A:.0f}; Mr = {Mr:.0f}; Mg = {Mg:.0f}")
print(f"lateral: drag {w_drag:.4f} - plates {w_MA:.4f} + chain z {w_cz:.4f} + Mr {w_Mr:.4f} + Mg {w_Mg:.4f} = {w_lat:.4f}")
th_yA = slopeP_at(560, x_r, a) - M_A * a / EIy + slopeP_at(Tc[2], x_r, a) - slopeP_at(Tc[2], -xg, a) + Mr * a / EIy + Mg * (-xg) / EIy
th_x_cpl = th_yA / np.tan(np.arctan2(500, a))
print(f"slope about y at A = {th_yA:.4e}; roll = slope cot(alpha) = {th_x_cpl:.4e} -> CG z {th_x_cpl * abs(y_cg):.4f}")
# twist between A and the rotor
Lm = 2 * ((w - t_wall) + (h - t_wall)); J = 4 * Am**2 * t_wall / Lm
Tt = 560 * (h / 2 + 500) + Tc[2] * (h / 2 + 50)
phi = Tt * L_oh / (G * J)
print(f"J = {J:.4e}, G = {G:.0f}, T = {Tt:.0f}, phi = {phi:.4e} -> CG z {phi * abs(y_cg):.4f}")
# vertical (x-y) bending: supports O and A, overhang 540 to the rotor (free end 640)
Mc = Tc[0] * (h / 2 + 50)                               # chain couple at the rotor and (opposite) at the generator
cant_v = 150 * L_oh**3 / (3 * EIz) + Mc * L_oh**2 / (2 * EIz) + q * L_oh**2 * (6 * 640**2 - 4 * 640 * L_oh + L_oh**2) / (24 * EIz)
cant_t = 150 * L_oh**2 / (2 * EIz) + Mc * L_oh / EIz + q * (L_oh**3 - 3 * 640 * L_oh**2 + 3 * 640**2 * L_oh) / (6 * EIz)
MzA = 150 * L_oh + Mc + q * 640**2 / 2
ag, bg = -xg, a + xg
thA = MzA * a / (3 * EIz) - 120 * ag * bg * (a + ag) / (6 * a * EIz) + Mc * (a**2 - 3 * ag**2) / (6 * a * EIz) - q * a**3 / (24 * EIz)
v_rot, th_rot = thA * L_oh + cant_v, thA + cant_t
print(f"vertical: M_A = {MzA:.0f}, theta_A = {thA:.4e}, cantilever {cant_v:.4f}; v_rot = {v_rot:.4f}, section rotation {th_rot:.4e} -> CG x {th_rot * abs(y_cg):.4f}")
