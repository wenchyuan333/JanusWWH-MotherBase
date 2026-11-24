#!/usr/bin/env python3
"""collatz_viz.py - Collatz conjecture 2D spiral + 3D animated GIF
Output:
  collatz_2d.png  - polar spiral, colored by sequence length
  collatz_3d.gif  - rotating 3D animation
"""
import sys
import os


def check_deps():
    missing = []
    for pkg, inst in (("numpy", "numpy"), ("matplotlib", "matplotlib"), ("PIL", "Pillow")):
        try:
            __import__(pkg)
        except ImportError:
            missing.append(inst)
    return missing


missing = check_deps()
if missing:
    print("Missing packages:", " ".join(missing))
    print("Run: pip install " + " ".join(missing))
    sys.exit(1)

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import Normalize
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from PIL import Image
import io

BG = "#07070f"


# ── Collatz core ─────────────────────────────────────────────────────────────
def collatz(n):
    seq = [n]
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        seq.append(n)
    return seq


N_MAX = 250
print("Computing sequences...")
sequences = {n: collatz(n) for n in range(1, N_MAX + 1)}
lengths = {n: len(sequences[n]) for n in sequences}
max_len = max(lengths.values())
print("Max sequence length:", max_len)


# ── 2D: Polar golden-angle spiral ────────────────────────────────────────────
print("Rendering 2D...")
fig1, ax1 = plt.subplots(
    figsize=(13, 13),
    subplot_kw={"projection": "polar"},
    facecolor=BG,
)
ax1.set_facecolor(BG)
ax1.set_axis_off()

cmap1 = cm.plasma
norm1 = Normalize(vmin=1, vmax=max_len)
golden = (1.0 + 5.0 ** 0.5) / 2.0

for n in range(1, N_MAX + 1):
    seq = sequences[n]
    L = len(seq)
    color = cmap1(norm1(L))
    theta_base = n * 2.0 * np.pi / golden
    thetas = [theta_base + i * 0.07 for i in range(L)]
    rs = [np.log1p(v) * 0.9 for v in seq]
    ax1.plot(thetas, rs, alpha=0.30, linewidth=0.55, color=color)
    # mark starting point
    ax1.scatter(
        [thetas[0]], [rs[0]],
        s=max(1.5, 8 - n * 0.02),
        color=color, alpha=0.85, zorder=5, linewidths=0,
    )

# colorbar
sm = cm.ScalarMappable(cmap=cmap1, norm=norm1)
sm.set_array([])
cbar = fig1.colorbar(sm, ax=ax1, pad=0.06, fraction=0.025, orientation="vertical")
cbar.set_label("Sequence length", color="#ccccdd", fontsize=11, labelpad=10)
cbar.ax.yaxis.set_tick_params(color="#888899")
plt.setp(cbar.ax.yaxis.get_ticklabels(), color="#aaaacc")
cbar.outline.set_edgecolor("#333355")

ax1.set_title(
    "Collatz Conjecture  ·  Polar Spiral\nN = 1\u2013250   colored by sequence length",
    color="#e8e0ff", fontsize=13, pad=22, fontweight="bold",
)
fig1.tight_layout()
fig1.savefig("collatz_2d.png", dpi=160, facecolor=BG, bbox_inches="tight")
plt.close(fig1)
print("Saved collatz_2d.png")


# ── 3D: Rotating GIF ─────────────────────────────────────────────────────────
print("Rendering 3D frames...")
N_3D = 90
FRAMES = 54
ELEV = 28

fig2 = plt.figure(figsize=(9, 7), facecolor=BG)
ax2 = fig2.add_subplot(111, projection="3d")

cmap2 = cm.rainbow
norm2 = Normalize(vmin=1, vmax=N_3D)

lines_data = []
for n in range(1, N_3D + 1):
    seq = sequences[n]
    xs = [n] * len(seq)
    ys = list(range(len(seq)))
    zs = [np.log1p(v) for v in seq]
    lines_data.append((xs, ys, zs, cmap2(norm2(n))))


def style_ax(ax, azim):
    ax.cla()
    ax.set_facecolor(BG)
    ax.tick_params(colors="#44445a", labelsize=6.5)
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.xaxis.pane.set_edgecolor("#1a1a2e")
    ax.yaxis.pane.set_edgecolor("#1a1a2e")
    ax.zaxis.pane.set_edgecolor("#1a1a2e")
    ax.grid(True, color="#111122", linewidth=0.35)
    for xs, ys, zs, color in lines_data:
        ax.plot(xs, ys, zs, color=color, alpha=0.50, linewidth=0.75)
    ax.set_xlabel("N", color="#8888aa", fontsize=8, labelpad=4)
    ax.set_ylabel("Step", color="#8888aa", fontsize=8, labelpad=4)
    ax.set_zlabel("log(val)", color="#8888aa", fontsize=8, labelpad=4)
    ax.set_title("Collatz 3D  ·  N = 1\u201390", color="#ddddf5", fontsize=11, pad=6)
    ax.view_init(elev=ELEV, azim=azim)


frames = []
for i in range(FRAMES):
    azim = -55.0 + 360.0 * i / FRAMES
    style_ax(ax2, azim)
    buf = io.BytesIO()
    fig2.savefig(buf, format="png", dpi=88, facecolor=BG, bbox_inches="tight")
    buf.seek(0)
    frames.append(Image.open(buf).copy())
    buf.close()
    if (i + 1) % 9 == 0:
        print("  frame", i + 1, "/", FRAMES)

plt.close(fig2)
frames[0].save(
    "collatz_3d.gif",
    save_all=True,
    append_images=frames[1:],
    duration=55,
    loop=0,
    optimize=False,
)
print("Saved collatz_3d.gif")
print("Done. Run time varies; 3D GIF may take 1-3 min on Termux.")