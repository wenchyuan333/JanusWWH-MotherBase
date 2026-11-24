#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LOOP-001-VIZ-001 v0.2
三步核實閉環方程式結構——100% 逼近視覺動畫
Termux 環境：python loop001_viz.py [--lang auto|zh|en] [--open|--no-open] [--share|--no-share]
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import animation, font_manager

# ─── 常數 ───────────────────────────────────────────────
BASELINE_TIMESTAMP = "2026-08-22T08:49+08:00"
C0  = {"A": 0.88, "B": 0.29, "C": 0.029}
ETA = {"A": 0.06, "B": 0.29, "C": 0.029}
MILESTONES = [0.90, 0.95, 0.99]
FRAMES_DEFAULT = 100

STRINGS = {
    "zh": {
        "title":    "LOOP-001｜三步核實閉環逼近 100%",
        "subtitle": "C_total(t+1) = 1 − (1 − C_total(t))·(1 − η(t))",
        "xlabel":   "輪次 t",
        "ylabel":   "覆蓋率 C",
        "legend":   ["軸 A（外部法度）", "軸 B（掛谷偏好）",
                     "軸 C（後繼歸納）", "C_total（幾何平均）"],
        "milestone": "達 {p}%: t = {t}",
        "not_reach": "未達 {p}% 於 {n} 輪內",
        "baseline":  f"基線 {BASELINE_TIMESTAMP}",
    },
    "en": {
        "title":    "LOOP-001 | 3-Source Verification Loop -> 100%",
        "subtitle": "C_total(t+1) = 1 - (1 - C_total(t)) * (1 - eta(t))",
        "xlabel":   "iteration t",
        "ylabel":   "coverage C",
        "legend":   ["Axis A (external norms)", "Axis B (Kakeya prior)",
                     "Axis C (successor induction)", "C_total (geo-mean)"],
        "milestone": "reach {p}%: t = {t}",
        "not_reach": "not reach {p}% within {n} iters",
        "baseline":  f"baseline {BASELINE_TIMESTAMP}",
    },
}

# ─── CJK 偵測（Termux 預設 DejaVu Sans 無 CJK glyph） ────
def detect_lang(pref: str) -> str:
    if pref in ("zh", "en"):
        return pref
    # auto：檢查系統是否有 CJK 字型
    for f in font_manager.fontManager.ttflist:
        name = f.name.lower()
        if any(k in name for k in ("noto sans cjk", "noto sans tc",
                                    "wenquanyi", "source han", "pingfang",
                                    "microsoft yahei", "simhei", "heiti")):
            # 找到 CJK 字型 → 設為預設
            matplotlib.rcParams["font.sans-serif"] = [f.name] + \
                matplotlib.rcParams["font.sans-serif"]
            return "zh"
    return "en"

# ─── 模型 ───────────────────────────────────────────────
def simulate(frames: int):
    Ca = np.zeros(frames + 1); Ca[0] = C0["A"]
    Cb = np.zeros(frames + 1); Cb[0] = C0["B"]
    Cc = np.zeros(frames + 1); Cc[0] = C0["C"]
    for t in range(frames):
        Ca[t+1] = 1 - (1 - Ca[t]) * (1 - ETA["A"])
        Cb[t+1] = 1 - (1 - Cb[t]) * (1 - ETA["B"])
        Cc[t+1] = 1 - (1 - Cc[t]) * (1 - ETA["C"])
    Ctot = (Ca * Cb * Cc) ** (1/3)
    return Ca, Cb, Cc, Ctot

def report_milestones(Ctot, frames, S):
    for p in MILESTONES:
        idx = np.where(Ctot >= p)[0]
        if len(idx):
            print(S["milestone"].format(p=int(p*100), t=int(idx[0])))
        else:
            print(S["not_reach"].format(p=int(p*100), n=frames))

# ─── 動畫 ───────────────────────────────────────────────
def render(outfile: Path, frames: int, S: dict):
    Ca, Cb, Cc, Ctot = simulate(frames)
    report_milestones(Ctot, frames, S)

    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=110)
    ax.set_xlim(0, frames)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel(S["xlabel"])
    ax.set_ylabel(S["ylabel"])
    ax.set_title(S["title"] + "\n" + S["subtitle"], fontsize=11)
    ax.axhline(1.0, color="lightgray", ls="--", lw=0.8)
    for p in MILESTONES:
        ax.axhline(p, color="lightgray", ls=":", lw=0.6)
    ax.text(0.99, 0.02, S["baseline"], transform=ax.transAxes,
            ha="right", va="bottom", fontsize=8, color="gray")

    (la,) = ax.plot([], [], lw=1.5, label=S["legend"][0])
    (lb,) = ax.plot([], [], lw=1.5, label=S["legend"][1])
    (lc,) = ax.plot([], [], lw=1.5, label=S["legend"][2])
    (lt,) = ax.plot([], [], lw=2.5, color="black", label=S["legend"][3])
    ax.legend(loc="center right", fontsize=9)

    xs = np.arange(frames + 1)
    def init():
        for ln in (la, lb, lc, lt):
            ln.set_data([], [])
        return la, lb, lc, lt
    def update(i):
        la.set_data(xs[:i+1], Ca[:i+1])
        lb.set_data(xs[:i+1], Cb[:i+1])
        lc.set_data(xs[:i+1], Cc[:i+1])
        lt.set_data(xs[:i+1], Ctot[:i+1])
        return la, lb, lc, lt

    anim = animation.FuncAnimation(fig, update, init_func=init,
                                   frames=frames+1, interval=80, blit=True)
    print(f"寫入 {outfile.name}…" if S is STRINGS["zh"]
          else f"writing {outfile.name}…")
    writer = animation.FFMpegWriter(fps=15, bitrate=1800)
    anim.save(str(outfile), writer=writer)
    print(f"完成：{outfile}" if S is STRINGS["zh"] else f"done: {outfile}")

# ─── Termux 整合 ────────────────────────────────────────
def termux_open(path: Path):
    if not shutil.which("termux-open"):
        print("[skip open] termux-open 不存在（pkg install termux-api）",
              file=sys.stderr)
        return
    subprocess.run(["termux-open", str(path)], check=False)

def termux_share(path: Path):
    if not shutil.which("termux-share"):
        print("[skip share] termux-share 不存在（pkg install termux-api）",
              file=sys.stderr)
        return
    # -a send：叫出系統分享 sheet；手選 Notion → ALBUM 頁
    subprocess.run(["termux-share", "-a", "send", str(path)], check=False)

# ─── 主入口 ─────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outfile", default="loop001_viz.mp4",
                    help="輸出檔名（副檔名決定格式：.mp4/.gif）")
    ap.add_argument("--frames", type=int, default=FRAMES_DEFAULT)
    ap.add_argument("--lang", choices=["auto", "zh", "en"], default="auto")
    ap.add_argument("--open", dest="do_open", action="store_true", default=True)
    ap.add_argument("--no-open", dest="do_open", action="store_false")
    ap.add_argument("--share", dest="do_share", action="store_true", default=True)
    ap.add_argument("--no-share", dest="do_share", action="store_false")
    args = ap.parse_args()

    lang = detect_lang(args.lang)
    S = STRINGS[lang]
    outfile = Path(args.outfile).resolve()

    render(outfile, args.frames, S)

    if args.do_open:
        termux_open(outfile)
    if args.do_share:
        termux_share(outfile)

if __name__ == "__main__":
    main()