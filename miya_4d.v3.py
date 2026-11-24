#!/usr/bin/env python3
# miya_4d_v3.py  SO(4) x Schwarzschild x Potts
# Tesseract + 24-cell + Clifford Torus + Black Hole + Phase Field
# pip install numpy matplotlib Pillow
import sys, os, subprocess

def _chk():
    m=[]
    for p,i in (("numpy","numpy"),("matplotlib","matplotlib"),("PIL","Pillow")):
        try: __import__(p)
        except ImportError: m.append(i)
    return m
m=_chk()
if m: print("pip install"," ".join(m)); sys.exit(1)

import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.collections as mc
from PIL import Image
import io

HOME=os.path.expanduser("~")
_g=os.path.join(HOME,"storage","pictures")
OUT=os.path.join(_g if os.path.isdir(_g) else HOME,"miya_4d_v3.gif")
BG="#01010A"; FRAMES=90; DPI=100

# ── SO(4) rotation ──
def R(i,j,theta):
    M=np.eye(4); M[i,i]=M[j,j]=np.cos(theta)
    M[i,j]=-np.sin(theta); M[j,i]=np.sin(theta)
    return M
XY,XZ,XW,YZ,YW,ZW=(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)

# ── Polytopes ──
def make_tesseract():
    V=np.array([[x,y,z,w] for x in [-1,1] for y in [-1,1]
                for z in [-1,1] for w in [-1,1]],dtype=float)
    E=[(i,j) for i in range(16) for j in range(i+1,16)
       if np.sum(V[i]!=V[j])==1]
    return V,E

def make_24cell():
    V=[]
    for s1 in (1,-1):
        for s2 in (1,-1):
            for i in range(4):
                for j in range(i+1,4):
                    v=np.zeros(4); v[i]=s1; v[j]=s2; V.append(v)
    V=np.unique(np.array(V),axis=0)
    E=[(i,j) for i in range(len(V)) for j in range(i+1,len(V))
       if abs(np.dot(V[i]-V[j],V[i]-V[j])-2.0)<1e-9]
    return V,E

def clifford_torus(n=36):
    a=np.linspace(0,2*np.pi,n,endpoint=False)
    b=np.linspace(0,2*np.pi,n,endpoint=False)
    A,B=np.meshgrid(a,b)
    return np.stack([np.cos(A),np.sin(A),np.cos(B),np.sin(B)],axis=-1).reshape(-1,4)/np.sqrt(2)

CT_PTS=clifford_torus(36)

# ── Projection R^4 -> R^3 -> R^2 ──
def proj4(pts,d3=3.5,d2=4.0):
    w=pts[:,3]; s3=np.clip(d3/(d3-w),0.2,8.0)
    p3=pts[:,:3]*s3[:,None]; z=p3[:,2]
    s2=np.clip(d2/(d2-z),0.2,8.0)
    return p3[:,:2]*s2[:,None], s3*s2

# ── Schwarzschild lensing (radial, post-projection) ──
def lens(p2,r_s=0.20):
    r=np.sqrt(p2[:,0]**2+p2[:,1]**2)
    f=1.0+r_s/np.maximum(r,r_s*1.2)
    return p2/f[:,None]

# ── Potts model q=3 Metropolis ──
_RNG=np.random.RandomState(42)
_grid=_RNG.randint(0,3,(28,28))

def potts_step(g,beta=0.87,n=3):
    N=g.shape[0]
    for _ in range(n*N*N):
        i=_RNG.randint(N); j=_RNG.randint(N)
        nb=[g[(i-1)%N,j],g[(i+1)%N,j],g[i,(j-1)%N],g[i,(j+1)%N]]
        s=g[i,j]; s2=_RNG.randint(3)
        dE=sum(1 if x!=s2 else -1 for x in nb)-sum(1 if x!=s else -1 for x in nb)
        if dE<=0 or _RNG.random()<np.exp(-beta*dE): g[i,j]=s2
    return g

def potts_mag(g):
    c=np.bincount(g.ravel(),minlength=3); return c.max()/g.size

# pre-warm
for _ in range(25): _grid=potts_step(_grid)

# ── Edge color ──
def ecol(w_avg,depth):
    wn=np.clip((w_avg+2.0)/4.0,0,1)
    if w_avg>=0: rc=(0.4+0.6*wn,0.8+0.2*wn,1.0)
    else: rc=(0.25*(1-wn),0.08+0.3*(1-wn),0.7+0.3*wn)
    br=np.clip(depth/4.0,0.2,1.0)
    return tuple(c*br for c in rc)

