"""Report figures for DP1 Part A.2: free-body diagram of the support beam + load table.

Run:  python3 make_fbd_figures.py      (writes PNG figures and the table CSV next to this file)

Everything the design has not fixed yet is a SYMBOL in the figures and the table:
  h  beam height, w beam width, t_p plate thickness, a  pin-A distance from pin O,
  W_b beam weight, W_p weight of one plate,  z_b = w/2 + t_b/2,  z_p = w/2 + t_p/2,  tan(alpha) = 500/a.
Only quantities set by the problem statement are printed as numbers.
"""
import csv, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon, Arc, FancyArrowPatch

HERE = os.path.dirname(os.path.abspath(__file__))
IN = 25.4

# ---- DRAWING-ONLY proportions. These set where things are drawn; no label or table entry uses them. ----
a, h, w, tp, bp = 500.0, 101.6, 101.6, 6.35, 50.8
tb = 0.5 * IN                     # bracket thickness, given (1/2 in)

# ---- quantities fixed by the problem statement ----
xL, xR = -1300.0, 50.0            # beam ends (100 mm past rotor axis; 50 mm past pin O, Fig. 2)
xg = -1200 + 39.49 * IN           # generator shaft
omega = 285 * 2 * np.pi / 60
P_fluid = 0.5 * 1000 * 0.25 * 2.5 ** 3; P_mech = 0.30 * P_fluid; P_elec = 0.82 * P_mech
tau = P_mech / omega              # N m
r1, r2 = 9.554 * IN / 2, 3.038 * IN / 2
T = tau / (r1 / 1000)             # chain tension, tight span
nx = (r1 - r2) / (xg + 1200); nz = -np.sqrt(1 - nx ** 2)

def geometry(h, w, tp, a):
    yb, yc = -h / 2, -h / 2 - 50
    P1 = np.array([-1200 + r1 * nx, yc, r1 * nz]); P2 = np.array([xg + r2 * nx, yc, r2 * nz])
    u = (P2 - P1) / np.linalg.norm(P2 - P1)
    return yb, yc, w / 2 + tb / 2, w / 2 + tp / 2, P1, P2, u

yb, yc, zb, zp, P1, P2, u = geometry(h, w, tp, a)
L = np.hypot(a, 500); ua = np.array([a / L, 500 / L, 0]); alpha = np.degrees(np.arctan2(500, a))

# symbolic resultant of the known loads about O (N, mm, N mm) -- constants computed from the givens
MY_CONST = 560 * 1200 + tau * 1000
MZ_CONST = 150 * 1200 + 120 * (-xg)

def known_loads(h, w, tp, a, Wb, Wp):
    yb, yc, zb, zp, P1, P2, u = geometry(h, w, tp, a)
    return [  # r [mm], F [N], C [N mm]
        ([-1200, yb - 350, 0], [0, -150, 0], None), ([-1200, yb - 500, 0], [0, 0, 560], None), ([-1200, 0, 0], None, [0, tau * 1000, 0]),
        (P1, T * u, None), (P2, -T * u, None), ([xg, h / 2, 0], [0, -120, 0], None), ([(xL + xR) / 2, 0, 0], [0, -Wb, 0], None),
        ([-a, 0, zp], [0, -Wp / 2, 0], None), ([-a, 0, -zp], [0, -Wp / 2, 0], None)]

def check_symbolic_sums():
    """The printed sums must equal a brute-force sum for any design values."""
    rng = np.random.default_rng(1)
    for _ in range(20):
        hh, ww, tt, aa, Wb, Wp = rng.uniform(50, 200), rng.uniform(101.6, 200), rng.uniform(3, 15), rng.uniform(200, 800), rng.uniform(0, 500), rng.uniform(0, 60)
        F = np.zeros(3); M = np.zeros(3)
        for r, Fv, C in known_loads(hh, ww, tt, aa, Wb, Wp):
            if Fv is not None: F += Fv; M += np.cross(r, Fv)
            if C is not None: M += C
        sym_F = np.array([0, -(270 + Wb + Wp), 560]); sym_M = np.array([-560 * (hh / 2 + 500), MY_CONST, MZ_CONST + 625 * Wb + aa * Wp])
        assert np.allclose(F, sym_F, atol=1e-6) and np.allclose(M, sym_M, atol=1e-3), (F, sym_F, M, sym_M)

# ---------------- style ----------------
plt.rcParams.update({
    "font.family": "STIXGeneral", "mathtext.fontset": "stix", "font.size": 10,
    "svg.fonttype": "none", "pdf.fonttype": 42, "axes.linewidth": 0.6,
})
C_APP = "#1d3f8f"     # known applied loads
C_RXN = "#b0242a"     # unknown reactions (assumed positive sense)
C_CHN = "#a86b00"     # chain forces
C_BODY = "#e9ecf0"; C_BODY2 = "#d6dbe2"; C_EDGE = "#2b2f36"; C_DIM = "#333333"; C_GHOST = "#8a929c"
LW = 0.9

def new_ax(xlim, ylim, width_in):
    hgt = width_in * (ylim[1] - ylim[0]) / (xlim[1] - xlim[0])
    fig = plt.figure(figsize=(width_in, hgt))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect("equal"); ax.axis("off")
    return fig, ax

def rect(ax, x, y, wd, ht, fc=C_BODY, ec=C_EDGE, lw=LW, ls="-", z=1, alpha=1):
    ax.add_patch(Rectangle((x, y), wd, ht, fc=fc, ec=ec, lw=lw, ls=ls, zorder=z, alpha=alpha))

def arrow(ax, p0, p1, c, lw=1.6, z=6, ms=11):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=ms, color=c, lw=lw, zorder=z,
                                 shrinkA=0, shrinkB=0, joinstyle="miter", capstyle="butt"))

def txt(ax, x, y, s, c="k", ha="left", va="center", size=10.5, z=8, **kw):
    ax.text(x, y, s, color=c, ha=ha, va=va, fontsize=size, zorder=z,
            bbox=dict(fc="white", ec="none", pad=0.6, alpha=0.85), **kw)

