import json, math

PI_LIT = [3, 2, 1, 4, 7, 6, 5, 8]  # 文獻指紋（被測物）
# 量到真實迷宮時：把量出的踩環順序換進上面這行，同一支程式直接對帳
CENTER = 8
OUTSIDE_R = 8.0

def radius(level):
    if level == CENTER:
        return 0.0
    return float(CENTER - level)   # 環 1 最外 (r=7) ... 環 7 最內 (r=1)

def polar_line(r0, r1, theta, tag, n):
    out = []
    for i in range(n):
        r = r0 + (r1 - r0) * i / (n - 1)
        out.append((r * math.cos(theta), r * math.sin(theta), tag))
    return out

def polar_arc(r, t0, t1, tag, n):
    out = []
    for i in range(n):
        t = t0 + (t1 - t0) * i / (n - 1)
        out.append((r * math.cos(t), r * math.sin(t), tag))
    return out

def build_walk():
    # 古典幾何：底部入口；弧掃 300 度、左右交替；徑向連接器換環
    seq = [0] + PI_LIT
    pts = []
    theta = -math.pi / 2.0
    sweep = math.radians(300.0)
    direction = 1
    first = seq[1]
    pts += polar_line(OUTSIDE_R, radius(first), theta, first, 12)
    cur_r = radius(first)
    for i in range(1, len(seq) - 1):
        a = seq[i]
        b = seq[i + 1]
        pts += polar_arc(cur_r, theta, theta + direction * sweep, a, 60)
        theta = theta + direction * sweep
        pts += polar_line(cur_r, radius(b), theta, b, 12)
        cur_r = radius(b)
        direction = -direction
    return pts

def extract_pi(pts):
    got = []
    for p in pts:
        tag = p[2]
        if not got or got[-1] != tag:
            got.append(tag)
    return got

def check_axioms(pi):
    seq = [0] + pi
    edges = set()
    deg = {}
    for i in range(len(seq) - 1):
        a, b = seq[i], seq[i + 1]
        e = (min(a, b), max(a, b))
        edges.add(e)
        deg[a] = deg.get(a, 0) + 1
        deg[b] = deg.get(b, 0) + 1
    nodes = set(seq)
    adj = {}
    for k in nodes:
        adj[k] = []
    for e in edges:
        adj[e[0]].append(e[1])
        adj[e[1]].append(e[0])
    seen = set([0])
    stack = [0]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    ends = sorted([k for k in deg if deg[k] == 1])
    rseq = seq[::-1]
    rev = set()
    for i in range(len(rseq) - 1):
        rev.add((min(rseq[i], rseq[i + 1]), max(rseq[i], rseq[i + 1])))
    return {
        "F1_no_choice_maxdeg_le2": all(d <= 2 for d in deg.values()),
        "F2_full_walk_endpoints_0_8": (sorted(pi) == list(range(1, CENTER + 1))) and (ends == [0, CENTER]),
        "F3_returnable_same_edges": rev == edges,
        "F4_contractible_tree": (seen == nodes) and (len(edges) == len(nodes) - 1),
        "edges": len(edges),
        "nodes": len(nodes),
    }

def descending_runs(pi):
    runs = []
    cur = [pi[0]]
    for x in pi[1:]:
        if x == cur[-1] - 1:
            cur.append(x)
        else:
            runs.append(cur)
            cur = [x]
    runs.append(cur)
    return [r for r in runs if len(r) >= 2]

def cretan_invariants(pi):
    runs = descending_runs(pi)
    mirror = False
    if len(runs) == 2:
        mirror = all(a + b == CENTER for a, b in zip(runs[0], runs[1][::-1]))
    return {
        "enters_at_3": pi[0] == 3,
        "approaches_center_from_5": pi[-2] == 5,
        "descending_runs": runs,
        "mirror_around_4": mirror,
    }

pts = build_walk()
pi_geom = extract_pi(pts)
receipt = {
    "pi_literature": PI_LIT,
    "pi_geometry": pi_geom,
    "fingerprint_match": pi_geom == PI_LIT,
    "axioms": check_axioms(PI_LIT),
    "cretan_invariants": cretan_invariants(PI_LIT),
    "walk_points": len(pts),
    "image": None,
}

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    zs = list(range(len(pts)))
    fig = plt.figure(figsize=(12, 5))
    a1 = fig.add_subplot(121)
    a1.plot(xs, ys, lw=1.1)
    a1.set_aspect("equal")
    a1.set_title("LABY-001 clear path diagram (schematic)")
    a2 = fig.add_subplot(122, projection="3d")
    a2.plot(xs, ys, zs, lw=1.0)
    a2.set_xlabel("x")
    a2.set_ylabel("y")
    a2.set_zlabel("step")
    a2.set_title("3D cycle lift: z = walk time")
    fig.tight_layout()
    fig.savefig("laby_receipt.png", dpi=140)
    receipt["image"] = "laby_receipt.png"
except Exception:
    print("matplotlib missing, text mode. install: pkg install python-matplotlib  (or pip install matplotlib)")
    step = max(1, len(pts) // 24)
    print("radius profile over walk time:")
    for i in range(0, len(pts), step):
        r = math.hypot(pts[i][0], pts[i][1])
        bar = "#" * int(round(r * 5))
        print("%4d | %-45s r=%.1f" % (i, bar, r))

print(json.dumps(receipt, ensure_ascii=False, indent=1))
