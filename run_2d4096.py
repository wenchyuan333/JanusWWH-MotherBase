import os, json, time, csv
import requests
from tqdm import tqdm

NOTION_VERSION = os.environ.get("NOTION_VERSION", "2022-06-28")

# OAuth mode: you must provide NOTION_OAUTH_TOKEN in env
NOTION_OAUTH_TOKEN = os.environ.get("NOTION_OAUTH_TOKEN", "").strip()

# Public API ids (32 chars, no dashes)
FMI_DATABASE_ID = os.environ.get("FMI_DATABASE_ID", "").strip()
TASK_PAGE_ID = os.environ.get("TASK_PAGE_ID", "").strip()

if not NOTION_OAUTH_TOKEN:
    raise SystemExit("Missing env NOTION_OAUTH_TOKEN (OAuth access token).")
if not FMI_DATABASE_ID:
    raise SystemExit("Missing env FMI_DATABASE_ID (database_id).")
if not TASK_PAGE_ID:
    raise SystemExit("Missing env TASK_PAGE_ID (page_id).")

HEADERS = {
    "Authorization": f"Bearer {NOTION_OAUTH_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json",
}

EDGE_RELATION_PROPS = ["前置公式", "依賴公式", "衍生公式", "六向互鎖節點"]
GATE_PROPS = ["頁面完備 Gate", "驗證狀態", "證據層級", "魯班鎖分流門"]

def post(path, payload):
    url = f"https://api.notion.com/v1/{path}"
    r = requests.post(url, headers=HEADERS, json=payload, timeout=60)
    if r.status_code >= 400:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text}")
    return r.json()

def patch(path, payload):
    url = f"https://api.notion.com/v1/{path}"
    r = requests.patch(url, headers=HEADERS, json=payload, timeout=60)
    if r.status_code >= 400:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text}")
    return r.json()

def extract_title(props):
    t = props.get("公式 ID")
    if not t or t.get("type") != "title":
        return None
    parts = t.get("title", [])
    return "".join([p.get("plain_text","") for p in parts]) if parts else None

def extract_select_name(p):
    if not p: return None
    t = p.get("type")
    if t == "select":
        s = p.get("select")
        return s.get("name") if s else None
    if t == "status":
        s = p.get("status")
        return s.get("name") if s else None
    return None

def extract_relation_ids(p):
    if not p or p.get("type") != "relation":
        return []
    return [x["id"].replace("-", "") for x in p.get("relation", [])]

def query_all_pages(database_id):
    pages = []
    cursor = None
    while True:
        payload = {"page_size": 100}
        if cursor:
            payload["start_cursor"] = cursor
        data = post(f"databases/{database_id}/query", payload)
        pages.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
    return pages

def write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fieldnames})

def eligibility(node):
    pg = node.get("頁面完備 Gate")
    vs = node.get("驗證狀態")
    ok = (pg == "COMPLETE") and (vs in ["✅ 可計算", "概念模型"])
    if not ok:
        return False, None, f"gate_denied: pageGate={pg}, verifyStatus={vs}"
    lane = "computable" if vs == "✅ 可計算" else "model"
    return True, lane, None

def update_task_receipt(task_page_id, receipt_obj):
    patch(f"pages/{task_page_id}", {
        "properties": {
            "Receipt": {
                "rich_text": [
                    {"type": "text", "text": {"content": json.dumps(receipt_obj, ensure_ascii=False, indent=2)}}
                ]
            }
        }
    })

def main():
    run_id = "2d4096-run-0"
    started_at = time.strftime("%Y-%m-%dT%H:%M:%S%z")

    pages = query_all_pages(FMI_DATABASE_ID)

    nodes, edges = [], []
    for page in tqdm(pages, desc="pages"):
        pid = page["id"].replace("-", "")
        props = page.get("properties", {})

        node = {"page_id": pid, "formula_id": extract_title(props)}
        for g in GATE_PROPS:
            node[g] = extract_select_name(props.get(g)) if g in props else None
        nodes.append(node)

        for rel_name in EDGE_RELATION_PROPS:
            to_ids = extract_relation_ids(props.get(rel_name))
            for to_pid in to_ids:
                edges.append({"from_page_id": pid, "to_page_id": to_pid, "edge_type": rel_name})

    eligible, denied = [], []
    for n in nodes:
        ok, lane, reason = eligibility(n)
        if ok:
            x = dict(n); x["lane"] = lane
            eligible.append(x)
        else:
            x = dict(n); x["deny_reason"] = reason
            denied.append(x)

    os.makedirs("out", exist_ok=True)
    with open("out/nodes.json", "w", encoding="utf-8") as f:
        json.dump(nodes, f, ensure_ascii=False, indent=2)

    edge_fields = ["from_page_id", "to_page_id", "edge_type"]
    node_fields = ["page_id", "formula_id"] + GATE_PROPS

    write_csv("out/edges.csv", edges, edge_fields)
    write_csv("out/gate_matrix.csv", nodes, node_fields)
    write_csv("out/eligible.csv", eligible, node_fields + ["lane"])
    write_csv("out/denied.csv", denied, node_fields + ["deny_reason"])

    finished_at = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    receipt = {
        "run_id": run_id,
        "status": "SNAPSHOT_DONE",
        "truth_layer": "FORMAL_MODEL",
        "started_at": started_at,
        "finished_at": finished_at,
        "counts": {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "eligible_total": len(eligible),
            "eligible_computable": sum(1 for x in eligible if x["lane"] == "computable"),
            "eligible_model": sum(1 for x in eligible if x["lane"] == "model"),
            "denied_total": len(denied),
        },
        "artifacts": [
            {"path": "out/nodes.json"},
            {"path": "out/edges.csv"},
            {"path": "out/gate_matrix.csv"},
            {"path": "out/eligible.csv"},
            {"path": "out/denied.csv"},
        ],
        "firewall": [
            "CALCULABLE != VERIFIED != PUBLISHED",
            "UNKNOWN != SUPPORTED",
            "ROUTES != DERIVES",
        ]
    }
    update_task_receipt(TASK_PAGE_ID, receipt)
    print("Done. Receipt updated on task page.")

if __name__ == "__main__":
    main()
