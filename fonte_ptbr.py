# Adiciona ã õ Ã Õ às fontes do Print I Love U, editando o data.win da SUA cópia do jogo.
#
# uso: python3 fonte_ptbr.py "CAMINHO/DO/JOGO"
#
# Como funciona: as duas fontes desenhadas do jogo (Font_Mio_2, pixelada, e Font_Author,
# manuscrita) têm as letras ë ï Ë Ï, que nenhum idioma do jogo usa. O script troca essas
# quatro por ã õ Ã Õ na lista de letras e desenha as novas a partir das próprias letras do jogo
# (â ô Â Ô com o til do ñ). Os desenhos vão para um espaço vazio da textura das fontes; a
# textura é recomprimida e o que vem depois dela no arquivo (outra textura e os áudios) é
# deslocado, com os ponteiros corrigidos. Nenhum arquivo do jogo vem neste repositório.
# Faz data.win.bak antes (se ainda não existir) e só troca o data.win depois de validar tudo.
import bz2, os, struct, sys
import numpy as np

SLOT = {'ã': 'ë', 'õ': 'ï', 'Ã': 'Ë', 'Õ': 'Ï'}      # letra nova -> vaga que ela ocupa
BASE = {'ã': 'â', 'õ': 'ô', 'Ã': 'Â', 'Õ': 'Ô'}      # letra do jogo usada como base
FONTS = ('Font_Mio_2', 'Font_Author')


# ---------- texturas do GameMaker: variante de QOI dentro de bzip2 ----------
# Segue o QoiConverter do UndertaleModTool: as diferenças de cor são em complemento de dois.
def sx(v, bits):  # inteiro com sinal de `bits` bits
    return v - (1 << bits) if v & (1 << (bits - 1)) else v


def qoi_decode(s):
    assert s[:4] == b'fioq'
    w, h, n = struct.unpack_from('<HHI', s, 4)
    out = np.empty((w * h, 4), np.uint8)
    idx = [(0, 0, 0, 0)] * 64
    r, g, b, a = 0, 0, 0, 255
    p, end, i, total = 12, 12 + n, 0, w * h
    while i < total:
        run = 0
        if p < end:
            b1 = s[p]; p += 1
            if (b1 & 0xc0) == 0x00: r, g, b, a = idx[b1]
            elif (b1 & 0xe0) == 0x40: run = b1 & 0x1f
            elif (b1 & 0xe0) == 0x60: run = ((b1 & 0x1f) << 8 | s[p]) + 32; p += 1
            elif (b1 & 0xc0) == 0x80:
                r = (r + sx((b1 >> 4) & 3, 2)) & 255; g = (g + sx((b1 >> 2) & 3, 2)) & 255; b = (b + sx(b1 & 3, 2)) & 255
            elif (b1 & 0xe0) == 0xc0:
                b2 = s[p]; p += 1
                r = (r + sx(b1 & 31, 5)) & 255; g = (g + sx(b2 >> 4, 4)) & 255; b = (b + sx(b2 & 15, 4)) & 255
            elif (b1 & 0xf0) == 0xe0:
                m = b1 << 16 | s[p] << 8 | s[p + 1]; p += 2
                r = (r + sx((m >> 15) & 31, 5)) & 255; g = (g + sx((m >> 10) & 31, 5)) & 255
                b = (b + sx((m >> 5) & 31, 5)) & 255; a = (a + sx(m & 31, 5)) & 255
            else:
                if b1 & 8: r = s[p]; p += 1
                if b1 & 4: g = s[p]; p += 1
                if b1 & 2: b = s[p]; p += 1
                if b1 & 1: a = s[p]; p += 1
            if (b1 & 0xc0) != 0x40:  # todo op menos RUN grava no índice
                idx[(r ^ g ^ b ^ a) & 63] = (r, g, b, a)
        k = min(run + 1, total - i)
        out[i:i + k] = (r, g, b, a); i += k
    assert p == end, 'textura com tamanho inesperado'
    return out.reshape(h, w, 4)


