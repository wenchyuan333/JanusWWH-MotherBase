#!/usr/bin/env python3
# hex_bond_fixture.py v1.2 | stdlib only | seed-fixed replay
# WHAT : honeycomb bond-percolation 50% crossing vs exact pc
# KNOWN: pc_hex = 1 - 2*sin(pi/18) = 0.6527036447 ; square = 0.5
# CLAIM: lattice statistics calibration only; no physics claim
import math, random, time

SEED = 20260806
PC_HEX = 1.0 - 2.0 * math.sin(math.pi / 18.0)

def find(par, x):
    while par[x] != x:
        par[x] = par[par[x]]
        x = par[x]
    return x

def union(par, sz, a, b):
    ra = find(par, a)
    rb = find(par, b)
    if ra == rb:
        return
    if sz[ra] < sz[rb]:
        ra, rb = rb, ra
    par[rb] = ra
    sz[ra] += sz[rb]

def hex_lat(L):
    bonds = []
    for i in range(L):
        for j in range(L):
            a = 2 * (i * L + j)
            bonds.append((a, a + 1))
            bonds.append((a, 2 * (i * L + (j - 1) % L) + 1))
            if i > 0:
                bonds.append((a, 2 * ((i - 1) * L + j) + 1))
    left = []
    right = []
    for j in range(L):
        left.append(2 * j)
        left.append(2 * j + 1)
        right.append(2 * ((L - 1) * L + j))
        right.append(2 * ((L - 1) * L + j) + 1)
    return bonds, 2 * L * L, left, right

def sq_lat(L):
    bonds = []
    for i in range(L):
        for j in range(L):
            s = i * L + j
            bonds.append((s, i * L + (j + 1) % L))
            if i + 1 < L:
                bonds.append((s, (i + 1) * L + j))
    left = [j for j in range(L)]
    right = [(L - 1) * L + j for j in range(L)]
    return bonds, L * L, left, right

def spans(bonds, n, left, right, p, rng):
    par = list(range(n))
    sz = [1] * n
    for a, b in bonds:
        if rng.random() < p:
            union(par, sz, a, b)
    roots = set(find(par, s) for s in left)
    for s in right:
        if find(par, s) in roots:
            return True
    return False

def p_span(bonds, n, left, right, p, R, rng):
    hits = 0
    for _ in range(R):
        if spans(bonds, n, left, right, p, rng):
            hits += 1
    return hits / R

def cross50(lat, L, p_lo, p_hi, R, rng):
    bonds, n, left, right = lat(L)
    steps = int(round((p_hi - p_lo) / 0.005))
    pp = None
    pv = None
    for k in range(steps + 1):
        p = p_lo + 0.005 * k
        v = p_span(bonds, n, left, right, p, R, rng)
        print("    p=%.3f P=%.4f" % (p, v))
        if pv is not None and pv < 0.5 <= v:
            t = (0.5 - pv) / (v - pv)
            return pp + t * (p - pp)
        pp = p
        pv = v
    return float("nan")

def main():
    R = 400
    rng = random.Random(SEED)
    t0 = time.time()
    print("hex_bond_fixture v1.2 seed=%d R=%d" % (SEED, R))
    print("true: hex pc=%.7f square pc=0.5" % PC_HEX)
    res = {}
    for L in (32, 64):
        print("[L=%d] honeycomb" % L)
        h = cross50(hex_lat, L, 0.58, 0.72, R, rng)
        res[("h", L)] = h
        print("  hex est L=%d: %.4f (d=%+.4f)" % (L, h, h - PC_HEX))
        print("[L=%d] square control" % L)
        s = cross50(sq_lat, L, 0.44, 0.58, R, rng)
        res[("s", L)] = s
        print("  sq  est L=%d: %.4f (d=%+.4f)" % (L, s, s - 0.5))
    h64 = res[("h", 64)]
    s64 = res[("s", 64)]
    print("elapsed %.1fs" % (time.time() - t0))
    if abs(h64 - PC_HEX) <= 0.012:
        print("VERDICT hex: PASS")
    elif abs(h64 - 0.5) < abs(h64 - PC_HEX):
        print("VERDICT hex: FAIL (square-like adjacency)")
    else:
        print("VERDICT hex: FAIL (off target)")
    if abs(s64 - 0.5) <= 0.012:
        print("VERDICT square control: OK")
    else:
        print("VERDICT square control: OFF")
    print("official run: set R=1000 and rerun")

main()
