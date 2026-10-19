#!/usr/bin/env python3
"""
熱拔插模組管理器 — 上線/卸載不中斷母體
"""
from pathlib import Path
import sys, importlib.util

ROOT = Path(__file__).resolve().parent.parent
MODULE_DIR = ROOT / "hotplug-modules"

class HotPlug:
    def __init__(self):
        self.loaded = {}

    def list_available(self):
        return [p.name for p in MODULE_DIR.glob("*/") if p.is_dir() and p.name != "__pycache__"]

    def load(self, name):
        path = MODULE_DIR / name / "__init__.py"
        if not path.exists():
            return f"❌ {name}: 不存在"
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
        self.loaded[name] = mod
        return f"✅ {name}: 已掛載"

    def status(self):
        return f"活躍模組: {list(self.loaded.keys()) or '無'}"

if __name__ == "__main__":
    hp = HotPlug()
    print("🔌 熱拔插系統就緒")
    print("可用模組:", hp.list_available())
