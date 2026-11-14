"""Figure 3 of the DP2 report: shaft layout along y and the three machined sections (groove, keyseat, pin hole).

Run:  python3 make_layout_figure.py      (writes fig_shaft_layout.png next to this file)

All dimensions in mm and taken from DP2/solution/calculate.py (Rev P3): 1346K534 shaft, OD 37.998-38.100,
ring groove for 93576A210 (root 36.982-37.084, width 0.787-0.838, R 0.20-0.25), ASME B17.1 Class 1 keyseat
(W 9.525 +0.051/0, S 32.733 +0/-0.381, R 0.79), pin hole 6.35 F7 at y = -185.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, FancyArrowPatch, Circle

HERE = os.path.dirname(os.path.abspath(__file__))
import matplotlib.font_manager as _fm
for _f in ("Roboto-Regular.ttf", "Roboto-Italic.ttf", "Roboto-Bold.ttf", "Roboto-BoldItalic.ttf"):
    _fm.fontManager.addfont(os.path.join(HERE, "fonts", _f))      # Roboto, per the report style guide
plt.rcParams.update({"font.family": "Roboto", "mathtext.fontset": "custom", "mathtext.rm": "Roboto", "mathtext.it": "Roboto:italic", "mathtext.bf": "Roboto:bold", "font.size": 9, "hatch.linewidth": 0.4})
C_BODY, C_BODY2, C_EDGE, C_DIM, C_GHOST, C_CUT = "#e9ecf0", "#d6dbe2", "#2b2f36", "#333333", "#8a929c", "#dfe3e8"
CL = dict(color="#7d848e", lw=0.5, ls=(0, (12, 3, 2, 3)))

D, R = 38.1, 19.05
yBOT, yTOP = -250.5, 303.5
yP, yK0, yK1, yGL, yGU = -185.0, -47.11, -24.89, -0.4937, 300.4937
BW = 12.7


def dim(ax, p0, p1, label, off=(0, 0), tsize=8, ms=5.5, text_off=(0, 0), rot=None, ha="center", va="center", bg=True):
    p0, p1 = np.array(p0, float) + off, np.array(p1, float) + off
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="<|-|>", mutation_scale=ms, color=C_DIM, lw=0.5, shrinkA=0, shrinkB=0, zorder=6))
    m = (p0 + p1) / 2 + np.array(text_off, float)
    d = p1 - p0
    ang = np.degrees(np.arctan2(d[1], d[0])) if rot is None else rot
    if ang > 90: ang -= 180
    if ang < -90: ang += 180
    ax.text(m[0], m[1], label, fontsize=tsize, ha=ha, va=va, rotation=ang, color=C_DIM, zorder=7,
            bbox=dict(fc="white", ec="none", pad=0.5) if bg else None)


def ext(ax, p, q):
    ax.plot([p[0], q[0]], [p[1], q[1]], color=C_DIM, lw=0.4, zorder=5)


def leader(ax, tip, txtpos, label, ha="left", tsize=8):
    ax.annotate(label, tip, xytext=txtpos, fontsize=tsize, color=C_DIM, ha=ha, va="center", zorder=7, bbox=dict(fc="white", ec="none", pad=0.6),
                arrowprops=dict(arrowstyle="-|>", color=C_DIM, lw=0.5, shrinkA=1, shrinkB=0, mutation_scale=6))


# ---------------------------------------------------------------- (a) layout along the shaft
def layout(ax):
    ax.set_xlim(-300, 372); ax.set_ylim(-124, 86); ax.set_aspect("equal"); ax.axis("off")
    # ghosts: rotor hub, sprocket, bearings
    ax.add_patch(Rectangle((-250, -D), 100, 2 * D, fc="none", ec=C_GHOST, lw=0.7, ls=(0, (3, 2))))
    ax.text(-200, D + 5, "rotor hub (OD = 2D)", fontsize=7.5, color="#555", ha="center", va="bottom")
    s0 = -50 - 0.284 * 25.4 / 2; s1 = s0 + 1.125 * 25.4
    ax.add_patch(Rectangle((s0, -58), 0.284 * 25.4, 116, fc="none", ec=C_GHOST, lw=0.7, ls=(0, (3, 2))))
    ax.add_patch(Rectangle((s0 + 0.284 * 25.4, -D), s1 - s0 - 0.284 * 25.4, 2 * D, fc="none", ec=C_GHOST, lw=0.7, ls=(0, (3, 2))))
    ax.text(-52, 60, "sprocket", fontsize=7.5, color="#555", ha="center", va="bottom")
    for b0, nm in ((0.0, "L"), (300 - BW, "U")):
        for sg in (1, -1):
            y0 = R if sg > 0 else -R - 16
            ax.add_patch(Rectangle((b0, y0), BW, 16, fc="none", ec=C_GHOST, lw=0.7, ls=(0, (3, 2))))
            ax.plot([b0, b0 + BW], [y0, y0 + 16], color=C_GHOST, lw=0.5); ax.plot([b0, b0 + BW], [y0 + 16, y0], color=C_GHOST, lw=0.5)
        ax.text(b0 + BW / 2, R + 20, f"bearing {nm}", fontsize=7.5, color="#555", ha="center", va="bottom")
    # shaft
    ax.add_patch(Rectangle((yBOT, -R), yTOP - yBOT, D, fc=C_BODY, ec=C_EDGE, lw=0.9, zorder=2))
    ax.plot([yBOT - 12, yTOP + 12], [0, 0], zorder=3, **CL)
    # grooves (drawn 3x wide so they are visible), keyseat (top view of the slot shown on the near side), pin hole
    for yg in (yGL, yGU):
        ax.add_patch(Rectangle((yg - 1.2, -R - 0.3), 2.4, D + 0.6, fc="white", ec="none", zorder=2.5))
        ax.add_patch(Rectangle((yg - 1.2, -R + 2.0), 2.4, D - 4.0, fc="#b9c0c9", ec=C_EDGE, lw=0.6, zorder=2.6))
    w = 9.525
    xs = np.r_[yK0 + w / 2 + (w / 2) * np.cos(np.linspace(np.pi / 2, 3 * np.pi / 2, 30)), yK1 - w / 2 + (w / 2) * np.cos(np.linspace(-np.pi / 2, np.pi / 2, 30))]
    zs = np.r_[(w / 2) * np.sin(np.linspace(np.pi / 2, 3 * np.pi / 2, 30)), (w / 2) * np.sin(np.linspace(-np.pi / 2, np.pi / 2, 30))]
    ax.add_patch(Polygon(np.c_[xs, zs], closed=True, fc="#b9c0c9", ec=C_EDGE, lw=0.7, zorder=3.2))
    ax.add_patch(Circle((yP, 0), 6.35 / 2, fc="white", ec=C_EDGE, lw=0.7, zorder=3.2))
    ax.plot([yP, yP], [-R - 6, R + 6], zorder=3.3, **CL)
    # section / detail markers
    for x, nm in ((yP, "C"), (-36.0, "B")):
        for sg in (1, -1):
            ax.plot([x, x], [sg * (R + 9), sg * (R + 17)], color="k", lw=1.1, zorder=6)
            ax.add_patch(FancyArrowPatch((x, sg * (R + 17)), (x + 9, sg * (R + 17)), arrowstyle="-|>", mutation_scale=6, color="k", lw=0.8, shrinkA=0, shrinkB=0, zorder=6))
        ax.text(x + 11, R + 17, nm, fontsize=9, weight="bold", ha="left", va="center")
    ax.add_patch(Circle((yGL, R - 1), 7.5, fc="none", ec="k", lw=0.7, zorder=6))
    ax.text(yGL + 8, R + 9, "A", fontsize=9, weight="bold", ha="left", va="bottom", zorder=6)
    leader(ax, (yGU - 0.6, -R + 1), (yGU - 40, -R - 27), "upper ring groove\n(same as detail A)", ha="right", tsize=7.5)
    leader(ax, (yGL + 0.6, -R + 1), (yGL + 34, -R - 27), "lower ring groove", ha="left", tsize=7.5)
    # y-station ruler
    yr = -84
    ax.plot([yBOT, yTOP], [yr, yr], color=C_DIM, lw=0.6)
    stations = [(yBOT, "−250.5\nend", 0), (yP, "−185\npin", 0), (-36.0, "−47.11 to −24.89\nkeyseat", -16), (0.0, "0\ndatum", 6),
                (300.0, "300", -13), (yTOP, "303.5\nend", 11)]
    for y, lab, dx in stations:
        ax.plot([y, y], [yr - 4, yr + 4], color=C_DIM, lw=0.6)
        ax.plot([y, y], [yr + 4, -R - 22 if abs(y - yP) > 1 and abs(y + 36) > 1 else -R - 20], color=C_DIM, lw=0.3, ls=(0, (2, 2)))
        ax.text(y + dx, yr - 7, lab, fontsize=7.5, ha="center", va="top", color=C_DIM, linespacing=1.05)
    ax.text(yTOP + 14, yr, "y (mm)", fontsize=8, ha="left", va="center", color=C_DIM)
    ax.text(-120, yr - 7, "−150 … −250\nhub", fontsize=7.5, ha="center", va="top", color="#777", linespacing=1.05)
    dim(ax, (yBOT, 70), (yTOP, 70), "554 overall", tsize=8, text_off=(60, 0))
    ext(ax, (yBOT, R + 2), (yBOT, 74)); ext(ax, (yTOP, R + 2), (yTOP, 74))
    dim(ax, (318, -R), (318, R), "", tsize=7.5)
    ax.text(323, 0, "Ø38.10\n(37.998\nmin)", fontsize=7.5, color=C_DIM, ha="left", va="center", linespacing=1.05)
    ext(ax, (yTOP + 2, R), (322, R)); ext(ax, (yTOP + 2, -R), (322, -R))
    ax.text(-296, 85, "(a) Shaft layout, to scale (ring grooves drawn 3× wide)", fontsize=9, ha="left", va="top")


# ---------------------------------------------------------------- detail A: ring groove profile
def groove(ax):
    a, t, r = 0.7874, 0.5588, 0.2032
    ax.set_xlim(-1.75, 3.1); ax.set_ylim(17.45, 20.62); ax.set_aspect("equal"); ax.axis("off")
    th = np.linspace(0, np.pi / 2, 16)
    xl = -a / 2 + r - r * np.cos(th[::-1]); yl = R - t + r - r * np.sin(th[::-1])      # left corner, floor -> wall
    xr = a / 2 - r + r * np.cos(th); yr = R - t + r - r * np.sin(th)
    # material polygon (shaft below the surface)
    px = np.r_[-1.6, -a / 2, xl[::-1], xr[::-1], a / 2, 1.6, 1.6, -1.6]
    py = np.r_[R, R, yl[::-1], yr[::-1], R, R, 17.75, 17.75]
    px = np.r_[-1.6, -a / 2, -a / 2, xl[0:1] * 0 - a / 2, (-a / 2 + r - r * np.cos(th)), (a / 2 - r + r * np.cos(th[::-1])), a / 2, a / 2, 1.6, 1.6, -1.6]
    py = np.r_[R, R, R - t + r, R - t + r, (R - t + r - r * np.sin(th)), (R - t + r - r * np.sin(th[::-1])), R - t + r, R, R, 17.75, 17.75]
    ax.add_patch(Polygon(np.c_[px, py], closed=True, fc=C_CUT, ec=C_EDGE, lw=0.9, hatch="////", zorder=2))
    ax.plot([-1.6, 1.6], [17.75, 17.75], color="white", lw=2.5, zorder=3)
    ax.plot([-1.6, -1.45, -1.3, -1.6], [17.75, 17.83, 17.69, 17.75], color="white", lw=0)
    # ring (ghost)
    ax.add_patch(Rectangle((-a / 2 + 0.03, R - t + 0.02), 0.635, 1.25, fc="none", ec=C_GHOST, lw=0.7, ls=(0, (3, 2)), zorder=4))
    ax.text(-a / 2 - 0.08, R + 0.28, "ring, 0.635 thick", fontsize=7, color="#555", ha="right", va="center")
    # dims
    ext(ax, (-a / 2, R + 0.03), (-a / 2, R + 0.95)); ext(ax, (a / 2, R + 0.03), (a / 2, R + 0.95))
    dim(ax, (-a / 2, R + 0.85), (a / 2, R + 0.85), "", ms=4.5)
    ax.text(a / 2 + 0.08, R + 0.85, "a = 0.787–0.838", fontsize=7.5, color=C_DIM, va="center", ha="left")
    ext(ax, (a / 2 + 0.03, R - t), (1.75, R - t)); ext(ax, (1.63, R), (1.75, R))
    dim(ax, (1.68, R - t), (1.68, R), "", ms=4.5)
    ax.text(1.80, R - t / 2, "t = 0.508–0.559", fontsize=7.5, color=C_DIM, va="center", ha="left")
    leader(ax, (-a / 2 + r * (1 - 0.707), R - t + r * (1 - 0.707)), (-1.55, R - t - 0.5), "R 0.20–0.25 (both corners)", ha="left", tsize=7.5)
    ax.text(0, 17.6, "root Ø36.982–37.084", fontsize=7.5, color=C_DIM, ha="center", va="center")
    ax.text(-1.75, 20.62, "(b) Detail A: ring groove", fontsize=9, ha="left", va="top")
    ax.text(-1.75, 20.34, r"worst case $r/t$ = 0.364, $a/t$ = 1.41, $K_t$ = 3.6", fontsize=7.5, ha="left", va="top", color="#444")


def disc(ax, cut_poly_list, title, sub, x0=-34):
    ax.set_xlim(x0, x0 + 76); ax.set_ylim(-31, 45); ax.set_aspect("equal"); ax.axis("off")
    for poly in cut_poly_list:
        ax.add_patch(Polygon(poly, closed=True, fc=C_CUT, ec=C_EDGE, lw=0.9, hatch="////", zorder=2))
    ax.plot([-R - 5, R + 5], [0, 0], zorder=3, **CL); ax.plot([0, 0], [-R - 5, R + 5], zorder=3, **CL)
    ax.text(x0, 45, title, fontsize=9, ha="left", va="top")
    ax.text(x0, 40.2, sub, fontsize=7.5, ha="left", va="top", color="#444")


# ---------------------------------------------------------------- section B-B: keyseat
def keyseat(ax):
    W, S, rf = 9.525, 32.733, 0.794
    yf = S - R                       # keyseat floor above the shaft centre
    a0 = np.arcsin((W / 2) / R)
    th = np.linspace(np.pi / 2 + a0, 2.5 * np.pi - a0, 200)
    cx, cy = R * np.cos(th), R * np.sin(th)
    t = np.linspace(0, np.pi / 2, 10)
    fl_r = np.c_[W / 2 - rf + rf * np.sin(t[::-1]), yf + rf - rf * np.cos(t[::-1])]   # right wall -> floor
    fl_l = np.c_[-W / 2 + rf - rf * np.sin(t), yf + rf - rf * np.cos(t)]              # floor -> left wall
    poly = np.r_[np.c_[cx, cy], fl_r, fl_l]
    disc(ax, [poly], "(c) Section B–B: keyseat", "ASME B17.1 Class 1, 3/8 in square key")
    ytop = R * np.cos(a0)
    ax.add_patch(Rectangle((-9.449 / 2, yf + 0.2), 9.449, 9.449, fc="none", ec=C_GHOST, lw=0.7, ls=(0, (3, 2)), zorder=4))
    ax.text(W / 2 + 1.5, yf + 7.2, "key, 9.449–9.525 sq.", fontsize=7, color="#555", ha="left", va="center")
    ext(ax, (-W / 2, ytop + 9.6), (-W / 2, 31.2)); ext(ax, (W / 2, ytop + 9.6), (W / 2, 31.2))
    dim(ax, (-W / 2, 30), (W / 2, 30), "", ms=4.5)
    ax.text(W / 2 + 1.5, 30, "W = 9.525 +0.051/0", fontsize=7.5, color=C_DIM, ha="left", va="center")
    ext(ax, (W / 2 + 0.5, yf), (29.5, yf)); ext(ax, (2, -R), (29.5, -R))
    dim(ax, (27.5, -R), (27.5, yf), "S = 32.733 +0/−0.381", tsize=7.5, text_off=(3.2, 0), bg=False)
    leader(ax, (-W / 2 + rf * 0.3, yf + rf * 0.3), (-33, 25.5), "R 0.79 (1/32 in)\nfloor fillet", ha="left", tsize=7.5)
    ax.text(0, -R - 5.5, r"$K_t$ = 2.17, $K_{ts}$ = 2.59 at $r/d$ = 0.0209", fontsize=7.5, ha="center", va="top", color="#444")


# ---------------------------------------------------------------- section C-C: pin hole
def pinhole(ax):
    h = 6.378 / 2
    a0 = np.arcsin(h / R)
    up = np.linspace(a0, np.pi - a0, 120); lo = np.linspace(np.pi + a0, 2 * np.pi - a0, 120)
    disc(ax, [np.c_[R * np.cos(up), R * np.sin(up)], np.c_[R * np.cos(lo), R * np.sin(lo)]],
         "(d) Section C–C: pin hole", "1/4 in 416 dowel pin 98380A556, slip fit", x0=-27)
    ax.add_patch(Rectangle((-D, -6.35 / 2), 2 * D, 6.35, fc="none", ec=C_GHOST, lw=0.7, ls=(0, (3, 2)), zorder=4))
    ax.text(31, 4.6, "pin, 76.2 long", fontsize=7, color="#555", ha="left", va="bottom")
    ax.add_patch(FancyArrowPatch((24, h + 6), (24, h), arrowstyle="-|>", mutation_scale=4.5, color=C_DIM, lw=0.5, shrinkA=0, shrinkB=0, zorder=6))
    ax.add_patch(FancyArrowPatch((24, -h - 6), (24, -h), arrowstyle="-|>", mutation_scale=4.5, color=C_DIM, lw=0.5, shrinkA=0, shrinkB=0, zorder=6))
    ax.text(21.5, -h - 7.5, "Ø6.35 F7\n(6.363–6.378)\nthrough", fontsize=7.5, color=C_DIM, ha="left", va="top", linespacing=1.05)
    dim(ax, (-R, -24.5), (R, -24.5), "Ø37.998–38.100", tsize=7.5)
    ext(ax, (-R, -3), (-R, -26)); ext(ax, (R, -3), (R, -26))
    ax.text(0, 24, r"$a/D$ = 0.168: $K_t$ = 2.11, $K_{ts}$ = 1.61", fontsize=7.5, ha="center", va="bottom", color="#444",
            bbox=dict(fc="white", ec="none", pad=0.6))


def main():
    fig = plt.figure(figsize=(7.4, 5.55))
    layout(fig.add_axes([0.0, 0.48, 1.0, 0.52]))
    groove(fig.add_axes([0.01, 0.05, 0.34, 0.42]))
    keyseat(fig.add_axes([0.355, 0.05, 0.32, 0.42]))
    pinhole(fig.add_axes([0.675, 0.05, 0.32, 0.42]))
    fig.text(0.01, 0.012, "Dimensions in mm. Dashed outlines are mating parts, not part of the shaft. y = 0 at the outer face of the lower bearing.",
             fontsize=7.8, color="#444", ha="left")
    fig.savefig(os.path.join(HERE, "fig_shaft_layout.png"), dpi=300, facecolor="white")


if __name__ == "__main__":
    main()
