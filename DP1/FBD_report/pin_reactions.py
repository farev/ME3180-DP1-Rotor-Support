"""Part B.1: pin loads, front and rear, for the chosen design.

Uses the equilibrium equations in the report (moments about pin O; mm, N, N mm) and
checks them against a direct 3-D sum of every force and moment on the beam free body.
"""
import numpy as np

IN, g = 25.4, 9.81

# ---------------- chosen design ----------------
h, w, t_wall = 4 * IN, 6 * IN, 3 / 16 * IN      # 6546K73: 6 in wide (z) x 4 in tall (y) x 3/16 in wall, 6061-T6
t_p, b_p, L_plate = 1 / 4 * IN, 5.0 * IN, 35.75 * IN    # 8992K61: 304 stainless 1/4 x 5 in bar, 35.75 in long
a = 660.0                                         # pin A at x = -660 mm
d_hole = 0.7531 * IN                              # mid of the 0.7525-0.7537 in reamed hole
rho_al = 2700.0                                   # 6061-T6, kg/m^3
rho_plate = 8000.0                                # 304 stainless (AZoM), kg/m^3
L_beam = 1350.0
t_b = 0.5 * IN                                    # brackets, given

# ---------------- givens ----------------
xg = -1200 + 39.49 * IN
omega = 285 * 2 * np.pi / 60
tau = 0.30 * 0.5 * 1000 * 0.25 * 2.5 ** 3 / omega * 1000        # N mm
r1, r2 = 9.554 * IN / 2, 3.038 * IN / 2
T = tau / r1
nx = (r1 - r2) / (xg + 1200); nz = -np.sqrt(1 - nx ** 2)

# ---------------- derived ----------------
A_beam = w / IN * h / IN - (w / IN - 2 * t_wall / IN) * (h / IN - 2 * t_wall / IN)   # in^2, sharp corners
W_b = A_beam * IN ** 2 * 1e-9 * rho_al * g * L_beam
W_p = (b_p * t_p * L_plate - 2 * np.pi / 4 * d_hole ** 2 * t_p) * 1e-9 * rho_plate * g
z_b, z_p = w / 2 + t_b / 2, w / 2 + t_p / 2
L_AB = np.hypot(a, 500); s, c = 500 / L_AB, a / L_AB
yb, yc = -h / 2, -h / 2 - 50
P1 = np.array([-1200 + r1 * nx, yc, r1 * nz]); P2 = np.array([xg + r2 * nx, yc, r2 * nz]); u = (P2 - P1) / np.linalg.norm(P2 - P1)

# ---------------- closed-form solution (same as the report) ----------------
M_x = -560 * (h / 2 + 500)
M_y = 560 * 1200 + tau
M_z = 150 * 1200 + 120 * (-xg) + 625 * W_b + a * W_p
O_z = -560.0
dP = -M_x / (z_p * s)                 # P_r - P_f
SP = M_z / (a * s)                    # P_f + P_r
P_f, P_r = (SP - dP) / 2, (SP + dP) / 2
O_y = ((270 + W_b + W_p) - SP * s) / 2
SOx = -SP * c
dOx = -(M_y + M_x * c / s) / z_b      # O_fx - O_rx
O_fx, O_rx = (SOx + dOx) / 2, (SOx - dOx) / 2

# ---------------- independent check: direct sum of all forces and moments ----------------
loads = [([-1200, yb - 350, 0], [0, -150, 0]), ([-1200, yb - 500, 0], [0, 0, 560]), (P1, T * u), (P2, -T * u),
         ([xg, h / 2, 0], [0, -120, 0]), ([-625, 0, 0], [0, -W_b, 0]), ([-a, 0, z_p], [0, -W_p / 2, 0]), ([-a, 0, -z_p], [0, -W_p / 2, 0]),
         ([0, 0, z_b], [O_fx, O_y, O_z]), ([0, 0, -z_b], [O_rx, O_y, 0]), ([-a, 0, z_p], P_f * np.array([c, s, 0])), ([-a, 0, -z_p], P_r * np.array([c, s, 0]))]
F = sum(np.array(f, float) for _, f in loads)
M = sum(np.cross(np.array(r, float), np.array(f, float)) for r, f in loads) + np.array([0, tau, 0])
assert np.abs(F).max() < 1e-6 and np.abs(M).max() < 1e-3, (F, M)

if __name__ == "__main__":
    print(f"W_b = {W_b:.2f} N (A = {A_beam:.3f} in^2), W_p = {W_p:.2f} N each, z_b = {z_b:.2f}, z_p = {z_p:.2f} mm")
    print(f"alpha = {np.degrees(np.arctan2(500, a)):.2f} deg, sin = {s:.4f}, cos = {c:.4f}, L_AB = {L_AB:.1f} mm")
    print(f"Sum of known loads: Fy = {-(270 + W_b + W_p):.1f} N; M_O = ({M_x:.0f}, {M_y:.0f}, {M_z:.0f}) N mm")
    print(f"P_r - P_f = {dP:.1f}, P_f + P_r = {SP:.1f}  ->  P_f = {P_f:.1f} N, P_r = {P_r:.1f} N")
    print(f"O_fx + O_rx = {SOx:.1f}, O_fx - O_rx = {dOx:.1f}, O_y = {O_y:.1f} each, O_z = {O_z:.0f}")
    rows = [("O", "Front", (O_fx, O_y, O_z)), ("O", "Rear", (O_rx, O_y, 0.0)),
            ("A", "Front", tuple(P_f * np.array([c, s, 0]))), ("A", "Rear", tuple(P_r * np.array([c, s, 0]))),
            ("B", "Front", tuple(-P_f * np.array([c, s, 0]))), ("B", "Rear", tuple(-P_r * np.array([c, s, 0])))]
    for p, side, f in rows:
        print(f"{p} {side:5s}  ({f[0]:8.1f}, {f[1]:8.1f}, {f[2]:7.1f})  |F| = {np.linalg.norm(f):7.1f} N")
    print("equilibrium residual: F", np.abs(F).max(), " M", np.abs(M).max())
