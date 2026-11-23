"""Libreria di concept visivi VoceInteriore2025 (sfondi generati, sempre diversi).
Ogni concept restituisce un'immagine RGB e i metadati usati dal registro anti-ripetizione
(tools/bg_log.json): soggetto, ambientazione, palette, luce, prospettiva, composizione, tono del testo.
Uso: render(concept, w, h, seed, variant) -> (Image, meta)
Le foto vere (persone, luoghi reali) si usano con {"photo": "backgrounds/<file>.jpg"} nello SPEC."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _grad(h, w, stops):
    """Gradiente verticale con stops [(pos, (r,g,b)), ...]."""
    y = np.linspace(0, 1, h)
    out = np.zeros((h, 3))
    for c in range(3):
        out[:, c] = np.interp(y, [s[0] for s in stops], [s[1][c] for s in stops])
    return np.broadcast_to(out[:, None, :], (h, w, 3)).astype(np.float32).copy()

def _noise1d(n, rng, octaves=6, rough=0.5):
    out = np.zeros(n); amp = 1.0; tot = 0
    for o in range(octaves):
        k = 2 ** (o + 2)
        pts = rng.random(k + 1)
        out += amp * np.interp(np.linspace(0, k, n), np.arange(k + 1), pts); tot += amp; amp *= rough
    return out / tot

def _ridge(col, base_y, amp, color, rng, h, w, rough=0.5, alpha=1.0):
    ys = (base_y - amp * _noise1d(w, rng, rough=rough)) * h
    yy = np.arange(h)[:, None]
    m = (yy >= ys[None, :]).astype(np.float32)[..., None] * alpha
    col[:] = col * (1 - m) + np.array(color, np.float32) * m
    return ys

def _glow(col, cx, cy, r, color, k=0.6):
    h, w, _ = col.shape
    y = np.linspace(0, 1, h)[:, None]; x = np.linspace(0, 1, w)[None, :]
    d = np.sqrt(((x - cx) * w / h) ** 2 + (y - cy) ** 2)
    col += np.exp(-(d / r) ** 2)[..., None] * np.array(color, np.float32) * k

def _grain(col, rng, s=3.5):
    col += rng.normal(0, s, col.shape[:2] + (1,)); return col

def _vignette(col, k=0.45):
    h, w, _ = col.shape
    y = np.linspace(0, 1, h)[:, None]; x = np.linspace(0, 1, w)[None, :]
    v = 1 - k * (((x - 0.5) * 1.6) ** 2 + ((y - 0.5) * 1.2) ** 2)
    col *= np.clip(v, 0.4, 1)[..., None]

def _img(col): return Image.fromarray(np.clip(col, 0, 255).astype(np.uint8))

def _bokeh(img, rng, n, colors, rmin, rmax, ymin=0, ymax=1, blur=6, alpha=(40, 120)):
    w, h = img.size; lay = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for _ in range(n):
        x = rng.random() * w; y = (ymin + rng.random() * (ymax - ymin)) * h; r = rmin + rng.random() * (rmax - rmin)
        c = colors[rng.integers(len(colors))]; a = int(alpha[0] + rng.random() * (alpha[1] - alpha[0]))
        d.ellipse((x - r, y - r, x + r, y + r), fill=tuple(c) + (a,))
    img = img.convert("RGBA"); img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(blur))); return img.convert("RGB")

# ---------------------------------------------------------------- concept
def candela(w, h, rng, v):
    warm = [(255, 190, 110), (255, 160, 90), (255, 210, 150)][v % 3]
    col = _grad(h, w, [(0, (8, 6, 6)), (0.6, (22, 14, 10)), (1, (12, 8, 6))])
    cx, cy = [0.5, 0.32, 0.68][v % 3], 0.6
    _glow(col, cx, cy - 0.04, 0.42, warm, 0.45); _glow(col, cx, cy - 0.04, 0.12, warm, 0.6)
    img = _img(_grain(col, rng)); d = ImageDraw.Draw(img)
    cw = w * 0.075; top = cy * h
    d.rounded_rectangle((cx * w - cw / 2, top, cx * w + cw / 2, h * 0.8), 8, fill=(236, 222, 200))
    d.ellipse((cx * w - cw * 1.6, h * 0.79, cx * w + cw * 1.6, h * 0.83), fill=(70, 52, 36))
    sh = Image.new("L", (w, h), 0); ImageDraw.Draw(sh).rectangle((cx * w, top, cx * w + cw / 2, h * 0.8), fill=60)
    img.paste((180, 160, 140), mask=sh.filter(ImageFilter.GaussianBlur(10)))
    fl = Image.new("RGBA", (w, h), (0, 0, 0, 0)); fd = ImageDraw.Draw(fl)
    fx, fy = cx * w, top - 8
    fd.ellipse((fx - 16, fy - 92, fx + 16, fy), fill=(255, 236, 190, 255))
    fd.ellipse((fx - 8, fy - 40, fx + 8, fy - 2), fill=(255, 255, 240, 255))
    img = img.convert("RGBA"); img.alpha_composite(fl.filter(ImageFilter.GaussianBlur(3)))
    d = ImageDraw.Draw(img); d.line((fx, top - 6, fx, top + 4), fill=(40, 30, 20), width=3)
    img = _bokeh(img, rng, 18, [warm], 20, 70, 0.45, 0.95, 14, (20, 70))
    return img, dict(soggetto="candela accesa", ambientazione="interno buio", palette="ambra scura",
                     luce="fiamma calda puntiforme", prospettiva="frontale ravvicinata", composizione=["centrale", "sinistra", "destra"][v % 3], tono="dark")

def finestra(w, h, rng, v):
    col = _grad(h, w, [(0, (28, 22, 20)), (1, (16, 12, 12))])
    light = [(255, 226, 170), (210, 228, 255), (255, 210, 190)][v % 3]
    img = _img(_grain(col, rng)).convert("RGBA")
    wx0, wy0, wx1, wy1 = w * 0.18, h * 0.12, w * 0.82, h * 0.58
    win = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(win)
    d.rectangle((wx0, wy0, wx1, wy1), fill=light + (255,))
    bar = int(w * 0.022)
    d.rectangle(((wx0 + wx1) / 2 - bar / 2, wy0, (wx0 + wx1) / 2 + bar / 2, wy1), fill=(30, 24, 22, 255))
    d.rectangle((wx0, (wy0 + wy1) / 2 - bar / 2, wx1, (wy0 + wy1) / 2 + bar / 2), fill=(30, 24, 22, 255))
    img.alpha_composite(win.filter(ImageFilter.GaussianBlur(4)))
    # luce proiettata sul pavimento
    beam = Image.new("L", (w, h), 0); bd = ImageDraw.Draw(beam)
    bd.polygon([(wx0, wy1), (wx1, wy1), (w * 1.05, h), (-w * 0.05, h)], fill=70)
    img.paste(light, mask=beam.filter(ImageFilter.GaussianBlur(40)))
    gl = np.array(img.convert("RGB"), np.float32); _glow(gl, 0.5, 0.35, 0.45, light, 0.25); _vignette(gl, 0.5)
    return _img(gl), dict(soggetto="finestra con luce", ambientazione="interno di casa", palette=["luce calda", "luce fredda", "luce rosata"][v % 3],
                          luce="controluce dalla finestra", prospettiva="frontale", composizione="finestra in alto, luce a terra", tono="dark")

def montagne(w, h, rng, v):
    P = [[(250, 214, 170), (240, 170, 140), (120, 90, 120), (60, 50, 80), (30, 26, 44)],
         [(200, 226, 245), (150, 190, 220), (90, 120, 160), (50, 70, 100), (24, 32, 50)],
         [(255, 236, 200), (230, 200, 160), (150, 130, 110), (90, 80, 70), (40, 36, 34)]][v % 3]
    col = _grad(h, w, [(0, P[1]), (0.45, P[0]), (1, P[0])])
    _glow(col, 0.5 + 0.2 * (rng.random() - 0.5), 0.42, 0.25, (255, 240, 210), 0.35)
    for i, (by, amp) in enumerate([(0.55, 0.16), (0.63, 0.14), (0.72, 0.12), (0.82, 0.1)]):
        c = np.array(P[min(i + 1, 4)], np.float32); _ridge(col, by, amp, c, rng, h, w, rough=0.55)
    _grain(col, rng, 2.5)
    return _img(col), dict(soggetto="catene montuose", ambientazione="montagna", palette=["tramonto pesca", "azzurro freddo", "sabbia"][v % 3],
                           luce="cielo luminoso diffuso", prospettiva="panoramica a strati", composizione="orizzonte a metà", tono="dark")

def mare(w, h, rng, v):
    sky = [[(30, 40, 80), (240, 150, 110), (255, 210, 150)], [(120, 170, 210), (200, 225, 240), (250, 245, 230)],
           [(12, 16, 36), (40, 50, 90), (120, 120, 170)]][v % 3]
    hz = 0.5
    col = _grad(h, w, [(0, sky[0]), (hz * 0.8, sky[1]), (hz, sky[2]), (hz + 0.001, tuple(int(c * 0.55) for c in sky[1])), (1, tuple(int(c * 0.25) for c in sky[0]))])
    sx = 0.5 + 0.25 * (rng.random() - 0.5)
    _glow(col, sx, hz - 0.03, 0.06, (255, 240, 200), 1.2 if v != 2 else 0.8)
    _glow(col, sx, hz - 0.03, 0.2, (255, 220, 170), 0.4)
    yy = np.arange(h); xx = np.arange(w)
    for y in range(int(hz * h), h, 3):
        t = (y - hz * h) / (h * (1 - hz)); width = 0.04 + 0.25 * t
        m = np.exp(-(((xx / w - sx) / width) ** 2)) * (0.5 + 0.5 * np.sin(xx * (0.02 + rng.random() * 0.05) + rng.random() * 6)) ** 4
        col[y:y + 2] += m[None, :, None] * np.array([255, 230, 190]) * 0.5 * (1 - 0.5 * t)
    _grain(col, rng, 3)
    return _img(col), dict(soggetto="sole sul mare", ambientazione="mare aperto", palette=["tramonto", "giorno chiaro", "notte lunare"][v % 3],
                           luce="riflesso sull'acqua", prospettiva="orizzonte frontale", composizione="orizzonte centrale", tono="dark")

def bosco(w, h, rng, v):
    tint = [(150, 190, 140), (200, 170, 120), (140, 160, 190)][v % 3]
    col = _grad(h, w, [(0, tuple(int(c * 0.9) for c in tint)), (1, tuple(int(c * 0.25) for c in tint))])
    img = _img(col).convert("RGBA")
    for layer, (n, dark, wmin, wmax) in enumerate([(14, 0.55, 8, 20), (10, 0.35, 18, 36), (6, 0.12, 36, 80)]):
        lay = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        c = tuple(int(x * dark) for x in tint) + (255,)
        for _ in range(n):
            x = rng.random() * w; tw = wmin + rng.random() * (wmax - wmin)
            d.rectangle((x - tw / 2, -10, x + tw / 2, h + 10), fill=c)
        img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(6 - 2 * layer)))
    rays = Image.new("L", (w, h), 0); rd = ImageDraw.Draw(rays); ox = w * (0.2 + 0.6 * rng.random())
    for _ in range(7):
        a = rng.random() * 0.6 + 0.2; x1 = ox + (rng.random() - 0.5) * w * 1.4
        rd.polygon([(ox - 10, -20), (ox + 10, -20), (x1 + 70, h), (x1 - 70, h)], fill=int(120 * a))
    img.paste((255, 245, 215), mask=rays.filter(ImageFilter.GaussianBlur(25)))
    arr = np.array(img.convert("RGB"), np.float32); _vignette(arr, 0.35); _grain(arr, rng, 3)
    return _img(arr), dict(soggetto="tronchi e raggi di luce", ambientazione="bosco", palette=["verde", "autunno", "bosco blu"][v % 3],
                           luce="raggi dall'alto nella nebbia", prospettiva="frontale immersiva", composizione="verticali ritmiche", tono="dark")

def stelle(w, h, rng, v):
    col = _grad(h, w, [(0, (4, 6, 18)), (0.7, (14, 20, 48)), (1, (30, 36, 70))])
    y = np.linspace(0, 1, h)[:, None]; x = np.linspace(0, 1, w)[None, :]
    ang = [0.6, -0.6, 0.25][v % 3]; band = np.exp(-(((y - 0.35) - ang * (x - 0.5)) / 0.12) ** 2)
    col += band[..., None] * np.array([90, 80, 120]) * 0.6
    n = int(w * h / 1400)
    for a, b, br in zip(rng.random(n), rng.random(n), rng.random(n) ** 3):
        yy, xx = int(a * h * 0.85), int(b * w); r = 1 + int(br * 2.5)
        col[yy:yy + r, xx:xx + r] += 255 * (0.3 + 0.7 * br)
    _ridge(col, 0.86, 0.1, (6, 8, 14), rng, h, w, rough=0.45)
    img = _img(_grain(col, rng, 2)).filter(ImageFilter.GaussianBlur(0.6))
    return img, dict(soggetto="cielo stellato e via lattea", ambientazione="collina di notte", palette="blu notte",
                     luce="stelle", prospettiva="dal basso verso il cielo", composizione="diagonale", tono="dark")

def citta(w, h, rng, v):
    col = _grad(h, w, [(0, [(10, 12, 30), (30, 20, 50), (14, 26, 40)][v % 3]), (0.7, [(40, 36, 70), (120, 60, 80), (40, 70, 90)][v % 3]), (1, (20, 18, 30))])
    img = _img(col); d = ImageDraw.Draw(img); x = -20
    while x < w + 20:
        bw = 50 + rng.random() * 110; bh = h * (0.1 + rng.random() * 0.16)
        d.rectangle((x, h - bh, x + bw, h), fill=(12, 12, 20))
        for wy in np.arange(h - bh + 16, h - 10, 26):
            for wx in np.arange(x + 10, x + bw - 10, 20):
                if rng.random() < 0.35: d.rectangle((wx, wy, wx + 8, wy + 12), fill=(255, 210, 140))
        x += bw + 4
    img = _bokeh(img, rng, 40, [(255, 200, 120), (255, 120, 120), (140, 200, 255)], 15, 55, 0.0, 0.55, 18, (25, 80))
    arr = np.array(img, np.float32); _grain(arr, rng, 3)
    return _img(arr), dict(soggetto="skyline con finestre accese", ambientazione="città di sera", palette=["blu notte", "tramonto urbano", "petrolio"][v % 3],
                           luce="luci della città sfocate", prospettiva="frontale dal basso", composizione="skyline in basso, bokeh in alto", tono="dark")

def pioggia(w, h, rng, v):
    base = [(40, 60, 90), (60, 50, 70), (30, 60, 60)][v % 3]
    col = _grad(h, w, [(0, base), (1, tuple(int(c * 0.4) for c in base))])
    img = _bokeh(_img(col), rng, 60, [(255, 190, 120), (255, 240, 220), (120, 180, 255), (255, 120, 100)], 25, 90, 0, 1, 26, (30, 110))
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for _ in range(260):
        x, y, r = rng.random() * w, rng.random() * h, 2 + rng.random() ** 2 * 10
        d.ellipse((x - r, y - r * 1.2, x + r, y + r * 1.2), fill=(255, 255, 255, 70)); d.ellipse((x - r * 0.4, y - r * 0.8, x, y - r * 0.2), fill=(255, 255, 255, 140))
    img = img.convert("RGBA"); img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(0.8)))
    arr = np.array(img.convert("RGB"), np.float32); _vignette(arr, 0.3)
    return _img(arr), dict(soggetto="gocce di pioggia sul vetro", ambientazione="dietro una finestra, sera", palette=["blu", "malva", "verde acqua"][v % 3],
                           luce="bokeh di luci lontane", prospettiva="primissimo piano", composizione="texture a tutto campo", tono="dark")

def acquerello(w, h, rng, v):
    paper = np.array([248, 243, 234], np.float32)
    col = np.broadcast_to(paper, (h, w, 3)).astype(np.float32).copy()
    tints = [[(230, 170, 150), (240, 200, 140), (180, 200, 220)], [(170, 200, 190), (200, 220, 170), (240, 210, 170)],
             [(200, 180, 220), (240, 190, 200), (190, 210, 235)]][v % 3]
    img = _img(col).convert("RGBA")
    for i in range(5):
        lay = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        cx, cy, r = rng.random() * w, (0.1 + rng.random() * 0.8) * h, w * (0.25 + rng.random() * 0.35)
        pts = [(cx + r * (0.7 + 0.5 * rng.random()) * np.cos(t), cy + r * (0.7 + 0.5 * rng.random()) * np.sin(t)) for t in np.linspace(0, 6.28, 24)]
        d.polygon(pts, fill=tints[i % 3] + (150,)); img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(40)))
    arr = np.array(img.convert("RGB"), np.float32); arr += rng.normal(0, 5, (h, w, 1))
    return _img(arr), dict(soggetto="macchie di acquerello", ambientazione="carta artistica", palette=["pesca e cielo", "salvia", "lavanda"][v % 3],
                           luce="chiara diffusa", prospettiva="piatta", composizione="macchie libere", tono="light")

def carta(w, h, rng, v):
    base = [(246, 240, 228), (236, 230, 218), (250, 246, 240)][v % 3]
    col = np.broadcast_to(np.array(base, np.float32), (h, w, 3)).copy()
    col += rng.normal(0, 6, (h, w, 1)); fib = _noise1d(h, rng, 8, 0.7)[:, None, None] * 10; col += fib - 5
    img = _img(col); d = ImageDraw.Draw(img)
    if v % 3 == 0: d.line((w * 0.1, h * 0.08, w * 0.9, h * 0.08), fill=(180, 150, 100), width=2)
    if v % 3 == 1: d.rectangle((w * 0.06, h * 0.04, w * 0.94, h * 0.96), outline=(170, 140, 90), width=3)
    return img.filter(ImageFilter.GaussianBlur(0.5)), dict(soggetto="carta pregiata", ambientazione="tipografico editoriale", palette="crema",
                                                           luce="neutra", prospettiva="piatta", composizione="solo tipografia", tono="light")

def colore(w, h, rng, v):
    base, shape = [((178, 64, 52), (232, 120, 90)), ((26, 72, 90), (60, 130, 140)), ((222, 168, 60), (245, 205, 110)),
                   ((60, 40, 90), (110, 80, 150)), ((40, 90, 60), (90, 150, 100))][v % 5]
    col = np.broadcast_to(np.array(base, np.float32), (h, w, 3)).copy(); img = _img(_grain(col, rng, 4))
    d = ImageDraw.Draw(img); kind = rng.integers(3)
    if kind == 0: d.ellipse((w * 0.15, h * 0.2, w * 0.85, h * 0.2 + w * 0.7), fill=shape)
    elif kind == 1: d.rounded_rectangle((w * 0.2, h * 0.18, w * 0.8, h * 0.82), radius=int(w * 0.3), fill=shape)
    else: d.rectangle((0, h * 0.62, w, h), fill=shape)
    return img, dict(soggetto="forma geometrica", ambientazione="grafica moderna a colore pieno",
                     palette=["terracotta", "petrolio", "senape", "prugna", "verde bosco"][v % 5],
                     luce="piatta", prospettiva="piatta", composizione=["cerchio", "arco", "fascia"][kind], tono="dark" if v % 5 != 2 else "light")

def lago(w, h, rng, v):
    sky = [[(255, 200, 160), (180, 140, 170)], [(190, 220, 240), (130, 170, 200)], [(255, 230, 190), (200, 170, 130)]][v % 3]
    col = _grad(h, w, [(0, sky[1]), (0.5, sky[0]), (1, sky[0])])
    top = col[: h // 2].copy(); ys = _ridge(top, 0.92, 0.35, tuple(int(c * 0.35) for c in sky[1]), rng, h // 2, w, rough=0.6)
    col[: h // 2] = top
    refl = top[::-1] * 0.82 + np.array([10, 20, 30]) * 0.2
    col[h // 2: h // 2 + refl.shape[0]] = refl[: h - h // 2]
    img = _img(col); low = img.crop((0, h // 2, w, h)).filter(ImageFilter.GaussianBlur(3)); img.paste(low, (0, h // 2))
    arr = np.array(img, np.float32)
    for y in range(h // 2, h, 7): arr[y] = arr[y] * 0.94 + 12
    _grain(arr, rng, 2.5)
    return _img(arr), dict(soggetto="lago che riflette le colline", ambientazione="lago", palette=["rosa", "azzurro", "dorato"][v % 3],
                           luce="calma diffusa", prospettiva="simmetrica", composizione="specchio orizzontale", tono="dark")

def grano(w, h, rng, v):
    col = _grad(h, w, [(0, [(250, 200, 140), (170, 200, 230), (255, 170, 120)][v % 3]), (0.55, (255, 230, 180)), (0.56, (200, 150, 70)), (1, (90, 60, 20))])
    _glow(col, 0.5 + 0.3 * (rng.random() - 0.5), 0.5, 0.18, (255, 240, 200), 0.7)
    img = _img(col); lay = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for _ in range(900):
        x = rng.random() * w; y0 = h * (0.55 + rng.random() * 0.45); ln = 40 + rng.random() * 140; bend = (rng.random() - 0.5) * 40
        c = (int(150 + rng.random() * 90), int(100 + rng.random() * 70), 30, 200)
        d.line((x, y0, x + bend, y0 - ln), fill=c, width=2); d.ellipse((x + bend - 4, y0 - ln - 14, x + bend + 4, y0 - ln + 4), fill=c)
    img = img.convert("RGBA"); img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(1.2)))
    arr = np.array(img.convert("RGB"), np.float32); _vignette(arr, 0.35); _grain(arr, rng, 3)
    return _img(arr), dict(soggetto="spighe di grano", ambientazione="campo al tramonto", palette=["oro caldo", "cielo azzurro e grano", "arancio"][v % 3],
                           luce="sole basso controluce", prospettiva="ad altezza d'erba", composizione="grano in basso, cielo sopra", tono="dark")

def croce(w, h, rng, v):
    base = [(20, 16, 14), (14, 18, 26), (26, 20, 30)][v % 3]
    col = _grad(h, w, [(0, base), (1, tuple(int(c * 0.5) for c in base))])
    _glow(col, 0.5, 0.42, 0.5, (255, 220, 170), 0.25)
    img = _img(_grain(col, rng)); lay = Image.new("L", (w, h), 0); d = ImageDraw.Draw(lay)
    cx = w * [0.5, 0.72, 0.28][v % 3]; t = w * 0.035
    d.rectangle((cx - t / 2, h * 0.12, cx + t / 2, h * 0.62), fill=255); d.rectangle((cx - w * 0.14, h * 0.24, cx + w * 0.14, h * 0.24 + t), fill=255)
    img.paste((255, 236, 200), mask=lay.filter(ImageFilter.GaussianBlur(18)))
    img.paste((255, 250, 235), mask=lay.filter(ImageFilter.GaussianBlur(3)).point(lambda p: int(p * 0.5)))
    return img, dict(soggetto="croce di luce", ambientazione="spazio simbolico scuro", palette=["ambra", "blu", "prugna"][v % 3],
                     luce="luce che nasce dalla croce", prospettiva="frontale", composizione=["centrale", "destra", "sinistra"][v % 3], tono="dark")

def sentiero(w, h, rng, v):
    col = _grad(h, w, [(0, [(200, 220, 240), (250, 210, 170), (220, 210, 230)][v % 3]), (0.45, (255, 245, 225)), (0.46, (110, 130, 90)), (1, (40, 50, 30))])
    _glow(col, 0.5, 0.45, 0.12, (255, 250, 230), 0.8)
    img = _img(col); d = ImageDraw.Draw(img)
    d.polygon([(w * 0.49, h * 0.46), (w * 0.51, h * 0.46), (w * 0.85, h), (w * 0.15, h)], fill=(200, 180, 140))
    arr = np.array(img, np.float32)
    for side in (0, 1):
        sub = np.zeros_like(arr); _ridge(sub, 0.5, 0.06, (1, 1, 1), rng, h, w)
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    for _ in range(60):
        side = rng.integers(2); x = (rng.random() * 0.35 if side == 0 else 0.65 + rng.random() * 0.35) * w
        y = h * (0.42 + rng.random() * 0.1); r = 30 + rng.random() * 90
        ld.ellipse((x - r, y - r, x + r, y + r * 1.5), fill=(50, 70, 40, 200))
    img = _img(arr).convert("RGBA"); img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(5)))
    arr = np.array(img.convert("RGB"), np.float32); _vignette(arr, 0.3); _grain(arr, rng, 3)
    return _img(arr), dict(soggetto="sentiero verso la luce", ambientazione="campagna", palette=["mattino", "tramonto", "lilla"][v % 3],
                           luce="luce in fondo al cammino", prospettiva="punto di fuga centrale", composizione="linee convergenti", tono="dark")

def nero(w, h, rng, v):
    """Fondo nero editoriale (slide 2 dei caroselli in 3 slide, STRATEGIA sez. 11): una sola frase serif bianca."""
    base = [(10, 10, 10), (14, 12, 10), (8, 10, 14)][v % 3]
    col = np.broadcast_to(np.array(base, np.float32), (h, w, 3)).copy()
    _glow(col, 0.5, 0.47, 0.55, (40, 36, 32), 0.35); _vignette(col, 0.5); _grain(col, rng, 2.5)
    return _img(col), dict(soggetto="fondo nero", ambientazione="tipografico", palette=["nero", "nero caldo", "nero blu"][v % 3],
                           luce="buio con lieve alone", prospettiva="piatta", composizione="solo tipografia", tono="dark")

def cielo(w, h, rng, v, palette="alba"):
    import brand
    pal = palette if palette in brand.PALETTES else ["alba", "notte", "oro", "mare", "viola"][v % 5]
    return brand.background(w, h, int(rng.integers(1000)), 0.8, pal), dict(soggetto="cielo con glow centrale", ambientazione="cielo", palette=pal,
                     luce="glow centrale con raggi", prospettiva="frontale", composizione="luce in basso al centro", tono="dark")

CONCEPTS = dict(candela=candela, finestra=finestra, montagne=montagne, mare=mare, bosco=bosco, stelle=stelle, citta=citta,
                pioggia=pioggia, acquerello=acquerello, carta=carta, colore=colore, lago=lago, grano=grano, croce=croce,
                sentiero=sentiero, nero=nero, cielo=cielo)

def photo(path, w, h, darken=0.45):
    """Foto vera dalla cartella backgrounds/: ritaglio a riempimento + velatura per la leggibilità."""
    p = path if os.path.isabs(path) else os.path.join(ROOT, path)
    im = ImageOps.fit(Image.open(p).convert("RGB"), (w, h), Image.LANCZOS)
    arr = np.array(im, np.float32) * (1 - darken); return _img(arr)

def render(spec, w, h, seed=1):
    """spec: {"concept": nome, "variant": n} oppure {"photo": "backgrounds/x.jpg", "meta": {...}}"""
    rng = np.random.default_rng(seed)
    if "clip" in spec:
        import json as _j
        cat = {c["file"]: c for c in _j.load(open(os.path.join(ROOT, "clips", "catalogo.json")))}
        c = cat[spec["clip"]]; m = {k: c[k] for k in ("soggetto", "ambientazione", "palette", "luce", "tono")}
        m.update(concept="clip:" + os.path.basename(c["file"])[:-4], prospettiva="video reale", composizione="video reale")
        if spec.get("frame_t") is not None:
            import subprocess, tempfile
            tmp = tempfile.mktemp(suffix=".jpg")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(spec["frame_t"]), "-i", os.path.join(ROOT, c["file"]), "-frames:v", "1", "-q:v", "2", tmp], stdin=subprocess.DEVNULL)
            src = tmp
        else: src = os.path.join(ROOT, c["poster"])
        m["tono"] = "dark"  # sulle foto reali il testo è sempre chiaro con velatura
        return photo(src, w, h, spec.get("darken", 0.35)), m
    if "photo" in spec:
        m = dict(spec.get("meta", {})); m.setdefault("tono", "dark"); m["concept"] = "foto:" + os.path.basename(spec["photo"])
        return photo(spec["photo"], w, h, spec.get("darken", 0.45)), m
    name = spec.get("concept", "cielo"); v = int(spec.get("variant", 0))
    img, m = CONCEPTS[name](w, h, rng, v) if name != "cielo" else cielo(w, h, rng, v, spec.get("palette", ""))
    m["concept"] = name; m["variant"] = v
    return img.resize((w, h)) if img.size != (w, h) else img, m
