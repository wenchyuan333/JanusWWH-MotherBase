import math


def umds_five_step_sim():
    A, M, C = 10.0, 5.0, 2.0
    eta, q, dt = 0.6, 2.0, 1.0
    R0 = A + M + C
    for _ in range(5):
        Fin = 0.2 * A
        Fout = 0.1 * M
        Fsink = 0.05 * C
        A, M, C = (
            A + dt * (q - Fin),
            M + dt * (eta * Fin - Fout),
            C + dt * ((1 - eta) * Fin + Fout - Fsink),
        )
    R5 = A + M + C
    return {"A": A, "M": M, "C": C, "R0": R0, "R5": R5, "dR": R5 - R0}


def miya4096_codec_fixture():
    qA, qM, qC, qEta = 5, 2, 7, 1
    z = qA + 8 * qM + 64 * qC + 512 * qEta
    decoded = (z % 8, (z // 8) % 8, (z // 64) % 8, (z // 512) % 8)
    return {"z": z, "decoded": decoded, "match": decoded == (qA, qM, qC, qEta)}


def apportion(weights, total_bits):
    raw = [w * total_bits for w in weights]
    floors = [int(math.floor(x)) for x in raw]
    remainder = total_bits - sum(floors)
    order = sorted(range(len(weights)), key=lambda i: raw[i] - floors[i], reverse=True)
    bits = floors[:]
    for i in range(remainder):
        bits[order[i]] += 1
    return bits


def qual_branch_fixture():
    Q = (0.7963, 0.0654, 0.1383)
    B = 12
    b_identity = apportion(Q, B)
    r_identity = [2 ** b for b in b_identity]
    exps = [math.exp(x) for x in Q]
    s = sum(exps)
    omega_softmax = tuple(e / s for e in exps)
    b_softmax = apportion(omega_softmax, B)
    r_softmax = [2 ** b for b in b_softmax]
    return {
        "b_identity": b_identity, "r_identity": r_identity,
        "omega_softmax": omega_softmax, "b_softmax": b_softmax, "r_softmax": r_softmax,
    }


def sys002_partition_entropy():
    counts = {"N": 4, "E": 3, "S": 3, "W": 2}
    total = sum(counts.values())
    p = [c / total for c in counts.values()]
    H_Q = -sum(pi * math.log2(pi) for pi in p if pi > 0)
    H_max = math.log2(len(counts))
    return {"p": p, "H_Q": H_Q, "H_max": H_max, "ratio": H_Q / H_max}


print("=== [1] UMDS five-step discrete simulation (Forward Euler) ===")
r1 = umds_five_step_sim()
print(f"final A={r1['A']:.4f} M={r1['M']:.4f} C={r1['C']:.4f}")
print(f"R0={r1['R0']:.4f} R5={r1['R5']:.4f} dR={r1['dR']:.4f}")

print()
print("=== [2] MIYA-4096 codec fixture ===")
r2 = miya4096_codec_fixture()
print(f"z={r2['z']} decoded={r2['decoded']} match={r2['match']}")

print()
print("=== [3] QUAL Q->Omega branch fixture ===")
r3 = qual_branch_fixture()
print(f"identity: b={r3['b_identity']} r={r3['r_identity']}")
print(f"softmax:  omega={tuple(round(x, 4) for x in r3['omega_softmax'])} b={r3['b_softmax']} r={r3['r_softmax']}")

print()
print("=== [4] SYS-002 partition entropy ===")
r4 = sys002_partition_entropy()
print(f"p={[round(x, 4) for x in r4['p']]} H_Q={r4['H_Q']:.4f} H_max={r4['H_max']:.4f} ratio={r4['ratio']:.4f}")

print()
all_ok = (
    abs(r1["dR"] - 8.8968) < 0.01
    and r2["match"]
    and r3["b_identity"] == [9, 1, 2]
    and r3["b_softmax"] == [6, 3, 3]
    and abs(r4["ratio"] - 0.9796) < 0.001
)
print(f"=== SUMMARY: formal_model_fixture_all_passed={all_ok} ===")
