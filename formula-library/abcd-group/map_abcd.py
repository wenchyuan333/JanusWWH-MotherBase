#!/usr/bin/env python3
"""
ABCD 四元群 — 母體結構映射
A=原點 B=內容 C=邊界 D=流轉
"""

ABCD = {
    'A': 'core-mother — 原點 / 核心本體',
    'B': 'formula-library — 顯現 / 知識內容',
    'C': 'database — 邊界 / 封存索引',
    'D': 'function-loop — 流轉 / 時間演化'
}

OP_TABLE = {
    ('A','A'): 'A', ('A','B'): 'B', ('A','C'): 'C', ('A','D'): 'D',
    ('B','A'): 'B', ('B','B'): 'A', ('B','C'): 'D', ('B','D'): 'C',
    ('C','A'): 'C', ('C','B'): 'D', ('C','C'): 'A', ('C','D'): 'B',
    ('D','A'): 'D', ('D','B'): 'C', ('D','C'): 'B', ('D','D'): 'A',
}

def lookup(a, b):
    return OP_TABLE.get((a.upper(), b.upper()), '?')

def show():
    print("=== ABCD 四元群 映射表 ===")
    for k,v in ABCD.items():
        print(f"  {k} → {v}")
    print("\n運算表:")
    for x in 'ABCD':
        row = ' '.join(lookup(x,y) for y in 'ABCD')
        print(f"  {x}: {row}")
    print("\n口訣：A立心，B顯相，C守界，D生新。")

if __name__ == "__main__":
    show()
