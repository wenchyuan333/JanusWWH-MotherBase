# ==================================================
# 🦉 JANUSWWH — 洛書母體系統 · 統一入口 v1.0
# 接入模組：基礎矩陣 / 交換 / 旋轉 / 循環位移 / 加法群 / 不變性
# ==================================================

import sys
import os

print("="*60)
print("🦉 洛書母體儲存庫 · 統一入口")
print("="*60)
print(f"📂 目前位置：{os.getcwd()}")
print(f"📦 已載入模組：")
print("  ✅ 基礎矩陣運算    matrix.py")
print("  ✅ 行列交換規則    swap.py")
print("  ✅ 旋轉對稱群      luoshu_permute.py")
print("  ✅ 完備數學系統    luoshu_complete.py")
print("="*60)

MENU = """
選擇要執行的模組：
  1 → 基礎矩陣系統
  2 → 行列交換測試
  3 → 洛書旋轉枚舉
  4 → 洛書完備系統（推薦）
  0 → 退出
"""

while True:
    print(MENU)
    choice = input("請輸入選項 > ").strip()
    
    if choice == "0":
        print("\n👋 母體已關閉，所有規則安全封存")
        break
    elif choice == "1":
        print("\n▶ 執行：基礎矩陣系統")
        exec(open("matrix.py").read())
    elif choice == "2":
        print("\n▶ 執行：行列交換測試")
        exec(open("swap.py").read())
    elif choice == "3":
        print("\n▶ 執行：洛書旋轉枚舉")
        exec(open("luoshu_permute.py").read())
    elif choice == "4":
        print("\n▶ 執行：洛書完備系統")
        exec(open("luoshu_complete.py").read())
    else:
        print("\n❌ 無效選項，請重新輸入")
    
    input("\n按 Enter 返回選單...")
    os.system("clear")

print("\n✅ 母體系統卸載完畢 · 全部已封存")

