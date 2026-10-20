import math, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as mpatches
import numpy as np

OUT = os.path.expanduser("~/storage/pictures/")
os.makedirs(OUT, exist_ok=True)

# ── observers ────────────────────────────────────────────────────────────────
velocities = [0.0, 0.50, 0.80, 0.95]
colors     = ["#2255aa", "#22aa55", "#aaaa22", "#aa2222"]
labels     = ["v = 0  (rest)", "v = 0.50c", "v = 0.80c", "v = 0.95c"]

def gamma(v): return 1.0 / math.sqrt(1 - v*v)
def proper_time(t, v): return t / gamma(v)   # tau = t * sqrt(1-v^2)

# ── numeric report ───────────────────────────────────────────────────────────
T_coord = 10.0
print("=== time dilation ===")
print(f"Coordinate time elapsed : {T_coord:.1f}  (rest frame)")
print()
print(f"{'v/c':>6}  {'gamma':>7}  {'proper time tau':>15}  {'ratio tau/T':>12}")
for v in velocities:
    g  = gamma(v)
    tau = proper_time(T_coord, v)
    print(f"{v:>6.2f}  {g:>7.4f}  {tau:>15.4f}  {tau/T_coord:>12.6f}")

print()
print("VERDICT: each person's clock ticks at a different rate.")
print("         Faster motion => slower proper time => younger traveller.")

# ── static figure ────────────────────────────────────────────────────────────
ts = [i * 0.1 for i in range(101)]
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

ax = axes[0]
for v, col, lab in zip(velocities, colors, labels):
    taus = [proper_time(t, v) for t in ts]
    ax.plot(ts, taus, "-", color=col, lw=2, label=lab)
ax.plot(ts, ts, "k--", lw=1, alpha=0.4, label="tau = T  (reference)")
ax.set_xlabel("coordinate time T"); ax.set_ylabel("proper time tau")
ax.set_title("Fig 1  Proper time vs coordinate time")
ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

ax = axes[1]
gs = [gamma(v) for v in velocities]
ax.bar(range(len(velocities)), gs, color=colors)
ax.set_xticks(range(len(velocities)))
ax.set_xticklabels([f"{v}c" for v in velocities])
ax.set_ylabel("Lorentz factor gamma")
ax.set_title("Fig 2  Gamma factor\n(how much coordinate time per unit proper time)")
for i, g in enumerate(gs):
    ax.text(i, g + 0.05, f"{g:.3f}", ha="center", fontsize=9)
ax.grid(True, alpha=0.3, axis="y")

fig.suptitle("Time dilation: everyone's clock ticks differently", fontsize=11)
fig.tight_layout()
fig.savefig(OUT + "fig_time_dilation.png", dpi=160)
plt.close(fig)

# ── GIF: four clocks ticking at different rates ───────────────────────────────
N_FRAMES = 72          # one full revolution of rest clock
FIG_GIF, AX_CLOCKS = plt.subplots(1, 4, figsize=(11, 3.2))
FIG_GIF.patch.set_facecolor("#111")

clock_axes = []
clock_hands = []
clock_texts = []

for i, (v, col, lab) in enumerate(zip(velocities, colors, labels)):
    ax = AX_CLOCKS[i]
    ax.set_facecolor("#222")
    ax.set_xlim(-1.3, 1.3); ax.set_ylim(-1.3, 1.3)
    ax.set_aspect("equal"); ax.axis("off")

    # clock face
    theta_ticks = [k * math.pi / 6 for k in range(12)]
    for th in theta_ticks:
        ax.plot([0.85*math.sin(th), math.sin(th)],
                [0.85*math.cos(th), math.cos(th)], color="white", lw=1.5)

    circle = plt.Circle((0, 0), 1.0, color=col, fill=False, lw=2.5)
    ax.add_patch(circle)

    hand, = ax.plot([0, 0], [0, 0.75], color=col, lw=3, solid_capstyle="round")
    tau_rate = 1.0 / gamma(v)
    txt = ax.text(0, -1.2, f"tau/T = {tau_rate:.4f}", ha="center",
                  fontsize=8.5, color=col)
    ax.text(0, 1.18, lab, ha="center", fontsize=8, color="white")

    clock_axes.append(ax)
    clock_hands.append((hand, tau_rate))
    clock_texts.append(txt)

elapsed_text = FIG_GIF.text(0.5, 0.97,
    "Coordinate time T = 0.00",
    ha="center", va="top", fontsize=10, color="white")

FIG_GIF.suptitle("Time dilation: same coordinate time, different proper time",
                  fontsize=10, color="white", y=0.06)

def update(frame):
    T = frame / N_FRAMES * 10.0       # coordinate time 0..10
    elapsed_text.set_text(f"Coordinate time T = {T:.2f}")
    for hand, tau_rate in clock_hands:
        tau = T * tau_rate             # proper time ticked
        angle = 2 * math.pi * (tau % 1.0)   # one rev per unit tau
        hx = 0.75 * math.sin(angle)
        hy = 0.75 * math.cos(angle)
        hand.set_data([0, hx], [0, hy])
    return [h for h, _ in clock_hands] + [elapsed_text]

ani = animation.FuncAnimation(FIG_GIF, update, frames=N_FRAMES,
                               interval=60, blit=True)

writer = animation.PillowWriter(fps=16)
gif_path = OUT + "time_dilation.gif"
ani.save(gif_path, writer=writer)
plt.close(FIG_GIF)

os.system(f"termux-media-scan {OUT}fig_time_dilation.png")
os.system(f"termux-media-scan {gif_path}")

print()
print("saved fig_time_dilation.png")
print(f"saved time_dilation.gif  ({gif_path})")
