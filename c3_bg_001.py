"""C3-BG-001 : chi(C3) 背景項與 alpha_IL=0 控制組
三層 q=3 Potts / 三角晶格 z=6 / 週期邊界 / Metropolis 單自旋翻轉
NumPy 向量化 3-子晶格棋盤更新（無 numba）
"""
import sys, time, json
import numpy as np

Q = 3
BETA = 0.50823
ALPHAS = (0.17, 0.0)
L_LIST = (9, 18, 27, 36, 54)
SEEDS = (369, 396, 639)
N_EQUIL = 20000
N_MEAS = 40000
MEAS_EVERY = 7
N_BLOCK = 20
PAPER_CHI = {9: 1.924, 18: 2.960, 27: 3.905, 36: 4.563, 54: 5.840}

if "--quick" in sys.argv:
    L_LIST = (9, 18, 27)
    SEEDS = (369,)
    N_EQUIL, N_MEAS = 2000, 6000

SHIFTS = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1))


def colour(L):
    x = np.arange(L)[:, None]
    y = np.arange(L)[None, :]
    return (x + 2 * y) % 3          # 三角晶格三著色, 需 L % 3 == 0


def nsum(field, val):
    t = np.zeros(field.shape, dtype=np.int16)
    for dx, dy in SHIFTS:
        t += (np.roll(np.roll(field, dx, 0), dy, 1) == val)
    return t


def run(L, alpha, seed):
    assert L % 3 == 0
    rng = np.random.default_rng(seed)
    N = L * L
    s = rng.integers(0, Q, size=(3, L, L)).astype(np.int8)
    masks = [colour(L) == c for c in range(3)]
    out = []
    for sweep in range(N_EQUIL + N_MEAS):
        for k in range(3):
            o1, o2 = (k + 1) % 3, (k + 2) % 3
            for c in range(3):
                s_old = s[k].copy()
                step = rng.integers(1, Q, size=(L, L)).astype(np.int8)
                s_new = (s_old + step) % Q
                dH = -BETA * (nsum(s_old, s_new) - nsum(s_old, s_old))
                b_new = (s[o1] == s_new).astype(np.int16) + (s[o2] == s_new)
                b_old = (s[o1] == s_old).astype(np.int16) + (s[o2] == s_old)
                dH = dH - alpha * (b_new - b_old)
                acc = (dH <= 0) | (rng.random((L, L)) < np.exp(-np.clip(dH, 0, 50)))
                s[k] = np.where(masks[c] & acc, s_new, s_old)
        if sweep >= N_EQUIL and (sweep - N_EQUIL) % MEAS_EVERY == 0:
            out.append(float(np.mean((s[0] == s[1]) & (s[1] == s[2]))))
    return np.asarray(out), N


def chi_jack(x, N, nb=N_BLOCK):
    m = len(x) // nb
    x = x[: m * nb]
    blocks = x.reshape(nb, m)
    chi = N * x.var()
    j = np.array([N * np.delete(blocks, i, 0).ravel().var() for i in range(nb)])
    return chi, float(np.sqrt((nb - 1) * j.var()))


def combine(vals, errs):
    v = np.mean(vals)
    e = np.sqrt(np.mean(np.square(errs)) / len(vals) + np.var(vals) / len(vals))
    return float(v), float(e)


def wls_slope(L, y, ye):
    lx, ly = np.log(np.asarray(L, float)), np.log(y)
    w = 1.0 / np.square(ye / y)
    S, Sx, Sy = w.sum(), (w * lx).sum(), (w * ly).sum()
    Sxx, Sxy = (w * lx * lx).sum(), (w * lx * ly).sum()
    d = S * Sxx - Sx * Sx
    return float((S * Sxy - Sx * Sy) / d), float(np.sqrt(S / d))


def fit_ABy(L, y):
    L = np.asarray(L, float)
    best = None
    for yy in np.arange(0.05, 2.401, 0.005):
        M = np.vstack([np.ones_like(L), L ** yy]).T
        coef, res, *_ = np.linalg.lstsq(M, y, rcond=None)
        r = float(np.sum((M @ coef - y) ** 2))
        if best is None or r < best[0]:
            best = (r, yy, coef[0], coef[1])
    return best[1], best[2], best[3]


def main():
    t0 = time.time()
    res = {}
    for alpha in ALPHAS:
        for L in L_LIST:
            vs, es = [], []
            for sd in SEEDS:
                x, N = run(L, alpha, sd)
                c, e = chi_jack(x, N)
                vs.append(c)
                es.append(e)
            res[(alpha, L)] = combine(vs, es)
            print(f"alpha={alpha:.2f} L={L:3d}  chi={res[(alpha,L)][0]:.4f} +- "
                  f"{res[(alpha,L)][1]:.4f}   [{time.time()-t0:.0f}s]", flush=True)

    Ls = list(L_LIST)
    full = np.array([res[(0.17, L)][0] for L in Ls])
    fulle = np.array([res[(0.17, L)][1] for L in Ls])
    bg = np.array([res[(0.0, L)][0] for L in Ls])
    bge = np.array([res[(0.0, L)][1] for L in Ls])

    s_full, s_full_e = wls_slope(Ls, full, fulle)
    s_bg, _ = wls_slope(Ls, bg, bge)
    conn = full - bg
    conne = np.sqrt(fulle ** 2 + bge ** 2)
    ok = conn > 0
    s_conn, s_conn_e = (wls_slope(np.array(Ls)[ok], conn[ok], conne[ok])
                        if ok.sum() >= 3 else (float("nan"), float("nan")))
    y_fit, A_fit, B_fit = fit_ABy(Ls, full)

    dev = max(abs(res[(0.17, L)][0] - PAPER_CHI[L]) / PAPER_CHI[L]
              for L in Ls if L in PAPER_CHI)

    print("\n--- C3-BG-001 ---")
    print(f"max |dev| vs paper Table 1 = {dev*100:.1f}%")
    print(f"s_full = {s_full:.4f} +- {s_full_e:.4f}")
    print(f"s_bg   = {s_bg:.4f}")
    print(f"s_conn = {s_conn:.4f} +- {s_conn_e:.4f}")
    print(f"3-param: y = {y_fit:.3f}, A = {A_fit:.4f}, B = {B_fit:.4f}")

    if dev > 0.20:
        v = "E | 可比性未建立, A-D 不判讀"
    elif s_bg > 0.2:
        v = "D | 控制組無效, 撤回本設計"
    elif abs(A_fit) < 1e-9 or abs(s_full - 0.589) < 1.5 * max(s_full_e, 1e-9):
        v = "A | 背景假說死, 0.589 是真斜率, Miya 登記推論錯誤"
    elif s_conn >= 1.4:
        v = "B | 0.589 為背景污染, 論文 3-6 節需重算"
    else:
        v = "C | 未定, 下一步是 G(r), 不是加大 L"
    print("VERDICT:", v)
    print(f"RECEIPT | python={sys.version.split()[0]} | numpy={np.__version__} | "
          f"beta={BETA} | Ls={Ls} | seeds={list(SEEDS)} | "
          f"equil={N_EQUIL} meas={N_MEAS} | elapsed={time.time()-t0:.1f}s")
    print("CEILING | single point beta_c, no peak scan, no G(r), w=0, z=6, L<=54")


if __name__ == "__main__":
    main()
