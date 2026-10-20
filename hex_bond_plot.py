#!/usr/bin/env python3
# hex_bond_plot.py v1.0 | recompute fixture sweep (same seed/order as v1.2) + save figure
# output: ~/storage/shared/DCIM/hex_bond_fixture.png (fallback: local dir)
import math, random, time, os

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

def sweep(lat, L, lo, hi, R, rng):
    bonds, n, left, right = lat(L)
    xs = []
    ys = []
    steps = int(round((hi - lo) / 0.005))
    for k in range(steps + 1):
        p = lo + 0.005 * k
        hits = 0
        for _ in range(R):
            if spans(bonds, n, left, right, p, rng):
                hits += 1
        xs.append(p)
        ys.append(hits / R)
    return xs, ys

def main():
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib missing: run  pip install matplotlib  then rerun")
        return
    R = 400
    rng = random.Random(SEED)
    t0 = time.time()
    series = []
    for L in (32, 64):
        print("[hex L=%d]" % L)
        xs, ys = sweep(hex_lat, L, 0.58, 0.72, R, rng)
        series.append(("hex L=%d" % L, xs, ys))
        print("[sq L=%d]" % L)
        xs, ys = sweep(sq_lat, L, 0.44, 0.58, R, rng)
        series.append(("sq L=%d" % L, xs, ys))
    fig, ax = plt.subplots(figsize=(8, 5))
    for label, xs, ys in series:
        ax.plot(xs, ys, marker=".", label=label)
    ax.axvline(PC_HEX, color="purple", ls="--", label="hex pc exact 0.6527036")
    ax.axvline(0.5, color="gray", ls=":", label="square pc exact 0.5")
    ax.axhline(0.5, color="black", lw=0.5)
    ax.set_xlabel("bond probability p")
    ax.set_ylabel("P_span (left-right crossing)")
    ax.set_title("hex_bond_fixture | seed=%d R=%d" % (SEED, R))
    ax.legend()
    ax.grid(alpha=0.3)
    outdir = os.path.expanduser("~/storage/shared/DCIM")
    if not os.path.isdir(outdir):
        outdir = "."
    out = os.path.join(outdir, "hex_bond_fixture.png")
    fig.savefig(out, dpi=200, bbox_inches="tight")
    print("elapsed %.1fs" % (time.time() - t0))
    print("FIGURE_SAVED: %s" % os.path.abspath(out))
    if outdir == ".":
        print("DCIM not visible; run termux-setup-storage, allow, rerun")

main()
