import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image
import io

OUTPUT = "/sdcard/DCIM/miya_3d_chain.gif"

steps = [
    ("magic square",          1.0),
    ("Decomp: f=sum u_j",     0.9),
    ("u_j in (1/3)Z",         0.75),
    ("Q_j in 9Z",             0.6),
    ("alpha-contra => u_j inZ",0.4),
    ("Q_j in 81Z, P_j inZ",   0.25),
    ("Sum P_j = 91, P_j<=81", 0.12),
    ("91=81+9+1+0 unique",    0.04),
    ("digit cube  QED",       0.0),
]

N = len(steps)
COLS_ACTIVE = ["#cc88ff","#44bbdd","#44bbdd","#44bbdd",
               "#88ff66","#88ff66","#ffcc44","#ffcc44","#ff5566"]
COL_DONE = "#334455"

frames = []
print("Rendering chain waterfall frames...")

def make_frame(active_up_to, alpha_anim=1.0):
    fig = plt.figure(figsize=(8,6), facecolor="#0a0a1a")
    ax = fig.add_subplot(111, projection="3d", facecolor="#0a0a1a")

    for i, (label, z) in enumerate(steps):
        y_pos = N - i
        if i < active_up_to:
            col = COL_DONE; a = 0.4
        elif i == active_up_to:
            col = COLS_ACTIVE[i]; a = alpha_anim
        else:
            col = "#111122"; a = 0.15

        # bar
        dx, dy, dz = 0.6, 0.5, z if z > 0.02 else 0.02
        verts = [[(0,y_pos,0),(dx,y_pos,0),(dx,y_pos,dz),(0,y_pos,dz)]]
        poly = Poly3DCollection(verts, alpha=a*0.7)
        poly.set_facecolor(col); poly.set_edgecolor(col)
        ax.add_collection3d(poly)

        # label
        ax.text(0.7, y_pos+0.15, z+0.03, label,
                color=col if i <= active_up_to else "#333355",
                fontsize=7.5, fontweight="bold" if i==active_up_to else "normal",
                alpha=a)

    ax.set_xlim(0,2); ax.set_ylim(0,N+1); ax.set_zlim(0,1.1)
    ax.set_xlabel("", color="#333"); ax.set_ylabel("Step", color="#666", fontsize=8)
    ax.set_zlabel("Set size (log scale)", color="#666", fontsize=8)
    ax.set_title("Jia-Xian Chain d=3  Closure", color="gold", fontsize=10, pad=8)
    ax.view_init(elev=20, azim=-55)
    ax.tick_params(colors="#444", labelsize=6)
    ax.xaxis.pane.fill=False; ax.yaxis.pane.fill=False; ax.zaxis.pane.fill=False
    ax.grid(True, color="#1a1a2a", linewidth=0.3)
    return fig

# Build frames: reveal each step, then hold, then rotate
for i in range(N):
    # fade-in frames for step i
    for alpha in [0.3, 0.6, 1.0]:
        fig = make_frame(i, alpha)
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=100, bbox_inches="tight", facecolor="#0a0a1a")
        plt.close(); buf.seek(0)
        frames.append(Image.open(buf).copy())
    # hold frames
    for _ in range(4):
        frames.append(frames[-1].copy())

# final rotation
print("  Adding final rotation...")
for azim in range(-55, -55+90, 3):
    fig = make_frame(N-1, 1.0)
    ax = fig.axes[0]; ax.view_init(elev=20, azim=azim)
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=100, bbox_inches="tight", facecolor="#0a0a1a")
    plt.close(); buf.seek(0)
    frames.append(Image.open(buf).copy())

frames[0].save(OUTPUT, save_all=True, append_images=frames[1:],
               duration=120, loop=0)
print(f"✅ {OUTPUT}")