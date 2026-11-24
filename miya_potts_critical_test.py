import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL = "distilgpt2"          # 本地小模型，可換 gpt2 / pythia-70m
BETA_C = 0.508230
T_CRIT = 1.0 / BETA_C         # = 1.9676...
PROMPT = "The boundary residual of the system is"

tok = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForCausalLM.from_pretrained(MODEL).eval()

@torch.no_grad()
def next_logits(prompt):
    ids = tok(prompt, return_tensors="pt").input_ids
    return model(ids).logits[0, -1]      # 未歸一化 logits = 能量景觀 (選項 C)

def observables(logits, T):
    beta = 1.0 / T
    p = F.softmax(logits * beta, dim=-1)
    mean = (p * logits).sum()
    chi = (p * logits**2).sum() - mean**2      # susceptibility = Var_p(logit)
    pr = 1.0 / (p**2).sum()                      # participation ratio
    return chi.item(), pr.item()

logits = next_logits(PROMPT)
grid = [1.0 + 0.02 * i for i in range(101)]      # T in [1.0, 3.0]
rows = [(T, *observables(logits, T)) for T in grid]
T_peak = max(rows, key=lambda r: r[1])[0]        # argmax chi

print(f"T_crit (=1/beta_c) = {T_CRIT:.4f}")
print(f"chi peak T_peak    = {T_peak:.4f}")
print(f"deviation          = {abs(T_peak - T_CRIT):.4f}")
for T, chi, pr in rows[::10]:
    print(f"T={T:.2f}  chi={chi:9.3f}  PR={pr:8.2f}")

# 證偽條款：若 |T_peak - 1.9676| > 0.15（跨多 prompt 與多模型仍成立），
# 則「β_c=0.508230 為機率雲臨界逆溫度」之主張被否，回 AAS 待證層降級。
