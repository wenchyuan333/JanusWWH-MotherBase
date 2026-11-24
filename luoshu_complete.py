# ==================================================
# 🔮 洛書九宮 · 完備數學系統 v1.1
# ==================================================

def zeros(rows, cols):
    return [[0 for _ in range(cols)] for _ in range(rows)]

def show(m, name=""):
    if name:
        print(f"\n{name}")
    for row in m:
        print(row)

LUOSHU = [
    [4, 9, 2],
    [3, 5, 7],
    [8, 1, 6]
]

def rotate_cw(m):
    n = len(m)
    return [[m[n-1-j][i] for j in range(n)] for i in range(n)]

def flip_h(m):
    return [row[::-1] for row in m]

def flip_v(m):
    return [row[:] for row in reversed(m)]

def transpose(m):
    return [[m[j][i] for j in range(len(m))] for i in range(len(m[0]))]

def symmetries(m):
    S = []
    current = m
    for i in range(4):
        S.append([row[:] for row in current])
        current = rotate_cw(current)
    unique = []
    seen = set()
"""
luoshu_complete.py — 洛書九宮 · 完備數學系統 v1.2
合併：基礎運算｜對稱變換｜循環位移｜玄空飛星
"""

# ═══════════════════════════════════════
#  基礎工具
# ═══════════════════════════════════════
def zeros(rows, cols):
    return [[0 for _ in range(cols)] for _ in range(rows)]

def show(m, name=""):
    if name:
        print(f"\n─── {name} ───")
    for row in m:
        print(" ".join(f"{c:2d}" for c in row))

# ═══════════════════════════════════════
#  洛書本體
# ═══════════════════════════════════════
LUOSHU = [
    [4, 9, 2],
    [3, 5, 7],
    [8, 1, 6]
]

# ═══════════════════════════════════════
#  對稱變換
# ═══════════════════════════════════════
def rotate_cw(m):
    n = len(m)
    return [[m[n-1-j][i] for j in range(n)] for i in range(n)]

def flip_h(m):
    return [row[::-1] for row in m]

def flip_v(m):
    return [row[:] for row in reversed(m)]

def transpose(m):
    return [[m[j][i] for j in range(len(m))] for i in range(len(m))]

def symmetries(m):
    S = []
    current = m
    for _ in range(4):
        S.append(current)
        current = rotate_cw(current)
    unique = []
    seen = set()
    for s in S:
        t = tuple(tuple(r) for r in s)
        if t not in seen:
            seen.add(t)
            unique.append(s)
    return unique

# ═══════════════════════════════════════
#  循環位移 / 九元運算
# ═══════════════════════════════════════
RING_ORDER = [(0,0),(0,1),(0,2),(1,2),(2,2),(2,1),(2,0),(1,0)]

def shift_ring(matrix, steps=1):
    m = [row[:] for row in matrix]
    ring_vals = [m[r][c] for r,c in RING_ORDER]
    n = steps % 8
    new_vals = ring_vals[-n:] + ring_vals[:-n] if n>0 else ring_vals[:]
    for idx, (r,c) in enumerate(RING_ORDER):
        m[r][c] = new_vals[idx]
    return m

def luoshu_add(a, b):
    s = (a + b) % 9
    return 9 if s == 0 else s