def qoi_encode(px):
    h, w, _ = px.shape
    flat = np.ascontiguousarray(px).reshape(-1, 4)
    v = flat.view('<u4').ravel()
    prev_v = np.empty_like(v); prev_v[0] = 0xff000000; prev_v[1:] = v[:-1]
    changes = np.nonzero(v != prev_v)[0]
    cols = flat[changes].tolist()
    o = bytearray(b'\0' * 12)
    idx = [(0, 0, 0, 0)] * 64  # igual ao decodificador
    pr, pg, pb, pa = 0, 0, 0, 255

    def runs(n):
        while n > 0:
            c = min(n, 0x2020); n -= c
            if c < 33: o.append(0x40 | (c - 1))
            else: c -= 33; o.append(0x60 | (c >> 8)); o.append(c & 0xff)

    last = -1
    for pos, (r, g, b, a) in zip(changes.tolist(), cols):
        runs(pos - last - 1); last = pos
        hh = (r ^ g ^ b ^ a) & 63
        if idx[hh] == (r, g, b, a):
            o.append(hh)
        else:
            idx[hh] = (r, g, b, a)
            vr, vg, vb, va = r - pr, g - pg, b - pb, a - pa
            if -17 < vr < 16 and -17 < vg < 16 and -17 < vb < 16 and -17 < va < 16:
                if va == 0 and -3 < vr < 2 and -3 < vg < 2 and -3 < vb < 2:
                    o.append(0x80 | (vr << 4 & 48) | (vg << 2 & 12) | (vb & 3))
                elif va == 0 and -9 < vg < 8 and -9 < vb < 8:
                    o.append(0xc0 | (vr & 31)); o.append((vg << 4 & 240) | (vb & 15))
                else:
                    o.append(0xe0 | (vr >> 1 & 15))
                    o.append((vr << 7 & 128) | (vg << 2 & 124) | (vb >> 3 & 3))
                    o.append((vb << 5 & 224) | (va & 31))
            else:
                o.append(0xf0 | (8 if vr else 0) | (4 if vg else 0) | (2 if vb else 0) | (1 if va else 0))
                if vr: o.append(r)
                if vg: o.append(g)
                if vb: o.append(b)
                if va: o.append(a)
        pr, pg, pb, pa = r, g, b, a
    runs(len(v) - last - 1)
    o[0:12] = b'fioq' + struct.pack('<HHI', w, h, len(o) - 12)
    return bytes(o)


# ---------- desenho das letras novas ----------
def accent_mask(m, pixel):
    acc = np.zeros_like(m)
    if pixel:                       # fonte pixelada: o acento ocupa as 2 primeiras "linhas" (10 px)
        acc[:10] = m[:10]; return acc
    ink = m.sum(1); top = np.nonzero(ink)[0][0]   # manuscrita: corta na linha mais vazia
    cut = min(range(top + 4, top + 26), key=lambda y: (ink[y], -y))
    acc[:cut] = m[:cut]; return acc


def bbox(m):
    ys, xs = np.nonzero(m); return ys.min(), ys.max(), xs.min(), xs.max()


def build(full, font, new):
    pixel = font == 'Font_Mio_2'
    bm, dm = full(BASE[new])[..., 3] > 0, full('ñ')[..., 3] > 0
    acc, til = accent_mask(bm, pixel), accent_mask(dm, pixel)
    ay0, ay1, ax0, ax1 = bbox(acc); ty0, ty1, tx0, tx1 = bbox(til)
    if not pixel and new.isupper():  # maiúscula manuscrita: til reduzido ao tamanho do circunflexo
        crop = til[ty0:ty1 + 1, tx0:tx1 + 1]; H0, W0 = crop.shape
        h = ay1 - ay0 + 1; w = max(h, round(W0 * h / H0))
        def near(n, N):  # vizinho mais próximo, mesmo arredondamento do PIL (soma acumulada)
            s, v, out = N / n, N / n * 0.5, []
            for _ in range(n): out.append(int(v)); v += s
            return np.array(out)
        ry, rx = near(h, H0), near(w, W0)
        til = np.zeros_like(til); til[ay0:ay0 + h, tx0:tx0 + w] = crop[ry][:, rx]
        ty0, ty1, tx0, tx1 = bbox(til)
    dx = round(((ax0 + ax1) - (tx0 + tx1)) / 2); dy = ay1 - ty1
    if pixel: dx = 5 * round(dx / 5)
    out = bm & ~acc
    ys, xs = np.nonzero(til); ys, xs = ys + dy, xs + dx
    assert ys.min() >= 0 and xs.min() >= 0 and xs.max() < out.shape[1]
    out[ys, xs] = True
    img = np.zeros(bm.shape + (4,), np.uint8); img[out] = 255
    return img


