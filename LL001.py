import numpy as np
from time import time
from collections import defaultdict

MAGIC = 42

def enumerate_magic_cubes():
    cube = np.full((3, 3, 3), -1, dtype=int)
    used = [False] * 28
    results = []

    def recurse(idx):
        if idx == 27:
            results.append(cube.copy())
            return
        a, b, c = idx // 9, (idx // 3) % 3, idx % 3
        forced = []
        if c == 2:
            forced.append(MAGIC - cube[a, b, 0] - cube[a, b, 1])
        if b == 2:
            forced.append(MAGIC - cube[a, 0, c] - cube[a, 1, c])
        if a == 2:
            forced.append(MAGIC - cube[0, b, c] - cube[1, b, c])
        if forced:
            if len(set(forced)) != 1:
                return
            v = forced[0]
            if not (1 <= v <= 27 and not used[v]):
                return
            cube[a, b, c] = v
            used[v] = True
            recurse(idx + 1)
            used[v] = False
            cube[a, b, c] = -1
            return
        for v in range(1, 28):
            if used[v]:
                continue
            cube[a, b, c] = v
            used[v] = True
            recurse(idx + 1)
            used[v] = False
            cube[a, b, c] = -1

    t0 = time()
    recurse(0)
    print("found", len(results), "cubes in", round(time() - t0, 1), "s")
    return results


def dft_mags(cube):
    F = np.fft.fftn(cube.astype(complex) - 14)
    return tuple(sorted(set(np.round(np.abs(F).flatten(), 4))))


cubes = enumerate_magic_cubes()

groups = defaultdict(list)
for c in cubes:
    groups[dft_mags(c)].append(c)

print("distinct DFT signatures:", len(groups))
sqrt3 = np.sqrt(3)
for magset, cs in sorted(groups.items(), key=lambda x: -len(x[1])):
    labels = []
    for m in magset:
        if m < 0.001:
            labels.append("0")
        else:
            r = m / sqrt3
            if abs(r - round(r)) < 0.01:
                labels.append(str(int(round(r))) + "*sqrt3")
            else:
                labels.append(str(round(m, 3)))
    print(" ", len(cs), "cubes ->", labels)