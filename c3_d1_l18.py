"""C3-BG-001-D1 (v2) : L=18 comparability + H3 inter-layer convention control
Contract locked in RUN|C3-BG-001 section 9 + 10 (pre-registered, Kernel 19.2)
"""
import sys, time, json
import numpy as np

Q, L, ALPHA = 3, 18, 0.17
BETAS = (0.495, 0.500, 0.505, 0.50823, 0.515, 0.520, 0.525)
BETA_C = 0.50823
SEED = 369
N_EQUIL, N_MEAS, MEAS_EVERY, N_BLOCK = 10000, 30000, 7, 20
PAPER = 2.960
QUICK_CHI_BC = 2.1286
SHIFTS = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1))

if "--smoke" in sys.argv:
    BETAS = (0.505, BETA_C, 0.515)
    N_EQUIL, N_MEAS = 300, 900
def nsum(f, v):
    t = np.zeros(f.shape, dtype=np.int16)
    for dx, dy in SHIFTS:
        t += (np.roll(np.roll(f, dx, 0), dy, 1) == v)
    return t