"""Genera tutti i contenuti di una giornata da un file JSON (vedi ISTRUZIONI.md).
Uso: python3 make_day.py day.json OUT_DIR MUSIC_DIR
Produce: post.jpg o slide_1..n.jpg (carosello), story_1..n.jpg, reel.mp4, preview.jpg, report.txt
Ogni elemento può avere: "bg" (concept o foto, vedi tools/scenes.py), "layout" (centro|alto|basso|sinistra|grande),
"font" (serif_i|serif|sans), "frame" (true/false). Il registro tools/bg_log.json blocca le ripetizioni
(per forzare: "allow_repeat": true nello SPEC, solo con motivo scritto in "repeat_reason")."""
import sys, os, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from brand import *
import scenes, bg_log
import reel as R
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

INK = (34, 28, 62); INK_GOLD = (150, 104, 40)
FONTS = {"serif_i": SERIF_I, "serif": SERIF, "sans": SANS_B}

def scrim(img, y0, y1, k=0.45):
    """Velatura morbida dietro al testo per la leggibilità su sfondi ricchi."""
    w, h = img.size; m = np.zeros((h, 1), np.float32); yy = np.arange(h)[:, None]
    m = np.clip(1 - np.abs(yy - (y0 + y1) / 2) / ((y1 - y0) / 2 + 220), 0, 1) ** 1.5 * k
    a = Image.fromarray((np.broadcast_to(m, (h, w)) * 255).astype(np.uint8))
    img.paste((0, 0, 0), mask=a)

def block(img, text, fpath, size, x, cy, maxw, fill, align="center", shadow=True, lh=1.22):
    d = ImageDraw.Draw(img)
    while True:
        f = font(fpath, size); lines = wrap(d, text, f, maxw); Hh = int(len(lines) * size * lh)
        if Hh < img.height * 0.5 or size < 30: break
        size -= 4
    y0 = cy - Hh // 2
    def xpos(ln): return x if align == "left" else x - d.textlength(ln, font=f) / 2
    if shadow:
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
        for i, ln in enumerate(lines): sd.text((xpos(ln), y0 + i * size * lh + 3), ln, font=f, fill=(0, 0, 0, 150))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    d = ImageDraw.Draw(img)
    for i, ln in enumerate(lines): d.text((xpos(ln), y0 + i * size * lh), ln, font=f, fill=fill)
    return y0, y0 + Hh

def kicker_at(img, text, x, y, fill, align, size):
    if align == "left":
        d = ImageDraw.Draw(img); f = font(SANS, size); xx = x
        for c in text.upper(): d.text((xx, y), c, font=f, fill=fill); xx += d.textlength(c, font=f) + 7
        d.line((x, y + size + 22, x + 90, y + size + 22), fill=fill, width=3)
    else:
        spaced(img, text.upper(), SANS, size, x, y, fill=fill, track=8); ornament(img, x, y + 62, fill=fill)

