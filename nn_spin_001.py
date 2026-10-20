#!/usr/bin/env python3
"""NN-SPIN-001 v0.1
NN <-> spin-glass replica-overlap fixture.
Zero dependency: Python 3 standard library only. Target: Termux CPython.

Replay:  python3 nn_spin_001.py
Smoke  :  python3 nn_spin_001.py --quick     (result NOT citable)
"""
import math
import random
import sys
import time

CFG = {
    "n_in": 20,
    "n_hidden": 16,
    "n_train": 1500,
    "epochs": 40,
    "lr": 0.05,
    "betas": [0.25, 0.5, 0.75, 1.0, 1.5, 2.0],
    "beta_ref": 1.0,
    "n_replicas": 6,
    "sweeps": 800,
    "burn": 200,
    "measure_every": 25,
    "seeds": [1, 2, 3],
    "q2_onset": 0.10,
    "sigma_gate": 3.0,
    "acc_margin": 0.05,
}

if "--quick" in sys.argv:
    CFG.update({"n_train": 400, "epochs": 10, "sweeps": 150, "burn": 50,
                "seeds": [1], "betas": [0.5, 1.0, 2.0]})


# ---------- task: 3-hidden-unit teacher, sign readout ----------
def make_task(rng, n_in, n_train):
    scale = 1.0 / math.sqrt(n_in)
    t1 = [[rng.gauss(0.0, 1.0) for _ in range(n_in)] for _ in range(3)]
    t2 = [rng.gauss(0.0, 1.0) for _ in range(3)]
    xs, ys = [], []
    for _ in range(n_train):
        x = [rng.gauss(0.0, 1.0) for _ in range(n_in)]
        h = [math.tanh(scale * sum(t1[k][j] * x[j] for j in range(n_in)))
             for k in range(3)]
        o = sum(t2[k] * h[k] for k in range(3))
        xs.append(x)
        ys.append(1.0 if o > 0.0 else -1.0)
    return xs, ys


def majority_baseline(ys):
    pos = sum(1 for y in ys if y > 0.0)
    return max(pos, len(ys) - pos) / float(len(ys))


# ---------- student: 1 hidden layer, tanh, squared loss, plain SGD ----------
def train_student(rng, xs, ys, cfg):
    n_in, n_h, lr = cfg["n_in"], cfg["n_hidden"], cfg["lr"]
    scale = 1.0 / math.sqrt(n_in)
    w1 = [[rng.gauss(0.0, 1.0) for _ in range(n_in)] for _ in range(n_h)]
    w1_init = [row[:] for row in w1]
    w2 = [rng.gauss(0.0, 1.0) / math.sqrt(n_h) for _ in range(n_h)]
    idx = list(range(len(xs)))
    for _ in range(cfg["epochs"]):
        rng.shuffle(idx)
        for t in idx:
            x, y = xs[t], ys[t]
            a = []
            for i in range(n_h):
                z = scale * sum(w1[i][j] * x[j] for j in range(n_in))
                a.append(math.tanh(z))
            o = sum(w2[i] * a[i] for i in range(n_h))
            d = o - y
            for i in range(n_h):
                dz = d * w2[i] * (1.0 - a[i] * a[i]) * scale
                w2[i] -= lr * d * a[i]
                row = w1[i]
                for j in range(n_in):
                    row[j] -= lr * dz * x[j]
    # accuracy
    ok = 0
    for t in range(len(xs)):
        x = xs[t]
        o = 0.0
        for i in range(n_h):
            z = scale * sum(w1[i][j] * x[j] for j in range(n_in))
            o += w2[i] * math.tanh(z)
        if (o > 0.0) == (ys[t] > 0.0):
            ok += 1
    return w1_init, w1, ok / float(len(xs))


def shuffle_matrix(rng, w):
    flat = [v for row in w for v in row]
    rng.shuffle(flat)
    n_col = len(w[0])
    return [flat[i * n_col:(i + 1) * n_col] for i in range(len(w))]


# ---------- weights -> normalised couplings ----------
def couplings(w, n_in):
    n = len(w)
    j = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for k in range(i + 1, n):
            v = sum(w[i][t] * w[k][t] for t in range(n_in)) / float(n_in)
            j[i][k] = v
            j[k][i] = v
    sq, cnt = 0.0, 0
    for i in range(n):
        for k in range(i + 1, n):
            sq += j[i][k] * j[i][k]
            cnt += 1
    rms = math.sqrt(sq / cnt) if cnt > 0 else 0.0
    if rms <= 1e-12:
        return None  # degenerate coupling matrix -> contract row F
    for i in range(n):
        for k in range(n):
            j[i][k] /= rms
    return j


