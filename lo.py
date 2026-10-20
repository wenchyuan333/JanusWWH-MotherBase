import numpy as np

M = np.array([[4,9,2],[3,5,7],[8,1,6]], float)
print("M_Luo=")
print(M)
print("det=", np.linalg.det(M), "應=360")
w, v = np.linalg.eig(M)
print("eig=", w, "應有15, ±3√5≈±6.708")

# 用你公式主索引的前3公式當 X 測試
# 這裡先用小數據，你之後把 csv 放 ~/storage 下載
X = np.array([[0.62,0.38,0.45],
              [0.31,0.18,0.99],
              [1.2,2.3,3.4]])
Y = M @ X
print("\nY=M·X=")
print(Y)

# C3 120°魯班鎖
theta = 2*np.pi/3
R = np.array([[np.cos(theta),-np.sin(theta),0],
              [np.sin(theta),np.cos(theta),0],
              [0,0,1]])
Yl = R @ Y
print("\nY_locked 120°=")
print(Yl)

# 電感擾動 Dr.Mood
L = np.array([[0.12,0.03,0.02],[0.03,0.10,0.04],[0.02,0.04,0.11]])
Yf = Yl + L @ Yl * 0.05
print("\nY_final 電感擾動後=")
print(Yf)

# 解密驗證
Mi = np.linalg.inv(M)
Xr = Mi @ Y
print("\n解密 Xr=M^-1·Y 回得來? ", np.allclose(X, Xr))
print("殘差", np.linalg.norm(X-Xr), "應→2.22e-16")
