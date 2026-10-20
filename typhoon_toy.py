#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TYPHOON-TOY-001 | West Pacific TC track toy model (MAX coverage version)
CLAIM: SYMBOLIC (illustrative toy model, NOT a forecast)
Seed: CWA typhoon bulletin 2026-08-24 14:00 (real positions)
Dynamics: constant steering + beta drift + seeded ensemble noise
Coverage: vectorized ensemble + Luoshu 3x3 overlay + coverage readout
Deps: numpy, matplotlib, Pillow
Run:  python3 typhoon_toy.py
Out:  ~/storage/pictures/typhoon_toy.gif (fallback: $HOME)
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

# ---- initial conditions (CWA 2026-08-24 14:00) ----
# name, latN, lonE, heading_deg, speed_kmh, vmax_ms, p_hpa, color
SYSTEMS = [
    ("SAUDEL", 24.5, 134.8, 292.5, 24.0, 51.0, 925, "#ff5555"),
    ("NARRA",  20.2, 107.5, 157.5,  7.0, 18.0, 998, "#ffcc55"),
    ("ATSANI", 16.0, 138.1,   0.0, 20.0, 18.0, 998, "#55ccff"),
    ("TD24",   24.8, 118.5, 292.5, 15.0, 12.0, 1000, "#cc88ff"),
]

# ---- toy parameters (NOT calibrated) ----
DT_H   = 3.0      # step, hours
HOURS  = 72.0     # horizon, hours
N_ENS  = 16       # ensemble members per system (MAX)
BETA_U = -1.2     # beta drift westward, m/s (scaled by intensity)
BETA_V = +2.4     # beta drift poleward, m/s
NOISE  = 0.8      # steering noise, m/s
SEED   = 20260824

LON_MIN, LON_MAX = 100.0, 150.0
LAT_MIN, LAT_MAX = 5.0, 35.0

# ---- Luoshu 3x3 magic square (SYMBOLIC overlay, does NOT affect dynamics) ----
LUOSHU = [[4, 9, 2],
          [3, 5, 7],
          [8, 1, 6]]


def run_tracks(lat0, lon0, heading, speed, vmax, n_ens, seed):
    """Vectorized ensemble integration -> (lats, lons) arrays (n_ens, steps+1)."""
    rng = np.random.default_rng(seed)
    u0 = speed * np.sin(np.radians(heading))   # eastward km/h
    v0 = speed * np.cos(np.radians(heading))   # northward km/h
    f = vmax / 50.0
    u_b = BETA_U * f / 3.6
    v_b = BETA_V * f / 3.6
    steps = int(round(HOURS / DT_H))
    lat = np.full(n_ens, float(lat0))
    lon = np.full(n_ens, float(lon0))
    lats = np.empty((n_ens, steps + 1))
    lons = np.empty((n_ens, steps + 1))
    lats[:, 0], lons[:, 0] = lat0, lon0
    for s in range(steps):
        u = u0 + u_b + rng.normal(0.0, NOISE, n_ens) / 3.6
        v = v0 + v_b + rng.normal(0.0, NOISE, n_ens) / 3.6
        dlon = u / (111.0 * np.cos(np.radians(lat)))
        dlat = v / 111.0
        lon = lon + dlon * DT_H
        lat = lat + dlat * DT_H
        lats[:, s + 1] = lat
        lons[:, s + 1] = lon
    return lats, lons


def coverage(all_lats, all_lons):
    """Return (Luoshu cells hit, 1x1 deg cells hit, total 1x1 deg cells)."""
    luo = np.zeros((3, 3), dtype=bool)
    lon_e = np.linspace(LON_MIN, LON_MAX, 4)
    lat_e = np.linspace(LAT_MIN, LAT_MAX, 4)
    for i in range(3):
        for j in range(3):
            in_cell = ((all_lons >= lon_e[j]) & (all_lons < lon_e[j + 1]) &
                       (all_lats >= lat_e[2 - i]) & (all_lats < lat_e[3 - i]))
            luo[i, j] = in_cell.any()
    nlon = int(LON_MAX - LON_MIN)
    nlat = int(LAT_MAX - LAT_MIN)
    grid = np.zeros((nlat, nlon), dtype=bool)
    ilon = np.clip((all_lons - LON_MIN).astype(int), 0, nlon - 1)
    ilat = np.clip((LAT_MAX - all_lats).astype(int), 0, nlat - 1)
    grid[ilat, ilon] = True
    return int(luo.sum()), int(grid.sum()), nlat * nlon


