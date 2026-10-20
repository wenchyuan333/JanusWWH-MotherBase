import math


def sigma(x):
    return 1.0 / (1.0 + math.exp(-x))


def F_in(A, k_in=2.0, A_sat=1.0):
    return k_in * A / (1.0 + A / A_sat)


def F_out(M, alpha=0.1, M_floor=0.5, k_leak=0.5):
    return alpha * M / (M ** 3 + M_floor ** 3) + k_leak * M


def eta_cmd(M, C, b0=1.0, b1=0.5, b2=1.0, M_ref=1.0, C_ref=1.0):
    return sigma(b0 + b1 * M / M_ref - b2 * C / C_ref)


def simulate_umds(x0=(1.0, 0.05, 0.0, 0.5), dt=0.001, T=60.0, q=0.5, k_C=1.0, tau_eta=0.5):
    A, M, C, eta = x0
    steps = int(T / dt)
    for _ in range(steps):
        Fin = F_in(A)
        Fout = F_out(M)
        dA = q - Fin
        dM = eta * Fin - Fout
        dC = (1 - eta) * Fin + Fout - k_C * C
        deta = (eta_cmd(M, C) - eta) / tau_eta
        A += dt * dA
        M += dt * dM
        C += dt * dC
        eta += dt * deta
    return A, M, C, eta


def quantize_8(value, v_min, v_max):
    q = math.floor(8 * (value - v_min) / (v_max - v_min))
    return min(7, max(0, q))


def pack_12bit(qA, qM, qC, qEta):
    return qA + 8 * qM + 64 * qC + 512 * qEta


def address_64x64(z):
    return z % 64, z // 64


def pisano_check(num_seeds=64):
    fail = []
    for x0 in range(num_seeds):
        for y0 in range(num_seeds):
            x, y = x0, y0
            for _ in range(96):
                x, y = (x + y) % 64, x % 64
            if (x, y) != (x0, y0):
                fail.append((x0, y0))
    total = num_seeds * num_seeds
    return total, total - len(fail), len(fail), fail[:10]


print("=== [1] UMDS-001 ODE simulation (Euler, baseline S16 params, includes minimal control law) ===")
A, M, C, eta = simulate_umds()
print(f"final state: A={A:.4f} M={M:.4f} C={C:.4f} eta={eta:.4f}")

predicted_A = 0.3333
predicted_M = 0.277
predicted_C = 0.5
predicted_eta = 0.654
tol = 0.02
match_A = abs(A - predicted_A) < tol
match_M = abs(M - predicted_M) < tol
match_C = abs(C - predicted_C) < tol
match_eta = abs(eta - predicted_eta) < tol
print(f"predicted equilibrium: A={predicted_A} M={predicted_M} C={predicted_C} eta={predicted_eta} (tol={tol})")
print(f"equilibrium_match: A={match_A} M={match_M} C={match_C} eta={match_eta}")

print()
print("=== [2] 12-bit codec + 64x64 address (quantized final UMDS state) ===")
qA = quantize_8(A, 0.0, 1.0)
qM = quantize_8(M, 0.0, 1.0)
qC = quantize_8(C, 0.0, 1.0)
qEta = quantize_8(eta, 0.0, 1.0)
z = pack_12bit(qA, qM, qC, qEta)
x, y = address_64x64(z)
print(f"quantized: qA={qA} qM={qM} qC={qC} qEta={qEta} -> z={z} -> address(x,y)=({x},{y})")

print()
print("=== [3] Fibonacci Q-lock 64x64 fine scan (Pisano return check, pi(64)=96) ===")
total, passed, failed, first_fail = pisano_check(64)
print(f"[pisano-check] total_seeds={total} passed={passed} failed={failed}")
if failed:
    print(f"[pisano-check] first_failing_seeds={first_fail}")

print()
all_ok = match_A and match_M and match_C and match_eta and (failed == 0)
print(f"=== SUMMARY: all_formulas_passed={all_ok} ===")