# ---------- patch ----------
def main(game):
    path = os.path.join(game, 'data.win') if os.path.isdir(game) else game
    b = bytearray(open(path, 'rb').read())
    u32 = lambda o: struct.unpack_from('<I', b, o)[0]
    if 'ãõÃÕ'.encode() in b:
        print('A fonte já está corrigida. Nada a fazer.'); return
    ch = {}; o = 8
    while o < len(b): ch[bytes(b[o:o + 4]).decode()] = (o, u32(o + 4)); o += 8 + u32(o + 4)
    assert list(ch)[-2:] == ['TXTR', 'AUDO'], 'data.win com formato inesperado'

    i = b.find(b'xyz{|}~'); ms = b.rfind(b' !"#$%', 0, i)
    MAP = bytes(b[ms:ms + u32(ms - 4)]).decode()
    assert b.count('ëïËÏ'.encode()) == 1 and all(c in MAP for c in SLOT.values()), 'mapa da fonte não encontrado'
    newmap = MAP.translate(str.maketrans({v: k for k, v in SLOT.items()})).encode()
    b[ms:ms + len(newmap)] = newmap

    ts, tl = ch['TPAG'][0] + 8, ch['TPAG'][1]
    ss = ch['SPRT'][0] + 8
    fonts = {}
    for k in range(u32(ss)):
        sp = u32(ss + 4 + 4 * k)
        if not sp: continue
        np_ = u32(sp); name = bytes(b[np_:np_ + u32(np_ - 4)]).decode('utf-8', 'replace') if 0 < np_ < len(b) else ''
        if name not in FONTS: continue
        off = next(q for q in range(40, 160, 4) if u32(sp + q) == len(MAP))
        fonts[name] = (u32(sp + 4), u32(sp + 8), [u32(sp + off + 4 + 4 * j) for j in range(len(MAP))])
    assert set(fonts) == set(FONTS), 'fontes não encontradas'

    xs = ch['TXTR'][0] + 8; ntex = u32(xs); tents = [u32(xs + 4 + 4 * k) for k in range(ntex)]
    E1, E2 = tents[1], tents[2]; blob1, blob2 = u32(E1 + 24), u32(E2 + 24)
    assert b[blob1:blob1 + 4] == b'2zoq' and b[blob2:blob2 + 4] == b'2zoq'
    print('Lendo a textura das fontes (pode levar 1-2 minutos)...')
    tex = qoi_decode(bz2.decompress(bytes(b[blob1 + 12:blob1 + u32(E1 + 8)])))

    occ = tex[..., 3] > 0
    for k in range(u32(ts)):
        t = u32(ts + 4 + 4 * k); sx, sy, sw, sh = struct.unpack_from('<4H', b, t)
        if struct.unpack_from('<H', b, t + 20)[0] == 1: occ[sy:sy + sh, sx:sx + sw] = True

    def find_spot(h, w, pad=2):
        ii = np.pad(occ.astype(np.int32).cumsum(0).cumsum(1), ((1, 0), (1, 0)))
        hh, ww = h + 2 * pad, w + 2 * pad
        s = ii[hh:, ww:] - ii[:-hh, ww:] - ii[hh:, :-ww] + ii[:-hh, :-ww]
        ys, xs_ = np.nonzero(s == 0); k = np.lexsort((xs_, ys))[0]
        return ys[k] + pad, xs_[k] + pad

    for font in FONTS:
        FW, FH, frames = fonts[font]
        def full(c, frames=frames, FW=FW, FH=FH):
            sx, sy, sw, sh, tx, ty, tw, th = struct.unpack_from('<8H', b, frames[MAP.index(c)])
            can = np.zeros((FH, FW, 4), np.uint8); can[ty:ty + th, tx:tx + tw] = tex[sy:sy + sh, sx:sx + sw]
            return can
        for new, old in SLOT.items():
            img = build(full, font, new)
            yy, xx = np.nonzero(img[..., 3]); y0, y1, x0, x1 = yy.min(), yy.max(), xx.min(), xx.max()
            crop = img[y0:y1 + 1, x0:x1 + 1]; h, w = crop.shape[:2]
            tp = frames[MAP.index(old)]
            assert sum(p == tp for f in fonts.values() for p in f[2]) == 1
            assert struct.unpack_from('<3H', b, tp + 16) == (FW, FH, 1)
            sy, sx = find_spot(h, w)
            tex[sy:sy + h, sx:sx + w] = crop; occ[sy - 2:sy + h + 2, sx - 2:sx + w + 2] = True
            struct.pack_into('<8H', b, tp, sx, sy, w, h, x0, y0, w, h)
            print(f'  {font}: {new} desenhada')

    print('Recomprimindo a textura...')
    q = qoi_encode(tex)
    assert np.array_equal(qoi_decode(q), tex), 'falha ao recomprimir a textura'
    W, H = tex.shape[1], tex.shape[0]
    newblob = b'2zoq' + struct.pack('<HHI', W, H, len(q)) + bz2.compress(q, 9)

    end1 = blob1 + len(newblob); start2 = -(-end1 // 128) * 128; delta = start2 - blob2
    out = bytearray(bytes(b[:blob1]) + newblob + bytes(start2 - end1) + bytes(b[blob2:]))
    struct.pack_into('<I', out, E1 + 8, len(newblob))
    struct.pack_into('<I', out, E2 + 24, blob2 + delta)
    to, tlen = ch['TXTR']; struct.pack_into('<I', out, to + 4, tlen + delta)
    struct.pack_into('<I', out, 4, u32(4) + delta)
    ao = ch['AUDO'][0] + delta; na = struct.unpack_from('<I', out, ao + 8)[0]
    for k in range(na):
        p = ao + 12 + 4 * k; struct.pack_into('<I', out, p, struct.unpack_from('<I', out, p)[0] + delta)

    # validação antes de trocar o arquivo
    n = bytes(out); U = lambda o: struct.unpack_from('<I', n, o)[0]
    o = 8; seen = []
    while o < len(n): seen.append(n[o:o + 4].decode()); o += 8 + U(o + 4)
    assert o == len(n) and seen == list(ch) and U(4) == len(n) - 8
    for k in range(ntex):
        e = U(xs + 4 + 4 * k); p = U(e + 24)
        assert n[p:p + 4] == b'2zoq' and len(bz2.decompress(n[p + 12:p + U(e + 8)])) == U(p + 8)
    a0 = ch['AUDO'][0]
    for k in range(u32(a0 + 8)):
        po, pn = u32(a0 + 12 + 4 * k), U(a0 + delta + 12 + 4 * k)
        assert pn == po + delta and n[pn:pn + 4 + u32(po)] == bytes(b[po:po + 4 + u32(po)])

    bak = path + '.bak'
    if not os.path.exists(bak):
        os.replace(path, bak); print(f'Backup do original: {bak}')
    open(path + '.tmp', 'wb').write(n); os.replace(path + '.tmp', path)
    print('OK! Fonte corrigida. Agora rode o apply.py para instalar a tradução com til.')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('uso: python3 fonte_ptbr.py "CAMINHO/DO/JOGO"')
    main(sys.argv[1])
