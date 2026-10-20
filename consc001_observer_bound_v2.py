#!/usr/bin/env python3
# consc001_observer_bound_v2.py  --  paste and run
# CONSC-001 : upper bound on a per-observer "consciousness" acceleration,
#             inferred from lunar laser ranging (LLR) residuals.
#
# v2 changes:
#   * all figure text is ASCII  -> no CJK font, no tofu boxes, no warnings
#   * Fig 2 runs the FULL 50 yr, A values spaced by decades
#   * linear-in-A trick: simulate once with A = 1, then rescale
#   * Fig 5 (new) = tau sweep, the corrected test #4
#   * numeric slope fits printed, not eyeballed

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

matplotlib.rcParams["axes.unicode_minus"] = False
# For Chinese titles instead: pkg install noto-fonts-cjk, then uncomment
# matplotlib.rcParams["font.sans-serif"] = ["Noto Sans CJK TC", "DejaVu Sans"]

SEED    = 20260817          # registered seed (SEED-001 rule)
rng     = np.random.default_rng(SEED)

G       = 6.674e-11        # m^3 kg^-1 s^-2
M_HUMAN = 70.0             # kg
YEAR    = 3.15576e7        # s
T       = 50 * YEAR        # observation span
TAU     = 86400.0          # correlation time, 1 day  (DECLARED IN ADVANCE)
X_LIM   = 1e-3             # LLR residual, 1 mm
N_POP   = 8e9              # observers
N_STEP  = int(T / TAU)


def walk_exact(n):
    n = np.asarray(n, dtype=float)
    return np.sqrt(n * (n + 1.0) * (2.0 * n + 1.0) / 6.0)


def walk_approx(n):
    n = np.asarray(n, dtype=float)
    return np.sqrt(n ** 3 / 3.0)


def K_of(tau, span=T):
    # closed form: K = sqrt(tau) * span**1.5 / sqrt(3)
    return tau ** 2 * walk_approx(span / tau)


K       = TAU ** 2 * walk_exact(N_STEP)
K_APX   = TAU ** 2 * walk_approx(N_STEP)
A_MAX   = X_LIM / K
EPS_MAX = A_MAX / np.sqrt(N_POP)
G_HUMAN = G * M_HUMAN / 1.0 ** 2
K_CLOSED = np.sqrt(TAU) * T ** 1.5 / np.sqrt(3.0)

print("=== CONSC-001 v2 ===")
print(f"seed            = {SEED}")
print(f"n steps         = {N_STEP}")
print(f"K exact         = {K:.5e} s^2")
print(f"K approx        = {K_APX:.5e} s^2   rel.diff = {abs(K-K_APX)/K:.2e}")
print(f"K closed form   = {K_CLOSED:.5e} s^2   rel.diff = {abs(K-K_CLOSED)/K:.2e}")
print(f"A_max           = {A_MAX:.4e} m/s^2")
print(f"eps_max         = {EPS_MAX:.4e} m/s^2")
print(f"g_human @ 1 m   = {G_HUMAN:.4e} m/s^2")
print(f"ratio           = {G_HUMAN / EPS_MAX:.4e}")

# ---- corrected test #4 : tau sweep -------------------------------------
A_DAY  = X_LIM / K_of(86400.0)
A_YEAR = X_LIM / K_of(YEAR)
print("\n--- test #4 (tau) ---")
print(f"A_max(tau=1 day)  = {A_DAY:.4e}")
print(f"A_max(tau=1 yr )  = {A_YEAR:.4e}")
print(f"ratio             = {A_DAY / A_YEAR:.3f}   expected sqrt(365.4) = "
      f"{np.sqrt(YEAR / 86400.0):.3f}")
print("=> bound TIGHTENS by ~19x, i.e. 1.3 decades, NOT two decades")

# ---- Fig 1 : sqrt(N) vs the cancellation myth ---------------------------
Ns  = np.unique(np.logspace(0, 5, 26).astype(int))
rms = np.array([rng.normal(size=(4000, int(N))).sum(axis=1).std() for N in Ns])
sel = Ns > 10
slope1 = np.polyfit(np.log10(Ns[sel]), np.log10(rms[sel]), 1)[0]
print(f"\nFig1 fitted slope = {slope1:+.4f}   expected +0.5")

fig, ax = plt.subplots(figsize=(5.4, 4.2))
ax.loglog(Ns, rms, "o", ms=5, label="Monte Carlo")
ax.loglog(Ns, np.sqrt(Ns), "-", label=r"$\sqrt{N}$  (prediction)")
ax.loglog(Ns, 1.0 / Ns, "--", label=r"$1/N$  (cancellation myth)")
ax.set_xlabel("N observers")
ax.set_ylabel(r"rms of $\sum_i \zeta_i$")
ax.set_title(f"Fig 1  contradictory != cancelling  (slope {slope1:+.3f})")
ax.legend()
fig.tight_layout()
fig.savefig("fig1_sqrtN.png", dpi=160)
plt.close(fig)

