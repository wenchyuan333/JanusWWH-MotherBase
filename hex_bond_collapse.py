#!/usr/bin/env python3
# hex_bond_collapse.py v1.0 | FSS collapse -> extract nu (2D percolation: 4/3)
import math, random, time, os
SEED = 20260807
R = 400
STEP = 0.0025
PC_HEX = 1.0 - 2.0 * math.sin(math.pi / 18.0)
PC_SQ = 0.5
NU_TRUE = 4.0 / 3.0

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

def hex_lat(L):
    b = []
    for i in range(L):
        for j in range(L):
            a = 2 * (i * L + j)
            b.append((a, a + 1))
            b.append((a, 2 * (i * L + (j - 1) % L) + 1))
            if i > 0:
                b.append((a, 2 * ((i - 1) * L + j) + 1))
    left = []
    right = []
    for j in range(L):
        left += [2 * j, 2 * j + 1]
        right += [2 * ((L - 1) * L + j), 2 * ((L - 1) * L + j) + 1]
    return b, 2 * L * L, left, right

def sq_lat(L):
    b = []
    for i in range(L):
        for j in range(L):
            s = i * L + j
            b.append((s, i * L + (j + 1) % L))
            if i + 1 < L:
                b.append((s, (i + 1) * L + j))
    return b, L * L, list(range(L)), [(L - 1) * L + j for j in range(L)]

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

def sweep(lat, L, pc, lo, hi, rng, tag):
    bonds, n, left, right = lat(L)
    xs, ys = [], []
    steps = int(round((hi - lo) / STEP))
    for k in range(steps + 1):
        p = lo + STEP * k
        hits = 0
        for _ in range(R):
            if spans(bonds, n, left, right, p, rng):
                hits += 1
        xs.append(p)
        ys.append(hits / R)
    print("  done %s L=%d" % (tag, L))
    return {"pc": pc, "L": L, "xs": xs, "ys": ys, "tag": tag}

def interp(xs, ys, x):
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    lo, hi = 0, len(xs) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if xs[mid] <= x:
            lo = mid
        else:
            hi = mid
    t = (x - xs[lo]) / (xs[hi] - xs[lo])
    return ys[lo] + t * (ys[hi] - ys[lo])

def curve_rms(a, b):
    lo = max(a[0][0], b[0][0])
    hi = min(a[0][-1], b[0][-1])
    if lo >= hi:
        return None
    n = 200
    dx = (hi - lo) / n
    acc = 0.0
    for k in range(n + 1):
        x = lo + dx * k
        d = interp(a[0], a[1], x) - interp(b[0], b[1], x)
        acc += d * d
    return math.sqrt(acc / (n + 1))

def cost(series, nu):
    sc = []
    for c in series:
        f = c["L"] ** (1.0 / nu)
        sc.append(([(x - c["pc"]) * f for x in c["xs"]], c["ys"]))
    tot, cnt = 0.0, 0
    for i in range(len(sc)):
        for j in range(i + 1, len(sc)):
            d = curve_rms(sc[i], sc[j])
            if d is not None:
                tot += d
                cnt += 1
    return tot / max(cnt, 1)

def best_nu(series):
    bnu, bc = None, None
    for k in range(201):
        nu = 1.0 + 0.005 * k
        c = cost(series, nu)
        if bc is None or c < bc:
            bc, bnu = c, nu
    return bnu, bc

def main():
    rng = random.Random(SEED)
    t0 = time.time()
    print("collapse v1.0 seed=%d R=%d" % (SEED, R))
    hexs = [sweep(hex_lat, L, PC_HEX, 0.60, 0.70, rng, "hex") for L in (32, 64, 96)]
    sqs = [sweep(sq_lat, L, PC_SQ, 0.44, 0.56, rng, "sq") for L in (32, 64)]
    nh, ch = best_nu(hexs)
    ns, cs = best_nu(sqs)
    na, ca = best_nu(hexs + sqs)
    print("RESULT nu_hex=%.3f (cost %.5f) d=%+.3f" % (nh, ch, nh - NU_TRUE))
    print("RESULT nu_sq =%.3f (cost %.5f) d=%+.3f" % (ns, cs, ns - NU_TRUE))
    print("RESULT nu_all=%.3f (cost %.5f) d=%+.3f" % (na, ca, na - NU_TRUE))
    if abs(na - NU_TRUE) <= 0.15:
        print("VERDICT: CONSISTENT with nu=4/3")
    else:
        print("VERDICT: outside demo band; raise R / sizes, rerun")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("no matplotlib; skip figure")
        print("elapsed %.1fs" % (time.time() - t0))
        return
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    for c in hexs + sqs:
        lb = "%s L=%d" % (c["tag"], c["L"])
        ax1.plot(c["xs"], c["ys"], marker=".", label=lb)
        f = c["L"] ** (1.0 / na)
        ax2.plot([(x - c["pc"]) * f for x in c["xs"]], c["ys"], marker=".", label=lb)
    ax1.set_title("raw")
    ax1.set_xlabel("p")
    ax1.set_ylabel("P_span")
    ax1.legend(fontsize=8)
    ax1.grid(alpha=0.3)
    ax2.set_title("collapsed nu=%.3f (true 1.333)" % na)
    ax2.set_xlabel("(p-pc)*L^(1/nu)")
    ax2.grid(alpha=0.3)
    outdir = os.path.expanduser("~/storage/shared/DCIM")
    if not os.path.isdir(outdir):
        outdir = "."
    out = os.path.join(outdir, "hex_bond_collapse.png")
    fig.savefig(out, dpi=200, bbox_inches="tight")
    print("elapsed %.1fs" % (time.time() - t0))
    print("FIGURE_SAVED: %s" % os.path.abspath(out))

main()
