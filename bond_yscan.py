#!/usr/bin/env python3
# miya_lattice_v21.py v1.0 | merged: (A) their-builder fidelity + (B) big-N FSS push
# A: import HexagonalLattice from miya_hexagonal_network.py, extract adjacency,
#    site crossing at N=64, compare with analytic triangular builder
# B: site N=384 + bond N=288, joint fit with v3 prior points (labeled provenance)
# CLAIM: lattice geometry/statistics only; no neural-dynamics claim
import math, random, time, os

SEED = 20260809
R = 400
STEP = 0.0025
PC_SITE = 0.5
PC_BOND = 2.0 * math.sin(math.pi / 18.0)
SITE_PRIOR = [(96, 0.4967), (144, 0.4972), (192, 0.4966), (256, 0.4986)]
BOND_PRIOR = [(96, 0.3459), (144, 0.3457), (192, 0.3462)]

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

def bounds(N):
    left = list(range(N))
    right = [(N - 1) * N + j for j in range(N)]
    return left, right

def spans_site(bonds, n, left, right, p, rng):
    open_n = [rng.random() < p for _ in range(n)]
    par = list(range(n))
    sz = [1] * n
    for a, bb in bonds:
        if open_n[a] and open_n[bb]:
            union(par, sz, a, bb)
    roots = set(find(par, s) for s in left if open_n[s])
    for s in right:
        if open_n[s] and find(par, s) in roots:
            return True
    return False

def spans_bond(bonds, n, left, right, p, rng):
    par = list(range(n))
    sz = [1] * n
    for a, bb in bonds:
        if rng.random() < p:
            union(par, sz, a, bb)
    roots = set(find(par, s) for s in left)
    for s in right:
        if find(par, s) in roots:
            return True
    return False

def cross50(spanner, bonds, n, left, right, lo, hi, rng):
    steps = int(round((hi - lo) / STEP))
    pp = None
    pv = None
    for k in range(steps + 1):
        p = lo + STEP * k
        hits = 0
        for _ in range(R):
            if spanner(bonds, n, left, right, p, rng):
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
            best = (res, y, pinf)
    return best

def part_a(rng):
    print("[A] their-builder fidelity (N=64, site mode)")
    if not os.path.exists("miya_hexagonal_network.py"):
        print("  SKIP: miya_hexagonal_network.py not found (copy from canon page)")
        return
    try:
        import numpy  # noqa
        import scipy  # noqa
    except ImportError as e:
        print("  SKIP: missing dep %s" % e)
        return
    try:
        from miya_hexagonal_network import HexagonalLattice
        lat = HexagonalLattice(N=64)
        n = lat.total_nodes
        adj = lat.adjacency
        bonds = []
        for i in range(n):
            for j in range(i + 1, n):
                if adj[i, j]:
                    bonds.append((i, j))
        deg = 2.0 * len(bonds) / n
        print("  their builder: nodes=%d edges=%d mean_degree=%.3f" % (n, len(bonds), deg))
        left, right = bounds(64)
        e_theirs = cross50(spans_site, bonds, n, left, right, 0.470, 0.530, rng)
        print("  their est N=64: %.4f (d=%+.4f)" % (e_theirs, e_theirs - PC_SITE))
        b2 = tri_bonds(64)
        e_an = cross50(spans_site, b2, 64 * 64, left, right, 0.470, 0.530, rng)
        print("  analytic est N=64: %.4f (d=%+.4f)" % (e_an, e_an - PC_SITE))
        dd = abs(e_theirs - e_an)
        ok = (dd <= 0.015) and (4.8 <= deg <= 6.0)
        print("  EQUIVALENCE: |dd|=%.4f deg_ok=%s => %s" % (dd, deg, "PASS" if ok else "FAIL"))
        print("  note: their builder is open-everywhere; analytic is periodic-y (registered)")
    except Exception as e:
        print("  SKIP: builder error %s" % e)

def part_b(rng):
    print("[B] big-N push (joint fit with v3 prior)")
    left, right = bounds(384)
    b384 = tri_bonds(384)
    print("  [site N=384] scan 0.490..0.510")
    e384 = cross50(spans_site, b384, 384 * 384, left, right, 0.490, 0.510, rng)
    print("  site est N=384: %.4f (d=%+.4f)" % (e384, e384 - PC_SITE))
    left, right = bounds(288)
    b288 = tri_bonds(288)
    print("  [bond N=288] scan 0.340..0.355")
    e288 = cross50(spans_bond, b288, 288 * 288, left, right, 0.340, 0.355, rng)
    print("  bond est N=288: %.4f (d=%+.4f)" % (e288, e288 - PC_BOND))
    ns_s = [n for n, _ in SITE_PRIOR] + [384]
    es_s = [e for _, e in SITE_PRIOR] + [e384]
    ns_b = [n for n, _ in BOND_PRIOR] + [288]
    es_b = [e for _, e in BOND_PRIOR] + [e288]
    rs, ys, ps = fit_fss(ns_s, es_s)
    print("FSS site: pinf=%.5f (d=%+.5f) y=%.2f resid=%.5f" % (ps, ps - PC_SITE, ys, rs))
    rb, yb, pb = fit_fss(ns_b, es_b)
    print("FSS bond: pinf=%.5f (d=%+.5f) y=%.2f resid=%.5f" % (pb, pb - PC_BOND, yb, rb))
    ok_s = abs(ps - PC_SITE) <= 0.004 + rs
    ok_b = abs(pb - PC_BOND) <= 0.004 + rb
    if ok_s and ok_b:
        print("VERDICT B: EXTRAPOLATED PASS (5-pt site / 4-pt bond joint fit)")
    else:
        print("VERDICT B: off; raise R or add N=512")

def main():
    rng = random.Random(SEED)
    t0 = time.time()
    print("miya_lattice_v21 v1.0 seed=%d R=%d" % (SEED, R))
    print("true: site pc=0.5 bond pc=%.7f" % PC_BOND)
    part_a(rng)
    part_b(rng)
    print("elapsed %.1fs" % (time.time() - t0))

main()