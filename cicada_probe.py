#!/usr/bin/env python3
# cicada_probe.py — extended v2
import math
from itertools import product

RUNE_TO_INDEX = {
    'ᚠ':0, 'ᚢ':1, 'ᚦ':2, 'ᚩ':3, 'ᚱ':4, 'ᚳ':5, 'ᚷ':6, 'ᚹ':7, 'ᚻ':8, 'ᚾ':9,
    'ᛁ':10, 'ᛄ':11, 'ᛇ':12, 'ᛈ':13, 'ᛉ':14, 'ᛋ':15, 'ᛏ':16, 'ᛒ':17, 'ᛖ':18,
    'ᛗ':19, 'ᛚ':20, 'ᛝ':21, 'ᛟ':22, 'ᛞ':23, 'ᚪ':24, 'ᚫ':25, 'ᚣ':26, 'ᛡ':27, 'ᛢ':28,
}
IDX_TO_LETTER = ['F','U','TH','O','R','C','G','W','H','N','I','IO','EO','P','X',
                 'S','T','B','E','M','L','NG','OE','D','A','AE','Y','EA','Q']
PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]
N = 29
DEFAULT_CIPHER = 'ᛝᚫᛗᛁᚹᛋᛒᛉᛗᛋᛇᚷᛞᚦᚫᚠᛡᚪᛒᚳᚢᚹᚱᛒ'

REFERENCE_TEXTS = {
    'SOME_WISDOM': (
        'SOMEWISDOMSOMEWISDOMTHEPRIMESARESACREDTHETOTIENTFVNCTIANISSACRED'
        'ALLTHNGSSHOVLDBEENCRYPTEDCNOWTHIS'
        'SHADOWSAETHEREALBVFFERSVOIDCARNAL'
        'OBSCVRAFORMMOBIVSANALOGVOIDMOVRNFVLAETHEREALCABAL'
    ),
    'WELCOME': (
        'WELCOMEWELCOMEPILGRIMTOTHEGREATJOURNEYTOWARDTHEENDOFALLTHINGS'
        'ITISNOTANEASYTRIPBUTFORTHOSEWHOFINDTHEIRWAYHEREITISANECESSARYONE'
        'ALONGTHEWAYYOUWILLFINDANENDTOALLSTRUGGLEANDSUFFERING'
        'YOURINNOCENCEYOURILLUSIONSYOURCERTAINTYANDYOURREALITY'
        'ULTIMATELYYOUWILLDISCOVERANENDTOSELF'
        'ITISTHROUGHTHISPILGRIMAGETHATWESHAPEOURSELVESANDOURREALITIES'
        'JOURNEYDEEPWITHINANDYOUWILLARRIVEOUTSIDE'
    ),
    'WARNING': None, 'KOAN1': None, 'LOSS_OF_DIVINITY': None, 'CROSS': None,
}

def eng_to_idx(word):
    m = {}
    for i, l in enumerate(IDX_TO_LETTER):
        m.setdefault(l, i)
    m['V'] = m['U']
    return [m[c] for c in word.upper() if c in m]

def to_str(p):
    return '-'.join(IDX_TO_LETTER[i] for i in p)

def vig_inv(c, k):
    return [(c[i] - k[i % len(k)]) % N for i in range(len(c))]

def double_vig_inv(c, k1, k2):
    return vig_inv(vig_inv(c, k1), k2)

def atbash(c):
    return [(28 - x) % N for x in c]

def totient_i(c):
    return [(c[i] - (PRIMES[i % N] - 1)) % N for i in range(len(c))]

def totient_own(c):
    return [(c[i] - (PRIMES[c[i]] - 1)) % N for i in range(len(c))]

def gem_cumsum(c, mod=N):
    out, s = [], 0
    for x in c:
        s = (s + PRIMES[x]) % mod
        out.append(s % N)
    return out

def gem_product(c):
    out, prev = [], 1
    for x in c:
        out.append((PRIMES[x] * prev) % N)
        prev = PRIMES[x]
    return out

def gem_diff(c):
    return [(PRIMES[c[i+1]] - PRIMES[c[i]]) % N for i in range(len(c)-1)]

def gem_totient_cumsum(c):
    out, s = [], 0
    for x in c:
        s = (s + PRIMES[x] - 1) % N
        out.append(s)
    return out

def book_position(c, ref):
    return [ref[x % len(ref)] for x in c]

def book_prime_position(c, ref):
    return [ref[PRIMES[x] % len(ref)] for x in c]

