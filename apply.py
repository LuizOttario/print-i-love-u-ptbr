# usage: python3 -I apply.py <original languages.json> <out.json> [com-til]
# Replaces only the value spans of the "en" block; every other byte is copied as-is.
import re, sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pt import PT

src, dst = sys.argv[1], sys.argv[2]
# the game's pixel font has no ã/õ glyphs (they render as nothing), so swap them by default
ALT = None if sys.argv[3:] == ["com-til"] else str.maketrans("ãõÃÕ", "aoAO")
raw = open(src, 'rb').read().decode('utf-8')
orig = json.loads(raw, strict=False)
en = orig['en']

STR = r'"((?:[^"\\]|\\.)*)"'
start = re.search(r'"en"\s*:\s*\{', raw).end()
end = re.search(r'\}\s*,\s*"it"\s*:', raw[start:]).start() + start
pairs = list(re.finditer(STR + r'\s*:\s*' + STR, raw[start:end], re.S))
assert [p.group(1) for p in pairs] == list(en), "raw scan != parsed keys"

w = en['second_trash_message_bad']
PT['second_trash_message_bad'] = "Um pensamento:\n" + "FRACA...PERTINHO DE VOCÊ...TODA MINHA..." * w.count("WEAK...")

def keep(k, v):  # entries left untranslated on purpose
    return (k.startswith('_') and k.endswith('_')) or v.strip(' .') == ''
missing = [k for k in en if k not in PT and not keep(k, en[k])]
extra = [k for k in PT if k not in en]
assert not missing and not extra, (missing, extra)

def enc(v):  # decoded text -> raw file form: \n escape, real CRLF kept, quotes escaped
    v = v.replace('\\', '\\\\').replace('"', '\\"')
    return re.sub(r'(?<!\r)\n', r'\\n', v)

out = raw[start:end]
for p in reversed(pairs):
    k = p.group(1)
    if k in PT:
        v = PT[k].translate(ALT) if ALT else PT[k]
        out = out[:p.start(2)] + enc(v) + out[p.end(2):]
new = raw[:start] + out + raw[end:]
open(dst, 'wb').write(new.encode('utf-8'))

# ---- validation ----
back = open(dst, 'rb').read().decode('utf-8')          # still UTF-8
d = json.loads(back, strict=False)
assert list(d) == list(orig)
assert list(d['en']) == list(en) and len(d['en']) == 224
assert all(d[l] == orig[l] for l in orig if l != 'en'), "other languages changed"
assert back[:start] == raw[:start] and back[start + len(out):] == raw[end:]
assert back.count('\r\n') == raw.count('\r\n')
assert back.replace('\r\n', '').count('\n') == raw.replace('\r\n', '').count('\n') == 0
strip = lambda s: re.sub(r'^\[[0-9.]+\]', '', s)
for k in en:
    a, b = en[k], strip(d['en'][k])
    for ch in '#~@\n\r':
        assert a.count(ch) == b.count(ch), (k, repr(ch), a.count(ch), b.count(ch))
    assert a.startswith('~') == b.startswith('~'), k
print("OK", dst, "| traduzidas:", sum(d['en'][k] != en[k] for k in en), "/ 224",
      "| CRLF:", back.count('\r\n'), "| chars:", sorted({c for v in d['en'].values() for c in v if ord(c) > 126}))