def outof(ax, x, y, c, r=16, z=7):   # vector toward viewer
    ax.add_patch(Circle((x, y), r, fc="white", ec=c, lw=1.5, zorder=z)); ax.add_patch(Circle((x, y), r * 0.28, fc=c, ec=c, zorder=z + 0.1))

def into(ax, x, y, c, r=16, z=7):    # vector away from viewer
    ax.add_patch(Circle((x, y), r, fc="white", ec=c, lw=1.5, zorder=z))
    k = r * 0.62; ax.plot([x - k, x + k], [y - k, y + k], color=c, lw=1.4, zorder=z + 0.1); ax.plot([x - k, x + k], [y + k, y - k], color=c, lw=1.4, zorder=z + 0.1)

def dim(ax, p0, p1, off, label, ext0=None, ext1=None, tsize=9.5, tpos=0.5, rot=None):
    """Linear dimension between p0 and p1, offset by vector off; ext0/ext1 are the feature points for extension lines."""
    p0, p1, off = np.array(p0, float), np.array(p1, float), np.array(off, float)
    q0, q1 = p0 + off, p1 + off
    n = off / (np.linalg.norm(off) or 1)
    for e, q in ((ext0 if ext0 is not None else p0, q0), (ext1 if ext1 is not None else p1, q1)):
        e = np.array(e, float); s = e + n * 6
        ax.plot([s[0], q[0] + n[0] * 8], [s[1], q[1] + n[1] * 8], color=C_DIM, lw=0.45, zorder=2)
    ax.add_patch(FancyArrowPatch(q0, q1, arrowstyle="<|-|>", mutation_scale=6.5, color=C_DIM, lw=0.55, zorder=2, shrinkA=0, shrinkB=0))
    m = q0 + (q1 - q0) * tpos
    d = q1 - q0; ang = np.degrees(np.arctan2(d[1], d[0])) if rot is None else rot
    if ang > 90: ang -= 180
    if ang < -90: ang += 180
    ax.text(m[0], m[1], label, fontsize=tsize, ha="center", va="center", rotation=ang, color=C_DIM, zorder=3,
            bbox=dict(fc="white", ec="none", pad=0.8))

def cg_mark(ax, x, y, r=14):
    ax.add_patch(Circle((x, y), r, fc="white", ec="k", lw=0.9, zorder=5))
    ax.add_patch(matplotlib.patches.Wedge((x, y), r, 0, 90, fc="k", zorder=5.1)); ax.add_patch(matplotlib.patches.Wedge((x, y), r, 180, 270, fc="k", zorder=5.1))

def pin(ax, x, y, r=9, z=5):
    ax.add_patch(Circle((x, y), r, fc="white", ec="k", lw=0.9, zorder=z))

def triad(ax, o, axes, L=95, lab=None):
    for (dx, dy), name in zip(axes, lab):
        if dx is None:  # out-of-plane marker
            (outof if dy > 0 else into)(ax, o[0], o[1], "k", r=11, z=4); ax.text(o[0] - 20, o[1] - 22, name, fontsize=11, style="italic", ha="right", va="top", zorder=4); continue
        ax.add_patch(FancyArrowPatch(o, (o[0] + dx * L, o[1] + dy * L), arrowstyle="-|>", mutation_scale=9, color="k", lw=0.9, zorder=4, shrinkA=0, shrinkB=0))
        ax.text(o[0] + dx * (L + 22), o[1] + dy * (L + 22), name, fontsize=11, style="italic", ha="center", va="center", zorder=4)

def legend(ax, x, y, extra=None, dy=34):
    items = [(C_APP, "Applied load"), (C_CHN, "Chain force"), (C_RXN, "Pin reaction (assumed + sense)")]
    for i, (c, s) in enumerate(items):
        yy = y - i * dy
        ax.add_patch(FancyArrowPatch((x, yy), (x + 70, yy), arrowstyle="-|>", mutation_scale=8, color=c, lw=1.4, shrinkA=0, shrinkB=0))
        ax.text(x + 85, yy, s, fontsize=9, va="center")
    lines = ["Dimensions in mm"] + (extra or [])
    for j, s in enumerate(lines):
        ax.text(x, y - (len(items) + j) * dy, s, fontsize=9, va="center", color="#444")

def save(fig, name):
    for ext in ("png",):
        fig.savefig(os.path.join(HERE, f"{name}.{ext}"), dpi=300, facecolor="white")
    plt.close(fig)

ALEN = 175  # arrow length in mm (drawing units)

