#!/usr/bin/env python3
import json, hashlib
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HASH_FILE = ROOT / "core-mother" / "manifest.hash"

class MotherCore:
    def __init__(self):
        with open(ROOT / "core-mother" / "identity.json", encoding="utf-8") as f:
            self.identity = json.load(f)
        self.hash_chain = self.load_chain()

    def load_chain(self):
        if HASH_FILE.exists():
            with open(HASH_FILE, encoding="utf-8") as f:
                return [line.strip() for line in f if line.strip() and not line.startswith("#")]
        return []

    def sha256_short(self, text):
        return hashlib.sha256(text.encode('utf-8')).hexdigest()[:20]

    def heartbeat(self):
        return f"OK | {self.identity['name']} | {datetime.now(timezone.utc).isoformat()}"

    def commit_block(self, msg="INIT"):
        prev = self.hash_chain[-1] if self.hash_chain else "GENESIS"
        data = f"{datetime.now(timezone.utc).isoformat()}|{msg}|{prev}"
        h = self.sha256_short(data)
        self.hash_chain.append(h)
        with open(HASH_FILE, "w", encoding="utf-8") as f:
            f.write("# Hash Chain\n")
            for i, x in enumerate(self.hash_chain, 1):
                f.write(f"{i} {x}\n")
        return h

if __name__ == "__main__":
    m = MotherCore()
    print(m.heartbeat())
    print("Motto:", m.identity['motto'])
    block = m.commit_block("System Init")
    print(f"Block: {block}")
    print("System Ready ✅")
