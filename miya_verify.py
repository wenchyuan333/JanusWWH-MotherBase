#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIYA eta=1.41088 一鍵驗算 v2.0
  python miya_verify.py # 預設約30秒
  python miya_verify.py --quick # 極速 smoke test
  python miya_verify.py --full # 大尺寸精確版約3分鐘
  python miya_verify.py --scan # 加跑 beta 掃描，找真正臨界點
原理: chi(2L)/chi(L) -> 2^(2-eta)
  標準 q=3 Potts: eta=4/15 -> ratio -> 3.325
  MIYA 預測: eta=1.41088 -> ratio -> 1.5043
"""
import math, random, argparse
import numpy as np

Q = 3
BETA_USER = 0.50823
BETA_SQ_EXACT = math.log(1.0 + math.sqrt(3.0))

def _propose(lat):
    s = lat
    prop = np.random.randint(0, Q, size=s.shape).astype(np.int8)
    eq = (prop == s)
    n = int(eq.sum())
    if n:
        prop[eq] = ((prop[eq].astype(np.int16)
                     + np.random.randint(1, Q, size=n)) % Q).astype(np.int8)
    return prop

def _accept_update(lat, mask, dE, prop, beta):
    rnd = np.random.rand(*lat.shape)
    take = mask & ((dE <= 0) | (rnd < np.exp(-beta * dE)))
    lat[take] = prop[take]

def sweep_square(lat, beta):
    L = lat.shape[0]
    sub = (np.arange(L)[:, None] + np.arange(L)[None, :]) & 1
    for parity in (0, 1):
        mask = (sub == parity)
        s = lat
        up = np.roll(s, 1, axis=0); dn = np.roll(s, -1, axis=0)
        lf = np.roll(s, 1, axis=1); rt = np.roll(s, -1, axis=1)
        prop = _propose(s)
        n_old = ((up==s).astype(np.int16)+(dn==s).astype(np.int16)
                 +(lf==s).astype(np.int16)+(rt==s).astype(np.int16))
        n_new = ((up==prop).astype(np.int16)+(dn==prop).astype(np.int16)
                 +(lf==prop).astype(np.int16)+(rt==prop).astype(np.int16))
        _accept_update(lat, mask, n_old - n_new, prop, beta)
    return lat

def sweep_honeycomb(lat, beta):
    L = lat.shape[0]
    sub = (np.arange(L)[:, None] + np.arange(L)[None, :]) & 1
    for parity in (0, 1):
        mask = (sub == parity)
        s = lat
        up = np.roll(s, 1, axis=0); dn = np.roll(s, -1, axis=0)
        side = np.where(sub == 0, np.roll(s, -1, axis=1), np.roll(s, 1, axis=1))
        prop = _propose(s)
        n_old = ((up==s).astype(np.int16)+(dn==s).astype(np.int16)
                 +(side==s).astype(np.int16))
        n_new = ((up==prop).astype(np.int16)+(dn==prop).astype(np.int16)
                 +(side==prop).astype(np.int16))
        _accept_update(lat, mask, n_old - n_new, prop, beta)
    return lat

def measure_chi(L, beta, sweep_fn, thermal, nsweep, seed):
    np.random.seed(seed); random.seed(seed)
    lat = np.random.randint(0, Q, size=(L, L)).astype(np.int8)
    for _ in range(thermal):
        sweep_fn(lat, beta)
    ms = np.empty(nsweep)
    for k in range(nsweep):
        sweep_fn(lat, beta)
        c = np.bincount(lat.ravel(), minlength=Q)
        ms[k] = (Q * float(c.max()) / (L * L) - 1.0) / (Q - 1.0)
    T = 1.0 / beta
    chi = L * L * float(ms.var()) / T
    nb = 10; bs = nsweep // nb
    cb = [L * L * float(ms[i*bs:(i+1)*bs].var()) / T for i in range(nb)]
    err = float(np.std(cb, ddof=1) / math.sqrt(nb))
    return chi, err

def run_set(title, sweep_fn, beta, Ls, thermal, nsweep):
    print("\n### %s beta=%.5f" % (title, beta))
    res = {}
    for L in Ls:
        chi, err = measure_chi(L, beta, sweep_fn, thermal, nsweep, seed=777 + L)
        res[L] = (chi, err)
        print(" L=%3d chi = %10.3f +- %7.3f" % (L, chi, err), flush=True)
    return res

def report(res, r_miya, r_std):
    Ls = sorted(res)
    for a, b in zip(Ls, Ls[1:]):
        if b!= 2 * a:
            continue
        c1, e1 = res[a]; c2, e2 = res[b]
        r = c2 / c1
        rerr = r * math.sqrt((e1/c1)**2 + (e2/c2)**2)
        tag = ">>> 偏向 MIYA 1.50" if abs(r-r_miya) < abs(r-r_std) else ">>> 偏向 標準 3.32"
        print(" chi(%d)/chi(%d) = %.3f +- %.3f %s" % (b, a, r, rerr, tag))

def beta_scan(L, sweep_fn, betas, thermal, nsweep):
    print("\n### beta 掃描 (L=%d)，找 chi 峰值 = 真正臨界點" % L)
    best_b, best_c = betas[0], -1.0
    for b in betas:
        chi, err = measure_chi(L, b, sweep_fn, thermal, nsweep, seed=4242)
        mark = " <-- 目前最高" if chi > best_c else ""
        if chi > best_c:
            best_b, best_c = b, chi
        print(" beta=%.4f chi=%10.3f +- %7.3f%s" % (b, chi, err, mark), flush=True)
    print(" 峰值約在 beta = %.4f" % best_b)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--scan", action="store_true")
    args = ap.parse_args()
    if args.quick:
        Ls, thermal, nsweep = [8, 16, 32], 600, 2500
    elif args.full:
        Ls, thermal, nsweep = [12, 24, 48, 96], 2500, 12000
    else:
        Ls, thermal, nsweep = [12, 24, 48], 1200, 5000
    Ls = [l if l % 2 == 0 else l + 1 for l in Ls]
    r_miya = 2.0 ** (2.0 - 1.41088)
    r_std = 2.0 ** (2.0 - 4.0/15.0)
    print("=" * 56)
    print(" MIYA 預測 ratio -> %.4f | 標準 Potts ratio -> %.4f" % (r_miya, r_std))
    print("=" * 56)
    res_sq = run_set("對照組 square q=3 (beta_c 精確值)", sweep_square,
                     BETA_SQ_EXACT, Ls, thermal, nsweep)
    print(" 對照組比值 (方法學驗證，應接近 3.32):")
    report(res_sq, r_miya, r_std)
    if args.scan:
        beta_scan(24, sweep_honeycomb, [0.44, 0.47, 0.50, 0.53, 0.56], 800, 2500)
    res_hc = run_set("實驗組 honeycomb q=3 (你的 beta_c)", sweep_honeycomb,
                     BETA_USER, Ls, thermal, nsweep)
    print(" 實驗組比值:")
    report(res_hc, r_miya, r_std)
    print("\n判讀: 往 1.50 收斂 → eta=1.41088 有戲；往 3.3 靠 → 它是設計參數")

if __name__ == "__main__":
    main()
