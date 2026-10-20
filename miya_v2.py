import os
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

out = "miya_v2_results"
os.makedirs(out, exist_ok=True)

dt = 0.05
t = np.arange(0.0, 100.0 + dt, dt)
n = len(t)

A = np.zeros(n)
M = np.zeros(n)
C = np.zeros(n)
A[0] = 10.0
M[0] = 5.0
C[0] = 2.0

q = 2.0
eta = 0.6

for i in range(n - 1):
    fin = 0.2 * A[i]
    fout = 0.1 * M[i]
    fsink = 0.05 * C[i]
    A[i + 1] = A[i] + dt * (q - fin)
    M[i + 1] = M[i] + dt * (eta * fin - fout)
    C[i + 1] = C[i] + dt * ((1.0 - eta) * fin + fout - fsink)

R = A + M + C
Fsink = 0.05 * C
ledger_left = np.diff(R) / dt
ledger_right = q - Fsink[:-1]
ledger_error = ledger_left - ledger_right

Q = np.array((0.7963, 0.0654, 0.1383))
Q = Q / Q.sum()
Omega = np.exp(Q)
Omega = Omega / Omega.sum()

qA = 5
qM = 2
qC = 7
qEta = 1
z = qA + 8 * qM + 64 * qC + 512 * qEta
decoded = (
    z % 8,
    (z // 8) % 8,
    (z // 64) % 8,
    (z // 512) % 8,
)
codec_pass = decoded == (qA, qM, qC, qEta)

fig, axes = plt.subplots(2, 2, figsize=(12, 9))

axes[0, 0].plot(t, A, label="A")
axes[0, 0].plot(t, M, label="M")
axes[0, 0].plot(t, C, label="C")
axes[0, 0].set_title("UMDS states")
axes[0, 0].set_xlabel("time")
axes[0, 0].legend()
axes[0, 0].grid(alpha=0.25)

axes[0, 1].plot(M, C, color="purple")
axes[0, 1].scatter(M[0], C[0], color="red", label="start")
axes[0, 1].scatter(12.0, 40.0, color="black", marker="*", label="equilibrium")
axes[0, 1].set_title("UMDS phase: M versus C")
axes[0, 1].set_xlabel("M")
axes[0, 1].set_ylabel("C")
axes[0, 1].legend()
axes[0, 1].grid(alpha=0.25)

axes[1, 0].plot(t[:-1], ledger_error, color="darkred")
axes[1, 0].axhline(0.0, color="black", linestyle="--")
axes[1, 0].set_title("Ledger residual")
axes[1, 0].set_xlabel("time")
axes[1, 0].grid(alpha=0.25)

x = np.arange(3)
width = 0.35
axes[1, 1].bar(x - width / 2, Q, width, label="Q")
axes[1, 1].bar(x + width / 2, Omega, width, label="softmax Q")
axes[1, 1].set_xticks(x)
axes[1, 1].set_xticklabels(("component 1", "component 2", "component 3"))
axes[1, 1].set_title("QUAL branches")
axes[1, 1].legend()
axes[1, 1].grid(axis="y", alpha=0.25)

fig.suptitle(
    "MIYA v2 | z="
    + str(z)
    + " | codec="
    + str(codec_pass)
)
fig.tight_layout()
fig.savefig(
    os.path.join(out, "miya_v2_dashboard.png"),
    dpi=200,
)
plt.close(fig)

data = np.column_stack((t, A, M, C, R, Fsink))
np.savetxt(
    os.path.join(out, "miya_v2_data.csv"),
    data,
    delimiter=",",
    header="t,A,M,C,R,Fsink",
    comments="",
)

print("MIYA v2 completed")
print("final A =", round(A[-1], 6))
print("final M =", round(M[-1], 6))
print("final C =", round(C[-1], 6))
print("max ledger error =", np.max(np.abs(ledger_error)))
print("z =", z)
print("decoded =", decoded)
print("codec pass =", codec_pass)
print("saved miya_v2_results/miya_v2_dashboard.png")
print("CALCULABLE != VERIFIED != PUBLISHED")
