"""Motore grafico VoceInteriore2025: sfondi, testi, card post/storie/video."""
import math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

import os
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts") + "/"
SERIF_I = F+"cormorant-garamond-latin-500-italic.woff"
SERIF   = F+"cormorant-garamond-latin-600-normal.woff"
SANS    = F+"montserrat-latin-500-normal.woff"
SANS_B  = F+"montserrat-latin-600-normal.woff"
SANS_X  = F+"montserrat-latin-800-normal.woff"   # registro "forte": maiuscolo d'impatto
GOLD = (238, 202, 132)
CREAM = (250, 243, 230)

def font(p, s): return ImageFont.truetype(p, s)

PALETTES = {
    "alba":  dict(top=(12,20,44),  mid=(58,40,78),  low=(196,122,70), glow=(255,205,140), stars=0),
    "notte": dict(top=(4,8,22),    mid=(16,30,70),  low=(40,80,120),  glow=(190,215,255), stars=1),
    "oro":   dict(top=(22,12,10),  mid=(78,30,34),  low=(206,150,70), glow=(255,215,150), stars=0),
    "mare":  dict(top=(4,22,34),   mid=(10,60,84),  low=(60,150,160), glow=(200,240,235), stars=0),
    "viola": dict(top=(18,8,36),   mid=(70,30,96),  low=(214,120,140),glow=(255,200,200), stars=1),
}
def background(w, h, seed=1, glow_y=0.78, palette="alba"):
    """Alba: blu notte in alto, glow dorato in basso, raggi tenui e grana."""
    rng = np.random.default_rng(seed)
    y = np.linspace(0, 1, h)[:, None]; x = np.linspace(0, 1, w)[None, :]
    P = PALETTES[palette]; top = np.array(P["top"]); mid = np.array(P["mid"]); low = np.array(P["low"])
    t = y
    col = np.where(t[..., None] < 0.55,
                   top + (mid - top) * (t[..., None] / 0.55),
                   mid + (low - mid) * ((t[..., None] - 0.55) / 0.45))
    col = np.broadcast_to(col, (h, w, 3)).astype(np.float32).copy()
    # glow centrale
    d = np.sqrt(((x - 0.5) * w / h) ** 2 + (y - glow_y) ** 2)
    glow = np.exp(-(d / 0.32) ** 2)[..., None]
    col += glow * np.array(P["glow"]) * 0.55
    # raggi di luce
    ang = np.arctan2(y - glow_y, (x - 0.5) * w / h)
    rays = (0.5 + 0.5 * np.sin(ang * 14 + seed)) ** 6 * np.exp(-d / 0.9)
    col += rays[..., None] * np.array([255, 225, 170]) * 0.06
    # vignettatura
    v = 1 - 0.45 * (((x - 0.5) * 1.6) ** 2 + ((y - 0.5) * 1.2) ** 2)
    col *= np.clip(v, 0.45, 1)[..., None]
    if P["stars"]:
        n = int(w * h / 9000); sy = rng.random(n) ** 1.8 * 0.6; sx = rng.random(n)
        for a, b, br in zip(sy, sx, rng.random(n)):
            yy, xx = int(a * h), int(b * w); r = 1 + int(br * 2)
            col[max(0,yy-r):yy+r, max(0,xx-r):xx+r] += 120 * br
    col += rng.normal(0, 4.0, (h, w, 1))
    return Image.fromarray(np.clip(col, 0, 255).astype(np.uint8))

def wrap(draw, text, fnt, maxw):
    out = []
    for para in text.split("\n"):
        line = ""
        for wd in para.split():
            test = (line + " " + wd).strip()
            if draw.textlength(test, font=fnt) <= maxw: line = test
            else: out.append(line); line = wd
        out.append(line)
    return out

def text_block(img, text, fpath, size, cx, cy, maxw, fill=CREAM, lh=1.22, shadow=True):
    """Testo centrato su (cx, cy); riduce la dimensione finché ci sta."""
    d = ImageDraw.Draw(img)
    while True:
        f = font(fpath, size); lines = wrap(d, text, f, maxw)
        H = int(len(lines) * size * lh)
        if H < img.height * 0.5 or size < 30: break
        size -= 4
    y0 = cy - H // 2
    if shadow:
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
        for i, ln in enumerate(lines):
            wl = sd.textlength(ln, font=f)
            sd.text((cx - wl / 2, y0 + i * size * lh + 3), ln, font=f, fill=(0, 0, 0, 150))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    d = ImageDraw.Draw(img)
    for i, ln in enumerate(lines):
        wl = d.textlength(ln, font=f)
        d.text((cx - wl / 2, y0 + i * size * lh), ln, font=f, fill=fill)
    return y0, y0 + H

def spaced(img, text, fpath, size, cx, y, fill=GOLD, track=6):
    d = ImageDraw.Draw(img); f = font(fpath, size)
    widths = [d.textlength(c, font=f) for c in text]
    total = sum(widths) + track * (len(text) - 1); x = cx - total / 2
    for c, wd in zip(text, widths):
        d.text((x, y), c, font=f, fill=fill); x += wd + track

def ornament(img, cx, y, half=70, fill=GOLD):
    d = ImageDraw.Draw(img)
    d.line([(cx - half, y), (cx - 12, y)], fill=fill, width=2)
    d.line([(cx + 12, y), (cx + half, y)], fill=fill, width=2)
    d.regular_polygon((cx, y, 6), 4, rotation=45, fill=fill)

def frame(img, m=40, fill=(226, 190, 120, 110)):
    d = ImageDraw.Draw(img); w, h = img.size
    d.rectangle([m, m, w - m, h - m], outline=fill, width=2)

def brand_footer(img, y=None):
    w, h = img.size; y = y or h - 110
    ink = (34, 28, 62)
    ornament(img, w // 2, y - 22, half=40, fill=ink)
    spaced(img, "VOCEINTERIORE2025", SANS_B, 26, w // 2, y, fill=ink, track=7)

def verse_card(w, h, kicker, verse, ref, seed=1, glow_y=0.95, palette="alba"):
    img = background(w, h, seed, glow_y, palette).convert("RGBA"); frame(img)
    top = int(h * 0.17)
    spaced(img, kicker.upper(), SANS, 28, w // 2, top, fill=GOLD, track=8)
    ornament(img, w // 2, top + 62)
    y0, y1 = text_block(img, verse, SERIF_I, 74 if h > w * 1.5 else 66, w // 2, int(h * 0.47), int(w * 0.78))
    spaced(img, ref.upper(), SANS, 30, w // 2, y1 + 40, fill=GOLD, track=6)
    brand_footer(img)
    return img
