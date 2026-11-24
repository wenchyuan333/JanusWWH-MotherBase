 from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Params:
q: float = 0.5
k_in: float = 2.0
A_sat: float = 1.0
alpha: float = 0.1
M_floor: float = 0.5
k_leak: float = 0.5
k_C: float = 1.0
tau_eta: float = 0.5
b0: float = 1.0
b1: float = 0.5
b2: float = 1.0
M_ref: float = 1.0
C_ref: float = 1.0


def sigma(x):
if x >= 0.0:
    z = math.exp(-x)
    return 1.0 / (1.0 + z)
z = math.exp(x)
return z / (1.0 + z)


def fin(A, p):
return p.k_in * A / (1.0 + A / p.A_sat)


def fout(M, p):
return p.alpha * M / (M**3 + p.M_floor**3) + p.k_leak * M


def eta_cmd(M, C, p, branch):
if branch == "c_proxy_s16":
    residual = C / p.C_ref
elif branch == "ledger_perfect_zero":
    residual = 0.0
else:
    raise ValueError("unknown branch: " + branch)
return sigma(p.b0 + p.b1 * M / p.M_ref - p.b2 * residual)


def rhs(x, p, branch):
A, M, C, eta = x
fi = fin(A, p)
fo = fout(M, p)
return (
    p.q - fi,
    eta * fi - fo,
    (1.0 - eta) * fi + fo - p.k_C * C,
    (eta_cmd(M, C, p, branch) - eta) / p.tau_eta,
)


def add(x, k, scale):
return tuple(xi + scale * ki for xi, ki in zip(x, k))


def rk4_step(x, dt, p, branch):
k1 = rhs(x, p, branch)
k2 = rhs(add(x, k1, dt / 2.0), p, branch)
k3 = rhs(add(x, k2, dt / 2.0), p, branch)
k4 = rhs(add(x, k3, dt), p, branch)
return tuple(x[i] + dt * (k1[i] + 2*k2[i] + 2*k3[i] + k4[i]) / 6.0 for i in range(4))


def heun_step(x, dt, p, branch):
k1 = rhs(x, p, branch)
predictor = add(x, k1, dt)
k2 = rhs(predictor, p, branch)
return tuple(x[i] + dt * (k1[i] + k2[i]) / 2.0 for i in range(4))


def integrate(method, dt, T, p, branch):
step = rk4_step if method == "RK4" else heun_step
x = (1.0, 0.05, 0.0, 0.5)
mins = list(x)
maxs = list(x)
total0 = sum(x[:3])
ledger_integral = 0.0
n = int(round(T / dt))
if abs(n * dt - T) > 1e-12:
    raise ValueError("T must be divisible by dt")
for _ in range(n):
    ext0 = p.q - p.k_C * x[2]
    xn = step(x, dt, p, branch)
    if not all(math.isfinite(v) for v in xn):
        raise ArithmeticError("non-finite state")
    ext1 = p.q - p.k_C * xn[2]
    ledger_integral += 0.5 * (ext0 + ext1) * dt
    x = xn
    for i, v in enumerate(x):
        mins[i] = min(mins[i], v)
        maxs[i] = max(maxs[i], v)
ledger_error = (sum(x[:3]) - total0) - ledger_integral
scale = max(1.0, abs(ledger_integral), abs(sum(x[:3]) - total0))
return {
    "method": method,
    "dt": dt,
    "steps": n,
    "final_state": list(x),
    "min_state": mins,
    "max_state": maxs,
    "normalized_ledger_error": abs(ledger_error) / scale,
    "nonnegative": min(mins[:3]) >= -1e-9,
    "eta_bounded": mins[3] >= -1e-9 and maxs[3] <= 1.0 + 1e-9,
}


def bisect(fun, a, b, iterations=80):
fa, fb = fun(a), fun(b)
if fa == 0.0:
    return a
if fb == 0.0:
    return b
if fa * fb > 0.0:
    raise ValueError("root not bracketed")
for _ in range(iterations):
    m = (a + b) / 2.0
    fm = fun(m)
    if fm == 0.0:
        return m
    if fa * fm <= 0.0:
        b, fb = m, fm
    else:
        a, fa = m, fm
return (a + b) / 2.0


def fixed_points(p, branch, M_max=10.0, cells=20000):
A = p.q / (p.k_in - p.q / p.A_sat)
C = p.q / p.k_C
def closure(M):
    eta = eta_cmd(M, C, p, branch)
    return fout(M, p) - eta * p.q
roots = []
a, fa = 0.0, closure(0.0)
for i in range(1, cells + 1):
    b = M_max * i / cells
    fb = closure(b)
    if fa == 0.0 or fa * fb < 0.0 or fb == 0.0:
        r = bisect(closure, a, b)
        if not roots or abs(r - roots[-1]) > 1e-7:
            eta = eta_cmd(r, C, p, branch)
            x = (A, r, C, eta)
            roots.append({"state": list(x), "residual_inf": max(abs(v) for v in rhs(x, p, branch))})
    a, fa = b, fb