def draw_luoshu(ax):
    lon_e = np.linspace(LON_MIN, LON_MAX, 4)
    lat_e = np.linspace(LAT_MIN, LAT_MAX, 4)
    for i in range(3):
        for j in range(3):
            x0, x1 = lon_e[j], lon_e[j + 1]
            y0, y1 = lat_e[2 - i], lat_e[3 - i]
            ax.add_patch(plt.Rectangle((x0, y0), x1 - x0, y1 - y0,
                                       fill=False, edgecolor="white",
                                       lw=0.6, alpha=0.30, zorder=1))
            ax.text((x0 + x1) / 2, (y0 + y1) / 2, str(LUOSHU[i][j]),
                    fontsize=9, color="white", alpha=0.45,
                    ha="center", va="center", zorder=1)
    ax.text(LON_MAX - 0.5, LAT_MIN + 1.5,
            "Luoshu 3x3\n4 9 2\n3 5 7\n8 1 6\n"
            "rows/cols/diag = 15\n"
            "opposite pairs = 10\n"
            "(SYMBOLIC overlay,\n not dynamics)",
            fontsize=7, color="white", alpha=0.75,
            ha="right", va="bottom", zorder=4)


def main():
    tracks = []
    for (name, lat, lon, heading, speed, vmax, p, color) in SYSTEMS:
        lats, lons = run_tracks(lat, lon, heading, speed, vmax, N_ENS, SEED)
        tracks.append({"name": name, "color": color, "lats": lats, "lons": lons})

    # coverage readout (all systems, all members)
    all_lats = np.concatenate([t["lats"] for t in tracks])
    all_lons = np.concatenate([t["lons"] for t in tracks])
    luo_hit, cells_hit, cells_total = coverage(all_lats, all_lons)
    print("coverage: Luoshu cells %d/9, 1x1deg cells %d/%d (%.1f%%)"
          % (luo_hit, cells_hit, cells_total, 100.0 * cells_hit / cells_total))

    n_steps = tracks[0]["lats"].shape[1] - 1
    fig, ax = plt.subplots(figsize=(8, 5.5), dpi=110)
    ax.set_xlim(LON_MIN, LON_MAX)
    ax.set_ylim(LAT_MIN, LAT_MAX)
    ax.set_xlabel("Longitude (E)")
    ax.set_ylabel("Latitude (N)")
    ax.grid(True, alpha=0.3)

    # Taiwan marker (approx, for orientation only)
    ax.plot(121.0, 23.7, marker="s", color="white", mec="gray", ms=7, zorder=5)
    ax.text(121.0, 24.8, "Taiwan", fontsize=8, color="gray", ha="center")

    draw_luoshu(ax)   # Luoshu 3x3 overlay (SYMBOLIC, visual only)

    seen = set()
    for t in tracks:
        n = t["lats"].shape[0]
        t["lines"], t["heads"] = [], []
        for k in range(n):
            ln, = ax.plot([], [], lw=1.0, alpha=0.35, color=t["color"])
            hd, = ax.plot([], [], "o", ms=4, color=t["color"], zorder=6)
            t["lines"].append(ln)
            t["heads"].append(hd)
        if t["name"] not in seen:
            seen.add(t["name"])
            ax.text(t["lons"][0, 0] + 0.6, t["lats"][0, 0] + 0.6,
                    t["name"], fontsize=8, color=t["color"])

    artists = [a for t in tracks for a in t["lines"] + t["heads"]]

    def update(s):
        for t in tracks:
            for k in range(t["lats"].shape[0]):
                t["lines"][k].set_data(t["lons"][k, : s + 1], t["lats"][k, : s + 1])
                t["heads"][k].set_data([t["lons"][k, s]], [t["lats"][k, s]])
        ax.set_title("TYPHOON-TOY-001 MAX  t=%3dh/%dh  (SYMBOLIC toy, NOT a forecast)"
                     % (int(s * DT_H), int(HOURS)))
        return artists

    ani = FuncAnimation(fig, update, frames=n_steps + 1, interval=100, blit=True)
    outdir = os.path.join(os.path.expanduser("~"), "storage", "pictures")
    if not os.path.isdir(outdir):
        outdir = os.path.expanduser("~")
    out = os.path.join(outdir, "typhoon_toy.gif")
    ani.save(out, writer=PillowWriter(fps=10))
    print("GIF saved:", out)
    print("DISCLAIMER: SYMBOLIC toy model. Not a forecast. "
          "Use CWA official products for decisions.")

    # trigger Android media scan so the GIF shows in the gallery immediately
    try:
        import subprocess
        subprocess.run(["termux-media-scan", out], check=False, timeout=30)
        print("media-scan: triggered (gallery should show it now)")
    except Exception as e:
        print("media-scan: skipped (%s)" % e)


if __name__ == "__main__":
    main()