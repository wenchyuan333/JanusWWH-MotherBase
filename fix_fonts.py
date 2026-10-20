import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

# --- 自動找 CJK 字型 ---
def find_cjk_font():
    candidates = [
        "/data/data/com.termux/files/usr/share/fonts/noto/NotoSansCJK-Regular.ttc",
        "/data/data/com.termux/files/usr/share/fonts/noto/NotoSansCJKsc-Regular.otf",
        os.path.expanduser("~/NotoSansCJKsc.otf"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    # fallback: search system
    for f in fm.findSystemFonts():
        if "Noto" in f and ("CJK" in f or "SC" in f or "TC" in f):
            return f
    return None

font_path = find_cjk_font()
if font_path:
    prop = fm.FontProperties(fname=font_path)
    fname = prop.get_name()
    matplotlib.rcParams["font.family"] = fname
    fm.fontManager.addfont(font_path)
    print(f"Using font: {fname} ({font_path})")
else:
    print("WARNING: No CJK font found. Chinese will still be boxes.")

# ===================== SCRIPT 1: GIF =====================
from PIL import Image, ImageDraw
OUTPUT1 = "/sdcard/DCIM/miya_chain.gif"

steps = [
    ("①", "magic square"),
    ("②③", "Structure decomp: f = sum u_j(k_j*x)"),
    ("④", "Section sum divisibility: u_j in (1/3)Z"),
    ("⑧", "alpha-contradiction: u_j in Z  [NEW]"),
    ("⑨", "Q_j in 81Z,  P_j = rho1^2+rho1*rho2+rho2^2  [NEW]"),
    ("⑩", "Sum P_j = 91,  P_j <= 81"),
    ("base-3", "Unique decomp: 91=81+9+1+0  =>  some P_j=0"),
    ("DONE", "Affine base-3 digit cube  QED"),
]

BG=(15,15,30); GOLD=(255,210,80); CYAN=(80,220,220); WHITE=(240,240,240)
W,H=700,400; frames=[]
for i in range(len(steps)):
    img=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(img)
    d.text((20,12),"Chain: d=3 Closure",fill=GOLD)
    for j,(num,label) in enumerate(steps[:i+1]):
        x,y=36,50+j*40
        col=CYAN if j==i else WHITE
        d.rectangle([x-4,y-4,x+640,y+28],outline=col,width=2 if j==i else 1)
        d.text((x+6,y+6),f"{num}  {label}",fill=col)
        if j<i: d.text((x+300,y+32),"v",fill=(120,120,120))
    frames.append(img.copy())
    if i==len(steps)-1: frames+=[img.copy()]*10

frames[0].save(OUTPUT1,save_all=True,append_images=frames[1:],duration=900,loop=0)
print(f"✅ {OUTPUT1}")

# ===================== SCRIPT 2: EISENSTEIN =====================
OUTPUT2="/sdcard/DCIM/miya_eisenstein.png"
import numpy as np

fig,ax=plt.subplots(figsize=(8,7),facecolor="#0f0f1e")
ax.set_facecolor("#0f0f1e")
vals={0:"#555555",1:"#ffaa00",9:"#00ccff",81:"#ff4466"}
for a in range(-9,10):
    for b in range(-9,10):
        P=a*a+a*b+b*b
        col=vals.get(P,"#1a1a2e")
        ax.scatter(a,b,color=col,s=18,zorder=2)

highlight=[(9,-9,"#ff4466","P=81"),(3,0,"#00ccff","P=9"),
           (1,0,"#ffaa00","P=1"),(0,0,"#aaaaaa","P=0")]
for (a,b,c,lbl) in highlight:
    ax.scatter(a,b,color=c,s=140,edgecolors="white",linewidths=1.8,zorder=5)
    ax.annotate(lbl,(a,b),textcoords="offset points",
                xytext=(8,6),color=c,fontsize=10,fontweight="bold")

import matplotlib.patches as mpatches
patches=[mpatches.Patch(color=v,label=f"P = {k}") for k,v in vals.items()]
ax.legend(handles=patches,loc="upper left",
          facecolor="#1a1a2e",edgecolor="#555",labelcolor="white",fontsize=10)
ax.set_title("Eisenstein lattice: P_j in {0,1,9,81}, Sum P_j = 91 = 81+9+1+0",
             color="gold",fontsize=11,pad=12)
ax.set_xlabel("rho_1",color="#aaa"); ax.set_ylabel("rho_2",color="#aaa")
ax.tick_params(colors="#666")
for spine in ax.spines.values(): spine.set_edgecolor("#333")
ax.set_xlim(-10,10); ax.set_ylim(-10,10)
ax.grid(True,color="#222",linewidth=0.5)
plt.tight_layout()
plt.savefig(OUTPUT2,dpi=150)
print(f"✅ {OUTPUT2}")

# ===================== SCRIPT 3: FLOWCHART =====================
OUTPUT3="/sdcard/DCIM/miya_flowchart.png"
import matplotlib.patches as mpatches2

nodes=[
    (0.5,0.93,"magic square","#2a1a4a","#cc88ff"),
    (0.5,0.83,"① Decomp: f = sum u_j(k_j x)","#0a2a3a","#44bbdd"),
    (0.5,0.73,"②③ u_j in (1/3)Z","#0a2a3a","#44bbdd"),
    (0.5,0.63,"④⑤ Pixel formula + Eisenstein  Q_j in 9Z","#0a2a3a","#44bbdd"),
    (0.5,0.53,"⑧ alpha-contradiction  =>  u_j in Z  [NEW]","#1a2a10","#88ff66"),
    (0.5,0.43,"⑨ Q_j in 81Z,  P_j in Z  [NEW]","#1a2a10","#88ff66"),
    (0.5,0.33,"⑩ Sum P_j = 91,  P_j <= 81","#2a1a00","#ffcc44"),
    (0.5,0.22,"base-3 unique decomp: 91=81+9+1+0\n=> some P_j = 0","#2a1a00","#ffcc44"),
    (0.5,0.10,"[OK]  Affine base-3 digit cube  QED","#1a0a0a","#ff5566"),
]

fig2,ax2=plt.subplots(figsize=(9,10),facecolor="#0a0a1a")
ax2.set_facecolor("#0a0a1a"); ax2.axis("off")
bw,bh=0.64,0.065
for (x,y,label,bg,fg) in nodes:
    rect=mpatches2.FancyBboxPatch((x-bw/2,y-bh/2),bw,bh,
         boxstyle="round,pad=0.01",facecolor=bg,edgecolor=fg,linewidth=1.8)
    ax2.add_patch(rect)
    ax2.text(x,y,label,ha="center",va="center",color=fg,
             fontsize=9,fontweight="bold",multialignment="center",
             fontproperties=prop if font_path else None)

for i in range(len(nodes)-1):
    _,y1,*_=nodes[i]; _,y2,*_=nodes[i+1]
    ax2.annotate("",xy=(0.5,y2+bh/2+0.003),xytext=(0.5,y1-bh/2-0.003),
                 arrowprops=dict(arrowstyle="->",color="#888888",lw=1.5))

ax2.set_title("Jia-Xian Chain  d=3  Closure  (2026-08-26)",
              color="gold",fontsize=12,pad=8)
ax2.set_xlim(0,1); ax2.set_ylim(0,1)
plt.tight_layout()
plt.savefig(OUTPUT3,dpi=160,bbox_inches="tight")
print(f"✅ {OUTPUT3}")