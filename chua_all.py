import numpy as np
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    HAVE_MPL = True
except Exception:
    HAVE_MPL = False

ALPHA, BETA = 15.6, 28.0
M0, M1 = -1.143, -0.714

def chua_diode(x):
    return M1*x + 0.5*(M0 - M1)*(abs(x + 1.0) - abs(x - 1.0))

def deriv(s, alpha=ALPHA, beta=BETA):
    x, y, z = s
    return np.array([alpha*(y - x - chua_diode(x)), x - y + z, -beta*y])

def rk4(s, dt, **kw):
    k1 = deriv(s, **kw); k2 = deriv(s + 0.5*dt*k1, **kw)
    k3 = deriv(s + 0.5*dt*k2, **kw); k4 = deriv(s + dt*k3, **kw)
    return s + (dt/6.0)*(k1 + 2*k2 + 2*k3 + k4)

def simulate(s0=(0.7, 0.0, 0.0), dt=0.005, n=200000, **kw):
    s = np.array(s0, float); out = np.empty((n, 3))
    for i in range(n):
        out[i] = s; s = rk4(s, dt, **kw)
    return out

def largest_lyapunov(dt=0.005, n=100000, d0=1e-9, **kw):
    s = np.array([0.7, 0.0, 0.0]); sp = s + np.array([d0, 0., 0.])
    acc, cnt = 0.0, 0
    for _ in range(n):
        s = rk4(s, dt, **kw); sp = rk4(sp, dt, **kw)
        d = np.linalg.norm(sp - s)
        if d > 0:
            acc += np.log(d/d0); cnt += 1
            sp = s + (sp - s)*(d0/d)
    return acc/(cnt*dt)

def bifurcation(a_lo=8.0, a_hi=16.0, na=400, dt=0.005, n=60000, burn=40000):
    A, X = [], []
    for a in np.linspace(a_lo, a_hi, na):
        s = np.array([0.7, 0.0, 0.0]); xs = np.empty(n)
        for i in range(n):
            s = rk4(s, dt, alpha=a); xs[i] = s[0]
        xt = xs[burn:]
        pk = xt[1:-1][(xt[1:-1] > xt[:-2]) & (xt[1:-1] > xt[2:])]
        A.extend([a]*len(pk)); X.extend(pk.tolist())
    return np.array(A), np.array(X)

def jacobian(F, v, h=1e-6):
    n = len(v); f0 = F(v); J = np.zeros((n, n))
    for j in range(n):
        dv = v.copy(); dv[j] += h; J[:, j] = (F(dv) - f0)/h
    return J

def min_absdet(F, lo, hi, grid=15):
    axs = [np.linspace(lo[i], hi[i], grid) for i in range(len(lo))]
    worst, where = np.inf, None
    for x in axs[0]:
        for y in axs[1]:
            for z in axs[2]:
                d = abs(np.linalg.det(jacobian(F, np.array([x, y, z]))))
                if d < worst: worst, where = d, (x, y, z)
    return worst, where

def F_demo(v):
    x, y, z = v
    return np.array([x + 0.1*np.sin(y), y + 0.1*np.sin(z), z + 0.1*np.sin(x)])

traj = simulate()
lam = largest_lyapunov()
print("[chaos] lambda_max approx %+.4f  (%s)" % (lam, "chaos" if lam > 0 else "non-chaos"))

m, loc = min_absdet(F_demo, [-3, -3, -3], [3, 3, 3])
tag = "no-fold" if m > 1e-9 else "FOLD FOUND"
print("[inject] min|detJ| = %.3e at %s -> %s" % (m, tuple(round(c, 2) for c in loc), tag))

print("[bifurc] scanning...")
A, X = bifurcation()

if HAVE_MPL:
    fig = plt.figure(figsize=(12, 5))
    ax1 = fig.add_subplot(1, 2, 1)
    ax1.plot(traj[:, 0], traj[:, 2], lw=0.2, color="teal")
    ax1.set_title("Chua double-scroll (x-z)"); ax1.set_xlabel("x"); ax1.set_ylabel("z")
    ax2 = fig.add_subplot(1, 2, 2)
    ax2.plot(A, X, ",", color="black", alpha=0.5)
    ax2.set_title("Bifurcation vs alpha"); ax2.set_xlabel("alpha"); ax2.set_ylabel("x peaks")
    plt.tight_layout(); plt.savefig("chua_all.png", dpi=130)
    print("[out] saved chua_all.png")
else:
    np.savetxt("chua_traj.csv", traj, delimiter=",")
    np.savetxt("chua_bifurc.csv", np.column_stack([A, X]), delimiter=",")
    print("[out] no matplotlib; saved chua_traj.csv and chua_bifurc.csv")
