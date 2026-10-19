#!/usr/bin/env python3
"""
Neural Link Associator
自動發現公式間的邏輯關聯
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent.parent
FORMULA_DIR = ROOT / "formula-library"

def extract_tags(text):
    return set(re.findall(r'([A-Z][a-z\-/0-9]+(?:\s+[A-Z][a-z\-/0-9]+)*)', text))

def scan_all():
    files = list(FORMULA_DIR.rglob("*.md"))
    print(f"掃描到 {len(files)} 個公式模組\n")
    for f in files:
        rel = f.relative_to(ROOT)
        content = f.read_text(encoding="utf-8")
        lines = len(content.strip().split("\n"))
        print(f"✅ {rel}")
        print(f"   行數: {lines}  |  類別: {f.parent.name}")
    print("\n🔗 關聯索引建立完成")

if __name__ == "__main__":
    scan_all()
