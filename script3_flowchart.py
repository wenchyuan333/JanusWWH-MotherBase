import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

OUTPUT = "/sdcard/DCIM/miya_flowchart.png"

nodes = [
    (0.5, 0.95, "magic square", "#2a1a4a", "#cc88ff"),
    (0.5, 0.85, "① 結構分解  f = Σ uⱼ(kⱼ·x)", "#0a2a3a", "#44bbdd"),
    (0.5, 0.75, "②③ 截面和整除  uⱼ ∈ (1/3)ℤ", "#0a2a3a", "#44bbdd"),
    (0.5, 0.65, "④⑤ 像素公式 + Eisenstein 範數  Qⱼ ∈ 9ℤ", "#0a2a3a", "#44bbdd"),
    (0.5, 0.55, "⑧ α-矛盾法  uⱼ ∈ ℤ  ✦NEW", "#1a2a10", "#88ff66"),
    (0.5, 0.45, "⑨ Qⱼ ∈ 81ℤ，Pⱼ ∈ ℤ  ✦NEW", "#1a2a10", "#88ff66"),
    (0.5, 0.35, "⑩ ΣPⱼ = 91，Pⱼ ≤ 81", "#2a1a00", "#ffcc44"),
    (0.5, 0.25, "base-3 唯一分解  91=81+9+1+0\n→ 至少一 Pⱼ=0", "#2a1a00", "#ffcc44"),
    (0.5, 0.13, "✅  仿射 base-3 digit cube  □", "#1a0a0a", "#ff5566"),
]

fig, ax = plt.subplots(figsize=(9, 10), facecolor="#0a0a1a")
ax.set_facecolor("#0a0a1a")
ax.axis("off")

bw, bh = 0.62, 0.065
for (x, y, label, bg, fg) in nodes:
    rect = mpatches.FancyBboxPatch(
        (x - bw/2, y - bh/2), bw, bh,
        boxstyle="round,pad=0.01",
        facecolor=bg, edgecolor=fg, linewidth=1.8
    )
    ax.add_patch(rect)
    ax.text(x, y, label, ha="center", va="center",
            color=fg, fontsize=9.2, fontweight="bold",
            multialignment="center")

# arrows
for i in range(len(nodes)-1):
    _, y1, *_ = nodes[i]
    _, y2, *_ = nodes[i+1]
    ax.annotate("", xy=(0.5, y2+bh/2+0.002),
                xytext=(0.5, y1-bh/2-0.002),
                arrowprops=dict(arrowstyle="->",
                                color="#888888", lw=1.4))

ax.set_title("甲線整除鏈  d=3  完整封口（2026-08-26）",
             color="gold", fontsize=12, pad=8)
ax.set_xlim(0,1); ax.set_ylim(0,1)

plt.tight_layout()
plt.savefig(OUTPUT, dpi=160, bbox_inches="tight")
print(f"✅ Saved: {OUTPUT}")