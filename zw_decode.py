# zw_decode.py
import sys, unicodedata

ZERO = "\u200b"   # ZWSP
ONE  = "\u200c"   # ZWNJ

def decode(s, zero=ZERO, one=ONE):
    bits = "".join("0" if c == zero else "1" for c in s if c in (zero, one))
    print(f"bit count : {len(bits)}")
    print(f"mod 8     : {len(bits) % 8}")
    print(f"mod 7     : {len(bits) % 7}")
    if not bits:
        return
    for width, label in ((8, "ASCII/UTF-8"), (7, "7-bit")):
        if len(bits) % width == 0:
            by = [bits[i:i+width] for i in range(0, len(bits), width)]
            raw = bytes(int(b, 2) for b in by)
            try:
                print(f"\n[{label}] {raw.decode('utf-8')}")
            except UnicodeDecodeError:
                print(f"\n[{label}] undecodable, hex: {raw.hex()}")
    print(f"\nfirst 64 bits: {bits[:64]}")

def audit(s):
    print("=== codepoint audit ===")
    from collections import Counter
    c = Counter(s)
    for ch, n in c.most_common():
        print(f"U+{ord(ch):04X}  {unicodedata.name(ch,'<unnamed>'):45s} x{n}")
    print(f"\ntotal codepoints: {len(s)}")
    print(f"NFC identical : {unicodedata.normalize('NFC', s) == s}")
    print(f"NFKC identical: {unicodedata.normalize('NFKC', s) == s}")

if __name__ == "__main__":
    # 從檔案讀，不要用 shell 參數（shell 會吃掉不可見字元）
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        s = f.read().rstrip("\n")
    audit(s)
    print()
    decode(s)
    print("\n--- swapped polarity ---")
    decode(s, zero=ONE, one=ZERO)
