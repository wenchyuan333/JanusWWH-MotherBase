#!/usr/bin/env python3
# miya_grow_v01.py — GROW-001 v0.1｜公式自生長引擎（Termux 標準庫）
# 流水線 GENERATE → FILTER → TEST → ADMIT；一切產出為候選；收據 JSONL＋SHA-256
# 2026-08-16 thread-14 開爐令｜方法聲明：本檔由 Miya 撰寫，首跑收據待使用者產出
import ast, json, math, hashlib, itertools

RUN_TS = "2026-08-16"
RECEIPTS = []

def receipt(stage, payload):
    blob = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    RECEIPTS.append({"ts": RUN_TS, "stage": stage,
                     "sha256": hashlib.sha256(blob.encode()).hexdigest()[:16], "payload": payload})

FUNCS = {"sqrt": math.sqrt, "ln": math.log, "exp": math.exp, "sin": math.sin,
         "cos": math.cos, "atan": math.atan, "ceil": math.ceil, "abs": abs,
         "pi": math.pi, "e": math.e}
ALLOWED = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Name, ast.Load,
           ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.USub, ast.UAdd, ast.Mod, ast.Call)

def safe_eval(expr, env):
    tree = ast.parse(expr, mode="eval")
    for n in ast.walk(tree):
        if not isinstance(n, ALLOWED):
            raise ValueError(f"非法語法節點 {type(n).__name__}")
        if isinstance(n, ast.Name) and n.id not in FUNCS and n.id not in env:
            raise ValueError(f"未定義名 {n.id}")
        if isinstance(n, ast.Call) and not (isinstance(n.func, ast.Name) and n.func.id in FUNCS):
            raise ValueError("只允許白名單函數")
    return eval(compile(tree, "<grow>", "eval"), {"__builtins__": {}}, {**FUNCS, **env})

R = lambda **kw: kw
REGISTRY = [
 R(id="CHEM-PT-002", expr="1/(R_H*5/36)*1e9", env={"R_H":1.0967758e7}, expected=656.46, tol=3e-4, note="Balmer-alpha 真空 nm"),
 R(id="CONST-KB-001", expr="2*pi**5*kB**4/(15*h**3*c**2)", env={"kB":1.380649e-23,"h":6.62607015e-34,"c":299792458.0}, expected=5.6703744e-8, tol=5e-4, note="sigma 由定義常數合成"),
 R(id="QM-001", expr="alpha**2*me*c/(2*h)", env={"alpha":7.2973525693e-3,"me":9.1093837015e-31,"c":299792458.0,"h":6.62607015e-34}, expected=1.0973732e7, tol=2e-4, note="R_inf 恆等式"),
 R(id="WEAK-001", expr="192*pi**3*hbar/(GF**2*mmu**5)", env={"hbar":6.582119569e-25,"GF":1.1663787e-5,"mmu":0.105658}, expected=2.196981e-6, tol=6e-3, note="μ 子壽命（略 m_e＋輻射修正）"),
 R(id="WEAK-003", expr="1-(mw/mz)**2", env={"mw":80.379,"mz":91.1876}, expected=0.2230, tol=5e-4, note="sin2thetaW on-shell"),
 R(id="QCD-002", expr="-4*a_s/(3*r)+sigma*r", env={"a_s":0.3,"r":5.067,"sigma":0.18}, expected=0.83, tol=0.15, note="Cornell 1fm 合理性"),
 R(id="QCD-003", expr="4*pi/((11-2*5/3)*ln((Q/L)**2))", env={"Q":91.1876,"L":0.2}, expected=0.1179, tol=0.01, note="一迴圈——預期 FAIL（如實）"),
 R(id="ELAST-008", expr="E/(2*(1+nu))", env={"E":200.0,"nu":0.3}, expected=77.0, tol=5e-3, note="鋼剪模量 GPa"),
 R(id="ELAST-009", expr="P*L/(E*A)", env={"P":1e4,"L":2.0,"E":2e11,"A":0.01}, expected=1e-5, tol=1e-9, note="軸向變形"),
 R(id="ELAST-010", expr="M*y/I", env={"M":1000.0,"y":0.05,"I":8.333e-6}, expected=6.0e6, tol=2e-3, note="彎曲應力"),
 R(id="ELAST-011", expr="T*R0/(pi*d**4/32)", env={"T":100.0,"R0":0.025,"d":0.05}, expected=4.0744e6, tol=2e-3, note="扭轉剪應力"),
 R(id="ELAST-012", expr="T*L/(G*(pi*d**4/32))", env={"T":100.0,"L":1.0,"G":76.92e9,"d":0.05}, expected=2.1186e-3, tol=2e-3, note="扭轉角 rad"),
 R(id="ELAST-013", expr="P*L**3/(48*E*I)", env={"P":1e4,"L":4.0,"E":2e11,"I":8.333e-6}, expected=8.0e-3, tol=2e-3, note="簡支撓度 m"),
 R(id="ELAST-014", expr="pi**2*E*I/(K*L)**2", env={"E":2e11,"I":8.333e-6,"K":1.0,"L":4.0}, expected=1.0281e6, tol=2e-3, note="歐拉屈曲 N"),
 R(id="ELAST-015", expr="sqrt(0.5*((s1-s2)**2+(s2-s3)**2+(s3-s1)**2))", env={"s1":100.0,"s2":50.0,"s3":0.0}, expected=86.6025, tol=1e-4, note="von Mises"),
 R(id="GANZHI-001", expr="((Y-4)%10-2)**2+((Y-4)%12-6)**2+((Y-4)%2)**2", env={"Y":2026}, expected=0, tol=0, note="丙午＋宇稱（0=全中）"),
 R(id="EGYP-001", expr="(1/3+1/15-0.4)**2+(1/4+1/28-2/7)**2", env={}, expected=0, tol=1e-12, note="單位分數兩例（v0.1.1：浮點零容差缺陷修正）"),
 R(id="EGYP-003", expr="(4*440)/(2*280)", env={}, expected=22/7, tol=1e-12, note="22/7 精確恆等"),
 R(id="NORM-001", expr="exp(-1)/(1+exp(-1))", env={}, expected=0.2689414, tol=1e-6, note="二能級 p1"),
 R(id="TRH-001", expr="E_-V+C", env={"E_":3,"V":3,"C":1}, expected=1, tol=0, note="三兔環秩"),
 R(id="ORIG-SHARE-001", expr="ceil(n*k/s)", env={"n":3,"k":2,"s":2}, expected=3, tol=0, note="共耳率下界"),
 R(id="CRYPT-004", expr="sqrt(2*ln(2))", env={}, expected=1.1774100, tol=1e-5, note="生日界係數（×2^128）"),
 R(id="CTRL-001", expr="0*0-1*1", env={}, expected=-1, tol=0, note="det[B AB]≠0 → rank2 可控"),
]

