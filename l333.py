import numpy as np
import math
from itertools import product
from collections import defaultdict

MAGIC = 42

def base3_digit_cubes():
    cubes = []
    for coeffs in product([1, 2], repeat=9):
        M = np.array([[coeffs[0], coeffs[1], coeffs[2]],
                      [coeffs[3], coeffs[4], coeffs[5]],
                      [coeffs[6], coeffs[7], coeffs[8]]])
        det = int(round(np.linalg.det(M))) % 3
        if det == 0:
            continue
        cube = np.zeros((3, 3, 3), dtype=int)
        for a, b, c in product(range(3), repeat=3):
            phi = [(coeffs[3*i]*a + coeffs[3*i+1]*b + coeffs[3*i+2]*c) % 3
                   for i in range(3)]
            cube[a, b, c] = 1 + phi[0] + 3*phi[1] + 9*phi[2]
        if sorted(cube.flatten().tolist()) != list(range(1, 28)):
            continue
        ok = True
        for axis in range(3):
            if not np.all(cube.sum(axis=axis) == MAGIC):
                ok = False
                break
        if ok:
            cubes.append(cube)
    return cubes


def dft_mags(cube):
    F = np.fft.fftn(cube.astype(complex) - 14)
    return tuple(sorted(set(np.round(np.abs(F).flatten(), 4))))


cubes = base3_digit_cubes()
print("base-3 digit family cubes:", len(cubes))

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