#!/usr/bin/env python3
# miya_4d_v2.py  --  SO(4) 4D Visualization
# pip install numpy matplotlib Pillow  then  python3 miya_4d_v2.py
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

def R(i,j,theta):
    M=np.eye(4)
    M[i,i]=M[j,j]=np.cos(theta)
    M[i,j]=-np.sin(theta); M[j,i]=np.sin(theta)
    return M

XY,XZ,XW,YZ,YW,ZW=(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)

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
       if abs(float(np.dot(V[i]-V[j],V[i]-V[j]))-2.0)<1e-9]
    return V,E

def clifford_torus(n=36):
    a=np.linspace(0,2*np.pi,n,endpoint=False)
    b=np.linspace(0,2*np.pi,n,endpoint=False)
    A,B=np.meshgrid(a,b)
    pts=np.stack([np.cos(A),np.sin(A),np.cos(B),np.sin(B)],axis=-1)/np.sqrt(2)
    return pts.reshape(-1,4)

CT=clifford_torus()
VT,ET=make_tesseract()
V24,E24=make_24cell()

def proj4(pts,d3=3.5,d2=4.0):
    w=pts[:,3]; s3=np.clip(d3/(d3-w),0.2,8.0)
    p3=pts[:,:3]*s3[:,None]
    z=p3[:,2]; s2=np.clip(d2/(d2-z),0.2,8.0)
    p2=p3[:,:2]*s2[:,None]
    return p2, s3*s2

def ecol(w_avg,depth):
    wn=np.clip((w_avg+2.0)/4.0,0,1)
    if w_avg>=0: r=0.4+0.6*wn; g=0.8+0.2*wn; b=1.0
    else: r=0.25*(1-wn); g=0.08+0.3*(1-wn); b=0.7+0.3*wn
    br=np.clip(depth/4.0,0.2,1.0)
    return (r*br, g*br, b*br)

RNG=np.random.RandomState(42)
SX=RNG.uniform(-2.8,2.8,350); SY=RNG.uniform(-2.8,2.8,350)
SS=RNG.uniform(0.1,2.5,350); SA=RNG.uniform(0.1,0.5,350)

def make_frame(t):
    ph=t*2*np.pi
    # 6-plane composite rotation with near-irrational speed ratios
    M=(R(*XY,ph*0.700)@R(*XZ,ph*0.450)@R(*XW,ph*0.273)
      @R(*YZ,ph*0.550)@R(*YW,ph*0.353)@R(*ZW,ph*0.159))

    fig=plt.figure(figsize=(10,10),facecolor=BG)
    ax=fig.add_axes([0.04,0.06,0.92,0.88])
    ax.set_facecolor(BG); ax.set_xlim(-2.8,2.8); ax.set_ylim(-2.8,2.8)
    ax.set_aspect("equal"); ax.axis("off")

    # stars
    twk=np.clip(0.4+0.6*np.sin(ph*1.8+SX*0.3+SY*0.4),0,1)
    sc=np.ones((350,4)); sc[:,3]=SA*twk
    ax.scatter(SX,SY,s=SS,c=sc,linewidths=0,zorder=1)

    # Clifford torus dots
    ct=CT@M.T; ct2,_=proj4(ct); ctw=ct[:,3]
    for i in range(0,len(ct2),4):
        wn=np.clip((ctw[i]+1.5)/3.0,0,1)
        ax.scatter([ct2[i,0]],[ct2[i,1]],s=3,
            c=[[(0.2+0.4*wn,0.1+0.2*wn,0.5+0.4*wn,0.13)]],linewidths=0,zorder=2)

    # 24-cell (background)
    r24=V24@M.T; p24,d24=proj4(r24*0.95); w24=r24[:,3]
    segs=[]; cols=[]
    for e0,e1 in E24:
        ec=ecol((w24[e0]+w24[e1])/2,(d24[e0]+d24[e1])/2)
        segs.append([(p24[e0,0],p24[e0,1]),(p24[e1,0],p24[e1,1])])
        cols.append((*ec,0.18))
    ax.add_collection(mc.LineCollection(segs,colors=cols,linewidths=0.5,zorder=3))

    # Tesseract (foreground, depth-sorted glow)
    rT=VT@M.T; pT,dT=proj4(rT); wT=rT[:,3]
    ed=sorted([(i,j,(dT[i]+dT[j])/2) for i,j in ET],key=lambda x:x[2])
    for e0,e1,da in ed:
        ec=ecol((wT[e0]+wT[e1])/2,da)
        lw=max(0.3,min(2.5,da*0.6))
        for w2,al in ((lw*5,0.04),(lw*2.5,0.10),(lw,0.65),(lw*0.4,0.90)):
            ax.plot([pT[e0,0],pT[e1,0]],[pT[e0,1],pT[e1,1]],
                color=(*ec,al),linewidth=w2,solid_capstyle="round",zorder=4)

    # vertex halos
    for i,(px,py) in enumerate(pT):
        vc=(0.7,1.0,1.0) if wT[i]>=0 else (0.5,0.2,1.0)
        s=np.clip(dT[i]*15,5,80)
        ax.scatter([px],[py],s=s,c=[[(*vc,0.75)]],linewidths=0,zorder=5)
        ax.scatter([px],[py],s=s*4,c=[[(*vc,0.08)]],linewidths=0,zorder=5)

    # rotation angle overlay
    planes=[("XY",0.700),("XZ",0.450),("XW",0.273),("YZ",0.550),("YW",0.353),("ZW",0.159)]
    for k,(pl,sp) in enumerate(planes):
        deg=(ph*sp)%(2*np.pi)*180/np.pi
        ax.text(-2.65,2.55-k*0.22,f"{pl}:{deg:6.1f}",
            color=(0.35,0.65,0.45,0.55),fontsize=5.5,fontfamily="monospace",zorder=6)
    ax.text(0,-2.68,"SO(4) | Tesseract + 24-cell + Clifford Torus",
        color=(0.3,0.5,0.8,0.45),fontsize=6,ha="center",fontfamily="monospace",zorder=6)

    buf=io.BytesIO()
    fig.savefig(buf,format="png",dpi=DPI,facecolor=BG,bbox_inches="tight",pad_inches=0)
    buf.seek(0); img=Image.open(buf).copy(); buf.close(); plt.close(fig)
    return img

print("Rendering",FRAMES,"frames...")
frames=[]
for i in range(FRAMES):
    frames.append(make_frame(i/FRAMES))
    if (i+1)%15==0: print(" frame",i+1,"/",FRAMES)

frames[0].save(OUT,save_all=True,append_images=frames[1:],duration=44,loop=0,optimize=False)
print("Done.",OUT)

try:
    subprocess.run(["termux-media-scan",OUT],capture_output=True,timeout=20)
except: pass