# =====================================================================================
# (a) SIDE VIEW  x right, y up, viewed from +z (front)
# =====================================================================================
def side_view():
    fig, ax = new_ax((-1720, 520), (-760, 630), 7.2)
    yt = h / 2
    # body
    rect(ax, -1450, yb - 625, 500, 500, fc="#f4f6f8", z=1)                         # rotor drum
    rect(ax, -1220, yb - 625, 40, 500, fc=C_BODY2, z=1.1)                          # rotor shaft band
    ax.text(-1440, yb - 610, "Rotor assembly", fontsize=8.5, color="#555", va="bottom")
    ax.plot([-1200, -1200], [yb, yb - 125], color=C_EDGE, lw=2.2, zorder=1.2)        # shaft
    rect(ax, -1200 - r1, yc - 7, 2 * r1, 14, fc=C_BODY2, z=1.3)                     # rotor sprocket
    ax.plot([xg, xg], [yb, yc], color=C_EDGE, lw=1.8, zorder=1.2)
    rect(ax, xg - r2, yc - 7, 2 * r2, 14, fc=C_BODY2, z=1.3)                        # generator sprocket
    rect(ax, xL, yb, xR - xL, h, z=2)                                               # beam
    rect(ax, -1300, yt, 200, 150, fc=C_BODY2, z=2)                                  # shaft box
    ax.text(-1200, yt + 75, "Shaft\nbox", fontsize=8.5, ha="center", va="center", color="#444", zorder=3)
    rect(ax, xg - 40, yt, 80, 100, fc=C_BODY2, z=2)                                 # generator
    ax.text(xg, yt + 50, "Gen.", fontsize=8.5, ha="center", va="center", color="#444", zorder=3)
    pin(ax, 0, 0); pin(ax, -a, 0)
    ax.text(-20, -22, "O", fontsize=12, ha="right", va="top", weight="bold", zorder=9)
    ax.text(-a - 18, -20, "A", fontsize=12, ha="right", va="top", weight="bold", zorder=9)
    cg_mark(ax, -1200, yb - 350)
    ax.add_patch(Circle((-1200, yb - 500), 9, fc="white", ec="k", lw=0.9, zorder=5))
    ax.text(-1180, yb - 350 + 4, "CG", fontsize=9.5, ha="left", va="bottom", zorder=8)
    ax.text(-1225, yb - 500 - 30, "COP", fontsize=9.5, ha="right", va="top", zorder=8)
    # plate line of action and B
    ax.plot([-a, 0], [0, 500], color=C_GHOST, lw=0.8, ls=(0, (6, 4)), zorder=1.5)
    ax.add_patch(Circle((0, 500), 9, fc="white", ec=C_GHOST, lw=0.9, zorder=3))
    ax.text(18, 512, "B", fontsize=8.5, color="#666", va="bottom")
    ax.add_patch(Arc((-a, 0), 150, 150, theta1=0, theta2=alpha, color="k", lw=0.6, zorder=3))
    ax.text(-a + 92 * np.cos(np.radians(alpha / 2)), 92 * np.sin(np.radians(alpha / 2)), r"$\alpha$", fontsize=9.5, ha="left", va="center", zorder=8)

    # ---- applied loads
    arrow(ax, (-1200, yb - 350 + 110), (-1200, yb - 350 + 16), C_APP)
    txt(ax, -1232, yb - 350 + 45, r"$W_r$ = 150 N", C_APP, ha="right")
    outof(ax, -1200, yb - 500, C_APP, r=17)
    txt(ax, -1170, yb - 500, r"$D$ = 560 N  (+$z$)", C_APP)
    # water torque: rotation about +y drawn as an ellipse around the shaft
    ecx, ecy = -1200, yb - 175
    th = np.linspace(np.radians(200), np.radians(-20), 60)    # front half of the ellipse moves toward +x
    ax.plot(ecx + 95 * np.cos(th), ecy + 26 * np.sin(th), color=C_APP, lw=1.5, zorder=6)
    ax.add_patch(FancyArrowPatch((ecx + 95 * np.cos(th[-3]), ecy + 26 * np.sin(th[-3])), (ecx + 95 * np.cos(th[-1]) + 4, ecy + 26 * np.sin(th[-1]) + 3),
                                 arrowstyle="-|>", mutation_scale=10, color=C_APP, lw=1.5, zorder=6, shrinkA=0, shrinkB=0))
    txt(ax, -1090, ecy - 40, rf"$\tau_w$ = {tau:.2f} N$\cdot$m", C_APP)
    arrow(ax, (xg, yt + 100 + 150), (xg, yt + 100), C_APP)
    txt(ax, xg + 16, yt + 100 + 95, r"$W_g$ = 120 N", C_APP)
    xc = (xL + xR) / 2
    arrow(ax, (xc, yb), (xc, yb - 190), C_APP)
    txt(ax, xc, yb - 230, r"$W_b$", C_APP, ha="center")
    arrow(ax, (-a, 130), (-a, 11), C_APP, lw=1.3, ms=9)
    txt(ax, -a - 14, 105, r"$W_p/2$ (each plate)", C_APP, ha="right", size=9.5)
    # chain
    arrow(ax, (P1[0], yc), (P1[0] + ALEN, yc), C_CHN)
    txt(ax, P1[0] + 20, yc - 36, rf"$T_{{c1}}$ = {T:.1f} N", C_CHN, size=10)
    arrow(ax, (P2[0], yc), (P2[0] - ALEN, yc), C_CHN)
    txt(ax, P2[0] + 50, yc - 40, rf"$T_{{c2}}$ = {T:.1f} N", C_CHN, size=10)
    # ---- reactions (assumed + sense)
    arrow(ax, (12, 0), (12 + 190, 0), C_RXN)
    txt(ax, 210, 2, r"$O_{f,x},\ O_{r,x}$", C_RXN)
    arrow(ax, (0, 12), (0, 12 + 190), C_RXN)
    txt(ax, 14, 165, r"$O_{f,y},\ O_{r,y}$", C_RXN)
    outof(ax, 80, -78, C_RXN, r=15)
    ax.plot([7, 69], [-7, -67], color=C_RXN, lw=0.6, zorder=6)
    txt(ax, 102, -80, r"$O_z$ (+$z$, front side)", C_RXN, size=10)
    arrow(ax, (-a + 6 * ua[0], 6 * ua[1]), (-a + 230 * ua[0], 230 * ua[1]), C_RXN)
    txt(ax, -a + 140, 215, r"$P_f,\ P_r$ (tension +)", C_RXN, ha="right", size=10)

    # ---- dimensions
    dim(ax, (-1200, 0), (0, 0), (0, 470), "1200", ext0=(-1200, yt + 150), ext1=(0, 512))
    dim(ax, (xL, 0), (-1200, 0), (0, 380), "100", ext0=(xL, yt + 150), ext1=(-1200, yt + 150))
    dim(ax, (-a, 0), (0, 0), (0, -300), r"$a$ ($\leq$ 800)", ext0=(-a, -12), ext1=(0, -100))
    dim(ax, (xg, 0), (0, 0), (0, -380), f"{-xg:.0f}", ext0=(xg, yc - 8), ext1=(0, -100))
    dim(ax, (0, 0), (xR, 0), (0, -380), "50", ext0=(0, -100), ext1=(xR, yb), tpos=2.3)
    dim(ax, (0, 0), (0, 500), (330, 0), "500", ext0=(12, 0), ext1=(12, 500))
    xs = -1500
    dim(ax, (xL, yb), (xL, yc), (xs - xL, 0), "50", ext0=(xL, yb), ext1=(-1200 - r1, yc))
    dim(ax, (xL, yb), (xL, yb - 350), (xs - 70 - xL, 0), "350", ext0=(xL, yb), ext1=(-1215, yb - 350))
    dim(ax, (xL, yb), (xL, yb - 500), (xs - 140 - xL, 0), "500", ext0=(xL, yb), ext1=(-1215, yb - 500))
    dim(ax, (xL, yb), (xL, yt), (-60, 0), r"$h$", ext0=(xL, yb), ext1=(xL, yt))
    triad(ax, (-1640, 470), [(1, 0), (0, 1), (None, 1)], lab=["x", "y", "z"])
    legend(ax, -620, -560, dy=36)
    save(fig, "fig_fbd_a_side")

