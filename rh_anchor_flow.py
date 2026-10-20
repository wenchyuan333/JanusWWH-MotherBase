#!/usr/bin/env python3
# rh_anchor_flow.py v1.0 | anchor-flow-backpressure on the RH side
# ANCHOR: first 40 zeta-zero heights (externally verified table, Platt-grade)
# FLOW  : prime staircase psi(x) from pure arithmetic  vs  spectral sum from zeros
# JUDGE : two independent constructions must agree within pre-declared band
# CLAIM : verifies the explicit-formula TRANSLATION only; zeros are input anchors;
#         no RH evidence is produced or claimed
import math

ZEROS = [14.134725142, 21.022039639, 25.010857580, 30.424876126, 32.935061588,
         37.586178159, 40.918719012, 43.327073281, 48.005150881, 49.773832478,
         52.970321478, 56.446247697, 59.347044003, 60.831778525, 65.112544048,
         67.079810529, 69.546401711, 72.067157674, 75.704690699, 77.144840069,
         79.337375020, 82.910380854, 84.735492981, 87.425274613, 88.809111208,
         92.491899271, 94.651344041, 95.870634228, 98.831194218, 101.317851006,
         103.725538040, 105.446623052, 107.168611184, 111.029535543, 111.874659177,
         114.320220915, 116.226680321, 118.790782866, 121.370125002, 122.946829294]

def psi_staircase(x):
    xs = int(math.floor(x))
    sieve = [True] * (xs + 1)
    sieve[0] = False
    if xs >= 1:
        sieve[1] = False
    p = 2
    while p * p <= xs:
        if sieve[p]:
            for m in range(p * p, xs + 1, p):
                sieve[m] = False
        p += 1
    total = 0.0
    for n in range(2, xs + 1):
        if sieve[n]:
            lp = math.log(n)
            pk = n
            while pk <= x:
                total += lp
                pk *= n
    return total

def psi_spectral(x):
    acc = 0.0
    lx = math.log(x)
    sx = math.sqrt(x)
    for g in ZEROS:
        rho_abs = math.sqrt(0.25 + g * g)
        theta = math.atan2(g, 0.5)
        acc += 2.0 * sx * math.cos(g * lx - theta) / rho_abs
    return x - math.log(2.0 * math.pi) - 0.5 * math.log(1.0 - 1.0 / (x * x)) - acc

def main():
    print("rh_anchor_flow v1.0 | anchors: first 40 zero heights (Platt-verified table)")
    print("formula: psi(x) = x - sum x^rho/rho - ln(2pi) - 0.5*ln(1-1/x^2)")
    print("band: |staircase - spectral| <= 1.5 at sample points (pre-declared)")
    print()
    samples = [5.5, 8.5, 16.5, 27.5, 32.5, 49.5, 64.5, 81.5, 100.5]
    worst = 0.0
    tot = 0.0
    for x in samples:
        a = psi_staircase(x)
        b = psi_spectral(x)
        d = a - b
        tot += abs(d)
        if abs(d) > worst:
            worst = abs(d)
        print("  x=%6.1f  primes=%8.3f  spectral=%8.3f  diff=%+.3f" % (x, a, b, d))
    print("mean |diff| = %.3f ; worst |diff| = %.3f" % (tot / len(samples), worst))
    if worst <= 1.5:
        print("VERDICT: SPECTRAL LOCK - zero spectrum back-pressures the prime staircase into shape")
    else:
        print("VERDICT: outside band; extend zero table or check code")
    print("NOTE: samples at half-integers (staircase jumps live at prime powers)")

main()