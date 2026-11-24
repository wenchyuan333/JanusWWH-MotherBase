#!/usr/bin/env python3
# miya_lattice_fss.py v1.0 | large-N FSS extrapolation for triangular lattice pc
# GOAL : confirm the v2 PASS is not a small-size accident: est(N) -> pc
# TRUE : site pc = 0.5 (exact) ; bond pc = 2*sin(pi/18) = 0.3472963553 (exact)
import math, random, time

SEED = 20260808
R = 200
STEP = 0.0025
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
        print("    p=%.4f P=%.4f" % (p, v))
        if pv is not None and pv < 0.5 <= v:
            t = (0.5 - pv) / (v - pv)
            return pp + t * (p - pp)
        pp = p
        pv = v
    return float("nan")

def fit_fss(ns, es):
    best = None
    for k in range(271):
        y = 0.3 + 0.01 * k
        xs = [n ** (-y) for n in ns]
        mx = sum(xs) / len(xs)
        me = sum(es) / len(es)
        sxx = sum((x - mx) ** 2 for x in xs)
        if sxx == 0:
            continue
        sxe = sum((xs[i] - mx) * (es[i] - me) for i in range(len(ns)))
        A = sxe / sxx
        pinf = me - A * mx
        res = math.sqrt(sum((es[i] - (pinf + A * xs[i])) ** 2 for i in range(len(ns))) / len(ns))
        if best is None or res < best[0]:
            best = (res, y, pinf, A)
    return best

def main():
    rng = random.Random(SEED)
    t0 = time.time()
    print("miya_lattice_fss v1.0 seed=%d R=%d" % (SEED, R))
    print("true: site pc=0.5 bond pc=%.7f" % PC_BOND)
    site_ns = (96, 144, 192, 256)
    bond_ns = (96, 144, 192)
    site_est = []
    bond_est = []
    for N in site_ns:
        b = tri_bonds(N)
        print("[site N=%d] scan 0.470..0.530" % N)
        e = cross50(spans_site, b, N, 0.470, 0.530, rng)
        site_est.append(e)
        print("  site est N=%d: %.4f (d=%+.4f)" % (N, e, e - PC_SITE))
    for N in bond_ns:
        b = tri_bonds(N)
        print("[bond N=%d] scan 0.330..0.360" % N)
        e = cross50(spans_bond, b, N, 0.330, 0.360, rng)
        bond_est.append(e)
        print("  bond est N=%d: %.4f (d=%+.4f)" % (N, e, e - PC_BOND))
    rs, ys, ps, _ = fit_fss(list(site_ns), site_est)
    print("FSS site: pinf=%.5f (true 0.5, d=%+.5f) y=%.2f resid=%.5f" % (ps, ps - PC_SITE, ys, rs))
    rb, yb, pb, _ = fit_fss(list(bond_ns), bond_est)
    print("FSS bond: pinf=%.5f (true %.7f, d=%+.5f) y=%.2f resid=%.5f" % (pb, PC_BOND, pb - PC_BOND, yb, rb))
    ok_s = abs(ps - PC_SITE) <= 0.004 + rs
    ok_b = abs(pb - PC_BOND) <= 0.004 + rb
    if ok_s and ok_b:
        print("VERDICT: EXTRAPOLATED PASS (not a small-size accident)")
    else:
        print("VERDICT: extrapolation off; raise R or add N=384")
    print("elapsed %.1fs" % (time.time() - t0))

main()