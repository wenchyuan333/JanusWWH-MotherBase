from PIL import Image, ImageDraw, ImageFont
import os

OUTPUT = "/sdcard/DCIM/miya_chain.gif"

steps = [
    ("①", "magic square"),
    ("②③", "結構分解\nf = Σ uⱼ(kⱼ·x)"),
    ("④", "截面和整除\nuⱼ ∈ (1/3)ℤ"),
    ("⑧", "α-矛盾法\nuⱼ ∈ ℤ  ✓"),
    ("⑨", "Q_j ∈ 81ℤ\nP_j = ρ₁²+ρ₁ρ₂+ρ₂² ∈ ℤ"),
    ("⑩", "ΣP_j = 91\n≤ 81 per j"),
    ("base-3", "唯一分解\n91 = 81+9+1+0\n→ 至少一 P_j = 0"),
    ("✅", "digit cube\n仿射 base-3  □"),
]

BG   = (15, 15, 30)
GOLD = (255, 210, 80)
CYAN = (80, 220, 220)
WHITE = (240, 240, 240)
W, H = 640, 380

frames = []
for i in range(len(steps)):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # title
    d.text((20, 16), "甲線整除鏈 d=3 封口", fill=GOLD)
    # draw all steps up to i
    for j, (num, label) in enumerate(steps[:i+1]):
        x = 40
        y = 60 + j * 38
        col = CYAN if j == i else WHITE
        d.rectangle([x-4, y-4, x+580, y+28], outline=col, width=1 if j<i else 2)
        d.text((x+4, y+4), f"{num}  {label.replace(chr(10),'  ')}", fill=col)
        if j < i:
            d.text((x+260, y+32), "↓", fill=(150,150,150))
    frames.append(img.copy())
    # hold last frame longer
    if i == len(steps)-1:
        frames += [img.copy()] * 8

frames[0].save(
    OUTPUT,
    save_all=True,
    append_images=frames[1:],
    duration=900,
    loop=0,
)
print(f"✅ Saved: {OUTPUT}")