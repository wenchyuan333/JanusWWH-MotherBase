#!/usr/bin/env python3
"""miya_4d.py v1.0
4D Tesseract x 6-plane rotation x Spacetime Jump x Perspective Projection
Requires: pip install numpy matplotlib Pillow
"""
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
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from PIL import Image
import io

HOME=os.path.expanduser("~")
_g=os.path.join(HOME,"storage","pictures")
OUT=os.path.join(_g if os.path.isdir(_g) else HOME,"miya_4d.gif")

BG="#02020F"
FRAMES=72
DPI=100

# ── Tesseract: 16 vertices of the 4D hypercube {-1,+1}^4 ──
VERTS=np.array([[x,y,z,w]
    for x in [-1,1] for y in [-1,1]
    for z in [-1,1] for w in [-1,1]],dtype=float)
EDGES=[(i,j) for i in range(16) for j in range(i+1,16)
       if int(np.sum(VERTS[i]!=VERTS[j]))==1]  # 32 edges

# ── 4D rotation matrix in plane (i,j) ──
def rot4(i,j,theta):
    R=np.eye(4)
    R[i,i]=R[j,j]=np.cos(theta)
    R[i,j]=-np.sin(theta)
    R[j,i]= np.sin(theta)
    return R

# ── Projection chain: R^4 → R^3 → R^2 ──
def proj(pts4, d3=3.0, d2=3.8):
    w=pts4[:,3]; s3=d3/(d3-w)
    p3=pts4[:,:3]*s3[:,None]
    z=p3[:,2];  s2=d2/(d2-z)
    p2=p3[:,:2]*s2[:,None]
    return p2, w

# ── Spacetime jump schedule: three jumps across 72 frames ──
JUMP_AT=[0.28, 0.55, 0.82]   # t in [0,1]
JUMP_W =np.pi*0.6            # jump magnitude (W-plane)

def jump_phase(t):
    total=0.0
    for jt in JUMP_AT:
        dt=t-jt
        if -0.04<dt<0.08:
            total+=JUMP_W*np.exp(-abs(dt)*35.0)
    return total

# ── Background star field (fixed seed) ──
RNG=np.random.RandomState(7)
SX=RNG.uniform(-2.4,2.4,300)
SY=RNG.uniform(-2.4,2.4,300)
SS=RNG.uniform(0.1,2.5,300)
SA=RNG.uniform(0.15,0.5,300)

