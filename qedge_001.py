#!/usr/bin/env python3
# qedge_001.py v0.2 (2026-08-15) -- Q-EDGE solver: components, circuit rank, islands
# CLAIM LAYER: STAGED (unexecuted). Readback decides promotion.
# CHANGE vs v0.1: embedded edge table REMOVED (hand-transcription proved lossy,
# twice; its gate correctly fired DATA CORRUPT on 2026-08-16). Data now comes
# from a live Notion API pull; correctness fixture is synthetic with known answers.
# Modes:
#   python3 qedge_001.py --selftest   synthetic known-answer fixture, offline
#   python3 qedge_001.py --fetch      live pull; needs NOTION_TOKEN env var
import json
import os
import sys
import urllib.request

DB_ID = "5e35c1fa-96a4-4b53-b3c7-435371764fa3"  # Formula Master Index (公式主索引)
NOTION_VERSION = "2022-06-28"
REL_FIELDS = ["前置公式", "衍生公式", "依賴公式", "六向互鎖節點", "巢狀父鎖"]


def analyze(rows):
    # rows: list of (node_id, title, [target_ids])  -- one entry per library row
    title = {}
    adj = {}

    def node(u, t=""):
        if u not in adj:
            adj[u] = set()
            title[u] = t
        elif t and not title[u]:
            title[u] = t

    directed = set()
    island_rows = 0
    for u, t, targets in rows:
        node(u, t)
        if not targets:
            island_rows += 1
        for v in targets:
            directed.add((u, v))
            node(v)
            adj[u].add(v)
            adj[v].add(u)

    edges = set()
    for u, v in directed:
        if u != v:
            edges.add((u, v) if u < v else (v, u))
    V, E = len(adj), len(edges)

    parent = {u: u for u in adj}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for u, v in edges:
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[rv] = ru

    comps = {}
    for u in adj:
        comps.setdefault(find(u), []).append(u)
    sizes = sorted((len(m) for m in comps.values()), reverse=True)
    mutual = sum(1 for (u, v) in directed if u < v and (v, u) in directed)
    return {
        "total_rows": len(rows),
        "nodes": V,
        "edges": E,
        "components": len(comps),
        "sizes": sizes,
        "circuit_rank": E - V + len(comps),
        "mutual_pairs": mutual,
        "island_rows": island_rows,
        "comps": comps,
        "title": title,
    }


def report(r):
    total = r["total_rows"]
    wired = total - r["island_rows"]
    print("library rows fetched      : %d" % total)
    print("edge-bearing rows         : %d" % wired)
    print("island rows (all 5 empty) : %d (%.1f%%)"
          % (r["island_rows"], 100.0 * r["island_rows"] / max(total, 1)))
    print("graph nodes (incl targets): %d" % r["nodes"])
    print("unique undirected edges   : %d" % r["edges"])
    print("connected components      : %d" % r["components"])
    if r["sizes"]:
        big = r["sizes"][0]
        print("largest component         : %d nodes (%.1f%% of subgraph, %.1f%% of fetched)"
              % (big, 100.0 * big / max(r["nodes"], 1), 100.0 * big / max(total, 1)))
        print("component sizes top10     : %s" % r["sizes"][:10])
    print("circuit rank (E - V + C)  : %d" % r["circuit_rank"])
    print("mutual pairs (2-cycles)   : %d" % r["mutual_pairs"])
    bigroot = max(r["comps"].values(), key=len) if r["comps"] else []
    bigroot.sort(key=lambda u: r["title"].get(u) or u)
    print("\nlargest component members (%d):" % len(bigroot))
    for u in bigroot:
        print("  - %s" % (r["title"].get(u) or u))
    print("\nCLAIM CEILING: undirected simple graph over the five declared relation")
    print("fields. If fetched rows < 940, coverage is partial and no whole-library")
    print("claim may be made. Directed cycles and edge-type-resolved analysis residual.")


def selftest():
    # triangle (rank 1) + one bridge pair + two bare rows; hand-checkable answers
    rows = [
        ("a", "A", ["b"]),
        ("b", "B", ["c"]),
        ("c", "C", ["a"]),
        ("d", "D", ["e"]),
        ("e", "E", []),
        ("f", "F", []),
        ("g", "G", []),
    ]
    r = analyze(rows)
    expect = {
        "nodes": 7,
        "edges": 4,
        "components": 4,      # {a,b,c}, {d,e}, {f}, {g}
        "circuit_rank": 1,
        "island_rows": 3,     # e, f, g have empty own relation fields
        "mutual_pairs": 0,
    }
    ok = True
    for k, v in expect.items():
        got = r[k]
        if got != v:
            ok = False
        print("  %-14s expect %-4s got %-4s %s" % (k, v, got, "OK" if got == v else "MISMATCH"))
    if r["components"] == 1:
        ok = False
        print("  trivially merged graph: gate has no teeth -> FAIL")
    print("SELFTEST: %s" % ("PASS" if ok else "FAIL"))
    return ok


def fetch_rows():
    token = os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")
    if not token:
        print("FAIL: set NOTION_TOKEN (read access to the formula index) first")
        sys.exit(1)
    rows = []
    cursor = None
    while True:
        body = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        req = urllib.request.Request(
            "https://api.notion.com/v1/databases/%s/query" % DB_ID,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": "Bearer " + token,
                "Notion-Version": NOTION_VERSION,
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            print("FAIL: Notion API error: %s" % exc)
            sys.exit(1)
        for page in payload.get("results", []):
            props = page.get("properties", {})
            t = ""
            tt = props.get("公式 ID", {}).get("title", [])
            if tt:
                t = tt[0].get("plain_text", "")
            targets = []
            for f in REL_FIELDS:
                for item in props.get(f, {}).get("relation", []):
                    tid = item.get("id", "").replace("-", "")
                    if tid:
                        targets.append(tid)
            rows.append((page.get("id", "").replace("-", ""), t, targets))
        if payload.get("has_more") and payload.get("next_cursor"):
            cursor = payload["next_cursor"]
        else:
            break
    return rows


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--selftest"
    if mode == "--selftest":
        sys.exit(0 if selftest() else 1)
    if mode == "--fetch":
        rows = fetch_rows()
        if not rows:
            print("FAIL: zero rows fetched; check token scope")
            sys.exit(1)
        report(analyze(rows))
        return
    print("usage: python3 qedge_001.py [--selftest|--fetch]")
    sys.exit(1)


if __name__ == "__main__":
    main()