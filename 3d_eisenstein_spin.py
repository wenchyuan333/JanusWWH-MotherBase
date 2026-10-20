import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from PIL import Image
import io, os

OUTPUT = "/sdcard/DCIM/miya_3d_eisenstein.gif"
frames = []

# Build (rho1, rho2, P) points
pts = []
for a in range(-9, 10):
    for b in range(-9, 10):
        P = a*a + a*b + b*b
        pts.append((a, b, P))
pts = np.array(pts, dtype=float)

def p_color(P):
    if P == 0:   return "#888888"
    if P == 1:   return "#ffaa00"
    if P == 9:   return "#00ccff"
    if P == 81:  return "#ff4466"
    return "#1a1a3a"

colors = [p_color(int(P)) for (_,_,P) in pts]

# Highlighted decomposition points: 91 = 81+9+1+0
highlight = [(9,-9,81,"#ff4466","P=81"),(3,0,9,"#00ccff","P=9"),
             (1,0,1,"#ffaa00","P=1"),(0,0,0,"#aaaaaa","P=0")]

print("Rendering 3D spin frames...")
for frame_i, azim in enumerate(range(0, 360, 4)):
    fig = plt.figure(figsize=(7,6), facecolor="#0a0a1a")
    ax = fig.add_subplot(111, projection="3d", facecolor="#0a0a1a")

    # scatter all points
    ax.scatter(pts[:,0], pts[:,1], pts[:,2],
               c=colors, s=6, alpha=0.5, depthshade=True)

    # highlight key decomposition
    for (a,b,P,c,lbl) in highlight:
        ax.scatter([a],[b],[P], color=c, s=120,
                   edgecolors="white", linewidths=1.2, zorder=10)
        ax.text(a+0.4, b+0.4, P+2, lbl, color=c, fontsize=7, fontweight="bold")

    # draw vertical lines from z=0 to P for highlights
    for (a,b,P,c,_) in highlight:
        ax.plot([a,a],[b,b],[0,P], color=c, alpha=0.5, linewidth=1)

    ax.set_xlabel("rho_1", color="#888", fontsize=8)
    ax.set_ylabel("rho_2", color="#888", fontsize=8)
    ax.set_zlabel("P_j", color="#888", fontsize=8)
    ax.set_title(f"Eisenstein Lattice  Sum P_j=91=81+9+1+0",
                 color="gold", fontsize=9, pad=6)
    ax.view_init(elev=25, azim=azim)
    ax.tick_params(colors="#555", labelsize=6)
    ax.xaxis.pane.fill = False; ax.yaxis.pane.fill = False; ax.zaxis.pane.fill = False
    ax.xaxis.pane.set_edgecolor("#222")
    ax.yaxis.pane.set_edgecolor("#222")
    ax.zaxis.pane.set_edgecolor("#222")
    ax.grid(True, color="#1a1a2a", linewidth=0.4)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=110, bbox_inches="tight", facecolor="#0a0a1a")
    plt.close()
    buf.seek(0)
    frames.append(Image.open(buf).copy())
    if frame_i % 10 == 0:
        print(f"  frame {frame_i}/90")

frames[0].save(OUTPUT, save_all=True, append_images=frames[1:],
               duration=60, loop=0, optimize=False)
print(f"✅ {OUTPUT}")