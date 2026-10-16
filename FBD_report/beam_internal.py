"""Part C: internal loads and stresses in the support beam (chosen design).

Section cut at x; resultant that the part to the RIGHT of the cut exerts on the LEFT part
(free end at x = -1300): F = -sum(F_left), M = -sum((r - x i) x F_left) - sum(C_left).
N > 0 tension; T = Mx.  Units: mm, N, N mm, MPa.
"""
import numpy as np
from pin_reactions import (IN, h, w, t_wall, a, xg, tau, T, P1, P2, u, W_b, W_p, z_b, z_p,
                           O_fx, O_rx, O_y, O_z, P_f, P_r, s, c, yb)

x_l, x_r = -1300.0, 50.0
q = W_b / (x_r - x_l)
# point loads: (x where it enters the beam, application point, force, couple)
pts = [(-1200, [-1200, yb - 350, 0], [0, -150, 0], [0, 0, 0]),
       (-1200, [-1200, yb - 500, 0], [0, 0, 560], [0, 0, 0]),
       (-1200, [-1200, 0, 0], [0, 0, 0], [0, tau, 0]),
       (-1200, P1, T * u, [0, 0, 0]),
       (xg, P2, -T * u, [0, 0, 0]),
       (xg, [xg, h / 2, 0], [0, -120, 0], [0, 0, 0]),
       (-a, [-a, 0, z_p], [0, -W_p / 2, 0], [0, 0, 0]), (-a, [-a, 0, -z_p], [0, -W_p / 2, 0], [0, 0, 0]),
       (-a, [-a, 0, z_p], P_f * np.array([c, s, 0]), [0, 0, 0]), (-a, [-a, 0, -z_p], P_r * np.array([c, s, 0]), [0, 0, 0]),
       (0, [0, 0, z_b], [O_fx, O_y, O_z], [0, 0, 0]), (0, [0, 0, -z_b], [O_rx, O_y, 0], [0, 0, 0])]

def internal(x):
    F = np.zeros(3); M = np.zeros(3); o = np.array([x, 0, 0])
    for xt, r, f, C in pts:
        if xt < x:
            F += f; M += np.cross(np.array(r, float) - o, f) + np.array(C, float)
    L = x - x_l; fw = np.array([0, -q * L, 0])                 # self-weight left of the cut
    F += fw; M += np.cross(np.array([x_l + L / 2, 0, 0]) - o, fw)
    return -F, -M                                              # N, Vy, Vz ; T, My, Mz

# section (sharp corners, McMaster 6546K73)
A = w * h - (w - 2 * t_wall) * (h - 2 * t_wall)
Iz = (w * h**3 - (w - 2 * t_wall) * (h - 2 * t_wall)**3) / 12        # vertical bending (about z)
Iy = (h * w**3 - (h - 2 * t_wall) * (w - 2 * t_wall)**3) / 12        # lateral bending (about y)
Am = (w - t_wall) * (h - t_wall)
Sy = 241.3                                                         # McMaster: 35,000 psi

def stresses(x):
    (N, Vy, Vz), (Tx, My, Mz) = internal(x)
    corners = [(sy * h / 2, sz * w / 2) for sy in (1, -1) for sz in (1, -1)]
    sig = max((N / A - Mz * y / Iz + My * z / Iy for y, z in corners), key=abs)
    tau_t = abs(Tx) / (2 * Am * t_wall)
    return N, Tx, My, Mz, sig, tau_t, np.sqrt(sig**2 + 3 * tau_t**2)

if __name__ == "__main__":
    print(f"A = {A:.1f} mm2, Iz = {Iz:.4e}, Iy = {Iy:.4e} mm4, Am = {Am:.0f} mm2, Sz=Iz/(h/2) = {Iz/(h/2):.0f}, Sy=Iy/(w/2) = {Iy/(w/2):.0f}")
    xs = np.unique(np.concatenate([np.linspace(x_l, x_r, 2701), [-1200 + 1e-6, -660 - 1e-6, -660 + 1e-6, xg - 1e-6, xg + 1e-6, -1e-6, 1e-6]]))
    R = np.array([stresses(x) for x in xs])
    names = ["N", "T", "My", "Mz", "sigma", "tau", "vm"]
    for i, n in enumerate(names):
        k = np.argmax(np.abs(R[:, i])); print(f"peak |{n}| = {R[k, i]:.1f} at x = {xs[k]:.1f}")
    for x in [-1250, -1200 + 1e-6, -900, -660 - 1e-6, -660 + 1e-6, -400, xg - 1e-6, xg + 1e-6, -100, -1e-6, 1e-6]:
        N, Tx, My, Mz, sg, tt, vm = stresses(x)
        print(f"x={x:8.1f}  N={N:8.1f}  T={Tx:9.0f}  My={My:9.0f}  Mz={Mz:9.0f}  sig={sg:6.2f}  tau={tt:5.2f}  vm={vm:6.2f}")
