def zeros(rows, cols):
    return [[0 for _ in range(cols)] for _ in range(rows)]

def ones(rows, cols):
    return [[1 for _ in range(cols)] for _ in range(rows)]

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

def show(m):
    for row in m:
        print(row)

I = eye(2)
print("單位矩陣：")
show(I)

print("\n相乘結果：")
R = matmul(I, I)
show(R)