return {"M_search_domain": [0.0, M_max], "roots": roots, "outside_domain": "UNKNOWN"}


def stability_receipt(x, p, branch):
A, M, C, eta = x
fA = p.k_in / (1.0 + A / p.A_sat)**2
g = p.alpha * (p.M_floor**3 - 2.0*M**3) / (M**3 + p.M_floor**3)**2 + p.k_leak
sp = eta * (1.0 - eta)
hM = p.b1 / p.M_ref
hC = -p.b2 / p.C_ref if branch == "c_proxy_s16" else 0.0
f, k, t = p.q, p.k_C, 1.0 / p.tau_eta
u, v = sp * hM / p.tau_eta, sp * hC / p.tau_eta
a1 = g + k + t
a2 = g*k + g*t + k*t + f*(v-u)
a3 = g*k*t - f*u*k
stable = (-fA < 0.0 and a1 > 0.0 and a2 > 0.0 and a3 > 0.0 and a1*a2 > a3)
return {"lambda_A": -fA, "a1": a1, "a2": a2, "a3": a3, "a1a2_minus_a3": a1*a2-a3, "routh_hurwitz_stable": stable}


def sha256_bytes(data):
return hashlib.sha256(data).hexdigest()


def main():
if sys.version_info < (3, 10):
    raise SystemExit("FAIL preflight: Python >= 3.10 required")
p = Params()
if not (p.q < p.k_in * p.A_sat and min(asdict(p).values()) > 0.0):
    raise SystemExit("FAIL preflight: parameter domain")
manifest = {
    "model": "UMDS-STDLIB-CORE-v0.2",
    "parameters": asdict(p),
    "branches": ["c_proxy_s16", "ledger_perfect_zero"],
    "fixed_point_M_search_domain": [0.0, 10.0],
    "external_validation": "NOT_RUN",
}
results = []
for branch in manifest["branches"]:
    roots = fixed_points(p, branch)
    if not roots["roots"]:
        raise RuntimeError("no fixed point in declared domain: " + branch)
    rk4 = integrate("RK4", 0.01, 60.0, p, branch)
    heun = integrate("HEUN", 0.002, 60.0, p, branch)
    cross = max(abs(a-b) for a, b in zip(rk4["final_state"], heun["final_state"]))
    convergence = [integrate("RK4", dt, 60.0, p, branch) for dt in (0.02, 0.01, 0.005)]
    gates = {
        "fixed_point_residual": max(r["residual_inf"] for r in roots["roots"]) <= 1e-9,
        "solver_cross_check": cross <= 1e-3,
        "ledger": max(rk4["normalized_ledger_error"], heun["normalized_ledger_error"]) <= 1e-5,
        "nonnegative": rk4["nonnegative"] and heun["nonnegative"],
        "eta_bounded": rk4["eta_bounded"] and heun["eta_bounded"],
    }
    results.append({
        "branch": branch,
        "fixed_points": roots,
        "stability": [stability_receipt(r["state"], p, branch) for r in roots["roots"]],
        "RK4": rk4,
        "HEUN": heun,
        "solver_cross_difference": cross,
        "rk4_convergence": convergence,
        "execution_gates": gates,
        "execution_pass": all(gates.values()),
    })
script_path = Path(__file__)
receipt = {
    "truth_layer": "FORMAL_MODEL",
    "artifact_state": "RUNTIME_RECEIPT_CANDIDATE",
    "manifest": manifest,
    "manifest_sha256": sha256_bytes(json.dumps(manifest, sort_keys=True).encode()),
    "script_sha256": sha256_bytes(script_path.read_bytes()),
    "environment": {"python": platform.python_version(), "platform": platform.platform(), "third_party_dependencies": []},
    "results": results,
    "all_execution_gates_passed": all(r["execution_pass"] for r in results),
    "claim_firewall": "CALCULABLE != VERIFIED != PUBLISHED",
}
target = Path("umds_stdlib_receipt_v02.json")
temp = target.with_suffix(".json.tmp")
temp.write_text(json.dumps(receipt, indent=2, sort_keys=True), encoding="utf-8")
json.loads(temp.read_text(encoding="utf-8"))
os.replace(temp, target)
print(json.dumps({
    "status": "PASS" if receipt["all_execution_gates_passed"] else "FAIL",
    "receipt": str(target),
    "script_sha256": receipt["script_sha256"],
    "manifest_sha256": receipt["manifest_sha256"],
    "branches": [{"branch": r["branch"], "pass": r["execution_pass"], "fixed_points": len(r["fixed_points"]["roots"])} for r in results],
}, indent=2))


if __name__ == "__main__":
main()
