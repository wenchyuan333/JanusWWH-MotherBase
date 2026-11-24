#!/usr/bin/env python3
"""miya_viz.py v1.2
Riemann x Collatz(3n+1) x Collatz(3n-1 Three Universes) x Golden Spiral x Twin Flame
Requires: pip install numpy matplotlib Pillow
"""
import sys, os, subprocess

def _check():
    m = []
    for p, i in (("numpy","numpy"),("matplotlib","matplotlib"),("PIL","Pillow")):
        try: __import__(p)
        except ImportError: m.append(i)
    return m
m = _check()
if m:
    print("Run: pip install", " ".join(m)); sys.exit(1)

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from matplotlib.colors import Normalize
from PIL import Image
import io

HOME = os.path.expanduser("~")
_gal = os.path.join(HOME, "storage", "pictures")
OUT  = os.path.join(_gal if os.path.isdir(_gal) else HOME, "miya_viz.gif")

BG     = "#030308"
FRAMES = 60
DPI    = 100
PHI    = (1.0 + 5.0**0.5) / 2.0
GA     = 2.0 * np.pi / PHI**2   # golden angle

RZ = [14.135, 21.022, 25.011, 30.425, 32.935,
      37.586, 40.919, 43.327, 48.005, 49.774]

def rgba(c, a):
    r,g,b,_ = mcolors.to_rgba(c)
    return (r, g, b, float(np.clip(a,0,1)))

# ── Collatz 3n+1 ──
def cz(n):
    s=[n]
    while n!=1: n=n//2 if n%2==0 else 3*n+1; s.append(n)
    return s

# ── Collatz 3n-1 ──
_AM = {1,5,17}
_AC = {1:(1.0,0.30,0.30,0.28), 5:(0.30,1.0,0.50,0.28),
       17:(0.40,0.60,1.0,0.28), 0:(0.7,0.7,0.7,0.12)}
def cz_m(n, S=800):
    s,seen=[n],{n}
    for _ in range(S):
        n = n//2 if n%2==0 else 3*n-1
        if n<=0: break
        s.append(n)
        if n in _AM: return s,n
        if n in seen: return s,0
        seen.add(n)
    return s,0

print("Precomputing sequences...")
SEQ  = {n:cz(n)   for n in range(1,151)}
SEQM = {}; ATTR = {}
for n in range(1,151):
    s,a = cz_m(n); SEQM[n]=s; ATTR[n]=a
ML  = max(len(v) for v in SEQ.values())

def frame(t):
    ph = t*2.0*np.pi
    fig = plt.figure(figsize=(9,9), facecolor=BG)
    ax  = fig.add_axes([0,0,1,1])
    ax.set_facecolor(BG); ax.set_xlim(-1.06,1.06)
    ax.set_ylim(-1.06,1.06); ax.set_aspect("equal"); ax.axis("off")

    # L1 Golden spiral
    N=600; g=cm.YlOrRd
    idx=np.arange(N,dtype=float)
    rs=(idx/N)**0.52; th=idx*GA+ph*0.25
    xs=rs*np.cos(th); ys=rs*np.sin(th)
    sz=np.maximum(1.5,9.0*rs*(1-rs*0.25))
    bc=g(0.25+0.75*rs); bc[:,3]=0.55+0.45*rs
    sl=slice(0,N,2)
    ax.scatter(xs[sl],ys[sl],s=sz[sl],c=bc[sl],edgecolors="none",zorder=2)

    # L2 Collatz 3n+1 (inner, plasma)
    nm=Normalize(1,ML); cp=cm.plasma
    for n in range(1,151,2):
        s=SEQ[n]; cl=rgba(cp(nm(len(s))),0.20)
        ba=n*2.0*np.pi/PHI+ph*0.12
        th2=[ba+i*0.052 for i in range(len(s))]
        top=float(np.log1p(max(s)))
        rv=[np.log1p(v)/top*0.42 for v in s]   # inner 0-0.42
        ax.plot([r*np.cos(a) for r,a in zip(rv,th2)],
                [r*np.sin(a) for r,a in zip(rv,th2)],
                color=cl,linewidth=0.45,zorder=3)

    # L2b Collatz 3n-1 (outer, attractor-colored)
    for n in range(1,151,2):
        s=SEQM[n]; cl=_AC.get(ATTR[n],_AC[0])
        ba=n*2.0*np.pi/PHI+ph*0.08+np.pi*0.618
        th3=[ba+i*0.045 for i in range(len(s))]
        top=float(np.log1p(max(s))) if max(s)>0 else 1.0
        rv=[0.45+np.log1p(v)/top*0.50 for v in s]  # outer 0.45-0.95
        ax.plot([r*np.cos(a) for r,a in zip(rv,th3)],
                [r*np.sin(a) for r,a in zip(rv,th3)],
                color=cl,linewidth=0.55,zorder=3)

    # L3 Riemann rings
    th4=np.linspace(0,2*np.pi,300)
    cx=np.cos(th4); cy=np.sin(th4)
    for i,z in enumerate(RZ):
        rb=0.14+(z-14.0)/36.0*0.76
        r=rb+0.014*np.sin(ph*(i+1)*0.65)
        br=0.45+0.55*np.sin(ph*1.2+i*0.9)
        rc=cm.cool(0.15+0.7*(i/len(RZ)))
        for gw,lw,ga in ((1.0,0.6,0.35),(0.6,1.2,0.15),(0.3,2.0,0.06)):
            rr=r+0.009*(1-gw)
            ax.plot(rr*cx,rr*cy,color=rgba(rc,ga*br),linewidth=lw,zorder=4)

    # L4 Twin Flames
    T=3.5; NT=700
    tt=np.linspace(0,T*2*np.pi,NT)
    sp=0.11+0.07*np.sin(ph*0.75)
    for sd,fc,off in ((1,cm.autumn,0.0),(-1,cm.winter,np.pi)):
        rt=tt/(T*2*np.pi)*0.88
        ag=tt+ph*0.45+off
        xt=rt*np.cos(ag)-sd*sp*np.sin(ag)
        yt=rt*np.sin(ag)+sd*sp*np.cos(ag)
        fc2=[fc(i/NT) for i in range(NT)]
        for j in range(0,NT-1,2):
            ax.plot([xt[j],xt[j+1]],[yt[j],yt[j+1]],
                    color=rgba(fc2[j],0.45+0.50*(j/NT)),
                    linewidth=1.3,solid_capstyle="round",zorder=5)

    # Center glow
    for rg,ag in ((0.035,0.9),(0.07,0.45),(0.14,0.18),(0.25,0.07)):
        ax.add_patch(plt.Circle((0,0),rg,color="white",alpha=ag,zorder=6))

    buf=io.BytesIO()
    fig.savefig(buf,format="png",dpi=DPI,facecolor=BG)
    buf.seek(0); img=Image.open(buf).copy(); buf.close(); plt.close(fig)
    return img

print("Rendering",FRAMES,"frames...")
frames=[]
for i in range(FRAMES):
    frames.append(frame(i/FRAMES))
    if (i+1)%10==0: print("  frame",i+1,"/",FRAMES)

print("Saving to:",OUT)
frames[0].save(OUT,save_all=True,append_images=frames[1:],
               duration=48,loop=0,optimize=False)
print("Saved.")

try:
    r=subprocess.run(["termux-media-scan",OUT],capture_output=True,timeout=20)
    print("Gallery:","OK" if r.returncode==0 else r.stderr.decode("utf-8","replace").strip())
except FileNotFoundError:
    print("termux-media-scan not found. pkg install termux-api")
except Exception as e:
    print("Gallery error:",e)

print("Done.",OUT)