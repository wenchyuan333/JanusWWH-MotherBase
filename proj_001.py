#!/usr/bin/env python3
# proj_001.py v0.1 (2026-08-15) -- universal-law projection: commutativity closure gate
# CLAIM LAYER: STAGED (unexecuted). Promote to TESTED only after Termux readback.
# Canonical: law L projects through pi iff exists L~ with pi . L = L~ . pi
# Defect:    r = || S T - T~ S ||_inf ; r = 0 iff the projection is exact.
# Boundary:  finite chains, exact (not approximate) projection, stdlib only.
import sys

DEFECT_PASS = 1e-9     # positive fixture must fall below this
DEFECT_FIRE = 1e-6     # negative fixture must exceed this (the gate must bite)
PATH_STEPS = 50


def matmul(A, B):
    n, m, p = len(A), len(B), len(B[0])
    C = [[0.0] * p for _ in range(n)]
    for i in range(n):
        for k in range(m):
            a = A[i][k]
            if a == 0.0:
                continue
            for j in range(p):
                C[i][j] += a * B[k][j]
    return C


def matvec(A, x):
    return [sum(ai * xi for ai, xi in zip(row, x)) for row in A]


def inf_norm_mat(A):
    return max(max(abs(v) for v in row) for row in A)


def inf_norm_vec(v):
    return max(abs(x) for x in v)


def block_means(S, T):
    # candidate projected law T~ = (S T S^T)(S S^T)^-1 ; S one-hot => block means
    n = len(T)
    groups = [[i for i in range(n) if S[a][i] == 1] for a in range(len(S))]
    for g in groups:
        if len(g) == 0:
            raise ValueError("empty block: projection undefined")  # fail loud
    Tt = []
    for ga in groups:
        row = []
        for gb in groups:
            s = 0.0
            for i in ga:
                for j in gb:
                    s += T[i][j]
            row.append(s / len(ga))
        Tt.append(row)
    return Tt


def lump_sweep(S, T):
    # necessary condition: for each target block, block-sourced column sums
    # must be identical for every column inside that block
    n = len(T)
    worst = 0.0
    for b in range(len(S)):
        cols = [j for j in range(n) if S[b][j] == 1]
        for a in range(len(S)):
            vals = [sum(T[i][j] for i in range(n) if S[a][i] == 1) for j in cols]
            for v in vals[1:]:
                worst = max(worst, abs(v - vals[0]))
    return worst


def path_closure(S, T, Tt, x0, steps):
    x = list(x0)
    y = matvec(S, x0)
    worst = 0.0
    for _ in range(steps):
        x = matvec(T, x)
        y = matvec(Tt, y)
        proj_x = matvec(S, x)
        worst = max(worst, inf_norm_vec([p - q for p, q in zip(proj_x, y)]))
    return worst


def run_case(name, S, T, x0, expect_projectable):
    Tt = block_means(S, T)
    ST = matmul(S, T)
    TS = matmul(Tt, S)
    defect = inf_norm_mat(
        [[ST[i][j] - TS[i][j] for j in range(len(ST[0]))] for i in range(len(ST))])
    sweep = lump_sweep(S, T)
    path = path_closure(S, T, Tt, x0, PATH_STEPS)
    print("[%s]" % name)
    print("  defect ||S T - T~ S||_inf = %.6e" % defect)
    print("  sweep  (within-block sums) = %.6e" % sweep)
    print("  path closure (n <= %d)     = %.6e" % (PATH_STEPS, path))
    if expect_projectable:
        ok = defect < DEFECT_PASS and sweep < DEFECT_PASS and path < DEFECT_PASS
    else:
        ok = defect > DEFECT_FIRE   # gate must fire here, else it is decorative
    print("  expect %s -> %s" % (
        "PROJECTABLE" if expect_projectable else "NOT projectable",
        "PASS" if ok else "FAIL"))
    return ok


def main():
    # positive: swap-symmetric 4-state chain with genuine cross-block flow.
    # rows sum to 1; block-sourced column sums match within each block.
    T_pos = [
        [0.40, 0.10, 0.30, 0.20],
        [0.10, 0.40, 0.20, 0.30],
        [0.20, 0.30, 0.40, 0.10],
        [0.30, 0.20, 0.10, 0.40],
    ]
    # negative: move 0.05 of mass across the symmetry seam (non-unit scale).
    T_neg = [row[:] for row in T_pos]
    T_neg[0][0] = 0.35
    T_neg[0][2] = 0.35
    S = [
        [1, 1, 0, 0],
        [0, 0, 1, 1],
    ]
    x0 = [0.90, 0.10, 0.00, 0.00]

    print("proj_001 v0.1 | universal-law projection gate | 4 -> 2 lumping | eps_neg=0.05")
    ok1 = run_case("F1 positive / swap-symmetric chain", S, T_pos, x0, True)
    ok2 = run_case("F2 negative / symmetry broken", S, T_neg, x0, False)
    print("\nCLAIM CEILING: F1 r=0 proves projectability of THIS (T, S) pair only.")
    print("It does NOT prove cross-domain laws share one universal parent law.")
    print("\nVERDICT: %s" % ("ALL FIXTURES PASS" if (ok1 and ok2) else "FIXTURE FAILURE"))
    sys.exit(0 if (ok1 and ok2) else 1)


if __name__ == "__main__":
    main()