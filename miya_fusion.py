#!/usr/bin/env python3
# miya_fusion.py v1.1  fixed: all color alphas clipped to [0,1] as plain float
# pip install numpy matplotlib Pillow  then  python3 miya_fusion.py
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
from PIL import Image
import io

HOME=os.path.expanduser("~")
_g=os.path.join(HOME,"storage","pictures")
OUT=os.path.join(_g if os.path.isdir(_g) else HOME,"miya_fusion.gif")
BG="#010108"; FRAMES=72; DPI=100

# --- ALL color alphas go through c4() to avoid np.float64 / negative alpha ---
def c4(r,g,b,a):
    return (float(r), float(g), float(b), float(np.clip(a,0.0,1.0)))

# --- Tesseract ---
VT=np.array([[x,y,z,w] for x in [-1,1] for y in [-1,1]
             for z in [-1,1] for w in [-1,1]],dtype=float)
ET=[(i,j) for i in range(16) for j in range(i+1,16)
    if int(np.sum(VT[i]!=VT[j]))==1]

def R4(i,j,th):
    M=np.eye(4); M[i,i]=M[j,j]=np.cos(th)
    M[i,j]=-np.sin(th); M[j,i]=np.sin(th); return M

def proj4(pts,d3=3.0,d2=3.8):
    w=pts[:,3]; s3=np.clip(d3/(d3-w),0.15,9.0)
    p3=pts[:,:3]*s3[:,None]
    z=p3[:,2]; s2=np.clip(d2/(d2-z),0.15,9.0)
    return p3[:,:2]*s2[:,None], s3*s2

def atomic_ring(ax,ocx,ocy,rx,ry_base,tilt,spin,color,lw,base_alpha,zo):
    t=np.linspace(0,2*np.pi,120)
    ry=ry_base*abs(float(np.cos(tilt)))
    x=ocx+rx*np.cos(t+spin)
    y=ocy+ry*np.sin(t+spin)
    zd=ry_base*np.sin(t+spin)*float(np.sin(tilt))
    for k in range(len(t)-1):
        z_mid=(float(zd[k])+float(zd[k+1]))/2
        al=base_alpha*(0.28+0.72*(z_mid/max(ry_base,1e-6)+1)/2)
        ax.plot([x[k],x[k+1]],[y[k],y[k+1]],
            color=c4(*color,al),linewidth=lw,solid_capstyle="round",zorder=zo)

RZEROS=[14.135,21.022,25.011,30.425,32.935,37.586]

RNG=np.random.RandomState(7)
SX=RNG.uniform(-5.2,5.2,450); SY=RNG.uniform(-4.5,4.5,450)
SS=RNG.uniform(0.1,2.8,450); SA=RNG.uniform(0.1,0.55,450)

