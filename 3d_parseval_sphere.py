import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from PIL import Image
import io

OUTPUT = "/sdcard/DCIM/miya_3d_parseval.gif"

# The 4 valid P values on "sphere" shell by angle
# Use spherical coords: theta = j*pi/2, phi = P/81 * pi
np.random.seed(42)
vals_P = [81, 9, 1, 0]
labels = ["P=81", "P=9", "P=1", "P=0"]
cols   = ["#ff4466","#00ccff","#ffaa00","#888888"]

# Generate random valid (rho1,rho2) pairs for each P value
def gen_pts(P_target, n=60):
    found = []
    for a in range(-9,10):
        for b in range(-9,10):
            if a*a+a*b+b*b == P_target:
                found.append((a,b))
    if not found: return np.zeros((1,3))
    chosen = np.array(found)[np.random.choice(len(found),
                              min(n,len(found)),replace=False)]
    r = np.sqrt(P_target+1)
    # map to sphere surface
    theta = np.arctan2(chosen[:,1], chosen[:,0])
    phi = np.full(len(chosen), np.pi/2 * (1 - P_target/82))
    x = r * np.sin(phi)*np.cos(theta)
    y = r * np.sin(phi)*np.sin(theta)
    z = r * np.cos(phi)
    return np.stack([x,y,z],axis=1)

all_pts = [(gen_pts(P), c, lbl) for P,c,lbl in zip(vals_P,cols,labels)]

frames = []
print("Rendering Parseval sphere frames...")
for fi, azim in enumerate(range(0, 360, 4)):
    fig = plt.figure(figsize=(7,6.5), facecolor="#0a0a1a")
    ax = fig.add_subplot(111, projection="3d", facecolor="#0a0a1a")

    for (pts, col, lbl) in all_pts:
        ax.scatter(pts[:,0], pts[:,1], pts[:,2],
                   color=col, s=30, alpha=0.8, label=lbl)

    # equator ring
    t = np.linspace(0, 2*np.pi, 100)
    ax.plot(np.cos(t)*9.2, np.sin(t)*9.2, np.zeros(100),
            color="#333355", linewidth=0.8, alpha=0.5)

    ax.set_title("Parseval Shell: P_j distribution\nSum = 91 = 81+9+1+0",
                 color="gold", fontsize=9, pad=4)
    ax.legend(loc="upper left", facecolor="#0a0a1a",
              edgecolor="#333", labelcolor="white", fontsize=8)
    ax.view_init(elev=30, azim=azim)
    ax.set_xlabel("x",color="#555",fontsize=7)
    ax.set_ylabel("y",color="#555",fontsize=7)
    ax.set_zlabel("z",color="#555",fontsize=7)
    ax.tick_params(colors="#333",labelsize=5)
    ax.xaxis.pane.fill=False; ax.yaxis.pane.fill=False; ax.zaxis.pane.fill=False
    ax.set_facecolor("#0a0a1a")

    buf = io.BytesIO()
    plt.savefig(buf,format="png",dpi=110,bbox_inches="tight",facecolor="#0a0a1a")
    plt.close(); buf.seek(0)
    frames.append(Image.open(buf).copy())
    if fi % 10 == 0: print(f"  frame {fi}/90")

frames[0].save(OUTPUT,save_all=True,append_images=frames[1:],
               duration=55,loop=0)
print(f"✅ {OUTPUT}")