def make_frame(t):
    ph=t*2.0*np.pi
    jp=jump_phase(t)

    # ─ compose 6-plane rotation ─
    R=np.eye(4)
    for (i,j),speed in (((0,1),0.70),((0,2),0.45),((0,3),0.25),
                        ((1,2),0.55),((1,3),0.35),((2,3),0.15)):
        extra= jp if 3 in (i,j) else 0.0   # W-plane gets the jump
        R=rot4(i,j,ph*speed+extra)@R

    pts=(R@VERTS.T).T          # (16,4)
    p2,wc=proj(pts)            # p2:(16,2), wc:(16,)

    # ─ figure ─
    fig=plt.figure(figsize=(9,9),facecolor=BG)
    ax=fig.add_axes([0,0,1,1])
    ax.set_facecolor(BG)
    ax.set_xlim(-2.4,2.4); ax.set_ylim(-2.4,2.4)
    ax.set_aspect("equal"); ax.axis("off")

    # ─ stars with gravitational warp near origin ─
    dist=np.sqrt(SX**2+SY**2)+0.3
    warp=0.18*np.sin(ph*1.5)/dist
    ax.scatter(SX+warp*SX,SY+warp*SY,s=SS,color="white",alpha=SA,
               linewidths=0,zorder=1)

    # ─ tesseract edges with glow ─
    for e0,e1 in EDGES:
        x0,y0=p2[e0]; x1,y1=p2[e1]
        aw=(wc[e0]+wc[e1])/2.0           # avg W depth
        wn=(aw+1.8)/3.6                  # normalize to [0,1]
        # outer W>0: cyan-white; inner W<0: violet-blue
        if aw>=0:
            ec=(0.55+0.45*wn, 0.85+0.15*wn, 1.0)
        else:
            ec=(0.35*(1-wn), 0.15+0.4*(1-wn), 0.9+0.1*wn)
        for lw,al in ((5.5,0.05),(3.0,0.12),(1.2,0.55),(0.4,0.85)):
            ax.plot([x0,x1],[y0,y1],color=(*ec,al),
                    linewidth=lw,solid_capstyle="round",zorder=3)

    # ─ vertex halos ─
    for i,(px,py) in enumerate(p2):
        w=wc[i]
        if w>=0:
            vc=(0.75,1.0,1.0)
        else:
            vc=(0.55,0.25,1.0)
        ax.scatter([px],[py],s=60+40*abs(w),color=(*vc,0.7),
                   linewidths=0,zorder=4)
        ax.scatter([px],[py],s=200+80*abs(w),color=(*vc,0.08),
                   linewidths=0,zorder=4)

    # ─ dimensional trail: ghost copy at t-1 phase ─
    R2=np.eye(4)
    for (i,j),speed in (((0,1),0.70),((0,2),0.45),((0,3),0.25),
                        ((1,2),0.55),((1,3),0.35),((2,3),0.15)):
        R2=rot4(i,j,(ph-0.18)*speed)@R2
    pts2g=(R2@VERTS.T).T
    p2g,wg=proj(pts2g)
    for e0,e1 in EDGES:
        x0,y0=p2g[e0]; x1,y1=p2g[e1]
        aw=(wg[e0]+wg[e1])/2.0
        if aw>=0: gc=(0.3,0.6,0.9)
        else: gc=(0.4,0.1,0.7)
        ax.plot([x0,x1],[y0,y1],color=(*gc,0.10),
                linewidth=0.8,solid_capstyle="round",zorder=2)

    # ─ spacetime jump warp rays ─
    js=min(1.0, abs(jp)/JUMP_W)
    if js>0.05:
        n_rays=24
        for ri in range(n_rays):
            ang=ri*2*np.pi/n_rays+ph*0.1
            lng=2.5*js
            ax.plot([0,lng*np.cos(ang)],[0,lng*np.sin(ang)],
                    color=(1.0,1.0,1.0,0.22*js),
                    linewidth=1.5,zorder=5)
        # flash ring
        th=np.linspace(0,2*np.pi,200)
        for rr,al in ((0.2,0.6),(0.5,0.3),(1.0,0.15)):
            ax.plot(rr*np.cos(th)*js,rr*np.sin(th)*js,
                    color=(0.8,0.9,1.0,al*js),linewidth=1.0,zorder=5)

    # ─ center void ─
    for rr,al in ((0.04,0.9),(0.10,0.35),(0.22,0.10)):
        ax.add_patch(plt.Circle((0,0),rr,color="white",alpha=al,zorder=6))

    buf=io.BytesIO()
    fig.savefig(buf,format="png",dpi=DPI,facecolor=BG)
    buf.seek(0); img=Image.open(buf).copy(); buf.close(); plt.close(fig)
    return img

print("Rendering",FRAMES,"frames...")
frames=[]
for i in range(FRAMES):
    frames.append(make_frame(i/FRAMES))
    if (i+1)%12==0: print(" frame",i+1,"/",FRAMES)

print("Saving to:",OUT)
frames[0].save(OUT,save_all=True,append_images=frames[1:],
               duration=55,loop=0,optimize=False)
print("Saved.")

try:
    r=subprocess.run(["termux-media-scan",OUT],capture_output=True,timeout=20)
    print("Gallery:","OK" if r.returncode==0 else r.stderr.decode("utf-8","replace").strip())
except FileNotFoundError:
    print("termux-media-scan not found. pkg install termux-api")
except Exception as e:
    print("Gallery error:",e)

print("Done.",OUT)