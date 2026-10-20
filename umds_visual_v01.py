import hashlib
import html
import json
import os
from pathlib import Path

import umds_stdlib_v05 as model

OUT = Path("umds_v05_images")
OUT.mkdir(exist_ok=True)
PARENT_SCRIPT = Path("umds_stdlib_v05.py")
PARENT_RECEIPT = Path("umds_stdlib_receipt_v05.json")
VISUAL_RECEIPT = Path("umds_visual_receipt_v01.json")
COLORS = {
    "A": "#2563eb",
    "M": "#dc2626",
    "C": "#16a34a",
    "eta": "#9333ea",
    "branch_a": "#0f766e",
    "branch_b": "#c2410c",
    "grid": "#d1d5db",
    "text": "#111827",
    "muted": "#6b7280",
    "pass": "#16a34a",
    "fail": "#dc2626",
}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def trajectory(branch, dt=0.01, duration=60.0, sample_every=10):
    state = (1.0, 0.05, 0.0, 0.5)
    steps = int(round(duration / dt))
    rows = [(0.0,) + state]
    for step in range(1, steps + 1):
        state = model.rk4(state, dt, branch)
        if step % sample_every == 0 or step == steps:
            rows.append((step * dt,) + state)
    return rows


def svg_start(width, height, title):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{width/2}" y="34" text-anchor="middle" font-family="sans-serif" font-size="24" font-weight="700" fill="{COLORS["text"]}">{html.escape(title)}</text>',
    ]


def line(x1, y1, x2, y2, color, width=1, dash=None):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{color}" stroke-width="{width}"{dash_attr}/>'


def text(x, y, value, size=13, anchor="start", color=None, weight="400"):
    color = color or COLORS["text"]
    return f'<text x="{x:.2f}" y="{y:.2f}" text-anchor="{anchor}" font-family="sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}">{html.escape(str(value))}</text>'


def polyline(points, color, width=2.5):
    encoded = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
    return f'<polyline points="{encoded}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"/>'


def map_points(rows, column, x0, y0, width, height, xmin, xmax, ymin, ymax):
    result = []
    dx = max(xmax - xmin, 1e-15)
    dy = max(ymax - ymin, 1e-15)
    for row in rows:
        x = x0 + (row[0] - xmin) / dx * width
        y = y0 + height - (row[column] - ymin) / dy * height
        result.append((x, y))
    return result


def add_axes(parts, x0, y0, width, height, xmin, xmax, ymin, ymax, xlabel, ylabel):
    parts.append(line(x0, y0, x0, y0 + height, COLORS["text"], 1.5))
    parts.append(line(x0, y0 + height, x0 + width, y0 + height, COLORS["text"], 1.5))
    for i in range(6):
        gx = x0 + width * i / 5
        gy = y0 + height * i / 5
        parts.append(line(gx, y0, gx, y0 + height, COLORS["grid"], 0.8, "4 4"))
        parts.append(line(x0, gy, x0 + width, gy, COLORS["grid"], 0.8, "4 4"))
        xv = xmin + (xmax - xmin) * i / 5
        yv = ymax - (ymax - ymin) * i / 5
        parts.append(text(gx, y0 + height + 20, f"{xv:.1f}", 11, "middle", COLORS["muted"]))
        parts.append(text(x0 - 9, gy + 4, f"{yv:.2f}", 11, "end", COLORS["muted"]))
    parts.append(text(x0 + width / 2, y0 + height + 43, xlabel, 13, "middle", COLORS["text"], "600"))
    parts.append(text(x0 - 50, y0 + height / 2, ylabel, 13, "middle", COLORS["text"], "600"))


