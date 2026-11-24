#!/usr/bin/env python3
# miya_lattice_perc.py v1.0 | percolation fixture on the pi-phi lattice geometry
# FINDING: HexagonalLattice(N) nodes form a TRIANGULAR lattice (6-coordinated)
# KNOWN: triangular SITE pc = 1/2 (exact) ; BOND pc = 2*sin(pi/18) = 0.3472963553 (exact)
# CLAIM: calibrates lattice geometry only; says nothing about neural dynamics
# NOTE : crossing protocol uses open x (i=0 -> i=N-1), periodic y
import math, random, time

SEED = 20260806
R = 200
STEP = 0.005
PC_SITE = 0.5
PC_BOND = 2.0 * math.sin(math.pi / 18.0)

def find(par, x):
    while par[x] != x:
        par[x] = par[par[x]]
        x = par[x]
    return x

def union(par, sz, a, b):
    ra, rb = find(par, a), find(par, b)
    if ra == rb:
        return
    if sz[ra] < sz[rb]:
        ra, rb = rb, ra
    par[rb] = ra
    sz[ra] += sz[rb]

def tri_bonds(N):
    # node id = i*N + j ; analytic 6-neighbor adjacency of the staggered grid
    # equivalent to the cdist nearest-6 rule in HexagonalLattice, minus scipy
    b = []
    for i in range(N):
        for j in range(N):
            s = i * N + j
            if i + 1 < N:
                b.append((s, (i + 1) * N + j))
            b.append((s, i * N + (j + 1) % N))
            if j % 2 == 0:
                if i > 0:
                    b.append((s, (i - 1) * N + (j + 1) % N))
            else:
                if i + 1 < N:
                    b.append((s, (i + 1) * N + (j + 1) % N))
    return b

def spans_bond(bonds, N, p, rng):
    par = list(range(N * N))
    sz = [1] * (N * N)
    for a, bb in bonds:
        if rng.random() < p:
            union(par, sz, a, bb)
    roots = set(find(par, j) for j in range(N))
    base = (N - 1) * N
    for j in range(N):
        if find(par, base + j) in roots:
            return True
    return False

def spans_site(bonds, N, p, rng):
    open_n = [rng.random() < p for _ in range(N * N)]
    par = list(range(N * N))
    sz = [1] * (N * N)
    for a, bb in bonds:
        if open_n[a] and open_n[bb]:
            union(par, sz, a, bb)
    roots = set(find(par, j) for j in range(N) if open_n[j])
    base = (N - 1) * N
    for j in range(N):
        t = base + j
        if open_n[t] and find(par, t) in roots:
            return True
    return False

def cross50(spanner, bonds, N, lo, hi, rng):
    steps = int(round((hi - lo) / STEP))
    pp = None
    pv = None
    for k in range(steps + 1):
        p = lo + STEP * k
        hits = 0
        for _ in range(R):
            if spanner(bonds, N, p, rng):
                hits += 1
        v = hits / R
        print("    p=%.3f P=%.4f" % (p, v))
        if pv is not None and pv < 0.5 <= v:
            t = (0.5 - pv) / (v - pv)
            return pp + t * (p - pp)
        pp = p
        pv = v
    return float("nan")

def main():
    rng = random.Random(SEED)
    t0 = time.time()
    print("miya_lattice_perc v1.0 seed=%d R=%d" % (SEED, R))
    print("true: triangular site pc=0.5 bond pc=%.7f" % PC_BOND)
    for N in (48, 96, 144):
        b = tri_bonds(N)
        print("[site N=%d] scan 0.42..0.58" % N)
        e = cross50(spans_site, b, N, 0.42, 0.58, rng)
        print("  site est N=%d: %.4f (true 0.5, d=%+.4f)" % (N, e, e - PC_SITE))
    for N in (48, 96):
        b = tri_bonds(N)
        print("[bond N=%d] scan 0.28..0.42" % N)
        e = cross50(spans_bond, b, N, 0.28, 0.42, rng)
        print("  bond est N=%d: %.4f (true %.7f, d=%+.4f)" % (N, e, PC_BOND, e - PC_BOND))
    print("elapsed %.1fs" % (time.time() - t0))
    print("GUIDE: site N=144 within 0.012 of 0.5 AND bond N=96 within 0.012 of 0.347296 => PASS")
    print("       site est near 0.593 => built as square-like 4-neighbor")
    print("       bond est near 0.6527 => honeycomb 3-neighbor instead of triangular")

main()