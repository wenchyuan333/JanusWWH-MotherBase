#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
洛書九宮 · 玄空飛星 完整系統
版本: v2.1 一鍵覆蓋版
"""

class LuoShu:
    def __init__(self):
        self.center = 5
        # 原始洛書
        self.base = [
            [4, 9, 2],
            [3, 5, 7],
            [8, 1, 6]
        ]
    
    def show(self, mat, title=""):
        print(f"\n{title}")
        for row in mat:
            print(f"  {row[0]}  {row[1]}  {row[2]}")
    
    def rotate(self, mat, times=1):
        m = [row[:] for row in mat]
        for _ in range(times % 4):
            m = [
                [m[2][0], m[1][0], m[0][0]],
                [m[2][1], m[1][1], m[0][1]],
                [m[2][2], m[1][2], m[0][2]]
            ]
        return m
    
    def shift_outer(self, mat, steps=1):
        outer = [mat[0][0], mat[0][1], mat[0][2],
                 mat[1][2], mat[2][2], mat[2][1], mat[2][0], mat[1][0]]
        n = steps % 8
        outer = outer[-n:] + outer[:-n] if n > 0 else outer
        return [
            [outer[0], outer[1], outer[2]],
            [outer[7], 5, outer[3]],
            [outer[6], outer[5], outer[4]]
        ]
    
    def xuankong(self, star_num):
        """玄空飛星：入中、順飛"""
        seq = [5, 6, 7, 8, 9, 1, 2, 3, 4]
        idx = seq.index(star_num)
        seq = seq[idx:] + seq[:idx]
        positions = [[2,2],[1,0],[0,1],[1,2],[2,1],[1,1],[0,0],[0,2],[2,0]]
        flying = [[0]*3 for _ in range(3)]
        for pos, num in zip(positions, seq):
            flying[pos[0]][pos[1]] = num
        return flying

if __name__ == "__main__":
    ls = LuoShu()
    print("="*40)
    print("🔮 洛書玄空系統 v2.1 · 就緒")
    print("="*40)
    ls.show(ls.base, "【原始洛書】")
    
    ls.show(ls.rotate(ls.base, 1), "R90°")
    ls.show(ls.shift_outer(ls.base, 1), "外圈+1")
    ls.show(ls.xuankong(5), "玄空 · 五入中")
    
    print("\n✅ 全部就緒！")