def write_timeseries(branches):
    width, height = 1200, 820
    parts = svg_start(width, height, "UMDS v0.5 — State trajectories")
    legend_x = 420
    for index, name in enumerate(("A", "M", "C", "eta")):
        x = legend_x + index * 120
        parts.append(line(x, 62, x + 28, 62, COLORS[name], 4))
        parts.append(text(x + 36, 67, name, 13))
    panels = [
        ("c_proxy_s16", 90, "Branch A — R = C"),
        ("ledger_perfect_zero", 445, "Branch B0 — R = 0"),
    ]
    for branch, top, label in panels:
        rows = branches[branch]
        x0, y0, w, h = 105, top + 45, 1010, 250
        parts.append(text(x0, top + 22, label, 17, "start", COLORS["text"], "700"))
        add_axes(parts, x0, y0, w, h, 0.0, 60.0, 0.0, 1.05, "time", "state")
        for column, name in enumerate(("A", "M", "C", "eta"), start=1):
            points = map_points(rows, column, x0, y0, w, h, 0.0, 60.0, 0.0, 1.05)
            parts.append(polyline(points, COLORS[name]))
    parts.append(text(width / 2, height - 18, "FORMAL_MODEL · CALCULABLE ≠ VERIFIED ≠ PUBLISHED", 12, "middle", COLORS["muted"]))
    parts.append("</svg>")
    path = OUT / "umds_v05_timeseries.svg"
    path.write_text("\n".join(parts), encoding="utf-8")
    return path


def write_phase(branches):
    width, height = 1000, 700
    parts = svg_start(width, height, "UMDS v0.5 — Phase plane M versus C")
    x0, y0, w, h = 110, 90, 800, 500
    all_m = [row[2] for rows in branches.values() for row in rows]
    all_c = [row[3] for rows in branches.values() for row in rows]
    xmin, xmax = min(all_m), max(all_m)
    ymin, ymax = min(all_c), max(all_c)
    xpad = max((xmax - xmin) * 0.08, 0.02)
    ypad = max((ymax - ymin) * 0.08, 0.02)
    xmin, xmax = xmin - xpad, xmax + xpad
    ymin, ymax = ymin - ypad, ymax + ypad
    add_axes(parts, x0, y0, w, h, xmin, xmax, ymin, ymax, "M", "C")
    mapping = [
        ("c_proxy_s16", COLORS["branch_a"], "Branch A: R=C"),
        ("ledger_perfect_zero", COLORS["branch_b"], "Branch B0: R=0"),
    ]
    for idx, (branch, color, label) in enumerate(mapping):
        rows = [(row[2], row[3]) for row in branches[branch]]
        points = []
        for m, c in rows:
            px = x0 + (m - xmin) / (xmax - xmin) * w
            py = y0 + h - (c - ymin) / (ymax - ymin) * h
            points.append((px, py))
        parts.append(polyline(points, color, 3))
        parts.append(line(640, 55 + idx * 24, 675, 55 + idx * 24, color, 4))
        parts.append(text(685, 60 + idx * 24, label, 13))
        endx, endy = points[-1]
        parts.append(f'<circle cx="{endx:.2f}" cy="{endy:.2f}" r="6" fill="{color}"/>')
    parts.append(text(width / 2, height - 22, "Endpoint circles mark t=60; trajectories are numerical fixtures, not observations.", 12, "middle", COLORS["muted"]))
    parts.append("</svg>")
    path = OUT / "umds_v05_phase.svg"
    path.write_text("\n".join(parts), encoding="utf-8")
    return path


