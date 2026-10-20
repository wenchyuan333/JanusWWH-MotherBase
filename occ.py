#!/usr/bin/env python3
# star_globe_4096_occupancy.py v0.2 (2026-08-21)
# MIYA-4096 門牌佔格驗證器：z = sha256(公式ID) 前 12 bit ∈ [0,4096)
# (x, y) = (z % 64, z // 64)。統計佔格數，與均勻雜湊期望對帳。
# CLAIM: v0.1 機制已於 Termux 實跑通過（2026-08-21 n=100: occupied=99, 帶內）;
#        v0.2 新增防禦與共格報告尚未執行 = STAGED；均勻性主張仍待全庫 n=1192。
# 用法:
#   python3 occ.py ids.txt     # 一行一個公式 ID
#   cat ids.txt | python3 occ.py
#   python3 occ.py --selftest  # 決定性自檢（範圍＋冪等）
# 紀律: 純標準庫；不連網；失敗非零退出；輸出即 receipt（單行 JSON）。
# v0.2 變更（兩個缺口皆由今晚實測產生）:
#   1) 垃圾地板：n<2 或首行像 HTTP 錯誤頁 → 拒跑（14B/141B 事件）
#   2) 共格報告：collisions<=50 時逐對列出 cell 與成員 ID
import sys, json, hashlib, math

M = 4096  # 64 x 64 治理地址空間；地址 ≠ 身分（ENCODING ≠ MEASUREMENT）

def cell(fid):
    d = hashlib.sha256(fid.encode("utf-8")).digest()
    return ((d[0] << 8) | d[1]) >> 4  # 前 12 bit

def expected_occupied(n):
    return M * (1.0 - ((M - 1.0) / M) ** n)

def occupancy_sigma(n):
    lam = n / M
    var = M * (math.exp(-lam) - (1.0 + lam) * math.exp(-2.0 * lam))
    return math.sqrt(max(var, 0.0))

def emit(obj, code):
    print(json.dumps(obj, ensure_ascii=False, sort_keys=True))
    return code

def looks_like_error_page(ids):
    head = ids[0]
    return head.startswith("404") or "Not Found" in head or head.startswith("{") or head.startswith("<")

def main():
    args = sys.argv[1:]
    if args and args[0] == "--selftest":
        probe = "ZERO-001"
        c1, c2 = cell(probe), cell(probe)
        ok = (0 <= c1 < M) and (c1 == c2)
        return emit({"ok": ok, "selftest": "range+determinism", "cell_of_ZERO_001": c1}, 0 if ok else 1)
    if args:
        with open(args[0], "r", encoding="utf-8") as fh:
            ids = [ln.strip() for ln in fh if ln.strip()]
    else:
        ids = [ln.strip() for ln in sys.stdin if ln.strip()]
    n = len(ids)
    if n == 0:
        return emit({"ok": False, "err": "no ids (failure case: empty input)"}, 1)
    if n < 2 or looks_like_error_page(ids):
        return emit({"ok": False, "err": "input rejected: too small or looks like an HTTP error page", "n_ids": n}, 1)
    cells = {}
    for i in ids:
        cells.setdefault(cell(i), []).append(i)
    occ = len(cells)
    exp = expected_occupied(n)
    sig = occupancy_sigma(n)
    lo, hi = exp - 3.0 * sig, exp + 3.0 * sig
    ok = lo <= occ <= hi
    out = {
        "ok": ok,
        "n_ids": n,
        "occupied": occ,
        "collisions": n - occ,
        "expected_occupied": round(exp, 2),
        "sigma": round(sig, 2),
        "band_3sigma": [round(lo, 2), round(hi, 2)],
        "verdict": "UNIFORM_OK" if ok else "SUSPECT_NONUNIFORM",
        "note": "4096 是地址空間不是身分；同格多列＝粗粒化，非錯誤。replay: 同 ids 檔 → 同 receipt。",
    }
    if 0 < n - occ <= 50:
        out["shared_cells"] = {str(c): v for c, v in cells.items() if len(v) > 1}
    return emit(out, 0 if ok else 1)

if __name__ == "__main__":
    sys.exit(main())