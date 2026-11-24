import numpy as np
import math
from itertools import product
from collections import defaultdict

D = 4        # dimension
N = 3        # each side length
SIZE = N**D  # 81
MAGIC = N * (SIZE + 1) // 2  # 123 for 3^4
CENTER = (SIZE + 1) / 2      # 41

def base3_digit_hypercubes():
    cubes = []
    # coefficient matrix is D x D, entries in {1, 2}
    for coeffs in product([1, 2], repeat=D*D):
        M = np.array(coeffs).reshape((D, D))
        det = int(round(np.linalg.det(M))) % 3
        if det == 0:
            continue
        cube = np.zeros((N,)*D, dtype=int)
        for idx in product(range(N), repeat=D):
            phi = [sum(M[i][j]*idx[j] for j in range(D)) % 3 for i in range(D)]
            val = 1 + sum(phi[i] * (N**i) for i in range(D))
            cube[idx] = val
        if sorted(cube.flatten().tolist()) != list(range(1, SIZE+1)):
            continue
        ok = True
        for axis in range(D):
            if not np.all(cube.sum(axis=axis) == MAGIC):
                ok = False
                break
        if ok:
            cubes.append(cube)
    return cubes


def dft_mags(cube):
    F = np.fft.fftn(cube.astype(complex) - CENTER)
    return tuple(sorted(set(np.round(np.abs(F).flatten(), 4))))


cubes = base3_digit_hypercubes()
print("4D base-3 digit family cubes:", len(cubes))
print("expected magic sum:", MAGIC)

groups = defaultdict(int)
for c in cubes:
    groups[dft_mags(c)] += 1

print("distinct DFT signatures:", len(groups))
sqrt3 = math.sqrt(3)
for magset, count in sorted(groups.items(), key=lambda x: -x[1]):
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
    print(" ", count, "cubes ->", labels)