# ── Frame renderer ──
def make_frame(t):
    global _grid
    ph=t*2.0*np.pi
    _grid=potts_step(_grid)
    mag=potts_mag(_grid)
    crystal=np.clip((mag-0.45)/0.4,0,1)
    r_s=0.18+0.10*(1-mag)

    M=(R(*XY,ph*0.700)@R(*XZ,ph*0.450)@R(*XW,ph*0.273)
      @R(*YZ,ph*0.550)@R(*YW,ph*0.353)@R(*ZW,ph*0.159))

    fig=plt.figure(figsize=(10,10),facecolor=BG)
    ax=fig.add_axes([0.04,0.04,0.92,0.88])
    ax.set_facecolor(BG); ax.set_xlim(-2.8,2.8); ax.set_ylim(-2.8,2.8)
    ax.set_aspect("equal"); ax.axis("off")

    # stars (lensed)
    rng=np.random.RandomState(42)
    sx=rng.uniform(-2.8,2.8,350); sy=rng.uniform(-2.8,2.8,350)
    ss=rng.uniform(0.1,2.5,350)
    sp=lens(np.stack([sx,sy],axis=1),r_s=r_s*0.7)
    twk=np.clip(0.4+0.6*np.sin(ph*1.8+sx*0.3+sy*0.4),0,1)
    sc=np.ones((350,4)); sc[:,3]=rng.uniform(0.1,0.5,350)*twk
    ax.scatter(sp[:,0],sp[:,1],s=ss,c=sc,linewidths=0,zorder=1)

    # accretion disk (LineCollection for speed)
    for di in range(5):
        rf=di/4; rd=0.28+rf*0.44
        th=np.linspace(0,2*np.pi,120)
        bright=0.15+0.55*(1+np.sin(th+ph*0.5+di*0.4))/2
        if rf<0.4: dc=(1.0,0.8,0.5)
        elif rf<0.7: dc=(0.9,0.5,0.2)
        else: dc=(0.5,0.2,0.8)
        segs=[[(rd*np.cos(th[k]),rd*np.sin(th[k])),
               (rd*np.cos(th[k+1]),rd*np.sin(th[k+1]))]
              for k in range(len(th)-1)]
        cols=[(*dc,(0.25+0.4*crystal)*bright[k]) for k in range(len(th)-1)]
        ax.add_collection(mc.LineCollection(segs,colors=cols,
            linewidths=0.8+rf*1.2,zorder=2))

    # Clifford torus (faint)
    ct=CT_PTS@M.T; ct2,_=proj4(ct); ct2=lens(ct2,r_s)
    ct_w=ct[:,3]
    for i in range(0,len(ct2),4):
        if ct2[i,0]**2+ct2[i,1]**2<0.06: continue
        wn=np.clip((ct_w[i]+1.5)/3.0,0,1)
        ax.scatter([ct2[i,0]],[ct2[i,1]],s=3,
            c=[[(0.2+0.4*wn,0.1+0.2*wn,0.5+0.4*wn,0.10+0.07*crystal)]],
            linewidths=0,zorder=3)

    # 24-cell
    V24,E24=make_24cell(); r24=V24@M.T; p24,d24=proj4(r24*0.95)
    p24=lens(p24,r_s); w24=r24[:,3]
    segs,cols=[],[]
    for e0,e1 in E24:
        mx,my=(p24[e0]+p24[e1])/2
        if mx**2+my**2<0.06: continue
        segs.append([(p24[e0,0],p24[e0,1]),(p24[e1,0],p24[e1,1])])
        cols.append((*ecol((w24[e0]+w24[e1])/2,(d24[e0]+d24[e1])/2),
                     0.14+0.09*crystal))
    ax.add_collection(mc.LineCollection(segs,colors=cols,linewidths=0.5,zorder=4))

    # Tesseract
    VT,ET=make_tesseract(); rT=VT@M.T; pT,dT=proj4(rT)
    pT=lens(pT,r_s); wT=rT[:,3]
    ed=sorted([(i,j,(dT[i]+dT[j])/2) for i,j in ET],key=lambda x:x[2])
    for e0,e1,da in ed:
        mx,my=(pT[e0]+pT[e1])/2; mr=np.sqrt(mx**2+my**2)
        if mr<0.23: continue
        ec=ecol((wT[e0]+wT[e1])/2,da)
        ba=0.55+0.30*crystal
        lw=max(0.4,min(2.8,da*0.65))
        # gravitational redshift near horizon
        if mr<0.65:
            rs=np.clip((mr-0.23)/0.42,0,1)
            ec=(ec[0]*0.5+0.5*rs,ec[1]*rs,ec[2]*rs); ba*=rs
        for lw2,al in ((lw*5,0.04),(lw*2.5,0.10),(lw,ba),(lw*0.4,min(ba*1.3,0.95))):
            ax.plot([pT[e0,0],pT[e1,0]],[pT[e0,1],pT[e1,1]],
                color=(*ec,al),linewidth=lw2,solid_capstyle="round",zorder=5)
    for i,(px,py) in enumerate(pT):
        if px**2+py**2<0.053: continue
        vc=(0.7,1.0,1.0) if wT[i]>=0 else (0.5,0.2,1.0)
        s=np.clip(dT[i]*15,5,80)*(0.6+0.4*crystal)
        ax.scatter([px],[py],s=s,c=[[*vc,0.75]],linewidths=0,zorder=6)
        ax.scatter([px],[py],s=s*4,c=[[*vc,0.08]],linewidths=0,zorder=6)

    # photon sphere
    th=np.linspace(0,2*np.pi,300)
    for rr,al,lw in ((0.30,0.55,1.4),(0.325,0.20,0.8),(0.35,0.08,0.5)):
        ax.plot(rr*np.cos(th+ph*0.05),rr*np.sin(th+ph*0.05),
            color=(0.8,0.7,1.0,al),linewidth=lw,zorder=7)

    # corona + event horizon
    for rr,al in ((0.34,0.12),(0.28,0.22),(0.24,0.35)):
        cc=(1.0,0.6+0.3*np.sin(ph*2),0.3)
        ax.add_patch(plt.Circle((0,0),rr,color=cc,alpha=al,zorder=8))
    ax.add_patch(plt.Circle((0,0),0.22,color="#000000",zorder=9))
    ax.scatter([0],[0],s=15,c=[[1,1,1,0.9]],linewidths=0,zorder=10)

    # HUD
    for idx,(pl,ang) in enumerate([("XY",ph*0.700),("XZ",ph*0.450),
            ("XW",ph*0.273),("YZ",ph*0.550),("YW",ph*0.353),("ZW",ph*0.159)]):
        ax.text(-2.65,2.55-idx*0.22,f"{pl}: {ang%(2*np.pi)*180/np.pi:5.1f}",
            color=(0.4,0.7,0.5,0.6),fontsize=5.5,fontfamily="monospace",
            va="top",zorder=11)
    bw=1.2*crystal
    ax.barh(-2.62,bw,height=0.08,left=-0.6,color=(0.4,0.8,0.6,0.5),zorder=11)
    ax.text(-0.6,-2.72,f"Potts m={mag:.2f}",
        color=(0.4,0.7,0.5,0.5),fontsize=5,fontfamily="monospace",zorder=11)
    ax.text(0,-2.62,"SO(4) x Schwarzschild x Potts q=3",
        color=(0.3,0.5,0.8,0.5),fontsize=6,ha="center",
        fontfamily="monospace",zorder=11)

    buf=io.BytesIO()
    fig.savefig(buf,format="png",dpi=DPI,facecolor=BG,bbox_inches="tight",pad_inches=0)
    buf.seek(0); img=Image.open(buf).copy(); buf.close(); plt.close(fig)
    return img

print("Rendering",FRAMES,"frames...")
frames=[]
for i in range(FRAMES):
    frames.append(make_frame(i/FRAMES))
    if (i+1)%15==0:
        print(f"  frame {i+1}/{FRAMES}  Potts m={potts_mag(_grid):.3f}")

print("Saving to:",OUT)
frames[0].save(OUT,save_all=True,append_images=frames[1:],
    duration=44,loop=0,optimize=False)
print("Saved.")

try:
    r=subprocess.run(["termux-media-scan",OUT],capture_output=True,timeout=20)
    print("Gallery:","OK" if r.returncode==0 else r.stderr.decode().strip())
except FileNotFoundError: print("termux-media-scan not found")
except Exception as e: print("Gallery error:",e)
print("Done.",OUT)