def card(w, h, it, defaults, seed):
    bgspec = it.get("bg", defaults.get("bg", {"concept": "cielo", "palette": it.get("palette", defaults.get("palette", "alba"))}))
    if "palette" in it and bgspec.get("concept") == "cielo": bgspec = dict(bgspec, palette=it["palette"])
    bg, meta = scenes.render(bgspec, w, h, seed)
    img = bg.convert("RGBA"); tall = h > 1600
    layout = it.get("layout", defaults.get("layout", "centro")); fname = it.get("font", defaults.get("font", "serif_i"))
    light = meta.get("tono") == "light"
    fill = INK if light else CREAM; kfill = INK_GOLD if light else GOLD
    if it.get("frame", defaults.get("frame", False)): frame(img, 40 if not tall else 50, fill=(kfill + (110,)))
    cy = {"centro": 0.47, "alto": 0.33, "basso": 0.66, "sinistra": 0.5, "grande": 0.48}[layout] * h
    align = "left" if layout == "sinistra" else "center"; x = int(w * 0.11) if align == "left" else w // 2
    size = it.get("size") or {"grande": 112 if tall else 96}.get(layout, 86 if tall else 72)
    if fname == "sans": size = int(size * 0.72)
    maxw = int(w * (0.74 if align == "left" else 0.8))
    # misura per la velatura
    tmp = Image.new("RGBA", (w, h)); y0, y1 = block(tmp, it["text"], FONTS[fname], size, x, int(cy), maxw, fill, align, False)
    if not light and bgspec.get("concept") != "cielo": scrim(img, y0 - 120, y1 + 80, it.get("scrim", 0.42))
    y0, y1 = block(img, it["text"], FONTS[fname], size, x, int(cy), maxw, fill, align, shadow=not light)
    if it.get("number"): spaced(img, it["number"], SANS_B, 30, w // 2 if align == "center" else x + 40, int(y0 - 230), fill=kfill, track=6)
    if it.get("kicker"): kicker_at(img, it["kicker"], x, int(y0 - 140), kfill, align, 30 if tall else 28)
    if it.get("sub"):
        if align == "left": ImageDraw.Draw(img).text((x, y1 + 40), it["sub"].upper(), font=font(SANS, 30), fill=kfill)
        else: spaced(img, it["sub"].upper(), SANS, 30, w // 2, y1 + 40, fill=kfill, track=6)
    if it.get("note"):
        ny = int(h * (0.80 if layout != "basso" else 0.86)) if tall else int(h * 0.82)
        if layout == "basso" and not tall: ny = int(h * 0.87)
        spaced(img, it["note"].upper(), SANS, 24, w // 2, ny, fill=fill, track=4)
    # firma: scura su sfondi chiari, chiara su scuri
    fy = h - (110 if not tall else 230)
    if not light and bgspec.get("concept") != "cielo": scrim(img, fy - 30, fy + 40, 0.3)
    ornament(img, w // 2, fy - 22, half=40, fill=fill); spaced(img, "VOCEINTERIORE2025", SANS_B, 26, w // 2, fy, fill=fill, track=7)
    meta.update(layout=layout, font=fname)
    return img.convert("RGB"), meta

def main(spec_path, out, music_dir):
    S = json.load(open(spec_path)); os.makedirs(out, exist_ok=True)
    seed = S.get("seed", 1); made = []; warn = []; log_new = []; date = S.get("date", str(datetime.date.today()))
    D = {k: S[k] for k in ("bg", "layout", "font", "frame", "palette") if k in S}
    def rec(item, meta, group=None):
        e = dict(meta, date=date, item=item); e.pop("beats", None)
        if group: e["group"] = group
        log_new.append(e)
    if "carousel" in S:
        n = len(S["carousel"]); cd = dict(D, **S.get("carousel_style", {}))
        for i, sl in enumerate(S["carousel"], 1):
            it = dict(sl); it.setdefault("number", f"{i} / {n}" if sl.get("numbered", True) else None)
            img, meta = card(1080, 1350, it, cd, seed); img.save(f"{out}/slide_{i}.jpg", quality=93); made.append(f"slide_{i}.jpg")
            if i == 1 or "bg" in sl: rec(f"slide_{i}", meta, "carousel" if i > 1 else None)
    elif "post" in S:
        img, meta = card(1080, 1350, S["post"], D, seed); img.save(f"{out}/post.jpg", quality=93); made.append("post.jpg"); rec("post", meta)
    for i, st in enumerate(S.get("stories", []), 1):
        img, meta = card(1080, 1920, st, D, seed + i * 7); img.save(f"{out}/story_{i}.jpg", quality=93); made.append(f"story_{i}.jpg"); rec(f"story_{i}", meta)
    for t in [x.get("text", "") for x in S.get("carousel", [])] + [S.get("post", {}).get("text", "")]:
        if len(t) > 260: warn.append(f"Testo lungo ({len(t)} caratteri): verificare leggibilità")
    if "reel" in S:
        lib = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "music_library.json")))
        rs = dict(S["reel"]); rs.setdefault("palette", S.get("palette", "alba")); rs.setdefault("seed", seed)
        cuts, rmeta = R.render(rs, f"{out}/reel.mp4", music_dir, lib); made.append("reel.mp4"); rec("reel", rmeta)
        import subprocess
        for k, t in enumerate([0.0] + [(cuts[i] + cuts[i+1]) / 2 + 0.6 for i in range(len(cuts) - 1)]):
            subprocess.run(f"ffmpeg -v error -y -ss {t} -i {out}/reel.mp4 -frames:v 1 {out}/_frame_{k}.jpg", shell=True)
    probs = bg_log.check([e for e in log_new if "group" not in e])
    if probs and not S.get("allow_repeat"):
        print("RIPETIZIONE VISIVA – cambiare concept/variante/layout e rigenerare:\n- " + "\n- ".join(probs)); sys.exit(2)
    if probs: warn.append("Ripetizione consentita: " + S.get("repeat_reason", "(nessun motivo)"))
    thumbs = [Image.open(f"{out}/{m}") for m in made if m.endswith(".jpg")] + \
             [Image.open(f"{out}/{f}") for f in sorted(os.listdir(out)) if f.startswith("_frame_")]
    hh = 640; row = [t.resize((int(t.width * hh / t.height), hh)) for t in thumbs]
    sheet = Image.new("RGB", (sum(r.width for r in row) + 10 * len(row), hh), "white"); x = 0
    for r in row: sheet.paste(r, (x, 0)); x += r.width + 10
    sheet.save(f"{out}/preview.jpg", quality=85)
    json.dump(log_new, open(f"{out}/bg_entries.json", "w"), indent=1, ensure_ascii=False)
    open(f"{out}/report.txt", "w").write("Creati: " + ", ".join(made) + "\n" + "\n".join(warn))
    print("Creati:", made, "Avvisi:", warn)
    print(f"Dopo il controllo qualità registrare gli sfondi: python3 tools/bg_log.py --registra {out}/bg_entries.json")

if __name__ == "__main__":
    main(*sys.argv[1:4])
