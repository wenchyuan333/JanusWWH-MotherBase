import numpy as np, csv
M=np.array([[4,9,2],[3,5,7],[8,1,6]], float)
# 讀前3行數值當 X
X=[]
with open('formula.csv') as f:
    r=csv.reader(f)
    for row in r:
        try:
            nums=[float(x) for x in row[:3]]
            if len(nums)==3:
                X.append(nums)
                if len(X)>=3: break
        except: continue
X=np.array(X).T
print("X shape", X.shape)
Y=M@X
print("Y=",Y)
print("det", np.linalg.det(M), "sum check", Y.sum(axis=0))
