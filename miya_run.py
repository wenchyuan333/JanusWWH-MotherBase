import sys, math
import numpy as np
from llama_cpp import Llama

MODEL  = sys.argv[1] if len(sys.argv) > 1 else "qwen0.5b.gguf"
PROMPT = sys.argv[2] if len(sys.argv) > 2 else "The boundary residual of the system approaches"
BETA_C = 0.508230
T_CRIT = 1.0 / BETA_C

# 1) 取真實 logits：最後一個 token、全 vocab
llm  = Llama(model_path=MODEL, logits_all=True, verbose=False, n_ctx=512)
toks = llm.tokenize(PROMPT.encode("utf-8"))
llm.reset(); llm.eval(toks)
scores = np.array(llm.scores)
if scores.ndim == 1:
    scores = scores.reshape(-1, llm.n_vocab())
L = scores[llm.n_tokens - 1].astype(float).tolist()
np.savetxt("logits.txt", np.array(L))
print("vocab=%d  prompt_tokens=%d  -> logits.txt" % (len(L), len(toks)))

# 2) 比熱掃描：C = beta^2 * Var_p(logit)，找峰
def obs(L, T):
    b = 1.0 / T; m = max(L)
    ex = [math.exp(b * (x - m)) for x in L]; Z = sum(ex)
    p = [e / Z for e in ex]
    mean = sum(pi * x for pi, x in zip(p, L))
    var  = sum(pi * x * x for pi, x in zip(p, L)) - mean * mean
    return b * b * var, var, 1.0 / sum(pi * pi for pi in p)

Ts   = [0.3 + 0.02 * i for i in range(186)]   # 0.30 .. 4.00
rows = [(T,) + obs(L, T) for T in Ts]
Tpk  = max(rows, key=lambda r: r[1])[0]
print("T_crit=%.4f  C-peak@T=%.4f  |d|=%.4f  %s" % (
    T_CRIT, Tpk, abs(Tpk - T_CRIT),
    "PASS(<=0.15)" if abs(Tpk - T_CRIT) <= 0.15 else "FAIL(>0.15)"))
for r in rows[::15]:
    print("T=%.2f  C=%.4f  Var=%.3f  PR=%.1f" % r)