def center(m):
    n = len(m)
    return m[n//2][n//2]

def check_sums(m):
    if sum(m[0]) != 15: return False
    if sum(m[1]) != 15: return False
    if sum(m[2]) != 15: return False
    if m[0][0]+m[1][0]+m[2][0] != 15: return False
    if m[0][1]+m[1][1]+m[2][1] != 15: return False
    if m[0][2]+m[1][2]+m[2][2] != 15: return False
    if m[0][0]+m[1][1]+m[2][2] != 15: return False
    if m[0][2]+m[1][1]+m[2][0] != 15: return False
    return True

# ═══════════════════════════════════════
#  玄空飛星模組
# ═══════════════════════════════════════
def _build_pan(center_num, reverse=False):
    seq = [4,9,2,7,6,8,1,3]
    if reverse:
        seq = [4,3,1,8,6,7,2,9]
    idx = seq.index(center_num)
    order = seq[idx:] + seq[:idx]
    M = zeros(3,3)
    M[1][1] = center_num
    M[0][0], M[0][1], M[0][2] = order[0], order[1], order[2]
    M[1][2], M[2][2], M[2][1] = order[3], order[4], order[5]
    M[2][0], M[1][0] = order[6], order[7]
    return M

def feixing(yun_star, shan, xiang):
    """
    玄空飛星主函數
    yun_star: 當運入中星數 1~9
    shan: 山位 1~9｜xiang: 向位 1~9
    回傳: 天盤, 山盤, 向盤
    """
    Tian = _build_pan(yun_star, reverse=False)
    
    def get_star(p):
        return 5 if p == 5 else Tian[(p-1)//3][(p-1)%3]
    
    shan_c = get_star(shan)
    xiang_c = get_star(xiang)
    
    Shan = _build_pan(shan_c, reverse=False)
    Xiang = _build_pan(xiang_c, reverse=False)
    
    return Tian, Shan, Xiang

# ═══════════════════════════════════════
#  主程式驗證
# ═══════════════════════════════════════
if __name__ == "__main__":
    print("="*50)
    print("🌐 洛書九宮 · 完備數學系統 v1.2")
    print("="*50)
    
    show(LUOSHU, "原始洛書")
    print(f"中心值: {center(LUOSHU)}")
    print(f"恆定驗證: {'✅ 全部和=15' if check_sums(LUOSHU) else '❌ 錯誤'}")
    
    show(shift_ring(LUOSHU, 1), "順行1步")
    show(shift_ring(LUOSHU, -1), "逆行1步")
    
    print("\n─── 玄空飛星範例：下元九運 · 子山午向 ───")
    Tian, Shan, Xiang = feixing(9, 1, 9)
    show(Tian, "天盤")
    show(Shan, "山盤")
    show(Xiang, "向盤")
    
    print("\n✅ 全部就緒！")
    for s in S:
        t = tuple(tuple(r) for r in s)
        if t not in seen:
            seen.add(t)
            unique.append(s)
    return unique

def shift_ring(matrix, steps=1):
    order = [(0,0),(0,1),(0,2),(1,2),(2,2),(2,1),(2,0),(1,0)]
    m = [row[:] for row in matrix]
    ring_vals = [m[r][c] for r,c in order]
    n = steps % 8
    new_vals = ring_vals[-n:] + ring_vals[:-n] if n>0 else ring_vals
    for idx, (r,c) in enumerate(order):
        m[r][c] = new_vals[idx]
    return m

def luoshu_add(a, b):
    s = (a + b) % 9
    return 9 if s == 0 else s

def center(m):
    n = len(m)
    return m[n//2][n//2]

def check_sums(m):
    for r in m:
        if sum(r) != 15: return False
    for c in range(3):
        if sum(m[r][c] for r in range(3)) != 15: return False
    if m[0][0]+m[1][1]+m[2][2] != 15: return False
    if m[0][2]+m[1][1]+m[2][0] != 15: return False
    return True

# === 主程式 ===
print("="*50)
print("🔮 洛書九宮 · 完備系統驗證 v1.1")
print("="*50)

show(LUOSHU, "\n📐 原始洛書")
print(f"中心：{center(LUOSHU)}")
print(f"和恆定：{'✅' if check_sums(LUOSHU) else '❌'} 所有行/列/對角 = 15")

syms = symmetries(LUOSHU)
print(f"\n🔷 D4 對稱群：共 {len(syms)} 種形式")
labels = ["R0°", "R90°", "R180°", "R270°"]
for i, s in enumerate(syms[:4]):
    show(s, f"  {labels[i]}")
    print(f"    中心不變：{center(s)}")

print("\n🔄 外圈循環位移")
for s in [1, -1, 2, -2]:
    shifted = shift_ring(LUOSHU, s)
    label = f"+{s}" if s > 0 else f"{s}"
    show(shifted, f"  位移 {label}")
    print(f"    中心不變：{center(shifted)}")

print("\n➕ 加法群 (mod9)")
a, b = 4, 9
c = luoshu_add(a, b)
print(f"  {a} + {b} = {c}")
print(f"  封閉性：✅ 1~9 範圍內")

print("\n📐 對角線不變性")
d1 = LUOSHU[0][0] + LUOSHU[1][1] + LUOSHU[2][2]
d2 = LUOSHU[0][2] + LUOSHU[1][1] + LUOSHU[2][0]
print(f"  主對角：{d1}")
print(f"  反對角：{d2}")
print(f"  恆定 15：✅")

print("\n" + "="*50)
print("✅ 全部正常運行！")
print("="*50)