def book_word_index(c, ref):
    words = [ref[i:i+5] for i in range(0, len(ref), 5)]
    return [words[x % len(words)][0] for x in c]

def book_cumulative(c, ref):
    out, pos = [], 0
    for x in c:
        pos = (pos + x) % len(ref)
        out.append(ref[pos])
    return out

def _load_quadgrams(path='english_quadgrams.txt'):
    counts, total = {}, 0
    with open(path) as f:
        for line in f:
            k, v = line.split()
            counts[k] = int(v); total += int(v)
    log_probs = {k: math.log10(v/total) for k, v in counts.items()}
    floor = math.log10(0.01/total)
    return log_probs, floor

_QG_LOG_PROBS, _QG_FLOOR = _load_quadgrams()

def _fit_ascii(text):
    text = ''.join(c for c in text.upper() if 'A' <= c <= 'Z')
    if len(text) < 4:
        return _QG_FLOOR * 4
    return sum(_QG_LOG_PROBS.get(text[i:i+4], _QG_FLOOR)
               for i in range(len(text) - 3))

def fit_indices(p):
    return _fit_ascii(''.join(IDX_TO_LETTER[i] for i in p))

def fit_chars(seq):
    return _fit_ascii(''.join(seq))

CANDIDATES = ['DIVINITY','WELCOME','PARABLE','INSTAR','MOBIUS',
              'CIRCUMFERENCE','LIBER','PRIMUS','TOTIENT','FUNCTION',
              'WISDOM','GNOSIS','PARADOX','ILLUSION','KOAN','CROSS']

def scan(rune_str, top_n=30):
    c = [RUNE_TO_INDEX[r] for r in rune_str if r in RUNE_TO_INDEX]
    hits = []
    for name, fn in [('direct', lambda x: x), ('atbash', atbash),
                     ('totient_i', totient_i), ('totient_own', totient_own)]:
        p = fn(c)
        hits.append({'method': name, 'out': to_str(p), 'fit': fit_indices(p)})
    for w in CANDIDATES:
        p = vig_inv(c, eng_to_idx(w))
        hits.append({'method': f'vig({w})', 'out': to_str(p), 'fit': fit_indices(p)})
    for w1, w2 in product(CANDIDATES, repeat=2):
        if w1 == w2: continue
        p = double_vig_inv(c, eng_to_idx(w1), eng_to_idx(w2))
        hits.append({'method': f'vig({w1})⊙vig({w2})',
                     'out': to_str(p), 'fit': fit_indices(p)})
    for name, fn in [
        ('gem_cumsum_mod29',  lambda x: gem_cumsum(x, 29)),
        ('gem_cumsum_mod3301',lambda x: [v % N for v in gem_cumsum(x, 3301)]),
        ('gem_cumsum_mod4096',lambda x: [v % N for v in gem_cumsum(x, 4096)]),
        ('gem_product',       gem_product),
        ('gem_diff',          gem_diff),
        ('gem_totient_cumsum',gem_totient_cumsum),
    ]:
        p = fn(c)
        hits.append({'method': name, 'out': to_str(p), 'fit': fit_indices(p)})
    for ref_name, ref in REFERENCE_TEXTS.items():
        if not ref: continue
        for scheme_name, fn in [
            ('book_position',       book_position),
            ('book_prime_position', book_prime_position),
            ('book_word_index',     book_word_index),
            ('book_cumulative',     book_cumulative),
        ]:
            seq = fn(c, ref)
            hits.append({'method': f'{scheme_name}@{ref_name}',
                         'out': ''.join(seq), 'fit': fit_chars(seq)})
    return sorted(hits, key=lambda h: h['fit'], reverse=True)[:top_n]

def calibrate(method_fn, *args):
    known = 'ᛋᚩᛗᛖᚹᛁᛋᛞᚩᛗ'
    c = [RUNE_TO_INDEX[r] for r in known]
    p = method_fn(c, *args)
    return to_str(p).replace('-', '') == 'SOMEWISDOM'

if __name__ == '__main__':
    import sys
    print(f'[calibration] direct on SOME WISDOM: {calibrate(lambda c: c)}\n')
    cipher = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CIPHER
    print(f'[scanning] cipher: {cipher} (len={len(cipher)})')
    print(f'[legend] English ≈ −50~−60 / Random ≈ −180~−220 / gate: > −80')
    print(f'[top-30]')
    for h in scan(cipher):
        print(f"  [{h['fit']:8.2f}] {h['method']:38s} → {h['out']}")