def write_receipt_image(receipt):
    width, height = 1180, 760
    parts = svg_start(width, height, "UMDS v0.5 — Runtime Receipt")
    passed = receipt["all_execution_gates_passed"]
    status_color = COLORS["pass"] if passed else COLORS["fail"]
    parts.append(f'<rect x="60" y="62" width="1060" height="70" rx="12" fill="{status_color}" opacity="0.13"/>')
    parts.append(text(90, 105, "PASS" if passed else "FAIL", 30, "start", status_color, "800"))
    parts.append(text(250, 102, receipt["version"], 19, "start", COLORS["text"], "700"))
    parts.append(text(250, 124, "Truth layer: FORMAL_MODEL · External validation: NOT_RUN", 13, "start", COLORS["muted"]))
    y = 175
    for result in receipt["results"]:
        branch = result["branch"]
        roots = result["fixed_points"]["roots"]
        branch_pass = result["execution_pass"]
        color = COLORS["pass"] if branch_pass else COLORS["fail"]
        parts.append(f'<rect x="60" y="{y}" width="1060" height="220" rx="12" fill="#f9fafb" stroke="#d1d5db"/>')
        parts.append(text(85, y + 34, branch, 18, "start", COLORS["text"], "700"))
        parts.append(text(1085, y + 34, "PASS" if branch_pass else "FAIL", 17, "end", color, "800"))
        root = roots[0]["state"] if roots else [float("nan")] * 4
        parts.append(text(85, y + 68, f"Fixed point: A={root[0]:.6f}, M={root[1]:.6f}, C={root[2]:.6f}, eta={root[3]:.6f}", 14))
        gy = y + 100
        for gate_index, (gate, value) in enumerate(result["execution_gates"].items()):
            row = gate_index // 3
            col = gate_index % 3
            bx = 85 + col * 330
            by = gy + row * 48
            gate_color = COLORS["pass"] if value else COLORS["fail"]
            parts.append(f'<rect x="{bx}" y="{by}" width="300" height="34" rx="7" fill="{gate_color}" opacity="0.12"/>')
            parts.append(text(bx + 12, by + 22, gate, 12, "start", COLORS["text"], "600"))
            parts.append(text(bx + 285, by + 22, "PASS" if value else "FAIL", 12, "end", gate_color, "800"))
        y += 245
    parts.append(text(60, height - 54, "Script SHA-256: " + receipt["script_sha256"], 11, "start", COLORS["muted"]))
    parts.append(text(60, height - 32, "Manifest SHA-256: " + receipt["manifest_sha256"], 11, "start", COLORS["muted"]))
    parts.append("</svg>")
    path = OUT / "umds_v05_receipt.svg"
    path.write_text("\n".join(parts), encoding="utf-8")
    return path


def main():
    receipt = json.loads(PARENT_RECEIPT.read_text(encoding="utf-8"))
    actual_script_hash = sha256(PARENT_SCRIPT)
    if actual_script_hash != receipt["script_sha256"]:
        raise RuntimeError("parent script hash mismatch")
    branches = {
        "c_proxy_s16": trajectory("c_proxy_s16"),
        "ledger_perfect_zero": trajectory("ledger_perfect_zero"),
    }
    images = [
        write_timeseries(branches),
        write_phase(branches),
        write_receipt_image(receipt),
    ]
    image_hashes = {path.name: sha256(path) for path in images}
    visual_receipt = {
        "artifact": "UMDS-V05-VISUALS-v0.1",
        "truth_layer": "FORMAL_MODEL",
        "parent_script": str(PARENT_SCRIPT),
        "parent_script_sha256": actual_script_hash,
        "parent_receipt": str(PARENT_RECEIPT),
        "parent_receipt_sha256": sha256(PARENT_RECEIPT),
        "images": image_hashes,
        "external_validation": "NOT_RUN",
        "claim_firewall": "VISUALIZATION != MEASUREMENT != VERIFICATION",
    }
    temporary = Path(str(VISUAL_RECEIPT) + ".tmp")
    temporary.write_text(json.dumps(visual_receipt, indent=2, sort_keys=True), encoding="utf-8")
    json.loads(temporary.read_text(encoding="utf-8"))
    os.replace(temporary, VISUAL_RECEIPT)
    print(json.dumps({
        "status": "PASS",
        "images": [str(path) for path in images],
        "visual_receipt": str(VISUAL_RECEIPT),
        "image_sha256": image_hashes,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
