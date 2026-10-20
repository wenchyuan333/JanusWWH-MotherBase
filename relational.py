import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

C = 1.0
X_A, X_B = 0.0, 1.0
T_A, T_B = 0.0, 0.0

def boost(t, x, v):
    g = 1.0 / math.sqrt(1 - v*v)
    return g*(t - v*x), g*(x - v*t)

def ds2(t1, x1, t2, x2):
    return -(t2-t1)**2 + (x2-x1)**2

velocities = [i*0.05 for i in range(-18, 19)]
ds2_rest = ds2(T_A, X_A, T_B, X_B)

x_As, x_Bs, x_mids, intervals = [], [], [], []
for v in velocities:
    tA_, xA_ = boost(T_A, X_A, v)
    tB_, xB_ = boost(T_B, X_B, v)
    x_As.append(xA_); x_Bs.append(xB_)
    x_mids.append((xA_+xB_)/2)
    intervals.append(ds2(tA_, xA_, tB_, xB_))

print("=== relational invariant ===")
print(f"ds^2 rest = {ds2_rest:.6f}")
print(f"{'v':>6}  {'x_A':>8}  {'x_B':>8}  {'mid':>8}  {'ds^2':>12}")
for v, xA, xB, xm, d in zip(velocities, x_As, x_Bs, x_mids, intervals):
    print(f"{v:>6.2f}  {xA:>8.4f}  {xB:>8.4f}  {xm:>8.4f}  {d:>12.8f}")

drift = max(abs(d - ds2_rest) for d in intervals)
print(f"\nmax drift = {drift:.2e}")
print("VERDICT: " + ("interval invariant, positions shift." if drift < 1e-9
      else "MISMATCH -- check code."))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))

ax1.plot(velocities, x_As, "o-", ms=4, label="x_A (person A)")
ax1.plot(velocities, x_Bs, "s-", ms=4, label="x_B (person B)")
ax1.plot(velocities, x_mids, "--", color="gray", lw=1, label="midpoint")
ax1.set_xlabel("boost v/c"); ax1.set_ylabel("x coordinate")
ax1.set_title("Fig 1  Background moves:\npositions shift with every frame")
ax1.legend(fontsize=8); ax1.grid(True, alpha=0.3)

ax2.plot(velocities, intervals, "o-", color="#225", ms=4)
ax2.axhline(ds2_rest, color="r", ls="--", lw=1.5,
            label=f"rest value = {ds2_rest:.4f}")
ax2.set_xlabel("boost v/c"); ax2.set_ylabel("ds^2")
ax2.set_title("Fig 2  Between them stays:\ninterval is invariant")
ax2.legend(fontsize=8); ax2.grid(True, alpha=0.3)
ax2.set_ylim(ds2_rest - 0.5, ds2_rest + 0.5)

fig.tight_layout()
fig.savefig("fig_relational.png", dpi=160)
plt.close(fig)

t_vals = [i*0.1 for i in range(-10, 11)]
fig, axes = plt.subplots(1, 2, figsize=(10, 5))
for ax, (v_use, title) in zip(axes, [(0.0, "Rest frame"),
                                      (0.60, "Boosted frame  v=0.60c")]):
    for x0, col, name in [(X_A, "#225", "Person A"), (X_B, "#a22", "Person B")]:
        ts_ = [boost(t, x0, v_use)[0] for t in t_vals]
        xs_ = [boost(t, x0, v_use)[1] for t in t_vals]
        ax.plot(xs_, ts_, "-", color=col, lw=2, label=name)
        ax.plot(xs_[10], ts_[10], "o", color=col, ms=8)
    tA0, xA0 = boost(0, X_A, v_use)
    tB0, xB0 = boost(0, X_B, v_use)
    ax.annotate("", xy=(xB0, tB0), xytext=(xA0, tA0),
                arrowprops=dict(arrowstyle="<->", color="green", lw=2))
    mid_x = (xA0+xB0)/2; mid_t = (tA0+tB0)/2
    ax.text(mid_x, mid_t+0.15, f"ds^2={ds2_rest:.2f}",
            ha="center", fontsize=9, color="green")
    ax.set_xlabel("x"); ax.set_ylabel("t"); ax.set_title(title)
    ax.legend(fontsize=8); ax.grid(True, alpha=0.3)
    ax.set_xlim(-2.5, 3.5); ax.set_ylim(-1.2, 1.2)

fig.tight_layout()
fig.savefig("fig_worldlines.png", dpi=160)
plt.close(fig)
print("saved fig_relational.png  fig_worldlines.png")