def make_frame(t):
    ph=t*2*np.pi
    cy=0.7+0.14*np.sin(ph*1.3)
    cx=0.0

    fig=plt.figure(figsize=(10,9),facecolor=BG)
    ax=fig.add_axes([0,0,1,1])
    ax.set_facecolor(BG); ax.set_xlim(-5.2,5.2); ax.set_ylim(-4.5,4.5)
    ax.set_aspect("equal"); ax.axis("off")

    # stars
    twk=np.clip(0.4+0.6*np.sin(ph*2+SX*0.3),0,1)
    sc=np.ones((450,4)); sc[:,3]=SA*twk
    ax.scatter(SX,SY,s=SS,c=sc,linewidths=0,zorder=1)

    # FFT aura rings
    tr=np.linspace(0,2*np.pi,200)
    for k,freq in enumerate(RZEROS):
        rb=0.9+(freq-14)/24*2.8
        rp=rb+0.07*np.sin(ph*freq*0.07+k)
        br=max(0.0, 0.25+0.35*np.sin(ph*1.5+k*0.8))  # clamp >=0
        col=(0.15, 0.45+0.35*(k/6), 1.0)
        ax.plot(rp*np.cos(tr)+cx, rp*np.sin(tr)*0.32+cy,
            color=c4(*col, br*0.14), linewidth=1.5, zorder=2)
        ax.plot(rp*np.cos(tr)+cx, rp*np.sin(tr)*0.32+cy,
            color=c4(*col, 0.04), linewidth=4.0, zorder=2)

    # tractor beam
    bb=-3.8; bwt=0.65; bwb=2.0
    bp=0.10+0.06*np.sin(ph*2.5)
    for si in range(22):
        f=si/22
        y0=cy-0.28+f*(bb-(cy-0.28)); y1=cy-0.28+(f+0.045)*(bb-(cy-0.28))
        w0=bwt+f*(bwb-bwt); w1=bwt+(f+0.045)*(bwb-bwt)
        ax.add_patch(Polygon([(cx-w0,y0),(cx+w0,y0),(cx+w1,y1),(cx-w1,y1)],
            closed=True,facecolor=(0.2,0.9,0.4),
            alpha=float(np.clip(bp*(1-f*0.62),0,1)),edgecolor="none",zorder=3))
    sf=(t*2.5)%1.0
    sy2=cy-0.28+sf*(bb-(cy-0.28)); sw2=bwt+sf*(bwb-bwt)
    ax.plot([cx-sw2*0.85,cx+sw2*0.85],[sy2,sy2],
        color=c4(0.4,1.0,0.55,0.28),linewidth=0.8,zorder=4)

    # outer glow halos
    for rw,rh,al in ((7.0,1.9,0.022),(5.5,1.5,0.038),(4.2,1.1,0.065)):
        ax.add_patch(Ellipse((cx,cy),rw,rh,facecolor=(0.1,0.75,0.3),
            alpha=al,edgecolor="none",zorder=4))

    # saucer body
    ax.add_patch(Ellipse((cx,cy),4.6,1.15,facecolor=(0.05,0.09,0.09),
        edgecolor=(0.2,0.85,0.45),linewidth=2.2,zorder=5))
    ax.add_patch(Ellipse((cx,cy-0.1),4.3,0.82,facecolor=(0.03,0.06,0.07),
        alpha=0.9,edgecolor="none",zorder=6))
    for rw2,rh2,lw2 in ((3.0,0.70,0.9),(2.2,0.54,0.65),(1.5,0.40,0.5)):
        ax.add_patch(Ellipse((cx,cy),rw2,rh2,facecolor="none",
            edgecolor=(0.28,0.72,0.42),linewidth=lw2,zorder=7))

    # dome
    ax.add_patch(Ellipse((cx,cy+0.58),2.2,1.45,facecolor=(0.04,0.07,0.16),
        edgecolor=(0.25,0.55,1.0),linewidth=1.5,zorder=8))
    dg=float(np.clip(0.07+0.06*np.sin(ph*1.8),0,1))
    ax.add_patch(Ellipse((cx,cy+0.60),1.65,1.08,facecolor=(0.08,0.18,0.48),
        alpha=dg,edgecolor="none",zorder=9))
    ax.add_patch(Ellipse((cx-0.32,cy+0.90),0.60,0.32,facecolor=(0.7,0.85,1.0),
        alpha=0.07,edgecolor="none",zorder=10))

    # inner tesseract cage
    dome_cx=cx; dome_cy=cy+0.58
    M4=(R4(0,1,ph*0.85)@R4(0,3,ph*0.38)@R4(1,2,ph*0.60)@R4(2,3,ph*0.22))
    rT=VT@M4.T; pT,dT=proj4(rT*0.44); wT=rT[:,3]
    pT[:,0]+=dome_cx; pT[:,1]+=dome_cy
    ed=sorted([(i,j,(dT[i]+dT[j])/2) for i,j in ET],key=lambda x:x[2])
    for e0,e1,da in ed:
        wn=float(np.clip(((wT[e0]+wT[e1])/2+1.5)/3.0,0,1))
        if (wT[e0]+wT[e1])/2>=0:
            ec=(0.35+0.45*wn, 0.75+0.25*wn, 1.0)
        else:
            ec=(0.2*(1-wn), 0.15+0.3*(1-wn), 0.85+0.15*wn)
        lw3=max(0.25,min(1.6,float(da)*0.38))
        for lw4,al4 in ((lw3*5,0.05),(lw3*2,0.14),(lw3,0.60),(lw3*0.35,0.88)):
            ax.plot([pT[e0,0],pT[e1,0]],[pT[e0,1],pT[e1,1]],
                color=c4(*ec,al4),linewidth=lw4,solid_capstyle="round",zorder=11)

    # atomic rings
    atomic_ring(ax,dome_cx,dome_cy,0.55,0.55*0.55,np.pi/3,    ph*1.3, (0.7,0.82,1.0),1.8,0.75,12)
    atomic_ring(ax,dome_cx,dome_cy,0.55,0.55*0.55,np.pi/2,    ph*0.75,(1.0,0.88,0.35),1.8,0.75,12)
    atomic_ring(ax,dome_cx,dome_cy,0.50,0.55*0.55,np.pi*0.75, ph*0.45+np.pi/2,(0.5,1.0,0.82),1.5,0.70,12)

    # plasma core
    pp=0.035*np.sin(ph*3.8)
    for rr,al,col in (
        (0.26,0.50,(0.45,0.05,0.85)),
        (0.18,0.55,(0.58,0.15,1.0)),
        (0.12,0.70,(0.72,0.28,1.0)),
        (0.065,0.88,(0.88,0.52,1.0)),
        (0.028,1.00,(1.0,0.88,1.0)),
    ):
        rv=float(rr)+float(pp)
        ax.add_patch(Ellipse((dome_cx,dome_cy),rv*2,rv*1.35,
            facecolor=col,alpha=float(al),edgecolor="none",zorder=13))
    for k in range(8):
        ang2=k*np.pi/4+ph*2.5
        dist=0.28+0.09*np.sin(ph*4+k*1.2)
        ax.plot([dome_cx,dome_cx+dist*np.cos(ang2)],
                [dome_cy,dome_cy+dist*np.sin(ang2)*0.65],
                color=c4(0.75,0.35,1.0,0.38),linewidth=0.7,zorder=13)

    # rim lights
    for li in range(18):
        ang3=li*2*np.pi/18+ph*1.8
        lx=cx+2.25*np.cos(ang3); ly=cy+0.47*np.sin(ang3)-0.05
        hue=(li/18+t*0.42)%1.0
        r2,g2,b2=colorsys.hsv_to_rgb(hue,1.0,1.0)
        br2=float(0.5+0.5*np.sin(ph*5+li))
        ax.scatter([lx],[ly],s=110*br2,c=[[c4(r2,g2,b2,0.15*br2)]],linewidths=0,zorder=14)
        ax.scatter([lx],[ly],s=24*br2, c=[[c4(r2,g2,b2,0.88*br2)]],linewidths=0,zorder=15)

    # bottom nozzles
    for nx in (-1.3,0.0,1.3):
        na=float(np.clip(0.22+0.14*np.sin(ph*3.2+nx*2),0,1))
        ax.scatter([cx+nx],[cy-0.50],s=280,c=[[c4(0.15,1.0,0.5,na)]],linewidths=0,zorder=14)

    # antenna
    ax.plot([cx,cx],[cy+1.30,cy+1.60],color=c4(0.45,0.65,1.0,0.55),linewidth=0.9,zorder=15)
    ab=float(0.5+0.5*np.sin(ph*7))
    ax.scatter([cx],[cy+1.66],s=28*ab,c=[[c4(1.0,0.25,0.25,0.92*ab)]],linewidths=0,zorder=16)

    buf=io.BytesIO()
    fig.savefig(buf,format="png",dpi=DPI,facecolor=BG)
    buf.seek(0); img=Image.open(buf).copy(); buf.close(); plt.close(fig)
    return img

print("Rendering",FRAMES,"frames...")
frames=[]
for i in range(FRAMES):
    frames.append(make_frame(i/FRAMES))
    if (i+1)%12==0: print(" frame",i+1,"/",FRAMES)
frames[0].save(OUT,save_all=True,append_images=frames[1:],duration=50,loop=0,optimize=False)
print("Done.",OUT)
try: subprocess.run(["termux-media-scan",OUT],capture_output=True,timeout=20)
except: pass