import numpy as np
try:
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    HAVE_MPL = True
except Exception:
    HAVE_MPL = False

# ---- Chua ----
A, B, M0, M1 = 15.6, 28.0, -1.143, -0.714
def f(x): return M1*x + 0.5*(M0-M1)*(abs(x+1)-abs(x-1))
def dv(s,a=A):
    x,y,z=s; return np.array([a*(y-x-f(x)), x-y+z, -B*y])
def rk4(s,dt,a=A):
    k1=dv(s,a);k2=dv(s+0.5*dt*k1,a);k3=dv(s+0.5*dt*k2,a);k4=dv(s+dt*k3,a)
    return s+(dt/6)*(k1+2*k2+2*k3+k4)
def sim(n=200000,dt=0.005):
    s=np.array([0.7,0,0]);o=np.empty((n,3))
    for i in range(n): o[i]=s; s=rk4(s,dt)
    return o

# ---- Sethares/Plomp-Levelt dissonance ----
def d_pair(f1,f2,a1=1,a2=1):
    b1,b2,xs,s1,s2=3.5,5.75,0.24,0.0207,18.96
    s=xs/(s1*min(f1,f2)+s2); df=abs(f2-f1)
    return a1*a2*(np.exp(-b1*s*df)-np.exp(-b2*s*df))
def tone(f0,p):                       # partials at f0*p[i], amps 1/(i+1)
    return [(f0*pi, 1.0/(i+1)) for i,pi in enumerate(p)]
def dissonance(t1,t2):
    return sum(d_pair(a,b,x,y) for a,x in t1 for b,y in t2)
def curve(base=220.0, p=(1,2,3,4,5,6), lo=195.0, hi=579.0, n=500):
    t1=tone(base,p); fs=np.linspace(lo,hi,n)
    return fs, np.array([dissonance(t1, tone(fx,p)) for fx in fs])

# ---- ADSR ----
def adsr(n, a=0.1,d=0.15,s=0.7,r=0.25):
    e=np.ones(n); na,nd,nr=int(a*n),int(d*n),int(r*n); ns=n-na-nd-nr
    e[:na]=np.linspace(0,1,na)
    e[na:na+nd]=np.linspace(1,s,nd)
    e[na+nd:na+nd+ns]=s
    e[na+nd+ns:]=np.linspace(s,0,nr)
    return e

traj=sim()
# 諧和(整數倍) vs 非諧(2.13/3.57 漂移)兩條不協和度曲線
fs, dc_harm = curve(p=(1,2,3,4,5,6))
fs, dc_inh  = curve(p=(1,2.13,3.57,4.88,6.02))
env=adsr(1000)

print("[chua] traj pts:", len(traj))
print("[disson] harmonic min at ratio %.3f" % (fs[np.argmin(dc_harm)]/220))
print("[disson] inharmonic min at ratio %.3f" % (fs[np.argmin(dc_inh)]/220))

if HAVE_MPL:
    fig=plt.figure(figsize=(15,5))
    ax1=fig.add_subplot(1,3,1)
    ax1.plot(traj[:,0],traj[:,2],lw=0.2,color="teal")
    ax1.set_title("Chua double-scroll (x-z)")
    ax2=fig.add_subplot(1,3,2)
    ax2.plot(env,color="darkorange"); ax2.set_title("ADSR envelope"); ax2.set_ylim(0,1.05)
    ax3=fig.add_subplot(1,3,3)
    ax3.plot(fs/220, dc_harm, color="royalblue", label="harmonic 1,2,3..")
    ax3.plot(fs/220, dc_inh,  color="crimson",  label="inharmonic 2.13/3.57")
    ax3.set_title("Sensory dissonance vs ratio"); ax3.set_xlabel("f2/220"); ax3.legend()
    plt.tight_layout(); plt.savefig("chua_muro.png",dpi=130)
    print("[out] saved chua_muro.png")
else:
    np.savetxt("dissonance.csv", np.column_stack([fs, dc_harm, dc_inh]), delimiter=",")
    print("[out] no matplotlib; saved dissonance.csv")