# =====================================================================================
# (b) BOTTOM VIEW  x right, z up, viewed from −y (matches Figure 2 bottom view)
# =====================================================================================
def bottom_view():
    fig, ax = new_ax((-1720, 520), (-470, 440), 7.2)
    ax.add_patch(Circle((-1200, 0), 250, fc="none", ec=C_GHOST, lw=0.8, ls=(0, (6, 4)), zorder=1))
    ax.text(-1200 - 250 * 0.72, 250 * 0.72 + 12, "Rotor outline", fontsize=8.5, color="#666", ha="right")
    rect(ax, xL, -w / 2, xR - xL, w, z=2)
    ax.add_patch(Circle((-1200, 0), r1, fc="#f7f8fa", ec=C_EDGE, lw=LW, zorder=3))
    ax.add_patch(Circle((xg, 0), r2, fc="#f7f8fa", ec=C_EDGE, lw=LW, zorder=3))
    ax.plot([P1[0], P2[0]], [P1[2], P2[2]], color=C_GHOST, lw=0.8, ls=(0, (6, 4)), zorder=3.5)
    for z in (zb, -zb): pin(ax, 0, z, r=7, z=6)
    for z in (zp, -zp): pin(ax, -a, z, r=7, z=6)
    ax.text(-12, zb + 14, "O front", fontsize=9, ha="right", va="bottom", zorder=9); ax.text(-12, -zb - 14, "O rear", fontsize=9, ha="right", va="top", zorder=9)
    ax.text(-a + 12, zp + 14, "A front", fontsize=9, ha="left", va="bottom", zorder=9); ax.text(-a + 12, -zp - 14, "A rear", fontsize=9, ha="left", va="top", zorder=9)
    # applied
    arrow(ax, (-1200, 6), (-1200, 6 + 205), C_APP)
    txt(ax, -1185, 175, r"$D$ = 560 N", C_APP)
    th = np.linspace(np.radians(245), np.radians(125), 60)  # clockwise seen from below = +y rotation
    R = 175
    ax.plot(-1200 + R * np.cos(th), R * np.sin(th), color=C_APP, lw=1.5, zorder=6)
    ax.add_patch(FancyArrowPatch((-1200 + R * np.cos(th[-3]), R * np.sin(th[-3])), (-1200 + R * np.cos(th[-1]) + 3, R * np.sin(th[-1]) - 2),
                                 arrowstyle="-|>", mutation_scale=10, color=C_APP, lw=1.5, zorder=6, shrinkA=0, shrinkB=0))
    txt(ax, -1200 - R - 12, -10, r"$\tau_w$ (+$y$, into page)", C_APP, ha="right", size=10)
    arrow(ax, tuple(P1[[0, 2]]), tuple(P1[[0, 2]] + ALEN * u[[0, 2]]), C_CHN)
    txt(ax, P1[0] + 30, P1[2] - 34, r"$T_{c1}$", C_CHN)
    arrow(ax, tuple(P2[[0, 2]]), tuple(P2[[0, 2]] - ALEN * u[[0, 2]]), C_CHN)
    txt(ax, P2[0] - 70, P2[2] - 48, r"$T_{c2}$", C_CHN)
    # reactions
    arrow(ax, (8, zb), (8 + 190, zb), C_RXN); txt(ax, 120, zb + 34, r"$O_{f,x}$", C_RXN)
    arrow(ax, (8, -zb), (8 + 190, -zb), C_RXN); txt(ax, 120, -zb - 34, r"$O_{r,x}$", C_RXN)
    arrow(ax, (0, zb + 8), (0, zb + 8 + 165), C_RXN); txt(ax, 14, zb + 150, r"$O_z$", C_RXN)
    arrow(ax, (-a - 183, zp), (-a - 8, zp), C_RXN); txt(ax, -a - 170, zp + 34, r"$P_f\cos\alpha$", C_RXN)
    arrow(ax, (-a - 183, -zp), (-a - 8, -zp), C_RXN); txt(ax, -a - 170, -zp - 34, r"$P_r\cos\alpha$", C_RXN)
    # dims
    dim(ax, (-1200, 0), (0, 0), (0, 400), "1200", ext0=(-1200, 255), ext1=(0, zb + 180))
    dim(ax, (-1200, 0), (xg, 0), (0, -400), f"1003 (39.49 in)", ext0=(-1200, -255), ext1=(xg, -r2))
    dim(ax, (xg, 0), (0, 0), (0, -400), f"{-xg:.0f}", ext0=(xg, -r2), ext1=(0, -zb - 10))
    dim(ax, (-a, 0), (0, 0), (0, -300), r"$a$", ext0=(-a, -zp - 10), ext1=(0, -zb - 10))
    dim(ax, (0, -zb), (0, zb), (380, 0), r"2$z_b$", ext0=(205, -zb), ext1=(205, zb))
    triad(ax, (-1650, -330), [(1, 0), (0, 1), (None, -1)], lab=["x", "z", "y"], L=80)
    save(fig, "fig_fbd_b_bottom")

