#!/usr/bin/env python3
# miya_4d_v2.py -- 4D SO(4) Precision Visualization
# Tesseract + 24-cell + Clifford Torus + Depth Sort
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
OUT=os.path.join(_g if os.path.isdir(_g) else HOME,"miya_4d_v2.gif")
BG="#01010A"; FRAMES=90; DPI=100

# ============================================================
# SO(4) BASIS ROTATIONS
# ============================================================
def R(i,j,theta,n=4):
    """Rotation matrix in plane (i,j) by angle theta."""
    M=np.eye(n)
    M[i,i]=M[j,j]=np.cos(theta)
    M[i,j]=-np.sin(theta)
    M[j,i]= np.sin(theta)
    return M

XY,XZ,XW,YZ,YW,ZW=((0,1),(0,2),(0,3),(1,2),(1,3),(2,3))

def clifford_left(a):  return R(*XW,a)@R(*YZ,a)
def clifford_right(a): return R(*XW,a)@R(*YZ,-a)

# ============================================================
# POLYTOPE DEFINITIONS
# ============================================================
def make_tesseract():
    V=np.array([[x,y,z,w]
        for x in [-1,1] for y in [-1,1]
        for z in [-1,1] for w in [-1,1]],dtype=float)
    E=[(i,j) for i in range(16) for j in range(i+1,16)
       if np.sum(V[i]!=V[j])==1]
    return V, E

def make_24cell():
    perm4=[(a,b,c,d) for a in range(4) for b in range(4)
           if b!=a for c in range(4) if c not in (a,b)
           for d in range(4) if d not in (a,b,c)]
    V=[]
    for s1 in (1,-1):
        for s2 in (1,-1):
            for i in range(4):
                for j in range(i+1,4):
                    v=np.zeros(4); v[i]=s1; v[j]=s2
                    V.append(v)
    V=np.unique(np.array(V),axis=0)
    E=[(i,j) for i in range(len(V)) for j in range(i+1,len(V))
       if abs(np.dot(V[i]-V[j],V[i]-V[j])-2.0)<1e-9]
    return V, E

# ============================================================
# CLIFFORD TORUS
# ============================================================
def clifford_torus(n=40):
    """Flat torus embedded in S^3 subset R^4:
    (cos a, sin a, cos b, sin b) / sqrt(2)
    """
    a=np.linspace(0,2*np.pi,n,endpoint=False)
    b=np.linspace(0,2*np.pi,n,endpoint=False)
    A,B=np.meshgrid(a,b)
    pts=np.stack([np.cos(A),np.sin(A),np.cos(B),np.sin(B)],axis=-1)/np.sqrt(2)
    return pts.reshape(-1,4)

CT_PTS=clifford_torus(36)

# ============================================================
# PROJECTION CHAIN: R^4 -> R^3 -> R^2
# ============================================================
def proj4(pts, d3=3.5, d2=4.0):
    w=pts[:,3]; s3=np.clip(d3/(d3-w),0.2,8.0)
    p3=pts[:,:3]*s3[:,None]
    z=p3[:,2]; s2=np.clip(d2/(d2-z),0.2,8.0)
    p2=p3[:,:2]*s2[:,None]
    depth=s3*s2  # combined perspective depth
    return p2, depth

# ============================================================
# COLOR BY W-DEPTH
# ============================================================
def edge_color(w_avg, depth_avg):
    # w > 0: cyan-white ("closer" in W)
    # w < 0: violet-indigo ("farther" in W)
    wn=np.clip((w_avg+2.0)/4.0,0,1)
    if w_avg>=0:
        r=0.4+0.6*wn; g=0.8+0.2*wn; b=1.0
    else:
        r=0.25*(1-wn); g=0.08+0.3*(1-wn); b=0.7+0.3*wn
    bright=np.clip(depth_avg/4.0,0.2,1.0)
    return (r*bright, g*bright, b*bright)

