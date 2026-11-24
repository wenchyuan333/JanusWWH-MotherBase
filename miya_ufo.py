#!/usr/bin/env python3
# miya_ufo.py v1.0  --  Flying Saucer x Tractor Beam x Rim Lights
# pip install numpy matplotlib Pillow
import sys, os, subprocess, colorsys

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
from matplotlib.patches import Ellipse, Polygon
import matplotlib.colors as mcolors
from PIL import Image
import io

HOME=os.path.expanduser("~")
_g=os.path.join(HOME,"storage","pictures")
OUT=os.path.join(_g if os.path.isdir(_g) else HOME,"miya_ufo.gif")
BG="#000812"; FRAMES=60; DPI=100

RNG=np.random.RandomState(7)
SX=RNG.uniform(-5.5,5.5,500); SY=RNG.uniform(-1.0,4.5,500)
SS=RNG.uniform(0.1,3.5,500); SA=RNG.uniform(0.15,0.65,500)

MTN=np.array([[-5.5,-3.8],[-4.2,-3.8],[-3.8,-2.2],[-3.2,-3.0],
    [-2.5,-1.5],[-1.8,-2.8],[-1.0,-3.8],[0.0,-3.8],[0.5,-2.0],
    [1.2,-3.2],[2.0,-1.2],[2.8,-2.8],[3.5,-3.5],[4.5,-3.8],
    [5.5,-3.8],[5.5,-4.5],[-5.5,-4.5]])

