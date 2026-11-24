import math

# 齊物：不排名，只定位
# 計算：57個篩子，這裡用 57 個簡單篩子示範，之後換成你的真篩子
def sieve_57(x):
    # 32亮 25暗，亮就留，暗就衰減，這裡只是骨架
    # PI_MASK 000011110001111000111100011110001111000111100011110001111
    mask = "000011110001111000111100011110001111000111100011110001111"
    out = x
    for i, bit in enumerate(mask):
        if bit == "1":
            out = out * 0.99 + 0.01  # 亮：留下來一點
        else:
            out = out * 0.99  # 暗：衰減一點
    return out

# 纖維：收束
def fiber_C(t, lam=0.3):
    return (1 - math.exp(-lam * t)) + 0.01

def is_inside_circle(t, lam=0.3):
    return fiber_C(t, lam) > 0.5

# 資訊：過濾後還剩多少
def mutual_info(H_X, H_X_given_Y):
    return H_X - H_X_given_Y

# 窗口檢查
def xi_window(xi):
    return 1e-8 < xi < 1e-5

def ulysses_window(beta, delta, C, R):
    return beta*delta*C < R < delta*C

if __name__ == "__main__":
    print("sieve_57(1.0) =", sieve_57(1.0))
    print("fiber_C(5) =", fiber_C(5), "inside?", is_inside_circle(5))
    print("I =", mutual_info(2.0, 0.7))
    print("xi 1e-6 in window?", xi_window(1e-6))
    print("ulysses beta=0.7 delta=0.9 C=10 R=7 in window?", ulysses_window(0.7, 0.9, 10, 7))
