_v04.pynano umds_stdlib_v04.pyimport hashlib
import json
import math
import os
import platform
import sys
from pathlib import Path

VERSION = "UMDS-STDLIB-v0.4"
SCRIPT = "umds_stdlib_v04.py"
RECEIPT = "umds_stdlib_receipt_v04.json"
P = {
    "q": 0.5,
    "k_in": 2.0,
    "A_sat": 1.0,
    "alpha": 0.1,
    "M_floor": 0.5,
    "k_leak": 0.5,
    "k_C": 1.0,
    "tau_eta": 0.5,
    "b0": 1.0,
    "b1": 0.5,
    "b2": 1.0,
    "M_ref": 1.0,
    "C_ref": 1.0,
}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def sigma(x):
    if x >= 0.0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def f_in(A):
    return P["k_in"] * A / (1.0 + A / P["A_sat"])


def f_out(M):
    return (
        P["alpha"] * M / (M ** 3 + P["M_floor"] ** 3)
        + P["k_leak"] * M
    )


def eta_cmd(M, C, branch):
    if branch == "c_proxy_s16":
        residual = C / P["C_ref"]
    elif branch == "ledger_perfect_zero":
        residual = 0.0
    else:
        raise ValueError("unknown branch: " + branch)
    theta = (
        P["b0"]
        + P["b1"] * M / P["M_ref"]
        - P["b2"] * residual
    )
    return sigma(theta)


def rhs(x, branch):
    A, M, C, eta = x
    fin = f_in(A)
    fout = f_out(M)
    return (
        P["q"] - fin,
        eta * fin - fout,
        (1.0 - eta) * fin + fout - P["k_C"] * C,
        (eta_cmd(M, C, branch) - eta) / P["tau_eta"],
    )


def add(x, k, scale):
    return tuple(x[i] + scale * k[i] for i in range(4))


def rk4(x, dt, branch):
    k1 = rhs(x, branch)
    k2 = rhs(add(x, k1, dt / 2.0), branch)
    k3 = rhs(add(x, k2, dt / 2.0), branch)
    k4 = rhs(add(x, k3, dt), branch)
    return tuple(
        x[i] + dt * (k1[i] + 2.0 * k2[i] + 2.0 * k3[i] + k4[i]) / 6.0
        for i in range(4)
    )


def heun(x, dt, branch):
    k1 = rhs(x, branch)
    k2 = rhs(add(x, k1, dt), branch)
    return tuple(x[i] + dt * (k1[i] + k2[i]) / 2.0 for i in range(4))


def integrate(method, dt, duration, branch):
    step = rk4 if method == "RK4" else heun
    x = (1.0, 0.05, 0.0, 0.5)
    mins = list(x)
    maxs = list(x)
    total0 = sum(x[:3])
    ledger_integral = 0.0
    steps = int(round(duration / dt))
    if abs(steps * dt - duration) > 1e-12:
        raise ValueError("duration must be divisible by dt")
    for _ in range(steps):
        external0 = P["q"] - P["k_C"] * x[2]
        xn = step(x, dt, branch)
        if not all(math.isfinite(v) for v in xn):
            raise ArithmeticError("non-finite state")
        external1 = P["q"] - P["k_C"] * xn[2]
        ledger_integral += 0.5 * (external0 + external1) * dt
        x = xn
        for i, value in enumerate(x):
            mins[i] = min(mins[i], value)
            maxs[i] = max(maxs[i], value)
    total_delta = sum(x[:3]) - total0
    scale = max(1.0, abs(total_delta), abs(ledger_integral))
    return {
        "method": method,
        "dt": dt,
        "steps": steps,
        "final_state": list(x),
        "minimum_state": mins,
        "maximum_state": maxs,
        "normalized_ledger_error": abs(total_delta - ledger_integral) / scale,
        "nonnegative": min(mins[:3]) >= -1e-9,
        "eta_bounded": mins[3] >= -1e-9 and maxs[3] <= 1.0 + 1e-9,
    }


def bisect(fun, lo, hi):
    flo = fun(lo)
    fhi = fun(hi)
    if flo * fhi > 0.0:
        raise ValueError("root not bracketed")
    for _ in range(100):
        mid = (lo + hi) / 2.0
        fmid = fun(mid)
        if abs(fmid) <= 1e-14:
            return mid
        if flo * fmid <= 0.0:
            hi = mid
            fhi = fmid
        else:
            lo = mid
            flo = fmid
    return (lo + hi) / 2.0


def fixed_points(branch, m_max=10.0, cells=20000):
    A = P["q"] / (P["k_in"] - P["q"] / P["A_sat"])
    C = P["q"] / P["k_C"]

    def closure(M):
        eta = eta_cmd(M, C, branch)
        return f_out(M) - eta * P["q"]

    roots = []
    lo = 0.0
    flo = closure(lo)
    for i in range(1, cells + 1):
        hi = m_max * i / cells
        fhi = closure(hi)
        if flo == 0.0 or fhi == 0.0 or flo * fhi < 0.0:
            root = bisect(closure, lo, hi)
            if not roots or abs(root - roots[-1]["state"][1]) > 1e-7:
                state = (A, root, C, eta_cmd(root, C, branch))
                residual = max(abs(v) for v in rhs(state, branch))
                roots.append({"state": list(state), "residual_inf": residual})
        lo = hi
        flo = fhi
    return {
        "M_search_domain": [0.0, m_max],
        "outside_domain": "UNKNOWN",
        "roots": roots,
    }


