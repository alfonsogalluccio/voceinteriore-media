"""Genera tutti i contenuti di una giornata da un file JSON (vedi ISTRUZIONI.md).
Uso: python3 make_day.py day.json OUT_DIR MUSIC_DIR
Produce: post.jpg o slide_1..n.jpg (carosello), story_1..n.jpg, reel.mp4, preview.jpg, report.txt"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from brand import *
import reel as R
from PIL import Image

def card(w, h, kicker, text, sub=None, palette="alba", seed=1, size=None, footer_note=None, number=None):
    img = background(w, h, seed, 0.95, palette).convert("RGBA"); frame(img, 40 if h < 1600 else 50)
    top = int(h * (0.17 if h < 1600 else 0.19))
    if number: spaced(img, number, SANS_B, 30, w // 2, top - 70, fill=GOLD, track=6)
    if kicker:
        spaced(img, kicker.upper(), SANS, 28 if h < 1600 else 30, w // 2, top, fill=GOLD, track=8); ornament(img, w // 2, top + 62)
    y0, y1 = text_block(img, text, SERIF_I, size or (72 if h < 1600 else 86), w // 2, int(h * (0.48 if h < 1600 else 0.46)), int(w * 0.8))
    if sub: spaced(img, sub.upper(), SANS, 30, w // 2, y1 + 40, fill=GOLD, track=6)
    if footer_note: spaced(img, footer_note.upper(), SANS, 24, w // 2, int(h * 0.78), fill=CREAM, track=4)
    brand_footer(img, h - (110 if h < 1600 else 260))
    return img.convert("RGB")

def check_text_fits(img_text, maxlen):
    return len(img_text) <= maxlen

def main(spec_path, out, music_dir):
    S = json.load(open(spec_path)); os.makedirs(out, exist_ok=True)
    pal, seed = S.get("palette", "alba"), S.get("seed", 1); made = []; warn = []
    if "carousel" in S:
        n = len(S["carousel"])
        for i, sl in enumerate(S["carousel"], 1):
            card(1080, 1350, sl.get("kicker"), sl["text"], sl.get("sub"), pal, seed, sl.get("size"),
                 sl.get("note"), f"{i} / {n}" if sl.get("numbered", True) else None).save(f"{out}/slide_{i}.jpg", quality=93)
            made.append(f"slide_{i}.jpg")
    elif "post" in S:
        p = S["post"]; card(1080, 1350, p.get("kicker"), p["text"], p.get("sub"), pal, seed, p.get("size")).save(f"{out}/post.jpg", quality=93)
        made.append("post.jpg")
    for i, st in enumerate(S.get("stories", []), 1):
        card(1080, 1920, st.get("kicker"), st["text"], st.get("sub"), st.get("palette", pal), seed + i * 7,
             st.get("size"), st.get("note")).save(f"{out}/story_{i}.jpg", quality=93)
        made.append(f"story_{i}.jpg")
    for t in [x.get("text", "") for x in S.get("carousel", [])] + [S.get("post", {}).get("text", "")]:
        if len(t) > 260: warn.append(f"Testo lungo ({len(t)} caratteri): verificare leggibilità")
    if "reel" in S:
        lib = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "music_library.json")))
        rs = dict(S["reel"]); rs.setdefault("palette", pal); rs.setdefault("seed", seed)
        cuts = R.render(rs, f"{out}/reel.mp4", music_dir, lib); made.append("reel.mp4")
        # fotogrammi di controllo
        import subprocess
        for k, t in enumerate([0.0] + [ (cuts[i] + cuts[i+1]) / 2 + 0.6 for i in range(len(cuts) - 1)]):
            subprocess.run(f"ffmpeg -v error -y -ss {t} -i {out}/reel.mp4 -frames:v 1 {out}/_frame_{k}.jpg", shell=True)
    # foglio di anteprima per il controllo visivo
    thumbs = [Image.open(f"{out}/{m}") for m in made if m.endswith(".jpg")] + \
             [Image.open(f"{out}/{f}") for f in sorted(os.listdir(out)) if f.startswith("_frame_")]
    hh = 640; row = [t.resize((int(t.width * hh / t.height), hh)) for t in thumbs]
    sheet = Image.new("RGB", (sum(r.width for r in row) + 10 * len(row), hh), "white"); x = 0
    for r in row: sheet.paste(r, (x, 0)); x += r.width + 10
    sheet.save(f"{out}/preview.jpg", quality=85)
    open(f"{out}/report.txt", "w").write("Creati: " + ", ".join(made) + "\n" + "\n".join(warn))
    print("Creati:", made, "Avvisi:", warn)

if __name__ == "__main__":
    main(*sys.argv[1:4])
