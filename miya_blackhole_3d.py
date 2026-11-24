import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

G = 6.67430e-11
c = 2.99792458e8
hbar = 1.054571817e-34
k_B = 1.380649e-23
M_sun = 1.98892e30


def schwarzschild_quantities(M):
    r_s = 2 * G * M / c ** 2
    kappa = c ** 4 / (4 * G * M)
    A = 4 * math.pi * r_s ** 2
    S = k_B * A * c ** 3 / (4 * G * hbar)
    T_H = hbar * kappa / (2 * math.pi * c * k_B)
    P = hbar * c ** 6 / (15360 * math.pi * G ** 2 * M ** 2)
    t_evap = 5120 * math.pi * G ** 2 * M ** 3 / (hbar * c ** 4)
    return dict(r_s=r_s, kappa=kappa, A=A, S=S, T_H=T_H, P=P, t_evap=t_evap)


def kerr_quantities(M, a_star):
    r_s = 2 * G * M / c ** 2
    a = a_star * r_s / 2.0
    root = math.sqrt(max(0.0, 1 - a_star ** 2))
    r_plus = (r_s / 2.0) * (1 + root)
    r_minus = (r_s / 2.0) * (1 - root)
    A = 4 * math.pi * (r_plus ** 2 + a ** 2)
    Omega_H = a * c / (r_plus ** 2 + a ** 2)
    kappa = c ** 4 * root / (2 * G * M * (1 + root)) if root > 0 else 0.0
    T_H = hbar * kappa / (2 * math.pi * c * k_B)
    return dict(r_s=r_s, a=a, r_plus=r_plus, r_minus=r_minus, A=A, Omega_H=Omega_H, kappa=kappa, T_H=T_H)


M_target = 10 * M_sun
sch = schwarzschild_quantities(M_target)
print("=== [1] Schwarzschild real numbers (M = 10 Msun) ===")
for k, v in sch.items():
    print(f"  {k} = {v:.6e}")

a_star_target = 0.9
kerr = kerr_quantities(M_target, a_star_target)
print()
print(f"=== [2] Kerr real numbers (M = 10 Msun, a_star = {a_star_target}) ===")
for k, v in kerr.items():
    print(f"  {k} = {v:.6e}")

dE_dM = c ** 2
dS_dM = 8 * math.pi * k_B * G * M_target / (hbar * c)
T_via_thermo = dE_dM / dS_dM
T_via_kappa = sch["T_H"]
closed_loop_match = abs(T_via_thermo - T_via_kappa) / T_via_kappa < 1e-9
print()
print("=== [3] Closed-loop check (dE/dS vs kappa-derived T_H) ===")
print(f"  T_via_thermo = {T_via_thermo:.6e}")
print(f"  T_via_kappa  = {T_via_kappa:.6e}")
print(f"  closed_loop_match = {closed_loop_match}")

r_s_norm = 2.0
r_vals = np.linspace(r_s_norm, r_s_norm * 6, 60)
theta_vals = np.linspace(0, 2 * np.pi, 60)
R, THETA = np.meshgrid(r_vals, theta_vals)
X_sch = R * np.cos(THETA)
Y_sch = R * np.sin(THETA)
Z_sch = 2 * np.sqrt(r_s_norm * np.maximum(R - r_s_norm, 0))

a_star_norm = a_star_target
root_norm = math.sqrt(1 - a_star_norm ** 2)
r_plus_norm = (r_s_norm / 2.0) * (1 + root_norm)

phi_vals = np.linspace(0, 2 * np.pi, 60)
th_vals = np.linspace(0, np.pi, 60)
PHI, TH = np.meshgrid(phi_vals, th_vals)

X_hz = r_plus_norm * np.sin(TH) * np.cos(PHI)
Y_hz = r_plus_norm * np.sin(TH) * np.sin(PHI)
Z_hz = r_plus_norm * np.cos(TH)

r_E = (r_s_norm / 2.0) * (1 + np.sqrt(np.maximum(0.0, 1 - (a_star_norm ** 2) * np.cos(TH) ** 2)))
X_erg = r_E * np.sin(TH) * np.cos(PHI)
Y_erg = r_E * np.sin(TH) * np.sin(PHI)
Z_erg = r_E * np.cos(TH)

fig = plt.figure(figsize=(10, 5))
ax1 = fig.add_subplot(1, 2, 1, projection="3d")
ax2 = fig.add_subplot(1, 2, 2, projection="3d")

ax1.plot_surface(X_sch, Y_sch, Z_sch, cmap="inferno", linewidth=0, antialiased=True, alpha=0.9)
ax1.set_title("Schwarzschild embedding\n(Flamm's paraboloid, a=0)")
ax1.set_box_aspect((1, 1, 0.6))
ax1.set_axis_off()

ax2.plot_surface(X_erg, Y_erg, Z_erg, color="orange", alpha=0.35, linewidth=0)
ax2.plot_surface(X_hz, Y_hz, Z_hz, color="black", alpha=1.0, linewidth=0)
ax2.set_title(f"Kerr horizon + ergosphere\n(a_star={a_star_norm})")
ax2.set_box_aspect((1, 1, 1))
ax2.set_axis_off()

n_frames = 36


def update(frame):
    angle = frame * (360 / n_frames)
    ax1.view_init(elev=25, azim=angle)
    ax2.view_init(elev=20, azim=angle)
    return []


anim = FuncAnimation(fig, update, frames=n_frames, interval=80, blit=False)
anim.save("miya_blackhole_3d.gif", writer=PillowWriter(fps=12))
print()
print("saved miya_blackhole_3d.gif")