# ---- Fig 2 : full 50 yr random walk ------------------------------------
def unit_walk(n, tau, trials=200):
    # x_rms for A = 1, in metres
    z = rng.standard_normal((trials, n))
    np.cumsum(z, axis=1, out=z)     # velocity / (A*tau)
    np.cumsum(z, axis=1, out=z)     # position / (A*tau^2)
    return z.std(axis=0) * tau ** 2

base = unit_walk(N_STEP, TAU)
print(f"Fig2 endpoint check: MC {base[-1]:.4e} vs K {K:.4e}  "
      f"rel.diff {abs(base[-1]-K)/K:.3f}  (expect ~1/sqrt(2*trials) = "
      f"{1/np.sqrt(400):.3f})")

yrs = np.arange(1, N_STEP + 1) * TAU / YEAR
step = 25
slope2 = np.polyfit(np.log10(yrs[N_STEP // 2::step]),
                    np.log10(base[N_STEP // 2::step]), 1)[0]
print(f"Fig2 fitted slope = {slope2:+.4f}   expected +1.5")

fig, ax = plt.subplots(figsize=(5.4, 4.2))
for A, lab in [(1e-17, r"$A=10^{-17}$"),
               (1e-18, r"$A=10^{-18}$"),
               (A_MAX, r"$A=A_{max}$")]:
    ax.loglog(yrs[::step], (A * base)[::step], label=lab)
ax.axhline(X_LIM, color="k", ls=":", label="LLR limit 1 mm")
ax.axvline(50.0, color="gray", ls=":", lw=0.8)
ax.set_xlabel("years")
ax.set_ylabel(r"$x_{rms}$  (m)")
ax.set_title(f"Fig 2  random walk, $x \\propto T^{{1.5}}$  (slope {slope2:+.3f})")
ax.legend()
fig.tight_layout()
fig.savefig("fig2_walk.png", dpi=160)
plt.close(fig)

# ---- Fig 3 : bound vs N, coherent vs incoherent -------------------------
Nn = np.logspace(0, 10, 300)
fig, ax = plt.subplots(figsize=(5.4, 4.2))
ax.loglog(Nn, A_MAX / np.sqrt(Nn), label=r"incoherent  $A=\epsilon\sqrt{N}$")
ax.loglog(Nn, A_MAX / Nn, "--", label=r"coherent  $A=\epsilon N$")
ax.axhline(G_HUMAN, color="r", ls="-.", label="human gravity @ 1 m")
ax.axvline(N_POP, color="gray", ls=":", label="world population")
ax.plot([N_POP], [EPS_MAX], "k*", ms=12, label=r"$\epsilon_{max}$")
ax.set_xlabel("N")
ax.set_ylabel(r"$\epsilon_{max}$  (m/s$^2$)")
ax.set_title("Fig 3  bound vs N and coherence mode")
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig("fig3_bound.png", dpi=160)
plt.close(fig)

# ---- Fig 4 : three instruments ------------------------------------------
labels = ["eye\n(photon)", "knife\n(lab balance)", "Moon\n(LLR)"]
bounds = [1e-2, 1e-14, EPS_MAX]     # order of magnitude, cite each separately
fig, ax = plt.subplots(figsize=(5.4, 4.2))
bars = ax.bar(labels, bounds, color=["#bbbbbb", "#7777aa", "#222255"])
for b, v in zip(bars, bounds):
    ax.text(b.get_x() + b.get_width() / 2, v * 2.5, f"{v:.1e}",
            ha="center", fontsize=8)
ax.set_yscale("log")
ax.set_ylim(1e-27, 1e2)
ax.set_ylabel(r"$\epsilon_{max}$  (m/s$^2$)")
ax.set_title("Fig 4  bigger scale -> tighter bound")
fig.tight_layout()
fig.savefig("fig4_instruments.png", dpi=160)
plt.close(fig)

# ---- Fig 5 : tau sweep, the corrected test #4 --------------------------
taus = np.logspace(np.log10(60.0), np.log10(10 * YEAR), 200)
fig, ax = plt.subplots(figsize=(5.4, 4.2))
ax.loglog(taus / 86400.0, X_LIM / K_of(taus), label=r"$A_{max}(\tau)$")
ax.loglog(taus / 86400.0,
          A_DAY * (taus / 86400.0) ** -0.5, "--",
          label=r"$\propto \tau^{-1/2}$")
ax.plot([1.0], [A_DAY], "ko", label=r"$\tau=1$ day")
ax.plot([365.4], [A_YEAR], "rs", label=r"$\tau=1$ yr")
ax.set_xlabel(r"$\tau$  (days)")
ax.set_ylabel(r"$A_{max}$  (m/s$^2$)")
ax.set_title(r"Fig 5  the bound scales as $\tau^{-1/2}$, not 2 decades")
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig("fig5_tau.png", dpi=160)
plt.close(fig)

print("\nsaved fig1..fig5")