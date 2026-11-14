"""Report figures for DP2 (rotor shaft): free-body diagrams and internal-load diagrams.

Run:  python3 make_fbd_figures.py      (writes PNG figures next to this file)

Figures
  fig_fbd_views.png    Figure 1: (a) front view x-y and (b) side view z-y of the rotating assembly, side by side
  fig_fbd_a_front.png  Figure 1(a) alone
  fig_fbd_b_side.png   Figure 1(b) alone
  fig_fbd_c_top.png    Figure 1(c): top view of the sprocket plane (chain direction, torques)
  fig_internal_loads.png  Figure 2: V, M, T, N along the shaft

Coordinates (mm, N): origin on the shaft axis at the OUTER FACE of the lower bearing (datum of Figure 2 of the
assignment), bearing midplanes at y = 6.35 and 293.65 mm (1/2 in bearings, 300 mm between outer faces), y up the shaft, x toward the chain,
z downstream (drag direction). Reactions are drawn in their assumed positive sense; their values come from the
statics in the report (Table 3), which this script re-solves and checks.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch, Wedge, Arc, Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
IN = 25.4

# ---------------- problem data (DP2 Rev 2, Figure 2) ----------------
D, WR, WS, TQ, FC, ANG = 560.0, 120.0, 35.0, 19.63, 161.8, -4.732
BW = 0.5 * IN                                # bearing width (Req. 8)
yF0, yF1 = 0.0, 300.0                        # outer faces of the lower / upper bearing (datum = lower face)
yL, yU = yF0 + BW / 2, yF1 - BW / 2          # bearing midplanes, where the reactions act
yF, yHT, yHB, yP, yCG, yCOP = -50.0, -150.0, -250.0, -185.0, -350.0, -500.0
yGL, yGU = -0.4937, 300.4937                 # ring-groove centres (calculate.py)
yTOP, yBOT = 303.5, -250.5                   # shaft ends, 554 mm long
yK0, yK1 = -47.11, -24.89                    # keyseat (ASME B17.1), key 12.70 long centred at -36
yKk0, yKk1 = -36 - 6.35, -36 + 6.35
SPR_T, SPR_W, RP = 0.284 * IN, 1.125 * IN, 121.3
yS0 = yF - SPR_T / 2; yS1 = yS0 + SPR_W
d_draw = 1.5 * IN; r = d_draw / 2            # drawing / trial diameter only
RHO, G = 7850, 9.80665

th = np.radians(ANG)
FCX, FCZ = FC * np.cos(th), -FC * np.sin(th)          # rotation about +y: x -> (cos, 0, -sin)
span = yU - yL
RUz = -(D * (yCOP - yL) + FCZ * (yF - yL)) / span; RLz = -D - FCZ - RUz
RUx = -(FCX * (yF - yL)) / span; RLx = -FCX - RUx
A = np.pi * d_draw ** 2 / 4; w = RHO * G * A * 1e-9; WSH = w * (yTOP - yBOT)
RRING = WR + WS + WSH

def check_statics():
    loads = [((0, yCG, 0), (0, -WR, 0)), ((0, yF, 0), (0, -WS, 0)), ((0, (yTOP + yBOT) / 2, 0), (0, -WSH, 0)),
             ((0, yCOP, 0), (0, 0, D)), ((0, yF, 0), (FCX, 0, FCZ)), ((0, yL, 0), (RLx, 0, RLz)),
             ((0, yU, 0), (RUx, 0, RUz)), ((0, yGU, 0), (0, RRING, 0))]
    F = sum(np.array(f) for _, f in loads); M = sum(np.cross(p, f) for p, f in loads) + np.array([0, TQ * 1000 - TQ * 1000, 0])
    assert np.allclose(F, 0, atol=1e-9) and np.allclose(M, 0, atol=1e-6), (F, M)
    assert abs(RUz - 989.59) < 0.01 and abs(RLz + 1562.93) < 0.01 and abs(RUx - 31.63) < 0.01 and abs(RLx + 192.88) < 0.01
    assert abs(WSH - 48.62) < 0.01 and abs(RRING - 203.62) < 0.01

# ---------------- style (matches the DP1 report figures) ----------------
import matplotlib.font_manager as _fm
for _f in ("Roboto-Regular.ttf", "Roboto-Italic.ttf", "Roboto-Bold.ttf", "Roboto-BoldItalic.ttf"):
    _fm.fontManager.addfont(os.path.join(HERE, "fonts", _f))      # Roboto, per the report style guide
plt.rcParams.update({"font.family": "Roboto", "mathtext.fontset": "custom", "mathtext.rm": "Roboto", "mathtext.it": "Roboto:italic", "mathtext.bf": "Roboto:bold", "font.size": 10,
                     "svg.fonttype": "none", "pdf.fonttype": 42, "axes.linewidth": 0.6})
# blue and orange only (style guide: no red/green coding)
C_APP = "#1d3f8f"; C_ORG = "#d9730d"; C_RXN = C_ORG; C_CHN = C_APP
C_BODY = "#e9ecf0"; C_BODY2 = "#d6dbe2"; C_EDGE = "#2b2f36"; C_DIM = "#333333"; C_GHOST = "#8a929c"
LW = 0.9
HALO = [pe.withStroke(linewidth=3.2, foreground="white")]

def rect(ax, x, y, wd, ht, fc=C_BODY, ec=C_EDGE, lw=LW, ls="-", z=1, alpha=1, hatch=None):
    ax.add_patch(Rectangle((x, y), wd, ht, fc=fc, ec=ec, lw=lw, ls=ls, zorder=z, alpha=alpha, hatch=hatch))

def arrow(ax, p0, p1, c, lw=1.6, z=6, ms=11, halo=True):
    a = FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=ms, color=c, lw=lw, zorder=z,
                        shrinkA=0, shrinkB=0, joinstyle="miter", capstyle="butt")
    if halo: a.set_path_effects(HALO)
    ax.add_patch(a)

def txt(ax, x, y, s, c="k", ha="left", va="center", size=10.5, z=9, **kw):
    ax.text(x, y, s, color=c, ha=ha, va=va, fontsize=size, zorder=z,
            bbox=dict(fc="white", ec="none", pad=0.6, alpha=0.9), **kw)

def outof(ax, x, y, c, rr=13, z=7):   # vector toward the viewer
    ax.add_patch(Circle((x, y), rr, fc="white", ec=c, lw=1.5, zorder=z))
    ax.add_patch(Circle((x, y), rr * 0.3, fc=c, ec=c, zorder=z + 0.1))

def into(ax, x, y, c, rr=13, z=7):    # vector away from the viewer
    ax.add_patch(Circle((x, y), rr, fc="white", ec=c, lw=1.5, zorder=z))
    k = rr * 0.62
    ax.plot([x - k, x + k], [y - k, y + k], color=c, lw=1.4, zorder=z + 0.1)
    ax.plot([x - k, x + k], [y + k, y - k], color=c, lw=1.4, zorder=z + 0.1)

def dim(ax, p0, p1, off, label, ext0=None, ext1=None, tsize=9.5, tpos=0.5):
    p0, p1, off = np.array(p0, float), np.array(p1, float), np.array(off, float)
    q0, q1 = p0 + off, p1 + off
    n = off / (np.linalg.norm(off) or 1)
    for e, q in ((ext0 if ext0 is not None else p0, q0), (ext1 if ext1 is not None else p1, q1)):
        e = np.array(e, float); s = e + n * 5
        ax.plot([s[0], q[0] + n[0] * 7], [s[1], q[1] + n[1] * 7], color=C_DIM, lw=0.45, zorder=2)
    ax.add_patch(FancyArrowPatch(q0, q1, arrowstyle="<|-|>", mutation_scale=6.5, color=C_DIM, lw=0.55, zorder=2, shrinkA=0, shrinkB=0))
    m = q0 + (q1 - q0) * tpos
    dd = q1 - q0; ang = np.degrees(np.arctan2(dd[1], dd[0]))
    if ang > 90: ang -= 180
    if ang < -90: ang += 180
    ax.text(m[0], m[1], label, fontsize=tsize, ha="center", va="center", rotation=ang, color=C_DIM, zorder=3,
            bbox=dict(fc="white", ec="none", pad=0.8))

def cg_mark(ax, x, y, rr=11):
    ax.add_patch(Circle((x, y), rr, fc="white", ec="k", lw=0.9, zorder=5))
    ax.add_patch(Wedge((x, y), rr, 0, 90, fc="k", zorder=5.1)); ax.add_patch(Wedge((x, y), rr, 180, 270, fc="k", zorder=5.1))

def torque(ax, cx, cy, a, b, sense, c, label, lx, ly, ha="left"):
    """Rotation about +y seen from the front or side: the near half of the ellipse moves to the right.
    sense = +1 for +y, -1 for -y. Drawn as the near (lower) half with an arrowhead."""
    t = np.linspace(np.radians(195), np.radians(345), 60)
    xs, ys = cx + a * np.cos(t), cy + b * np.sin(t)
    if sense < 0: xs, ys = xs[::-1], ys[::-1]
    ln, = ax.plot(xs, ys, color=c, lw=1.5, zorder=7, solid_capstyle="butt"); ln.set_path_effects(HALO)
    tb = np.linspace(np.radians(15), np.radians(165), 40)
    ax.plot(cx + a * np.cos(tb), cy + b * np.sin(tb), color=c, lw=0.8, ls=(0, (3, 2.5)), zorder=0.9, alpha=0.7)
    ax.add_patch(FancyArrowPatch((xs[-4], ys[-4]), (xs[-1], ys[-1]), arrowstyle="-|>", mutation_scale=10, color=c,
                                 lw=1.5, zorder=7, shrinkA=0, shrinkB=0))
    txt(ax, lx, ly, label, c, ha=ha)

def triad2(ax, o, right, up, depth, L=70):
    """right/up: axis names along +screen x / +screen y; depth: (name, +1 toward viewer / -1 away)."""
    for (dx, dy), nm in (((1, 0), right), ((0, 1), up)):
        ax.add_patch(FancyArrowPatch(o, (o[0] + dx * L, o[1] + dy * L), arrowstyle="-|>", mutation_scale=9, color="k",
                                     lw=0.9, zorder=4, shrinkA=0, shrinkB=0))
        ax.text(o[0] + dx * (L + 16), o[1] + dy * (L + 16), nm, fontsize=11, style="italic", ha="center", va="center", zorder=4)
    nm, s = depth
    (outof if s > 0 else into)(ax, o[0], o[1], "k", rr=9, z=4)
    ax.text(o[0] - 14, o[1] - 16, nm, fontsize=11, style="italic", ha="right", va="top", zorder=4)

def legend(ax, x, y, dy=30, extra=()):
    items = [(C_APP, "Applied load"), (C_RXN, "Support reaction (assumed + sense)")]
    for i, (c, s) in enumerate(items):
        yy = y - i * dy
        ax.add_patch(FancyArrowPatch((x, yy), (x + 55, yy), arrowstyle="-|>", mutation_scale=8, color=c, lw=1.4, shrinkA=0, shrinkB=0))
        ax.text(x + 68, yy, s, fontsize=9, va="center")
    for j, s in enumerate(("Dimensions in mm",) + tuple(extra)):
        ax.text(x, y - (len(items) + j) * dy, s, fontsize=9, va="center", color="#444")

# ---------------- the body (shared by the front and side views) ----------------
# The FBD views are drawn NOT to scale along y: the 50 mm between the lower bearing and the chain line holds most of
# the loads, so the drawing stretches that region and compresses the bearing span. Dimensions carry the true values.
YK_TRUE = [-750, yCOP, yCG, yHB, yP, yHT, yS0, yF, yS1, yF0, yF0 + BW, yF1 - BW, yF1, yTOP]
YK_DRAW = [-840, -680, -520, -400, -312, -262, -128, -120, -60, 0, 18, 230, 248, 262]
def Y(y): return float(np.interp(y, YK_TRUE, YK_DRAW))
HB = 9   # half-height of a bearing on the drawing (= half of the 18 units given to 12.7 mm)

def body(ax, view):
    """view 'front': screen-x = x (z toward viewer). view 'side': screen-x = z (x away from viewer)."""
    # rotor (schematic drum, radius 250, below the hub)
    rect(ax, -250, Y(-750), 500, Y(yHB) - Y(-750), fc="#f4f6f8", z=0.5)
    for xx in (-125, 125):
        ax.plot([xx, xx], [Y(-750) + 4, Y(yHB) - 4], color="#c3c8cf", lw=0.8, zorder=0.6)
    ax.text(-240, Y(-750) + 8, "Rotor (schematic)", fontsize=8.5, color="#555", va="bottom", zorder=0.7)
    # hub (OD = 2d) and pin
    rect(ax, -d_draw, Y(yHB), 2 * d_draw, Y(yHT) - Y(yHB), fc=C_BODY2, z=2)
    ax.text(-d_draw - 8, (Y(yHT) + Y(yHB)) / 2 - 30, "Hub", fontsize=8.5, color="#444", ha="right", va="center", zorder=3)
    # shaft
    rect(ax, -r, Y(yBOT), 2 * r, Y(yTOP) - Y(yBOT), fc=C_BODY, z=3)
    ax.plot([0, 0], [Y(yHB) - 18, Y(yTOP) + 14], color="#9aa1aa", lw=0.5, ls=(0, (12, 3, 2, 3)), zorder=3.1)
    if view == "front":
        rect(ax, -d_draw, Y(yP) - 3.5, 2 * d_draw, 7, fc="#5b6370", ec=C_EDGE, lw=0.6, z=3.3)       # pin along x
    else:
        ax.add_patch(Circle((0, Y(yP)), 5, fc="#5b6370", ec=C_EDGE, lw=0.6, zorder=3.3))          # pin end-on
    # sprocket: toothed plate on the chain line, hub on the upper side
    t0, t1, h1 = Y(yS0), Y(yS0) + 16, Y(yS1)
    rect(ax, -RP - 4, t0, 2 * (RP + 4), t1 - t0, fc=C_BODY2, z=2.5)
    rect(ax, -d_draw, t1, 2 * d_draw, h1 - t1, fc=C_BODY2, z=2.5)
    ax.text(-RP - 8, t1 + 8, "Sprocket", fontsize=8.5, color="#444", ha="right", va="center", zorder=3)
    kw = 3 / 8 * IN
    if view == "front":   # key on +x and the set screw through the sprocket hub
        k0, k1 = Y(yKk0), Y(yKk1)
        rect(ax, r - kw / 2, k0, kw, k1 - k0, fc="#7a828d", ec=C_EDGE, lw=0.6, z=3.4)
        rect(ax, r + kw / 2, (k0 + k1) / 2 - 4, d_draw - r - kw / 2, 8, fc="#3d434c", ec=C_EDGE, lw=0.5, z=3.4)
    else:                 # key hidden behind the shaft
        rect(ax, -kw / 2, Y(yKk0), kw, Y(yKk1) - Y(yKk0), fc="none", ec=C_EDGE, lw=0.6, ls=(0, (2, 1.5)), z=3.4)
    # bearings as ghosts (removed from the free body) and the retaining rings just outside them
    for yy, sgn in ((yL, -1), (yU, +1)):
        yc = Y(yy)
        for s in (-1, 1):
            x0 = r + 1 if s > 0 else -r - 31
            rect(ax, x0, yc - HB, 30, 2 * HB, fc="none", ec=C_GHOST, lw=0.8, ls=(0, (3, 2)), z=2)
            ax.plot([x0, x0 + 30], [yc - HB, yc + HB], color=C_GHOST, lw=0.6, zorder=2)
            ax.plot([x0, x0 + 30], [yc + HB, yc - HB], color=C_GHOST, lw=0.6, zorder=2)
        rect(ax, -r - 6, yc + sgn * (HB + 3.5) - 2.5, 2 * r + 12, 5, fc="#202328", ec="#202328", lw=0.5, z=3.5)
    cg_mark(ax, 0, Y(yCG))
    ax.add_patch(Circle((0, Y(yCOP)), 7, fc="white", ec="k", lw=0.9, zorder=5))
    ax.text(-16, Y(yCG) - 4, "CG", fontsize=9.5, ha="right", va="top", zorder=8)
    ax.text(-20, Y(yCOP) - 20, "COP", fontsize=9.5, ha="right", va="top", zorder=8)

RX = r + 36   # x where the right-hand arrows start

def loads_common(ax):
    """Axial loads and the two torques, identical in both views."""
    arrow(ax, (0, Y(yCG) + 92), (0, Y(yCG) + 12), C_APP)
    txt(ax, -16, Y(yCG) + 52, r"$W_r$ = 120 N", C_APP, ha="right")
    arrow(ax, (0, Y(yS1) + 48), (0, Y(yS1) + 2), C_APP, lw=1.4, ms=10)          # sprocket weight, on the axis
    txt(ax, RX, -45, r"$W_s$ = 35 N", C_APP, size=9.5)
    ax.plot([RX - 4, 4], [-45, Y(yS1) + 22], color=C_APP, lw=0.5, zorder=8)
    ym = 140
    arrow(ax, (0, ym + 40), (0, ym - 40), C_APP, lw=1.4, ms=10)
    txt(ax, -r - 14, ym, r"$W_{sh}$ = 48.6 N", C_APP, ha="right", size=9.5)
    arrow(ax, (0, Y(yU) + HB + 8), (0, Y(yU) + 120), C_RXN)
    txt(ax, 14, Y(yU) + 104, r"$R_{ring}$", C_RXN)
    torque(ax, 0, Y(yP), 70, 15, +1, C_APP, r"$T_w$ = 19.63 N$\cdot$m (+$y$)", RX, Y(yP) - 34)
    torque(ax, 0, Y(yS0) - 22, 150, 18, -1, C_CHN, r"$T_c$ = 19.63 N$\cdot$m ($-y$)", RX + 40, -222)

def dims_left(ax, xbase=-330, step=34):
    items = [(yF, "50"), (yHT, "150"), (yP, "185"), (yHB, "250"), (yCG, "350"), (yCOP, "500")]
    for i, (yy, lab) in enumerate(items):
        x = xbase - i * step
        dim(ax, (x, 0), (x, Y(yy)), (0, 0), lab, tsize=9)
        stop = -8 if yy in (yCG, yCOP) else (-RP - 6 if yy == yF else -d_draw - 2)
        ax.plot([x - 5, stop], [Y(yy), Y(yy)], color=C_DIM, lw=0.45, zorder=1.8)
    ax.plot([xbase - (len(items) - 1) * step - 5, -r - 34], [0, 0], color=C_DIM, lw=0.45, zorder=1.8)
    dim(ax, (xbase, 0), (xbase, Y(yF1)), (0, 0), "300", tsize=9)
    ax.plot([xbase - 5, -r - 34], [Y(yF1), Y(yF1)], color=C_DIM, lw=0.45, zorder=1.8)


def bearings_and_chain(ax, inplane, outplane, out_sym):
    L = 150
    for yy, nm in ((yL, "L"), (yU, "U")):
        arrow(ax, (RX, Y(yy)), (RX + L, Y(yy)), C_RXN)
        txt(ax, RX + L + 10, Y(yy) + 1, rf"$R_{{{nm},{inplane}}}$", C_RXN)
        out_sym(ax, -r - 50, Y(yy), C_RXN, rr=11)
        txt(ax, -r - 68, Y(yy) + 1, rf"$R_{{{nm},{outplane}}}$", C_RXN, ha="right")
        ax.text(r + 6, Y(yy) + HB + 6, nm, fontsize=11, weight="bold", ha="left", va="bottom", zorder=9)

def view_front(ax):
    body(ax, "front"); loads_common(ax)
    bearings_and_chain(ax, "x", "z", outof)
    yc = Y(yF)
    arrow(ax, (RX, yc), (RX + 150, yc), C_CHN)
    txt(ax, RX + 160, yc + 1, r"$F_{c,x}$ = 161.25 N", C_CHN)
    outof(ax, RX + 172, yc - 45, C_CHN, rr=10)
    txt(ax, RX + 190, yc - 45, r"$F_{c,z}$ = 13.35 N", C_CHN)
    outof(ax, 0, Y(yCOP), C_APP, rr=15)
    txt(ax, 24, Y(yCOP), r"$D$ = 560 N (+$z$)", C_APP)
    dims_left(ax)
    triad2(ax, (-480, 330), "x", "y", ("z", +1), L=60)

def view_side(ax):
    body(ax, "side"); loads_common(ax)
    bearings_and_chain(ax, "z", "x", into)
    yc = Y(yF)
    arrow(ax, (RX, yc), (RX + 60, yc), C_CHN)
    txt(ax, RX + 70, yc + 1, r"$F_{c,z}$ = 13.35 N", C_CHN)
    into(ax, RX + 172, yc - 45, C_CHN, rr=10)
    txt(ax, RX + 190, yc - 45, r"$F_{c,x}$ = 161.25 N", C_CHN)
    arrow(ax, (10, Y(yCOP)), (10 + 200, Y(yCOP)), C_APP, lw=1.8, ms=12)
    txt(ax, 60, Y(yCOP) + 24, r"$D$ = 560 N", C_APP)
    dims_left(ax)
    triad2(ax, (-480, 330), "z", "y", ("x", -1), L=60)

def setup(ax, title=None):
    ax.set_xlim(-560, 560); ax.set_ylim(-870, 440); ax.set_aspect("equal"); ax.axis("off")
    if title: ax.text(0, 430, title, fontsize=11, ha="center", va="top")

def save(fig, name):
    fig.savefig(os.path.join(HERE, name), dpi=300, facecolor="white")
    plt.close(fig)

NOTES = ("Dimensions in mm; not to scale along y", "* pin position assumed (Req. 10)")

def fig_views():
    W, H = 1120, 1310
    fig = plt.figure(figsize=(7.4, 7.4 * H / (2 * W) + 0.5))
    fh = 7.4 * H / (2 * W) + 0.5; lgh = 0.5 / fh
    a1 = fig.add_axes([0, lgh, 0.5, 1 - lgh]); a2 = fig.add_axes([0.5, lgh, 0.5, 1 - lgh])
    setup(a1, "(a) Front view, x–y plane"); view_front(a1)
    setup(a2, "(b) Side view, z–y plane"); view_side(a2)
    lg = fig.add_axes([0, 0, 1, lgh]); lg.set_xlim(0, 1000); lg.set_ylim(0, 100); lg.axis("off")
    items = [(C_APP, "Applied load"), (C_RXN, "Support reaction (assumed + sense)")]
    x = 30
    for c, s in items:
        lg.add_patch(FancyArrowPatch((x, 66), (x + 40, 66), arrowstyle="-|>", mutation_scale=8, color=c, lw=1.4, shrinkA=0, shrinkB=0))
        lg.text(x + 50, 66, s, fontsize=8.5, va="center"); x += 62 + len(s) * 7.6
    lg.text(30, 25, "Dimensions in mm from the outer face of the lower bearing (y = 0). Not to scale along y.",
            fontsize=8.5, va="center", color="#444")
    save(fig, "fig_fbd_views.png")
    for fn, name, ttl in ((view_front, "fig_fbd_a_front.png", "(a) Front view, x–y plane"), (view_side, "fig_fbd_b_side.png", "(b) Side view, z–y plane")):
        fw = 5.0; mh = fw * H / W; lh = 0.62; fh = mh + lh
        fig = plt.figure(figsize=(fw, fh))
        ax = fig.add_axes([0, lh / fh, 1, mh / fh]); setup(ax, ttl); fn(ax)
        lg = fig.add_axes([0, 0, 1, lh / fh]); lg.set_xlim(0, 1000); lg.set_ylim(0, 100); lg.axis("off")
        x = 40
        for c, s_ in ((C_APP, "Applied load"), (C_CHN, "Chain load"), (C_RXN, "Support reaction (assumed + sense)")):
            lg.add_patch(FancyArrowPatch((x, 72), (x + 55, 72), arrowstyle="-|>", mutation_scale=8, color=c, lw=1.4, shrinkA=0, shrinkB=0))
            lg.text(x + 68, 72, s_, fontsize=8.5, va="center"); x += 85 + len(s_) * 10.2
        lg.text(40, 40, "Dimensions in mm from the outer face of the lower bearing (y = 0). Not to scale along y.", fontsize=8.5, va="center", color="#444")
        lg.text(40, 12, "Reactions act at the bearing midplanes, y = 6.35 and 293.65.", fontsize=8.5, va="center", color="#444")
        save(fig, name)

# ---------------- (c) top view of the sprocket plane ----------------
def fig_top():
    fig = plt.figure(figsize=(6.2, 4.4)); ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(-330, 430); ax.set_ylim(-270, 270); ax.set_aspect("equal"); ax.axis("off")
    # screen: x right, z DOWN (viewed from +y, looking down the shaft). Helper: (x, z) -> screen (x, -z)
    S = lambda x, z: (x, -z)
    # sprocket teeth outline and pitch circle
    n = 60; tt = np.linspace(0, 2 * np.pi, 4 * n + 1)
    rr = np.where((np.arange(len(tt)) % 4) < 2, RP + 4, RP - 6)
    ax.add_patch(Polygon(np.c_[rr * np.cos(tt), rr * np.sin(tt)], closed=True, fc=C_BODY2, ec=C_EDGE, lw=0.5, zorder=1))
    ax.add_patch(Circle((0, 0), RP, fc="none", ec="#7d848e", lw=0.6, ls=(0, (6, 3, 1.5, 3)), zorder=1.2))
    ax.add_patch(Circle((0, 0), d_draw, fc=C_BODY, ec=C_EDGE, lw=0.7, zorder=1.3))          # sprocket hub
    ax.add_patch(Circle((0, 0), r, fc="#cfd5dc", ec=C_EDGE, lw=0.9, zorder=1.4))            # shaft
    kw = 3 / 8 * IN
    rect(ax, r - kw / 2, -kw / 2, kw, kw, fc="#7a828d", ec=C_EDGE, lw=0.6, z=1.5)            # key on +x
    ax.plot([-RP - 30, 380], [0, 0], color="#9aa1aa", lw=0.5, ls=(0, (12, 3, 2, 3)), zorder=1.1)
    ax.plot([0, 0], [-RP - 30, RP + 30], color="#9aa1aa", lw=0.5, ls=(0, (12, 3, 2, 3)), zorder=1.1)
    # chain tight span, tangent on the upstream (-z) side
    u = np.array([np.cos(np.radians(4.732)), np.sin(np.radians(4.732))])      # (x, z) direction of F_c
    tp = RP * np.array([u[1], -u[0]])                                         # tangent point (x, z)
    p0 = S(*tp); p1 = S(*(tp + 330 * u))
    ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color="#d9c39a", lw=2.4, zorder=1.6, solid_capstyle="butt")
    ax.text(p1[0], p1[1] - 12, "chain, tight span", fontsize=8.5, color=C_CHN, ha="right", va="top", zorder=8)
    a_end = S(*(tp + 175 * u))
    arrow(ax, p0, a_end, C_CHN, lw=1.8, ms=12, halo=False, z=6.5)
    txt(ax, a_end[0] - 70, a_end[1] - 30, r"$F_c$ = 161.8 N", C_CHN)
    # angle between +x and the chain
    xa = S(*(tp + 250 * np.array([1, 0])))
    ax.plot([p0[0], xa[0]], [p0[1], xa[1]], color=C_DIM, lw=0.5, ls=(0, (4, 3)), zorder=1.7)
    ax.add_patch(Arc(p0, 360, 360, theta1=-4.732, theta2=0, color=C_DIM, lw=0.7, zorder=2))
    ax.text(p0[0] + 188, p0[1] + 14, r"$4.732^\circ$", fontsize=9.5, color=C_DIM, va="center", zorder=8)
    # equivalent at the axis: components
    arrow(ax, (0, 0), (175, 0), C_CHN, lw=1.4, ms=10)
    txt(ax, 182, 10, r"$F_{c,x}$ = 161.25 N", C_CHN, size=9.5)
    arrow(ax, (0, 0), S(0, 62), C_CHN, lw=1.4, ms=10)
    txt(ax, 10, -78, r"$F_{c,z}$ = 13.35 N", C_CHN, size=9.5)
    # drag direction (acts at the COP, below this plane)
    arrow(ax, (-215, 70), (-215, -70), C_APP, lw=1.6, ms=11)
    txt(ax, -215, -95, r"$D$ = 560 N", C_APP, ha="center")
    ax.text(-215, -118, "(at the COP, y = −500)", fontsize=8, color=C_APP, ha="center", va="center")
    ax.text(-215, 92, "water flow", fontsize=8.5, color="#555", ha="center")
    # torques: +y is toward the viewer, so +y turns counter-clockwise on the page
    def rot_arrow(R, a0, a1, c, lab, lpos, ha="left"):
        tt = np.radians(np.linspace(a0, a1, 60)); xs, ys = R * np.cos(tt), R * np.sin(tt)
        ln, = ax.plot(xs, ys, color=c, lw=1.5, zorder=6); ln.set_path_effects(HALO)
        ax.add_patch(FancyArrowPatch((xs[-4], ys[-4]), (xs[-1], ys[-1]), arrowstyle="-|>", mutation_scale=10, color=c, lw=1.5, zorder=6, shrinkA=0, shrinkB=0))
        txt(ax, lpos[0], lpos[1], lab, c, ha=ha, size=9.5)
    rot_arrow(RP + 28, 100, 165, C_APP, r"$T_w$ (+$y$, at the pin)", (-150, 175), ha="right")
    rot_arrow(RP + 28, 255, 195, C_CHN, r"$T_c$ ($-y$, through the key)", (-150, -175), ha="right")
    ax.text(r + 14, 22, "key", fontsize=8, color="#444", va="center", zorder=8)
    o = (330, -150)
    for (dx, dy), nm in (((1, 0), "x"), ((0, -1), "z")):
        ax.add_patch(FancyArrowPatch(o, (o[0] + dx * 55, o[1] + dy * 55), arrowstyle="-|>", mutation_scale=9, color="k", lw=0.9, zorder=4, shrinkA=0, shrinkB=0))
        ax.text(o[0] + dx * 70, o[1] + dy * 70, nm, fontsize=11, style="italic", ha="center", va="center", zorder=4)
    outof(ax, o[0], o[1], "k", rr=8, z=4); ax.text(o[0] - 14, o[1] + 14, "y", fontsize=11, style="italic", ha="right", va="bottom", zorder=4)
    ax.text(-320, 255, "Viewed from above (+y toward the viewer), sprocket plane y = −50 mm", fontsize=8.5, color="#444", va="top")
    save(fig, "fig_fbd_c_top.png")

# ---------------- Figure 2: internal loads ----------------
def internal(y, hub="line"):
    pts = [(yCOP, 0.0, D), (yF, FCX, FCZ), (yL, RLx, RLz), (yU, RUx, RUz)]
    Vx = Vz = Mbx = Mbz = 0.0
    for yi, fx, fz in pts:
        if yi < y:
            Vx += fx; Vz += fz; ry = yi - y; Mbx += ry * fz; Mbz += -ry * fx
    T = TQ if yP < y <= yK1 else 0.0           # full torque from the pin to the top of the keyseat (envelope used in the report)
    N = w * (y - yBOT) + (WR if y > yP else 0) + (WS if y > -36.0 else 0) - (RRING if y > yGU else 0)
    Mx, Mz = -Mbx / 1000, Mbz / 1000          # N m, sign chosen so both are positive on the overhang
    return Vx, Vz, Mx, Mz, np.hypot(Mx, Mz), T, N

def fig_internal():
    ys = np.unique(np.r_[np.linspace(yBOT, yTOP, 2400), [v + e for v in (yL, yU, yF, yP, yK1, -36.0, yGU) for e in (-1e-6, 1e-6)]])
    ys = ys[(ys >= yBOT) & (ys <= yTOP)]
    Q = np.array([internal(y) for y in ys])
    fig, axs6 = plt.subplots(1, 6, figsize=(7.4, 5.6), sharey=True, gridspec_kw=dict(width_ratios=[0.62, 0.3, 1, 1.15, 0.8, 0.8], wspace=0.1))
    fig.subplots_adjust(left=0.075, right=0.985, top=0.975, bottom=0.1)
    axs6[1].axis("off"); axs = [axs6[0]] + list(axs6[2:])
    feats = [(yU, "U"), (yL, "L"), (yF, "chain"), (yHT, "hub top"), (yP, "pin")]
    lab_y = {yU: yU, yL: yL + 12, yF: yF - 6, yHT: yHT + 6, yP: yP - 4}
    # shaft column
    a0 = axs[0]; a0.set_xlim(-60, 60)
    a0.add_patch(Rectangle((-d_draw, yHB), 2 * d_draw, yHT - yHB, fc=C_BODY2, ec=C_EDGE, lw=0.5))
    a0.add_patch(Rectangle((-48, yS0), 96, SPR_T, fc=C_BODY2, ec=C_EDGE, lw=0.5))
    a0.add_patch(Rectangle((-d_draw, yS0 + SPR_T), 2 * d_draw, yS1 - yS0 - SPR_T, fc=C_BODY2, ec=C_EDGE, lw=0.5))
    a0.add_patch(Rectangle((-r * 0.55, yBOT), 1.1 * r, yTOP - yBOT, fc=C_BODY, ec=C_EDGE, lw=0.6))
    for yy in (yGL, yGU): a0.add_patch(Rectangle((-r * 0.55 - 4, yy - 2), 1.1 * r + 8, 4, fc="#202328", ec="none"))
    for yy in (yL, yU):
        for s in (-1, 1): a0.add_patch(Rectangle((s * r * 0.55 + (0 if s > 0 else -12), yy - BW / 2), 12, BW, fc="none", ec=C_GHOST, lw=0.6, ls=(0, (2, 1.5))))
    a0.plot([-d_draw, d_draw], [yP, yP], color="#5b6370", lw=2)
    a0.axis("off")
    for yy, nm in feats:
        a0.text(-62, lab_y[yy], nm, fontsize=8, ha="right", va="center", color="#444")
    panels = [
        (axs[1], [(Q[:, 0], C_ORG, r"$V_x$"), (Q[:, 1], C_APP, r"$V_z$")], "Shear (N)", "{:.0f}"),
        (axs[2], [(Q[:, 2], C_APP, r"$M_x$"), (Q[:, 3], C_ORG, r"$M_z$"), (Q[:, 4], "k", r"$|M|$")], "Bending (N$\\cdot$m)", "{:.1f}"),
        (axs[3], [(Q[:, 5], C_APP, r"$T$")], "Torque (N$\\cdot$m)", "{:.2f}"),
        (axs[4], [(Q[:, 6], "#4a5fc1", r"$N$")], "Axial (N)", "{:.0f}"),
    ]
    for ax, series, title, f in panels:
        ax.set_xlabel(title, fontsize=9)
        for yy, _ in feats: ax.axhline(yy, color="#d0d3d8", lw=0.5, ls=(0, (3, 2)), zorder=0)
        ax.axvline(0, color="#888", lw=0.6, zorder=0.5)
        for v, c, lab in series:
            lwid = 2.0 if lab == r"$|M|$" else 1.2
            ls = (0, (4, 2)) if lab == r"$M_x$" else "-"
            ax.plot(v, ys, color=c, lw=lwid, ls=ls, label=lab, zorder=4 if lab == r"$M_x$" else 3)
            if lab == r"$|M|$": ax.fill_betweenx(ys, 0, v, color="k", alpha=0.06, zorder=1)
        ax.tick_params(labelsize=8, length=2.5, width=0.5); ax.grid(False)
        for s in ("top", "right"): ax.spines[s].set_visible(False)
        ax.legend(fontsize=8, frameon=False, loc="lower right" if title.startswith("Axial") else "upper right", handlelength=1.4, borderaxespad=0.2)
    # annotate the key values
    def note(ax, x, y, s, ha="left", c="k", dx=6, dy=0):
        s = s.replace("-", "\u2212")
        ax.plot([x], [y], "o", ms=2.6, color=c, zorder=5)
        ax.annotate(s, (x, y), xytext=(dx, dy), textcoords="offset points", fontsize=8, ha=ha, va="center", color=c,
                    bbox=dict(fc="white", ec="none", pad=0.3, alpha=0.9), zorder=6)
    aM = axs[2]; q = internal(yL); note(aM, q[4], yL, f"{q[4]:.1f} at L", ha="right", dx=-10, dy=9)
    q = internal(yGL); note(aM, q[4], yGL, f"{q[4]:.1f} groove", ha="right", dx=-12, dy=-5)
    q = internal(-24.65); note(aM, q[4], -24.65, f"{q[4]:.1f} keyseat", ha="right", dx=-12, dy=-7)
    q = internal(yP + 6.378 / 2); note(aM, q[4], yP + 6.378 / 2, f"{q[4]:.1f} pin hole", ha="right", dx=-8)
    aV = axs[1]
    note(aV, internal(yL + 1e-6)[1], yL + 150, f"{internal(yL + 1e-6)[1]:.1f}", c=C_APP, ha="left")
    note(aV, internal(yL - 1e-6)[1], yL - 40, f"{internal(yL - 1e-6)[1]:.1f}", c=C_APP, ha="right", dx=-6)
    aT = axs[3]; note(aT, TQ, -110, "19.63", c=C_APP, ha="right", dx=-6)
    aN = axs[4]; q = internal(yGU - 1e-6); note(aN, q[6], yGU - 30, f"{q[6]:.0f}", c="#4a5fc1", ha="right", dx=-6)
    axs[1].set_ylabel("y (mm)", fontsize=9)
    axs[1].yaxis.set_tick_params(labelleft=True)
    axs[1].set_yticks([-250, -150, -50, 0, 100, 200, 300])
    for ax in axs[1:]: ax.set_ylim(yBOT - 5, yTOP + 8)
    save(fig, "fig_internal_loads.png")

if __name__ == "__main__":
    check_statics()
    print(f"R_L = ({RLx:.2f}, {RLz:.2f})  R_U = ({RUx:.2f}, {RUz:.2f})  ring = {RRING:.1f} N")
    fig_views(); fig_top(); fig_internal()
    print("written:", [f for f in sorted(os.listdir(HERE)) if f.endswith(".png")])