# =====================================================================================
# (c) END VIEW  z right, y up, viewed from −x (from the rotor end toward the wall)
# =====================================================================================
def end_view():
    fig, ax = new_ax((-760, 900), (-710, 390), 5.6)
    yt = h / 2
    rect(ax, -250, yb - 625, 500, 500, fc="#f4f6f8", z=1)
    rect(ax, -20, yb - 625, 40, 500, fc=C_BODY2, z=1.1)
    ax.text(-240, yb - 610, "Rotor assembly", fontsize=8.5, color="#555", va="bottom")
    ax.plot([0, 0], [yb, yb - 125], color=C_EDGE, lw=2.2, zorder=1.2)
    rect(ax, -r1, yc - 7, 2 * r1, 14, fc=C_BODY2, z=1.3)
    rect(ax, -w / 2, yb, w, h, fc=C_BODY, z=2)
    ax.plot([-w / 2, w / 2], [yb, yt], color=C_EDGE, lw=0.4, zorder=2.1); ax.plot([-w / 2, w / 2], [yt, yb], color=C_EDGE, lw=0.4, zorder=2.1)
    cg_mark(ax, 0, yb - 350)
    ax.add_patch(Circle((0, yb - 500), 9, fc="white", ec="k", lw=0.9, zorder=5))
    ax.text(26, yb - 350 + 4, "CG", fontsize=9.5, ha="left", va="bottom", zorder=8)
    ax.text(-22, yb - 500 - 28, "COP", fontsize=9.5, ha="right", va="top", zorder=8)
    # applied
    arrow(ax, (0, yb - 350 + 150), (0, yb - 350 + 16), C_APP); txt(ax, -30, yb - 350 + 95, r"$W_r$", C_APP, ha="right")
    arrow(ax, (12, yb - 500), (12 + 215, yb - 500), C_APP); txt(ax, 240, yb - 500, r"$D$ = 560 N", C_APP)
    # reactions: plates (y-parts at x = −a) drawn above the pins, O_y (x = 0) pushing from below
    arrow(ax, (zp, 8), (zp, 8 + 185), C_RXN); txt(ax, zp + 14, 165, r"$P_f\sin\alpha$", C_RXN)
    arrow(ax, (-zp, 8), (-zp, 8 + 185), C_RXN); txt(ax, -zp - 14, 165, r"$P_r\sin\alpha$", C_RXN, ha="right")
    arrow(ax, (zb, -185), (zb, -8), C_RXN); txt(ax, zb + 14, -165, r"$O_{f,y}$", C_RXN)
    arrow(ax, (-zb, -185), (-zb, -8), C_RXN); txt(ax, -zb - 14, -165, r"$O_{r,y}$", C_RXN, ha="right")
    arrow(ax, (zb + 8, 0), (zb + 8 + 190, 0), C_RXN); txt(ax, zb + 205, 4, r"$O_z$", C_RXN)
    for z in (zp, -zp): pin(ax, z, 0, r=6, z=7)
    ax.text(w / 2 + 30, 62, "front", fontsize=8.5, ha="left", va="bottom", color="#444")
    ax.text(-w / 2 - 30, 62, "rear", fontsize=8.5, ha="right", va="bottom", color="#444")
    # dims
    dim(ax, (-zp, 0), (zp, 0), (0, 330), r"2$z_p$", ext0=(-zp, 200), ext1=(zp, 200))
    dim(ax, (0, 0), (0, yb - 500), (-430, 0), r"$h$/2 + 500", ext0=(-w / 2 - 10, 0), ext1=(-20, yb - 500), rot=90)
    dim(ax, (0, 0), (0, yb - 350), (-340, 0), r"$h$/2 + 350", ext0=(-w / 2 - 10, 0), ext1=(-20, yb - 350), rot=90)
    triad(ax, (-680, 230), [(1, 0), (0, 1), (None, -1)], lab=["z", "y", "x"], L=80)
    save(fig, "fig_fbd_c_end")

# =====================================================================================
# (d) ISOMETRIC overview
# =====================================================================================
TH, PH = 0.70, 0.42
CT, ST, CP, SP = np.cos(TH), np.sin(TH), np.cos(PH), np.sin(PH)
def prj(p):
    x, y, z = p
    x1 = x * CT + z * ST; z1 = -x * ST + z * CT
    return np.array([x1, y * CP - z1 * SP]), y * SP + z1 * CP

def iso_box(ax, c, hf, fcs=(C_BODY2, C_BODY, "#c7cdd6"), z0=2, ls="-", ec=C_EDGE, lw=0.8):
    c = np.array(c, float); out = []
    for d in range(3):
        for s in (-1, 1):
            n = np.zeros(3); n[d] = s
            _, dep = prj(n)
            if dep <= 1e-9: continue
            e = [k for k in range(3) if k != d]; q = []
            for s1, s2 in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                v = c.copy(); v[d] += s * hf[d]; v[e[0]] += s1 * hf[e[0]]; v[e[1]] += s2 * hf[e[1]]; q.append(prj(v)[0])
            ax.add_patch(Polygon(q, closed=True, fc=fcs[d] if fcs else "none", ec=ec, lw=lw, ls=ls, zorder=z0))

def iso_ring(ax, c, r, y, **kw):
    t = np.linspace(0, 2 * np.pi, 120); pts = np.array([prj((c[0] + r * np.cos(tt), y, c[2] + r * np.sin(tt)))[0] for tt in t])
    ax.plot(pts[:, 0], pts[:, 1], **kw); return pts

def iso_arrow(ax, p, d, c, L=ALEN, head_at_point=False, lw=1.6):
    p = np.array(p, float); d = np.array(d, float) / np.linalg.norm(d)
    tail, head = (p - d * L, p) if head_at_point else (p, p + d * L)
    arrow(ax, tuple(prj(tail)[0]), tuple(prj(head)[0]), c, lw=lw)
    return prj(head)[0], prj(tail)[0]