# ---------- Metropolis with incremental local fields ----------
def measure_q2(j, beta, cfg, rng):
    n = len(j)
    reps = cfg["n_replicas"]
    spins = [[1 if rng.random() < 0.5 else -1 for _ in range(n)]
             for _ in range(reps)]
    fields = [[sum(j[i][k] * s[k] for k in range(n)) for i in range(n)]
              for s in spins]
    acc = []
    for sweep in range(cfg["sweeps"]):
        for r in range(reps):
            s, h = spins[r], fields[r]
            for i in range(n):
                de = 2.0 * s[i] * h[i]
                if de <= 0.0 or rng.random() < math.exp(-beta * de):
                    delta = -2.0 * s[i]
                    s[i] = -s[i]
                    ji = j[i]
                    for k in range(n):
                        h[k] += ji[k] * delta
        if sweep >= cfg["burn"] and (sweep - cfg["burn"]) % cfg["measure_every"] == 0:
            for a in range(reps):
                for b in range(a + 1, reps):
                    q = sum(spins[a][i] * spins[b][i] for i in range(n)) / float(n)
                    acc.append(q * q)
    if not acc:
        return float("nan")
    return sum(acc) / float(len(acc))


def mean_sd(vals):
    m = sum(vals) / float(len(vals))
    if len(vals) < 2:
        return m, 0.0
    var = sum((v - m) ** 2 for v in vals) / float(len(vals) - 1)
    return m, math.sqrt(var)


def beta_onset(betas, q2s, thr):
    for i in range(len(betas)):
        if q2s[i] >= thr:
            if i == 0:
                return betas[0]
            x0, x1 = betas[i - 1], betas[i]
            y0, y1 = q2s[i - 1], q2s[i]
            if abs(y1 - y0) < 1e-12:
                return x1
            return x0 + (thr - y0) * (x1 - x0) / (y1 - y0)
    return float("nan")


def main():
    t_start = time.time()
    conds = ["init", "trained", "shuffled"]
    table = {c: {b: [] for b in CFG["betas"]} for c in conds}
    accs, baselines = [], []

    for seed in CFG["seeds"]:
        rng = random.Random(seed)
        xs, ys = make_task(rng, CFG["n_in"], CFG["n_train"])
        baselines.append(majority_baseline(ys))
        w_init, w_trained, acc = train_student(rng, xs, ys, CFG)
        accs.append(acc)
        w_shuf = shuffle_matrix(random.Random(seed + 10007), w_trained)
        mats = {"init": w_init, "trained": w_trained, "shuffled": w_shuf}
        for c in conds:
            j = couplings(mats[c], CFG["n_in"])
            if j is None:
                print("VERDICT: F | degenerate coupling matrix (%s, seed %d)"
                      % (c, seed))
                return 2
            for b in CFG["betas"]:
                q2 = measure_q2(j, b, CFG, random.Random(seed * 1000 + int(b * 100)))
                table[c][b].append(q2)

    # ---------- report ----------
    print("NN-SPIN-001 v0.1 | q2 = <q_ab^2>, scale-normalised couplings")
    print("beta      " + "".join("%-22s" % c for c in conds))
    stats = {c: {} for c in conds}
    for b in CFG["betas"]:
        line = "%-10.3f" % b
        for c in conds:
            m, sd = mean_sd(table[c][b])
            stats[c][b] = (m, sd)
            line += "%-22s" % ("%.4f +- %.4f" % (m, sd))
        print(line)

    for c in conds:
        q2s = [stats[c][b][0] for b in CFG["betas"]]
        print("beta_onset(%-9s) = %.4f" % (c, beta_onset(CFG["betas"], q2s,
                                                          CFG["q2_onset"])))

    acc_m = sum(accs) / float(len(accs))
    base_m = sum(baselines) / float(len(baselines))
    print("train_acc = %.4f | majority_baseline = %.4f" % (acc_m, base_m))

    # ---------- automatic verdict against the locked contract ----------
    br = CFG["beta_ref"]
    g = CFG["sigma_gate"]
    vals = {c: stats[c][br] for c in conds}
    if any(math.isnan(v[0]) or math.isinf(v[0]) for v in vals.values()):
        print("VERDICT: F | NaN or inf in q2")
        return 2
    if acc_m <= base_m + CFG["acc_margin"]:
        print("VERDICT: E | FAIL_TRAINING, run void, mapping NOT adjudicated")
        return 3
    mt, st = vals["trained"]
    mi, si = vals["init"]
    ms, ss = vals["shuffled"]
    effect = mt - max(mi, ms)
    noise = g * max(st, si, ss)
    if max(st, si, ss) > 0.5 * abs(effect) and abs(effect) > 0.0:
        print("VERDICT: D | not converged, UNKNOWN, raise sweeps and seeds only")
    elif mt >= mi + g * max(st, si) and mt >= ms + g * max(st, ss):
        print("VERDICT: A | claim survives at beta=%.2f, effect=%.4f gate=%.4f"
              % (br, effect, noise))
    elif abs(mt - ms) < g * max(st, ss):
        print("VERDICT: B | claim DEAD, effect indistinguishable from shuffled")
    else:
        print("VERDICT: C | claim DEAD, no ordering gain over init")

    print("RECEIPT | python=%s | cfg=%s | elapsed=%.1fs"
          % (sys.version.split()[0], CFG, time.time() - t_start))
    print("CEILING | single machine, n_hidden=%d, no finite-size scaling, "
          "no RSB claim, no LLM extrapolation" % CFG["n_hidden"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
