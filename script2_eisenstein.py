import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

OUTPUT = "/sdcard/DCIM/miya_eisenstein.png"

fig, ax = plt.subplots(figsize=(8, 7), facecolor="#0f0f1e")
ax.set_facecolor("#0f0f1e")

# Eisenstein norm P = a²+ab+b²
# plot all integer (a,b) with |a|,|b|<=9 coloured by P value
vals = {0:"#555555", 1:"#ffaa00", 9:"#00ccff", 81:"#ff4466"}
for a in range(-9, 10):
    for b in range(-9, 10):
        P = a*a + a*b + b*b
        col = vals.get(P, "#1a1a2e")
        ax.scatter(a, b, color=col, s=18, zorder=2)

# highlight the decomposition 91=81+9+1+0
# one possible (a,b) per P: P=81→(9,-9), P=9→(3,0), P=1→(1,0), P=0→(0,0)
highlight = [(9,-9,"#ff4466","P=81"),(3,0,"#00ccff","P=9"),
             (1,0,"#ffaa00","P=1"),(0,0,"#555555","P=0")]
for (a,b,c,lbl) in highlight:
    ax.scatter(a, b, color=c, s=120, edgecolors="white", linewidths=1.5, zorder=5)
    ax.annotate(lbl, (a,b), textcoords="offset points",
                xytext=(8,6), color=c, fontsize=9, fontweight="bold")

# legend
patches = [mpatches.Patch(color=v, label=f"P = {k}") for k,v in vals.items()]
ax.legend(handles=patches, loc="upper left",
          facecolor="#1a1a2e", edgecolor="#555", labelcolor="white", fontsize=9)

ax.set_title("Eisenstein 格點：P_j ∈ {0,1,9,81}，ΣP_j = 91 = 81+9+1+0",
             color="gold", fontsize=11, pad=12)
ax.set_xlabel("ρ₁", color="#aaa"); ax.set_ylabel("ρ₂", color="#aaa")
ax.tick_params(colors="#666")
for spine in ax.spines.values(): spine.set_edgecolor("#333")
ax.set_xlim(-10,10); ax.set_ylim(-10,10)
ax.grid(True, color="#222", linewidth=0.5)

plt.tight_layout()
plt.savefig(OUTPUT, dpi=150)
print(f"✅ Saved: {OUTPUT}")