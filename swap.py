def zeros(rows, cols):
    return [[0 for _ in range(cols)] for _ in range(rows)]

def eye(n):
    m = zeros(n, n)
    for i in range(n):
        m[i][i] = 1
    return m

def matmul(A, B):
    n = len(A)
    p = len(B)
    m = len(B[0])
    C = zeros(n, m)
    for i in range(n):
        for j in range(m):
            for k in range(p):
                C[i][j] += A[i][k] * B[k][j]
    return C

def swap_rows(m, i, j):
    """交換第 i 行 和 第 j 行"""
    m[i], m[j] = m[j], m[i]
    return m

def swap_cols(m, i, j):
    """交換第 i 列 和 第 j 列"""
    for row in m:
        row[i], row[j] = row[j], row[i]
    return m

def show(m, name=""):
    if name:
        print(f"\n{name}:")
    for row in m:
        print(row)

# === 測試：系統交換 ===
M = [[1, 2],
     [3, 4]]
show(M, "原始矩陣 M")

swap_rows(M, 0, 1)
show(M, "交換行後")

swap_cols(M, 0, 1)
show(M, "交換列後")

# 驗證：單位矩陣不變性
I = eye(2)
show(I, "單位矩陣")
show(matmul(I, M), "I × M = 不變")

