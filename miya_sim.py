import os
import csv

import matplotlib
matplotlib.use("Agg")

import numpy as np
import matplotlib.pyplot as plt
OUT = "miya_results"
os.makedirs(OUT, exist_ok=True)
UMDS parameters
q = 2.0
eta = 0.6
k_in = 0.2
k_out = 0.1
k_sink = 0.05
dt = 0.05
t_end = 100.0
t = np.arange(0.0, t_end + dt, dt)
n = len(t)
A = np.zeros(n)
M = np.zeros(n)
C = np.zeros(n)
F_in = np.zeros(n)
F_out = np.zeros(n)
F_sink = np.zeros(n)
A[0] = 10.0
M[0] = 5.0
C[0] = 2.0
for i in range(n - 1):
F_in[i] = k_in * A[i]
F_out[i] = k_out * M[i]
F_sink[i] = k_sink * C[i]
dA = q - F_in[i]
dM = eta * F_in[i] - F_out[i]
dC = (1.0 - eta) * F_in[i] + F_out[i] - F_sink[i]
A[i + 1] = A[i] + dt * dA
M[i + 1] = M[i] + dt * dM
C[i + 1] = C[i] + dt * dC
F_in[-1] = k_in * A[-1]
F_out[-1] = k_out * M[-1]
F_sink[-1] = k_sink * C[-1]
R = A + M + C
balance_lhs = np.diff(R) / dt
balance_rhs = q - F_sink[:-1]
balance_residual = balance_lhs - balance_rhs
A_star = q / k_in
M_star = eta * q / k_out
C_star = q / k_sink
csv_path = os.path.join(OUT, "umds_simulation.csv")
with open(csv_path, "w", newline="") as f:
writer = csv.writer(f)
writer.writerow([
"t",
"A",
"M",
"C",
"F_in",
"F_out",
"F_sink",
"R",
])
for i in range(n):
writer.writerow([
t[i],
A[i],
M[i],
C[i],
F_in[i],
F_out[i],
F_sink[i],
R[i],
])
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(t, A, label="A", linewidth=2.2)
ax.plot(t, M, label="M", linewidth=2.2)
ax.plot(t, C, label="C", linewidth=2.2)
ax.axhline(A_star, linestyle="--", alpha=0.5)
ax.axhline(M_star, linestyle="--", alpha=0.5)
ax.axhline(C_star, linestyle="--", alpha=0.5)
ax.set_title("UMDS State Evolution")
ax.set_xlabel("Time")
ax.set_ylabel("State")
ax.grid(alpha=0.25)
ax.legend()
fig.tight_layout()
fig.savefig(
os.path.join(OUT, "01_umds_states.png"),
dpi=200,
)
plt.close(fig)
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(t, F_in, label="F_in", linewidth=2)
ax.plot(t, F_out, label="F_out", linewidth=2)
ax.plot(t, F_sink, label="F_sink", linewidth=2)
ax.axhline(q, color="black", linestyle="--", label="q")
ax.set_title("UMDS Flow Evolution")
ax.set_xlabel("Time")
ax.set_ylabel("Flow")
ax.grid(alpha=0.25)
ax.legend()
fig.tight_layout()
fig.savefig(
os.path.join(OUT, "02_umds_flows.png"),
dpi=200,
)
plt.close(fig)
fig, ax = plt.subplots(figsize=(8, 7))
points = ax.scatter(
M,
C,
c=t,
cmap="viridis",
s=10,
)
ax.scatter(
M[0],
C[0],
color="red",
s=100,
label="Initial",
)
ax.scatter(
M_star,
C_star,
color="black",
marker="*",
s=180,
label="Equilibrium",
)
ax.set_title("UMDS Phase Trajectory")
ax.set_xlabel("M")
ax.set_ylabel("C")
ax.grid(alpha=0.25)
ax.legend()
colorbar = fig.colorbar(points, ax=ax)
colorbar.set_label("Time")
fig.tight_layout()
fig.savefig(
os.path.join(OUT, "03_umds_phase.png"),
dpi=200,
)
plt.close(fig)
fig, axes = plt.subplots(
2,
1,
figsize=(10, 8),
sharex=True,
)
axes[0].plot(t, R, color="purple", linewidth=2)
axes[0].set_title("Total Account R = A + M + C")
axes[0].set_ylabel("R")
axes[0].grid(alpha=0.25)
axes[1].plot(
t[:-1],
balance_residual,
color="darkred",
linewidth=1.5,
)
axes[1].axhline(0.0, color="black", linestyle="--")
axes[1].set_title("Accounting Residual")
axes[1].set_xlabel("Time")
axes[1].set_ylabel("Residual")
axes[1].grid(alpha=0.25)
fig.tight_layout()
fig.savefig(
os.path.join(OUT, "04_umds_balance.png"),
dpi=200,
)
plt.close(fig)
Q = np.array([0.7963, 0.0654, 0.1383], dtype=float)
Q = Q / Q.sum()
omega = np.exp(Q - np.max(Q))
omega = omega / omega.sum()
B = 12
raw_identity = Q * B
bits_identity = np.floor(raw_identity).astype(int)
remaining_identity = B - bits_identity.sum()
for index in np.argsort(
-(raw_identity - bits_identity)
)[:remaining_identity]:
bits_identity[index] += 1
raw_nested = omega * B
bits_nested = np.floor(raw_nested).astype(int)
remaining_nested = B - bits_nested.sum()
for index in np.argsort(
-(raw_nested - bits_nested)
)[:remaining_nested]:
bits_nested[index] += 1
radix_identity = 2 ** bits_identity
radix_nested = 2 ** bits_nested
labels = ["Component 1", "Component 2", "Component 3"]
x = np.arange(3)
width = 0.35
fig, axes = plt.subplots(
2,
1,
figsize=(10, 9),
)
axes[0].bar(
x - width / 2,
Q,
width,
label="Identity",
)
axes[0].bar(
x + width / 2,
omega,
width,
label="Nested softmax",
)
axes[0].set_xticks(x)
axes[0].set_xticklabels(labels)
axes[0].set_ylabel("Weight")
axes[0].set_title("QUAL Branch Comparison")
axes[0].legend()
axes[0].grid(axis="y", alpha=0.25)
axes[1].bar(
x - width / 2,
bits_identity,
width,
label="Identity bits",
)
axes[1].bar(
x + width / 2,
bits_nested,
width,
label="Nested bits",
)
axes[1].set_xticks(x)
axes[1].set_xticklabels(labels)
axes[1].set_ylabel("Bits")
axes[1].set_title("12-bit Allocation")
axes[1].legend()
axes[1].grid(axis="y", alpha=0.25)
fig.tight_layout()
fig.savefig(
os.path.join(OUT, "05_qual_branches.png"),
dpi=200,
)
plt.close(fig)
q_A = 5
q_M = 2
q_C = 7
q_eta = 1

