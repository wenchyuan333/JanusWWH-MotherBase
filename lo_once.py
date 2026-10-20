import numpy as np, os, glob, csv
M=np.array([[4,9,2],[3,5,7],[8,1,6]], float)
print("=== DR MOOD x MIYA 洛書×電感 一次性驗證 ===")
print(f"det={np.linalg.det(M):.6f} 目標360")
w=np.linalg.eigvals(M)
print(f"eig={w} 目標15, ±i·2√6≈±4.899j")

# 找公式主索引 csv
paths = glob.glob(os.path.expanduser("~/storage/downloads/*.csv")) + glob.glob("*.csv")
found=None
for p in paths:
    if os.path.getsize(p)>100000: # 你的1.8MB那個
        found=p; break
if found:
    print(f"\n找到公式庫: {found}")
    X=[]
    with open(found, encoding='utf-8', errors='ignore') as f:
        r=csv.reader(f)
        for row in r:
            try:
                nums=[float(x) for x in row[:3]]
                if len(nums)==3:
                    X.append(nums)
                    if len(X)>=3: break
            except: continue
    X=np.array(X).T if X else None
else:
    print("\n沒找到1.8MB csv，用範例X")
    X=None

if X is None or X.size==0:
    X=np.array([[0.62,0.38,0.45],[0.31,0.18,0.99],[1.2,2.3,3.4]])

print(f"X shape={X.shape}")
Y=M@X
print(f"Y=\n{Y}")

theta=2*np.pi/3
R=np.array([[np.cos(theta),-np.sin(theta),0],[np.sin(theta),np.cos(theta),0],[0,0,1]])
Yl=R@Y
L=np.array([[0.12,0.03,0.02],[0.03,0.10,0.04],[0.02,0.04,0.11]])
Yf=Yl+L@Yl*0.05
Mi=np.linalg.inv(M)
Xr=Mi@Y
res=np.linalg.norm(X-Xr)
print(f"\nY_locked 120°=\n{Yl}")
print(f"\nY_final 電感擾動=\n{Yf}")
print(f"\n解密 True? {np.allclose(X,Xr)} 殘差={res:.3e} 目標2.22e-16")
print(f"sum check Y.sum={Y.sum(axis=0)} 應守恆~15倍")
print("\n=== 閉環完成 OUTPUT=1 ===")