def stability(state, branch):
    A, M, C, eta = state
    fA = P["k_in"] / (1.0 + A / P["A_sat"]) ** 2
    g = (
        P["alpha"]
        * (P["M_floor"] ** 3 - 2.0 * M ** 3)
        / (M ** 3 + P["M_floor"] ** 3) ** 2
        + P["k_leak"]
    )
    sp = eta * (1.0 - eta)
    hM = P["b1"] / P["M_ref"]
    hC = -P["b2"] / P["C_ref"] if branch == "c_proxy_s16" else 0.0
    f = P["q"]
    k = P["k_C"]
    t = 1.0 / P["tau_eta"]
    u = sp * hM / P["tau_eta"]
    v = sp * hC / P["tau_eta"]
    a1 = g + k + t
    a2 = g * k + g * t + k * t + f * (v - u)
    a3 = g * k * t - f * u * k
    stable = fA > 0.0 and a1 > 0.0 and a2 > 0.0 and a3 > 0.0 and a1 * a2 > a3
    return {
        "lambda_A": -fA,
        "a1": a1,
        "a2": a2,
        "a3": a3,
        "a1a2_minus_a3": a1 * a2 - a3,
        "local_linear_stability": "STABLE" if stable else "NOT_STABLE_OR_UNRESOLVED",
    }


def max_diff(a, b):
    return max(abs(a[i] - b[i]) for i in range(len(a)))


def run_branch(branch):
    roots = fixed_points(branch)
    if not roots["roots"]:
        raise RuntimeError("no fixed point in declared domain")
    rk4_02 = integrate("RK4", 0.02, 60.0, branch)
    rk4_01 = integrate("RK4", 0.01, 60.0, branch)
    rk4_005 = integrate("RK4", 0.005, 60.0, branch)
    heun_001 = integrate("HEUN", 0.001, 60.0, branch)
    d1 = max_diff(rk4_02["final_state"], rk4_01["final_state"])
    d2 = max_diff(rk4_01["final_state"], rk4_005["final_state"])
    cross = max_diff(rk4_005["final_state"], heun_001["final_state"])
    gates = {
        "fixed_point_residual": max(r["residual_inf"] for r in roots["roots"]) <= 1e-9,
        "rk4_step_convergence": d2 <= d1 + 1e-14 and d2 <= 1e-5,
        "rk4_heun_cross_check": cross <= 1e-4,
        "ledger": max(
            rk4_005["normalized_ledger_error"],
            heun_001["normalized_ledger_error"],
        ) <= 1e-4,
        "nonnegative": rk4_005["nonnegative"] and heun_001["nonnegative"],
        "eta_bounded": rk4_005["eta_bounded"] and heun_001["eta_bounded"],
    }
    return {
        "branch": branch,
        "fixed_points": roots,
        "stability": [stability(r["state"], branch) for r in roots["roots"]],
        "RK4_dt_0_02": rk4_02,
        "RK4_dt_0_01": rk4_01,
        "RK4_dt_0_005": rk4_005,
        "HEUN_dt_0_001": heun_001,
        "convergence": {
            "coarse_to_medium": d1,
            "medium_to_fine": d2,
            "rk4_heun_cross_difference": cross,
        },
        "execution_gates": gates,
        "execution_pass": all(gates.values()),
    }


def write_atomic(path, value):
    target = Path(path)
    temporary = Path(path + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")
    json.loads(temporary.read_text(encoding="utf-8"))
    os.replace(temporary, target)


def preflight():
    if sys.version_info < (3, 10):
        raise RuntimeError("Python 3.10 or newer required")
    positive = [
        P["q"],
        P["k_in"],
        P["A_sat"],
        P["alpha"],
        P["M_floor"],
        P["k_leak"],
        P["k_C"],
        P["tau_eta"],
        P["M_ref"],
        P["C_ref"],
    ]
    if min(positive) <= 0.0:
        raise RuntimeError("positive parameter gate failed")
    if P["q"] >= P["k_in"] * P["A_sat"]:
        raise RuntimeError("capacity gate failed")


def main():
    preflight()
    script_hash = sha256(Path(__file__).read_bytes())
    manifest = {
        "version": VERSION,
        "parameters": P,
        "branches": ["c_proxy_s16", "ledger_perfect_zero"],
        "initial_state": [1.0, 0.05, 0.0, 0.5],
        "duration": 60.0,
        "fixed_point_M_search_domain": [0.0, 10.0],
        "external_validation": "NOT_RUN",
    }
    manifest_hash = sha256(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )
    results = [run_branch(branch) for branch in manifest["branches"]]
    passed = all(result["execution_pass"] for result in results)
    receipt = {
        "truth_layer": "FORMAL_MODEL",
        "artifact_state": "STDLIB_RUNTIME_RECEIPT" if passed else "RUNTIME_GATE_FAILED",
        "version": VERSION,
        "script_sha256": script_hash,
        "manifest_sha256": manifest_hash,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "third_party_dependencies": [],
        },
        "manifest": manifest,
        "results": results,
        "all_execution_gates_passed": passed,
        "external_validation": "NOT_RUN",
        "published": False,
        "claim_firewall": "CALCULABLE != VERIFIED != PUBLISHED",
    }
    write_atomic(RECEIPT, receipt)
    print(
        json.dumps(
            {
                "status": "PASS" if passed else "FAIL",
                "version": VERSION,
                "receipt": RECEIPT,
                "script_sha256": script_hash,
                "manifest_sha256": manifest_hash,
                "branches": [
                    {
                        "branch": result["branch"],
                        "pass": result["execution_pass"],
                        "fixed_point_count": len(result["fixed_points"]["roots"]),
                        "fixed_points": [
                            root["state"] for root in result["fixed_points"]["roots"]
                        ],
                    }
                    for result in results
                ],
                "external_validation": "NOT_RUN",
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
