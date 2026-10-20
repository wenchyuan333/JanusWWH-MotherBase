import math
import cmath


def three_hares_check():
    P = [[0, 0, 1], [1, 0, 0], [0, 1, 0]]

    def mat_mul(X, Y):
        n = len(X)
        return [[sum(X[i][k] * Y[k][j] for k in range(n)) for j in range(n)] for i in range(n)]

    def is_identity(X, tol=1e-9):
        n = len(X)
        for i in range(n):
            for j in range(n):
                expected = 1.0 if i == j else 0.0
                if abs(X[i][j] - expected) > tol:
                    return False
        return True

    P2 = mat_mul(P, P)
    P3 = mat_mul(P2, P)
    p3_identity = is_identity(P3)

    omega = cmath.exp(2j * math.pi / 3)
    omega2 = omega ** 2
    eigen_sum_zero = abs(1 + omega + omega2) < 1e-9

    A_amp, theta = 1.7, 0.35
    r = [A_amp * cmath.exp(1j * (theta + 2 * math.pi * k / 3)) for k in range(3)]
    r_sum_zero = abs(sum(r)) < 1e-9

    return {"P^3=I": p3_identity, "eigen_sum_zero": eigen_sum_zero, "r0+r1+r2_zero": r_sum_zero}


def combo001_fixture():
    A, M, C, eta, q = 10.0, 4.0, 2.0, 0.6, 1.0
    k_in, A_sat = 0.8, 10.0
    alpha, M_floor, k_leak = 0.5, 1.0, 0.05
    k_C = 0.1
    dt = 0.01

    Fin = k_in * A / (1 + A / A_sat)
    Fout = alpha * M / (M ** 3 + M_floor ** 3) + k_leak * M

    b_A = q - Fin
    b_M = eta * Fin - Fout
    b_C = (1 - eta) * Fin + Fout - k_C * C
    ledger_direct = q - k_C * C
    ledger_match = abs((b_A + b_M + b_C) - ledger_direct) < 1e-6

    z = (1.0, -1.0, 0.0)
    sigma, sqrt_dt = 0.1, math.sqrt(dt)
    noise = tuple(sigma * sqrt_dt * zi for zi in z)

    A1 = A + b_A * dt + noise[0]
    M1 = M + b_M * dt + noise[1]
    C1 = C + b_C * dt + noise[2]

    total1 = A1 + M1 + C1
    total0_expected = (A + M + C) + ledger_direct * dt
    step_match = abs(total1 - total0_expected) < 1e-6

    A_star = q / (k_in - q / A_sat)
    C_star = q / k_C

    return {
        "Fin": Fin, "Fout": Fout, "drift": (b_A, b_M, b_C),
        "ledger_check_A_eq_B": ledger_match,
        "euler_maruyama_step": (A1, M1, C1),
        "step_ledger_check": step_match,
        "fixed_point_A_star": A_star, "fixed_point_C_star": C_star,
        "nonneg": all(v >= 0 for v in (A1, M1, C1)),
    }


def combo002_fixture(n5_override=None):
    p = [0.90, 0.95, 0.80, 0.85, 1.00, 0.90]
    n = [0.10, 0.05, 0.20, 0.15, 0.00, 0.10]
    if n5_override is not None:
        n[4] = n5_override
    tau_plus = [0.70] * 6
    tau_minus = [0.25] * 6
    w = [1.0] * 6
    eps = 1e-9

    g = [(p[i] - n[i]) / (p[i] + n[i] + eps) for i in range(6)]
    h = [1 if (p[i] >= tau_plus[i] and n[i] <= tau_minus[i]) else 0 for i in range(6)]

    prod_h = 1
    for hi in h:
        prod_h *= hi

    terms = [(1 + g[i]) / 2 + eps for i in range(6)]
    log_sum = sum(w[i] * math.log(terms[i]) for i in range(6))
    U12 = prod_h * math.exp(log_sum / 6)

    direct_product = 1.0
    for t in terms:
        direct_product *= t
    U12_direct = prod_h * (direct_product ** (1.0 / 6))
    cross_check_match = abs(U12 - U12_direct) < 1e-9  # both paths now use the same eps-regularized terms

    r_plus = [max(0.0, tau_plus[i] - p[i]) / max(tau_plus[i], eps) for i in range(6)]
    r_minus = [max(0.0, n[i] - tau_minus[i]) / max(tau_minus[i], eps) for i in range(6)]
    R12 = math.sqrt(sum(rp ** 2 + rm ** 2 for rp, rm in zip(r_plus, r_minus)))

    return {"g": g, "h": h, "U12": U12, "U12_cross_check_match": cross_check_match, "R12": R12}


print("=== [A] Three-Hares Operator structural checks ===")
hares = three_hares_check()
for k, v in hares.items():
    print(f"  {k}: {v}")

print()
print("=== [B] COMBO-001 fixture (UMDS x C3 Brownian lock, Time/Space/Scale Gate) ===")
c1 = combo001_fixture()
print(f"  F_in={c1['Fin']:.6f} F_out={c1['Fout']:.6f}")
print(f"  drift (b_A,b_M,b_C) = {tuple(round(v, 6) for v in c1['drift'])}")
print(f"  ledger_check_A_eq_B: {c1['ledger_check_A_eq_B']}")
print(f"  euler_maruyama_step (A1,M1,C1) = {tuple(round(v, 6) for v in c1['euler_maruyama_step'])}")
print(f"  step_ledger_check: {c1['step_ledger_check']}")
print(f"  nonneg: {c1['nonneg']}")
print(f"  fixed_point A*={c1['fixed_point_A_star']:.6f} C*={c1['fixed_point_C_star']:.6f}")

print()
print("=== [C] COMBO-002 fixture (six-phase gate x 12-bipolar, PASS case) ===")
c2_pass = combo002_fixture()
print(f"  g={[round(v, 4) for v in c2_pass['g']]}")
print(f"  h={c2_pass['h']}")
print(f"  U12={c2_pass['U12']:.6f}  cross_check_match={c2_pass['U12_cross_check_match']}")
print(f"  R12={c2_pass['R12']:.6f}")

print()
print("=== [C'] COMBO-002 fixture (FIREWALL forced failure case, n5=0.30) ===")
c2_fail = combo002_fixture(n5_override=0.30)
print(f"  h={c2_fail['h']}")
print(f"  U12={c2_fail['U12']:.6f}  (expect 0.0, non-compensating hard gate)")

print()
all_ok = (
    all(hares.values())
    and c1["ledger_check_A_eq_B"]
    and c1["step_ledger_check"]
    and c1["nonneg"]
    and c2_pass["U12_cross_check_match"]
    and c2_fail["U12"] == 0.0
)
print(f"=== SUMMARY: combo_checks_all_passed={all_ok} ===")