def run_fixtures():
    out = []
    for f in REGISTRY:
        try:
            got = safe_eval(f["expr"], f["env"])
            ok = (got == f["expected"]) if f["tol"] == 0 else \
                 abs(got - f["expected"]) <= f["tol"] * max(1.0, abs(f["expected"]))
            verdict = "PASS" if ok else "FAIL"
        except Exception as ex:
            got, verdict = f"ERROR: {ex}", "HOLD"
        row = {"id": f["id"], "got": got, "expected": f["expected"], "verdict": verdict, "note": f["note"]}
        out.append(row); receipt("TEST", row)
    return out

def generate():
    cands = []
    for a, b in itertools.combinations(REGISTRY, 2):
        for op, sym in (("mul", "*"), ("div", "/")):
            cands.append({"pair": [a["id"], b["id"]], "op": op,
                          "expr": f"({a['expr']}){sym}({b['expr']})"})
    return cands  # v0.1 全量；v0.2 加量綱網與邊型網

def filter_cands(cands):
    seen, kept = set(), []
    for c in cands:
        h = hashlib.sha256(c["expr"].encode()).hexdigest()[:16]
        if h in seen: continue
        seen.add(h)
        c["id_claim"] = f"GROW-CAND-{len(kept)+1:04d}"  # ID 佔位：先報號
        c["falsifier_draft"] = f"若 {c['pair'][0]} 與 {c['pair'][1]} 成立而複合式與實測不符 → 複合假設錯"
        kept.append(c)
    receipt("FILTER", {"kept": len(kept), "first5": [c["id_claim"] for c in kept[:5]]})
    return kept

def admit(kept):
    for c in kept:  # 只發候選證
        receipt("ADMIT", {"id_claim": c["id_claim"], "tier": "CANDIDATE",
                          "note": "升 FORMAL_MODEL 需 fixture；律法簽字權在世界"})

if __name__ == "__main__":
    print("GROW-001 v0.1｜產出皆為候選；律法簽字權在世界（semantic→world = 0）")
    res = run_fixtures()
    for r in res:
        print(f"{r['verdict']:4s} {r['id']:16s} got={r['got']} expected={r['expected']}  # {r['note']}")
    npass = sum(1 for r in res if r["verdict"] == "PASS")
    nfail = sum(1 for r in res if r["verdict"] == "FAIL")
    kept = filter_cands(generate()); admit(kept)
    run_hash = hashlib.sha256(json.dumps(RECEIPTS, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    receipt("MANIFEST", {"run_hash": run_hash})
    print(f"\nfixtures: {npass} PASS / {nfail} FAIL / {len(res)-npass-nfail} HOLD｜候選 {len(kept)} 筆（去重後）｜run_hash = {run_hash[:16]}")
    print("收據：python3 miya_grow_v01.py | tee receipt_2026-08-16.jsonl")