# ============================================================
# FRAME RENDERER
# ============================================================
def make_frame(t):
    ph=t*2.0*np.pi

    # --- compound rotation: 6 planes at irrational speed ratios ---
    # ensures non-periodic, space-filling orbit
    M=(  R(*XY, ph*0.700)
       @ R(*XZ, ph*0.450)
       @ R(*XW, ph*0.273 + clifford_left(ph*0.100)[0,3])  # XW with Clifford mixing
       @ R(*YZ, ph*0.550)
       @ R(*YW, ph*0.353)
       @ R(*ZW, ph*0.159))

    fig=plt.figure(figsize=(10,10),facecolor=BG)
    ax=fig.add_axes([0.04,0.04,0.92,0.88])
    ax.set_facecolor(BG)
    ax.set_xlim(-2.8,2.8); ax.set_ylim(-2.8,2.8)
    ax.set_aspect("equal"); ax.axis("off")

    # --- background stars ---
    rng=np.random.RandomState(42)
    sx=rng.uniform(-2.8,2.8,350); sy=rng.uniform(-2.8,2.8,350)
    ss=rng.uniform(0.1,2.5,350)
    twk=np.clip(0.4+0.6*np.sin(ph*1.8+sx*0.3+sy*0.4),0,1)
    sc=np.ones((350,4)); sc[:,3]=rng.uniform(0.1,0.5,350)*twk
    ax.scatter(sx,sy,s=ss,c=sc,linewidths=0,zorder=1)

    # --- Clifford torus (faint, 4D slice) ---
    ct=CT_PTS@M.T
    ct2,ct_d=proj4(ct)
    ct_w=ct[:,3]
    # subsample every 4th point as dots
    for i in range(0,len(ct2),4):
        wn=np.clip((ct_w[i]+1.5)/3.0,0,1)
        col=(0.2+0.4*wn, 0.1+0.2*wn, 0.5+0.4*wn, 0.12)
        ax.scatter([ct2[i,0]],[ct2[i,1]],s=3,c=[col],linewidths=0,zorder=2)

    # --- 24-cell (background layer) ---
    V24,E24=make_24cell()
    r24=(V24@M.T)
    p24,d24=proj4(r24*0.95)
    w24=r24[:,3]
    segs24=[]
    cols24=[]
    for e0,e1 in E24:
        ec=edge_color((w24[e0]+w24[e1])/2,(d24[e0]+d24[e1])/2)
        depth_avg=(d24[e0]+d24[e1])/2
        segs24.append([(p24[e0,0],p24[e0,1]),(p24[e1,0],p24[e1,1])])
        cols24.append((*ec,0.18))
    lc24=mc.LineCollection(segs24,colors=cols24,linewidths=0.5,zorder=3)
    ax.add_collection(lc24)

    # --- Tesseract (foreground, depth-sorted, glow) ---
    VT,ET=make_tesseract()
    rT=(VT@M.T)
    pT,dT=proj4(rT)
    wT=rT[:,3]

    # depth-sort edges
    edge_data=[(i,j,(dT[i]+dT[j])/2) for i,j in ET]
    edge_data.sort(key=lambda x:x[2])

    for e0,e1,depth_avg in edge_data:
        ec=edge_color((wT[e0]+wT[e1])/2, depth_avg)
        lw_base=max(0.3,min(2.5, depth_avg*0.6))
        for lw,al in ((lw_base*5,0.04),(lw_base*2.5,0.10),(lw_base,0.65),(lw_base*0.4,0.90)):
            ax.plot([pT[e0,0],pT[e1,0]],[pT[e0,1],pT[e1,1]],
                color=(*ec,al),linewidth=lw,solid_capstyle="round",zorder=4)

    # vertex halos
    for i,(px,py) in enumerate(pT):
        w=wT[i]; d=dT[i]
        vc=(0.7,1.0,1.0) if w>=0 else (0.5,0.2,1.0)
        s=np.clip(d*15,5,80)
        ax.scatter([px],[py],s=s,c=[[*vc,0.75]],linewidths=0,zorder=5)
        ax.scatter([px],[py],s=s*4,c=[[*vc,0.08]],linewidths=0,zorder=5)

    # --- rotation angle annotation ---
    angles=[
        ("XY",ph*0.700),("XZ",ph*0.450),("XW",ph*0.273),
        ("YZ",ph*0.550),("YW",ph*0.353),("ZW",ph*0.159)
    ]
    for idx,(plane,ang) in enumerate(angles):
        deg=ang%(2*np.pi)*180/np.pi
        ax.text(-2.65, 2.55-idx*0.22, f"{plane}: {deg:5.1f}deg",
            color=(0.4,0.7,0.5,0.6),fontsize=5.5,
            fontfamily="monospace",va="top",zorder=6)

    # title
    ax.text(0,-2.62,"SO(4) | Tesseract + 24-cell + Clifford Torus",
        color=(0.3,0.5,0.8,0.5),fontsize=6,ha="center",
        fontfamily="monospace",zorder=6)

    buf=io.BytesIO()
    fig.savefig(buf,format="png",dpi=DPI,facecolor=BG,bbox_inches="tight",pad_inches=0)
    buf.seek(0); img=Image.open(buf).copy(); buf.close(); plt.close(fig)
    return img

print("Rendering",FRAMES,"frames...")
frames=[]
for i in range(FRAMES):
    frames.append(make_frame(i/FRAMES))
    if (i+1)%15==0: print(" frame",i+1,"/",FRAMES)

print("Saving to:",OUT)
frames[0].save(OUT,save_all=True,append_images=frames[1:],
    duration=44,loop=0,optimize=False)
print("Saved.")

try:
    r=subprocess.run(["termux-media-scan",OUT],capture_output=True,timeout=20)
    print("Gallery:","OK" if r.returncode==0 else r.stderr.decode("utf-8","replace").strip())
except FileNotFoundError: print("termux-media-scan not found")
except Exception as e: print("Gallery error:",e)
print("Done.",OUT)