def iso_view():
    fig, ax = new_ax((-1150, 1150), (-1070, 620), 7.2)
    off = np.array([560, -50, 0])
    P = lambda p: np.array(p, float) + off
    # rotor drum (behind beam)
    for yy in (yb - 625, yb - 125):
        pts = iso_ring(ax, P((-1200, 0, 0)), 250, yy + off[1], color=C_EDGE, lw=0.7, zorder=1)
    top = np.array([prj(P((-1200 + 250 * np.cos(t), yb - 125, 250 * np.sin(t))))[0] for t in np.linspace(0, 2 * np.pi, 180)])
    bot = np.array([prj(P((-1200 + 250 * np.cos(t), yb - 625, 250 * np.sin(t))))[0] for t in np.linspace(0, 2 * np.pi, 180)])
    i0, i1 = np.argmin(top[:, 0]), np.argmax(top[:, 0])
    for i in (i0, i1): ax.plot([top[i, 0], bot[i, 0]], [top[i, 1], bot[i, 1]], color=C_EDGE, lw=0.7, zorder=1)
    ax.fill(np.r_[top[:, 0]], np.r_[top[:, 1]], fc="#f4f6f8", zorder=0.9)
    ax.add_patch(Polygon([top[i0], top[i1], bot[i1], bot[i0]], fc="#f4f6f8", ec="none", zorder=0.8))
    ax.fill(bot[:, 0], bot[:, 1], fc="#f4f6f8", zorder=0.8)
    a0, a1 = prj(P((-1200, yb, 0)))[0], prj(P((-1200, yb - 125, 0)))[0]
    ax.plot([a0[0], a1[0]], [a0[1], a1[1]], color=C_EDGE, lw=2, zorder=1.5)
    g0, g1 = prj(P((xg, yb, 0)))[0], prj(P((xg, yc, 0)))[0]
    ax.plot([g0[0], g1[0]], [g0[1], g1[1]], color=C_EDGE, lw=1.6, zorder=1.5)
    for c, r in (((-1200, yc, 0), r1), ((xg, yc, 0), r2)):
        pts = np.array([prj(P((c[0] + r * np.cos(t), yc, r * np.sin(t))))[0] for t in np.linspace(0, 2 * np.pi, 100)])
        ax.add_patch(Polygon(pts, fc="#f7f8fa", ec=C_EDGE, lw=0.8, zorder=1.6))
    q1, q2 = prj(P(P1))[0], prj(P(P2))[0]
    ax.plot([q1[0], q2[0]], [q1[1], q2[1]], color=C_GHOST, lw=0.8, ls=(0, (6, 4)), zorder=1.7)
    iso_box(ax, P(((xL + xR) / 2, 0, 0)), ((xR - xL) / 2, h / 2, w / 2), z0=2)
    iso_box(ax, P((-1200, h / 2 + 75, 0)), (100, 75, w / 2 * 0.95), z0=2.1)
    iso_box(ax, P((xg, h / 2 + 50, 0)), (40, 50, w / 2 * 0.7), z0=2.1)
    # plate line of action (ghost)
    for z in (zp, -zp):
        b0, b1 = prj(P((-a, 0, z)))[0], prj(P((0, 500, z)))[0]
        ax.plot([b0[0], b1[0]], [b0[1], b1[1]], color=C_GHOST, lw=0.7, ls=(0, (6, 4)), zorder=1.8)
    bb = prj(P((0, 500, zp)))[0]; ax.add_patch(Circle(bb, 8, fc="white", ec=C_GHOST, zorder=3)); ax.text(bb[0] + 14, bb[1] + 6, "B", fontsize=10, color="#666")
    for pt, nm, dx, dy in (((0, 0, 0), "O", 16, 34), ((-a, 0, zp), "A", -24, 30)):
        q = prj(P(pt))[0]; ax.text(q[0] + dx, q[1] + dy, nm, fontsize=12, weight="bold", ha="center", zorder=9)
    for pt in ((0, 0, zb), (0, 0, -zb), (-a, 0, zp), (-a, 0, -zp)):
        ax.add_patch(Circle(prj(P(pt))[0], 6, fc="white", ec="k", lw=0.8, zorder=5))
    cgq = prj(P((-1200, yb - 350, 0)))[0]; cg_mark(ax, *cgq, r=12)
    cpq = prj(P((-1200, yb - 500, 0)))[0]; ax.add_patch(Circle(cpq, 8, fc="white", ec="k", lw=0.8, zorder=5))
    ax.text(cgq[0] + 18, cgq[1] + 4, "CG", fontsize=9.5, zorder=8); ax.text(cpq[0] - 16, cpq[1] - 8, "COP", fontsize=9.5, ha="right", va="top", zorder=8)

    def lab(q, s, c, dx=10, dy=0, ha="left", size=10.5):
        txt(ax, q[0] + dx, q[1] + dy, s, c, ha=ha, size=size)
    _, tl = iso_arrow(ax, P((-1200, yb - 350 + 14, 0)), (0, -1, 0), C_APP, L=120, head_at_point=True); lab(tl, r"$W_r$", C_APP, dx=-14, dy=-60, ha="right")
    hd, _ = iso_arrow(ax, P((-1200, yb - 500, 12)), (0, 0, 1), C_APP, L=240); lab(hd, r"$D$", C_APP, dx=8, dy=-8)
    # water torque about +y near rotor top
    cyy = yb - 175
    th = np.linspace(np.radians(150), np.radians(-200), 90)
    ring = np.array([prj(P((-1200 + 105 * np.cos(t), cyy, 105 * np.sin(t))))[0] for t in -th])
    ax.plot(ring[:-2, 0], ring[:-2, 1], color=C_APP, lw=1.5, zorder=6)
    ax.add_patch(FancyArrowPatch(tuple(ring[-4]), tuple(ring[-1]), arrowstyle="-|>", mutation_scale=10, color=C_APP, lw=1.5, shrinkA=0, shrinkB=0, zorder=6))
    lab(ring[45], r"$\tau_w$", C_APP, dx=-12, dy=-14, ha="right")
    _, tl = iso_arrow(ax, P((xg, h / 2 + 100, 0)), (0, -1, 0), C_APP, L=150, head_at_point=True); lab(tl, r"$W_g$", C_APP, dx=-12, dy=-6, ha="right")
    hd, _ = iso_arrow(ax, P(((xL + xR) / 2, -h / 2, 0)), (0, -1, 0), C_APP, L=150); lab(hd, r"$W_b$", C_APP, dy=-6)
    for z in (zp, -zp):
        hd, _ = iso_arrow(ax, P((-a, -h / 2, z)), (0, -1, 0), C_APP, L=95, lw=1.2)
    lab(hd, r"$W_p/2$ (×2)", C_APP, dx=-50, dy=-14, ha="right", size=9.5)
    hd, _ = iso_arrow(ax, P(P1), u, C_CHN, L=200); lab(hd, r"$T_{c1}$", C_CHN, dx=6, dy=-14)
    hd, _ = iso_arrow(ax, P(P2), -u, C_CHN, L=200); lab(hd, r"$T_{c2}$", C_CHN, dx=10, dy=-22)
    # reactions
    hd, _ = iso_arrow(ax, P((8, 0, zb)), (1, 0, 0), C_RXN, L=210); lab(hd, r"$O_{f,x}$", C_RXN, dx=6, dy=-12)
    hd, _ = iso_arrow(ax, P((8, 0, -zb)), (1, 0, 0), C_RXN, L=210); lab(hd, r"$O_{r,x}$", C_RXN, dx=6, dy=8)
    hd, _ = iso_arrow(ax, P((0, 8, zb)), (0, 1, 0), C_RXN, L=180); lab(hd, r"$O_{f,y}$", C_RXN, dx=10, dy=4)
    hd, _ = iso_arrow(ax, P((0, 8, -zb)), (0, 1, 0), C_RXN, L=180); lab(hd, r"$O_{r,y}$", C_RXN, dx=-10, dy=4, ha="right")
    hd, _ = iso_arrow(ax, P((0, 0, zb + 8)), (0, 0, 1), C_RXN, L=200); lab(hd, r"$O_z$", C_RXN, dx=-4, dy=-14, ha="right")
    hd, _ = iso_arrow(ax, P((-a, 0, zp) + 8 * ua), ua, C_RXN, L=230); lab(hd, r"$P_f$", C_RXN, dx=10, dy=-14)
    hd, _ = iso_arrow(ax, P((-a, 0, -zp) + 8 * ua), ua, C_RXN, L=230); lab(hd, r"$P_r$", C_RXN, dx=-10, dy=6, ha="right")
    # triad
    o = np.array([-1060, -990])
    for v, nm in (((1, 0, 0), "x"), ((0, 1, 0), "y"), ((0, 0, 1), "z")):
        q = prj(v)[0]
        ax.add_patch(FancyArrowPatch(tuple(o), tuple(o + q * 85), arrowstyle="-|>", mutation_scale=9, color="k", lw=0.9, shrinkA=0, shrinkB=0))
        ax.text(*(o + q * 108), nm, fontsize=11, style="italic", ha="center", va="center")
    save(fig, "fig_fbd_d_iso")