def make_frame(t):
    ph=t*2.0*np.pi
    cy=1.0+0.18*np.sin(ph*1.3)
    cx=0.3*np.sin(ph*0.4)

    fig=plt.figure(figsize=(11,8),facecolor=BG)
    ax=fig.add_axes([0,0,1,1])
    ax.set_facecolor(BG); ax.set_xlim(-5.5,5.5); ax.set_ylim(-4.5,4.5)
    ax.set_aspect("equal"); ax.axis("off")

    # stars
    twk=np.clip(0.5+0.5*np.sin(ph*2.5+SX*0.4+SY*0.3),0,1)
    cols=np.ones((len(SX),4)); cols[:,3]=SA*twk
    ax.scatter(SX,SY,s=SS,c=cols,linewidths=0,zorder=1)

    # mountains + city glow
    ax.add_patch(Polygon(MTN,closed=True,
        facecolor=(0.04,0.06,0.08),edgecolor=(0.10,0.18,0.24),linewidth=0.6,zorder=2))
    for cx2,col2,off in ((-3.0,(1.0,0.6,0.1),0.0),(0.0,(0.5,0.8,1.0),1.0),(3.5,(1.0,0.4,0.2),2.0)):
        al=0.05+0.02*np.sin(ph*3+off)
        ax.scatter([cx2],[-3.5],s=3000,c=[[col2[0],col2[1],col2[2],al]],linewidths=0,zorder=3)

    # tractor beam
    bb=-3.2; bwt=0.85; bwb=2.4
    bpulse=0.12+0.07*np.sin(ph*2.2)
    for si in range(24):
        f0=si/24; f1=(si+1)/24
        y0=cy-0.35+f0*(bb-(cy-0.35)); y1=cy-0.35+f1*(bb-(cy-0.35))
        w0=bwt+f0*(bwb-bwt); w1=bwt+f1*(bwb-bwt)
        ax.add_patch(Polygon([(cx-w0,y0),(cx+w0,y0),(cx+w1,y1),(cx-w1,y1)],
            closed=True,facecolor=(0.25,1.0,0.45),
            alpha=bpulse*(1-f0*0.6),edgecolor="none",zorder=4))
    sf=(t*2.8)%1.0
    sy=cy-0.35+sf*(bb-(cy-0.35)); sw=bwt+sf*(bwb-bwt)
    ax.plot([cx-sw*0.88,cx+sw*0.88],[sy,sy],color=(0.5,1.0,0.6,0.35),linewidth=0.8,zorder=5)

    # outer glow
    for rw,rh,al in ((5.2,1.4,0.03),(4.0,1.1,0.05),(3.0,0.85,0.08)):
        ax.add_patch(Ellipse((cx,cy),rw,rh,facecolor=(0.2,0.9,0.35),alpha=al,edgecolor="none",zorder=5))

    # saucer body
    ax.add_patch(Ellipse((cx,cy),3.8,1.0,facecolor=(0.10,0.14,0.12),
        edgecolor=(0.25,0.65,0.35),linewidth=1.2,zorder=6))
    ax.add_patch(Ellipse((cx,cy-0.12),3.5,0.72,facecolor=(0.07,0.10,0.09),alpha=0.85,edgecolor="none",zorder=7))
    ax.add_patch(Ellipse((cx,cy),2.2,0.55,facecolor=(0.14,0.22,0.16),
        edgecolor=(0.35,0.75,0.45),linewidth=0.7,zorder=8))
    ax.add_patch(Ellipse((cx,cy),1.2,0.32,facecolor=(0.18,0.28,0.20),
        edgecolor=(0.5,0.9,0.55),linewidth=0.5,zorder=9))

    # dome
    ax.add_patch(Ellipse((cx,cy+0.52),1.6,1.0,facecolor=(0.08,0.14,0.22),
        edgecolor=(0.35,0.65,1.0),linewidth=0.9,zorder=10))
    dg=0.10+0.08*np.sin(ph*2.0)
    ax.add_patch(Ellipse((cx,cy+0.55),1.2,0.72,facecolor=(0.15,0.35,0.55),alpha=dg,edgecolor="none",zorder=11))
    ax.add_patch(Ellipse((cx-0.22,cy+0.72),0.45,0.28,facecolor=(0.7,0.85,1.0),alpha=0.12,edgecolor="none",zorder=12))

    # rim lights (16 rotating color-cycling)
    rrx,rry=1.85,0.40
    for li in range(16):
        ang=li*2*np.pi/16+ph*1.5
        lx=cx+rrx*np.cos(ang); ly=cy+rry*np.sin(ang)-0.08
        hue=(li/16+t*0.4)%1.0
        r,g,b=colorsys.hsv_to_rgb(hue,1.0,1.0)
        br=0.5+0.5*np.sin(ph*4+li*0.8)
        ax.scatter([lx],[ly],s=120*br,c=[[[r,g,b,0.18*br]]],linewidths=0,zorder=13)
        ax.scatter([lx],[ly],s=28*br,c=[[[r,g,b,0.85*br]]],linewidths=0,zorder=14)

    # bottom nozzles
    for nx in (-1.0,0.0,1.0):
        na=0.28+0.18*np.sin(ph*3+nx*2)
        ax.scatter([cx+nx],[cy-0.45],s=220,c=[[[0.3,1.0,0.5,na]]],linewidths=0,zorder=13)

    # antenna + blink
    ax.plot([cx,cx],[cy+1.0,cy+1.25],color=(0.6,0.8,1.0,0.7),linewidth=1.0,zorder=14)
    ablink=0.5+0.5*np.sin(ph*6)
    ax.scatter([cx],[cy+1.3],s=35*ablink,c=[[[1.0,0.3,0.3,0.9*ablink]]],linewidths=0,zorder=15)

    buf=io.BytesIO()
    fig.savefig(buf,format="png",dpi=DPI,facecolor=BG)
    buf.seek(0); img=Image.open(buf).copy(); buf.close(); plt.close(fig)
    return img

print("Rendering",FRAMES,"frames...")
frames=[]
for i in range(FRAMES):
    frames.append(make_frame(i/FRAMES))
    if (i+1)%10==0: print(" frame",i+1,"/",FRAMES)

print("Saving to:",OUT)
frames[0].save(OUT,save_all=True,append_images=frames[1:],duration=50,loop=0,optimize=False)
print("Saved.")

try:
    r=subprocess.run(["termux-media-scan",OUT],capture_output=True,timeout=20)
    print("Gallery:","OK" if r.returncode==0 else r.stderr.decode("utf-8","replace").strip())
except FileNotFoundError: print("termux-media-scan not found")
except Exception as e: print("Gallery error:",e)
print("Done.",OUT)