z = q_A + (q_M << 3) + (q_C << 6) + (q_eta << 9)

decoded = np.array((z % 8, (z // 8) % 8, (z // 64) % 8, (z // 512) % 8))
original = np.array((q_A, q_M, q_C, q_eta))
codec_pass = np.array_equal(original, decoded)

fig, ax = plt.subplots(figsize=(9, 6))
x = np.arange(4)
ax.bar(
x - 0.18,
original,
width=0.36,
label="Original",
)
ax.bar(
x + 0.18,
decoded,
width=0.36,
label="Decoded",
)
ax.set_xticks(x)
ax.set_xticklabels([
"q_A",
"q_M",
"q_C",
"q_eta",
])
ax.set_ylim(0, 8)
ax.set_ylabel("Base-8 digit")
ax.set_title(
"MIYA-4096 z="
+ str(z)
+ " readback="
+ str(codec_pass)
)
ax.grid(axis="y", alpha=0.25)
ax.legend()
fig.tight_layout()
fig.savefig(
os.path.join(OUT, "06_miya4096_codec.png"),
dpi=200,
)
plt.close(fig)
print("=" * 60)
print("MIYA simulation completed")
print("=" * 60)
print("Final UMDS state:")
print("A =", round(A[-1], 6))
print("M =", round(M[-1], 6))
print("C =", round(C[-1], 6))
print("R =", round(R[-1], 6))
print()
print("Equilibrium:")
print("A_star =", round(A_star, 6))
print("M_star =", round(M_star, 6))
print("C_star =", round(C_star, 6))
print()
print(
"Max accounting residual =",
np.max(np.abs(balance_residual)),
)
print()
print("Identity bits =", bits_identity)
print("Identity radix =", radix_identity)
print("Nested bits =", bits_nested)
print("Nested radix =", radix_nested)
print()
print("MIYA-4096 z =", z)
print("Decoded =", tuple(decoded))
print("Codec readback pass =", codec_pass)
print()
print("Output directory =", os.path.abspath(OUT))
print("CALCULABLE != VERIFIED != PUBLISHED")