# =====================================================================================
# TABLE (Part A.2): locations and vector components
# =====================================================================================
def f(v, d=1):
    if abs(v) < 0.5 * 10 ** -d: v = 0.0
    s = f"{abs(v) + 1e-9:.{d}f}"   # round half up
    return ("−" if v < 0 else "") + s

def thou(v):  # 691633 -> "691 633"
    return f"{v:,.0f}".replace(",", " ")

def table():
    known = [
        ("Rotor assembly weight", r"$W_r$", "Rotor CG", ("−1200", r"$-(h/2 + 350)$", "0"), ("0", "−150", "0"), ("0", "0", "0")),
        ("Water drag", r"$D$", "Center of pressure", ("−1200", r"$-(h/2 + 500)$", "0"), ("0", "0", "560"), ("0", "0", "0")),
        ("Water torque on rotor", r"$\tau_w$", "Rotor shaft (couple)", ("−1200", "any", "0"), ("0", "0", "0"), ("0", thou(tau * 1000), "0")),
        ("Chain, tight span, on rotor sprocket", r"$T_{c1}$", "Rotor sprocket, tangent pt", (f(P1[0]), r"$-(h/2 + 50)$", f(P1[2])), (f(T * u[0]), "0", f(T * u[2])), ("0", "0", "0")),
        ("Chain, tight span, on generator sprocket", r"$T_{c2}$", "Gen. sprocket, tangent pt", (f(P2[0]), r"$-(h/2 + 50)$", f(P2[2])), (f(-T * u[0]), "0", f(-T * u[2])), ("0", "0", "0")),
        ("Generator + sprocket weight", r"$W_g$", "Generator shaft axis", (f(xg), "any", "0"), ("0", "−120", "0"), ("0", "0", "0")),
        ("Beam self-weight", r"$W_b$", "Beam centroid", (f((xL + xR) / 2, 0), "0", "0"), ("0", r"$-W_b$", "0"), ("0", "0", "0")),
        ("Front plate, half weight", r"$W_p/2$", "Pin A, front", (r"$-a$", "0", r"$+z_p$"), ("0", r"$-W_p/2$", "0"), ("0", "0", "0")),
        ("Rear plate, half weight", r"$W_p/2$", "Pin A, rear", (r"$-a$", "0", r"$-z_p$"), ("0", r"$-W_p/2$", "0"), ("0", "0", "0")),
    ]
    unknown = [
        ("Pin O, front side (bracket on beam)", r"$\mathbf{O}_f$", "Pin O, +z side", ("0", "0", r"$+z_b$"), (r"$O_{f,x}$", r"$O_{f,y}$", r"$O_z$")),
        ("Pin O, rear side (bracket on beam)", r"$\mathbf{O}_r$", "Pin O, −z side", ("0", "0", r"$-z_b$"), (r"$O_{r,x}$", r"$O_{r,y}$", "0")),
        ("Front plate on beam (two-force)", r"$\mathbf{P}_f$", "Pin A, +z side", (r"$-a$", "0", r"$+z_p$"), (r"$P_f\cos\alpha$", r"$P_f\sin\alpha$", "0")),
        ("Rear plate on beam (two-force)", r"$\mathbf{P}_r$", "Pin A, −z side", (r"$-a$", "0", r"$-z_p$"), (r"$P_r\cos\alpha$", r"$P_r\sin\alpha$", "0")),
    ]
    rows = []
    for i, (name, sym, where, r, F, C) in enumerate(known, 1):
        rows.append(dict(n=str(i), name=name, sym=sym, where=where, x=r[0], y=r[1], z=r[2], Fx=F[0], Fy=F[1], Fz=F[2], Mx=C[0], My=C[1], Mz=C[2], kind="known"))
    for j, (name, sym, where, r, F) in enumerate(unknown, len(known) + 1):
        rows.append(dict(n=str(j), name=name, sym=sym, where=where, x=r[0], y=r[1], z=r[2], Fx=F[0], Fy=F[1], Fz=F[2], Mx="0", My="0", Mz="0", kind="unknown"))

    cols = [("n", "#", "c", 0.28), ("name", "Load", "l", 2.55), ("sym", "Sym.", "c", 0.5), ("where", "Acts at", "l", 1.7),
            ("x", "x", "r", 0.65), ("y", "y", "r", 1.05), ("z", "z", "r", 0.62),
            ("Fx", r"$F_x$", "r", 0.95), ("Fy", r"$F_y$", "r", 0.95), ("Fz", r"$F_z$", "r", 0.55),
            ("Mx", r"$M_x$", "r", 0.45), ("My", r"$M_y$", "r", 0.72), ("Mz", r"$M_z$", "r", 0.45)]
    X = np.r_[0, np.cumsum([c[3] for c in cols])]
    rh = 0.255
    notes = [
        r"$h$ beam height, $w$ beam width ($\geq$ 101.6), $t_p$ plate thickness, $a$ distance from pin O to pin A ($\leq$ 800), $W_b$ beam weight, $W_p$ weight of one plate.",
        r"$z_b = w/2 + t_b/2 = w/2 + 6.35$ (brackets $t_b$ = 12.7);   $z_p = w/2 + t_p/2$;   $\cos\alpha = a/\sqrt{a^2 + 500^2}$,  $\sin\alpha = 500/\sqrt{a^2 + 500^2}$.",
    ]
    H = 0.75 + rh * (len(rows) + 2) + 0.27 * 3 + 0.25 * len(notes) - 0.2
    fig = plt.figure(figsize=(X[-1] + 0.3, H)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(-0.15, X[-1] + 0.15); ax.set_ylim(0, H); ax.axis("off")
    y = H - 0.22
    ax.text(0, y, "Table 1. External loads on the support-beam free body (Figure 2 coordinates, origin at pin O on the beam neutral axis)", fontsize=10.5, weight="bold", va="top")
    y -= 0.4
    def hline(yy, lw): ax.plot([0, X[-1]], [yy, yy], color="k", lw=lw)
    hline(y, 1.1)
    for g0, g1, t in ((4, 7, "Location (mm)"), (7, 10, "Force (N)"), (10, 13, r"Couple (N$\cdot$mm)")):
        ax.text((X[g0] + X[g1]) / 2, y - 0.13, t, ha="center", va="center", fontsize=9.5)
        ax.plot([X[g0] + 0.06, X[g1] - 0.06], [y - 0.25, y - 0.25], color="k", lw=0.5)
    y -= 0.27
    al_ha = {"l": "left", "c": "center", "r": "right"}
    def put(k_al, x0, x1, yy, s, **kw):
        xx = {"l": x0 + 0.05, "c": (x0 + x1) / 2, "r": x1 - 0.06}[k_al]
        ax.text(xx, yy - rh / 2, s, ha=al_ha[k_al], va="center", **kw)
    for (k, head, al, _), x0, x1 in zip(cols, X[:-1], X[1:]): put(al, x0, x1, y, head, fontsize=9.5, weight="bold")
    y -= rh; hline(y, 0.6)
    def section(label):
        nonlocal y
        ax.text(0.05, y - 0.14, label, fontsize=9, style="italic", va="center", color="#333"); y -= 0.27
    def body(kind):
        nonlocal y
        for i, r in enumerate([r for r in rows if r["kind"] == kind]):
            if i % 2: ax.add_patch(Rectangle((0, y - rh), X[-1], rh, fc="#f1f3f6", ec="none", zorder=0))
            for (k, _, al, _), x0, x1 in zip(cols, X[:-1], X[1:]): put(al, x0, x1, y, r[k], fontsize=9.2)
            y -= rh
    section("Known (applied) loads"); body("known"); hline(y, 0.6)
    section(r"Unknown pin reactions (drawn in the + sense; plates act along A$\rightarrow$B at angle $\alpha$, + = tension)"); body("unknown"); hline(y, 1.1)
    for j, s in enumerate(notes):
        ax.text(0, y - 0.18 - j * 0.25, s, fontsize=8.6, va="top", color="#333")
    for ext in ("png",):
        fig.savefig(os.path.join(HERE, f"table_fbd_loads.{ext}"), dpi=300, facecolor="white")
    plt.close(fig)

    def plain(s):
        for a_, b_ in (("$", ""), ("\\mathbf{", ""), ("\\cos\\alpha", " cos(alpha)"), ("\\sin\\alpha", " sin(alpha)"), ("\\tau", "tau"), ("{", ""), ("}", ""), ("−", "-")):
            s = s.replace(a_, b_)
        return s
    with open(os.path.join(HERE, "table_fbd_loads.csv"), "w", newline="") as fh:
        wr = csv.writer(fh)
        wr.writerow(["#", "Load", "Symbol", "Acts at", "x (mm)", "y (mm)", "z (mm)", "Fx (N)", "Fy (N)", "Fz (N)", "Mx (N mm)", "My (N mm)", "Mz (N mm)"])
        for r in rows:
            wr.writerow([plain(str(r[k])) for k in ("n", "name", "sym", "where", "x", "y", "z", "Fx", "Fy", "Fz", "Mx", "My", "Mz")])
        wr.writerow([])
        wr.writerow(["", "Definitions", "z_b = w/2 + 6.35; z_p = w/2 + t_p/2; cos(alpha) = a/sqrt(a^2+500^2); sin(alpha) = 500/sqrt(a^2+500^2)"])

if __name__ == "__main__":
    check_symbolic_sums()
    side_view(); bottom_view(); end_view(); iso_view(); table()
    print(f"tau = {tau:.3f} N m, T_c = {T:.2f} N, My_const = {MY_CONST:.0f} N mm, Mz_const = {MZ_CONST:.0f} N mm; symbolic sums verified")
