"""Part C: internal load diagrams N, Vy, Vz, T, My, Mz along the support beam (PNG, no title)."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from beam_internal import internal, x_l, x_r, xg, a

plt.rcParams.update({"font.family": "STIXGeneral", "mathtext.fontset": "stix", "font.size": 10, "axes.linewidth": 0.6})
eps = 1e-6
xs = np.unique(np.concatenate([np.linspace(x_l, x_r, 2701)] + [[k - eps, k + eps] for k in (-1200, -a, xg, 0)]))
D = np.array([np.concatenate(internal(x)) for x in xs])
panels = [(0, 1, r"$N$ (N)", "N"), (1, 1, r"$V_y$ (N)", "N"), (2, 1, r"$V_z$ (N)", "N"), (3, 1e3, r"$T = M_x$ (N$\cdot$m)", "N·m"), (4, 1e3, r"$M_y$ (N$\cdot$m)", "N·m"), (5, 1e3, r"$M_z$ (N$\cdot$m)", "N·m")]
fig, axs = plt.subplots(6, 1, figsize=(6.5, 10.2), sharex=True)
for ax, (i, sc, lab, unit) in zip(axs, panels):
    y = D[:, i] / sc
    ax.fill_between(xs, y, color="#4a78b5", alpha=0.18, lw=0); ax.plot(xs, y, color="#1f4e8c", lw=1.2)
    ax.axhline(0, color="k", lw=0.5); ax.set_ylabel(lab)
    k = np.argmax(np.abs(y)); ax.plot(xs[k], y[k], "o", color="#c0392b", ms=3.5, zorder=5)
    txt = f"{y[k]:.0f} {unit}" if i in (0, 1, 2) else f"{y[k]:.1f} {unit}"
    ax.annotate(txt, (xs[k], y[k]), xytext=(8, -12 if y[k] < 0 else 6), textcoords="offset points", fontsize=9, color="#c0392b")
    lo, hi = min(y.min(), 0), max(y.max(), 0); pad = 0.25 * (hi - lo); ax.set_ylim(lo - pad, hi + pad)
    for xv in (-1200, -a, xg, 0): ax.axvline(xv, color="#999", lw=0.5, ls=(0, (4, 3)))
    ax.tick_params(direction="in", length=3, width=0.5)
top = axs[0]
for xv, s in ((-1200, "Rotor"), (-a, "A"), (xg, "Gen."), (0, "O")):
    top.text(xv, top.get_ylim()[1], s, ha="center", va="bottom", fontsize=9)
axs[-1].set_xlabel(r"$x$ (mm)"); axs[-1].set_xlim(x_l, x_r)
fig.tight_layout(h_pad=0.6)
fig.savefig("fig_beam_internal_loads.png", dpi=300, facecolor="white")
