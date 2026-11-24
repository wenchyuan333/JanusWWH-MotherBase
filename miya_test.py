import sys, math, random
BETA_C = 0.508230
T_CRIT = 1.0 / BETA_C
def load(p):
    return [float(x) for x in open(p).read().split()]
def synth(n=20000):
    random.seed(0)
    return [random.gauss(0,1) + (3 if random.random()<0.05 else 0) for _ in range(n)]
def obs(L, T):
    b = 1.0/T; m = max(L)
    ex = [math.exp(b*(x-m)) for x in L]; Z = sum(ex)
    p = [e/Z for e in ex]
    mean = sum(pi*x for pi,x in zip(p,L))
    var  = sum(pi*x*x for pi,x in zip(p,L)) - mean*mean
    return b*b*var, var, 1.0/sum(pi*pi for pi in p)   # 比熱C, Var, PR
L = load(sys.argv[1]) if len(sys.argv)>1 else synth()
rows = [(1.0+0.02*i,)+obs(L,1.0+0.02*i) for i in range(101)]
Tpk = max(rows, key=lambda r:r[1])[0]
print("T_crit=%.4f  C-peak=%.4f  |d|=%.4f" % (T_CRIT, Tpk, abs(Tpk-T_CRIT)))
for r in rows[::10]:
    print("T=%.2f  C=%.4f  Var=%.3f  PR=%.1f" % r)
