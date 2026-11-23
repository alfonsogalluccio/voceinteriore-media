"""Scarica nuovi video da Pexels (licenza Pexels, uso libero) e li aggiunge alla libreria clips/.
Gira dentro GitHub Actions (.github/workflows/scarica-clip.yml) con il segreto PEXELS_API_KEY.

Richieste: clips/richieste.json
  {"richieste": [{"cerca": "man hoodie from behind", "quanti": 3, "prefisso": "uomo"}]}
Per ogni richiesta cerca video verticali, salta quelli già in libreria (CODICI_PEXELS.md e catalogo.json),
taglia 15 s in 1080x1920 senza audio, crea il poster, aggiunge la voce a catalogo.json con "da_verificare": true
e la riga a CODICI_PEXELS.md. Alla fine svuota le richieste.
Le clip "da_verificare" vanno guardate (poster e fotogrammi) e completate in italiano prima di usarle."""
import json, os, re, subprocess, sys, urllib.parse, urllib.request, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIPS = os.path.join(ROOT, "clips"); CAT = os.path.join(CLIPS, "catalogo.json")
REQ = os.path.join(CLIPS, "richieste.json"); CODES = os.path.join(CLIPS, "CODICI_PEXELS.md")
KEY = os.environ.get("PEXELS_API_KEY", "")
MAX_PER_RUN = 10

def api(url):
    r = urllib.request.Request(url, headers={"Authorization": KEY, "User-Agent": "voceinteriore-clip/1.0"})
    with urllib.request.urlopen(r, timeout=60) as f: return json.load(f)

def known_ids():
    ids = set()
    if os.path.exists(CODES):
        ids |= set(re.findall(r"\b(\d{5,9})\b", open(CODES).read()))   # tabella e scartati
    for c in json.load(open(CAT)):
        m = re.match(r"(\d+)", c.get("originale", "")); ids |= {m.group(1)} if m else set()
        if c.get("pexels_id"): ids.add(str(c["pexels_id"]))
    return ids

def best_file(v):
    fs = [f for f in v.get("video_files", []) if f.get("width") and f.get("height") and f["height"] > f["width"]]
    ok = [f for f in fs if f["height"] >= 1920]
    if not ok: return None
    return min(ok, key=lambda f: f["height"])          # il più leggero che arriva a 1920

def slug(url):
    m = re.search(r"/video/([a-z0-9-]+?)-?\d+/?$", url or "")
    return (m.group(1) if m else "").replace("-", " ")

def main():
    if not KEY: sys.exit("Manca il segreto PEXELS_API_KEY")
    req = json.load(open(REQ)).get("richieste", []) if os.path.exists(REQ) else []
    if not req: print("Nessuna richiesta"); return
    cat = json.load(open(CAT)); ids = known_ids(); added = []
    for r in req:
        need = int(r.get("quanti", 3)); pref = re.sub(r"[^a-z0-9-]", "", r.get("prefisso", "clip").lower()) or "clip"
        q = urllib.parse.quote(r["cerca"])
        data = api(f"https://api.pexels.com/videos/search?query={q}&orientation=portrait&per_page=40")
        for v in data.get("videos", []):
            if need <= 0 or len(added) >= MAX_PER_RUN: break
            vid = str(v["id"])
            if vid in ids or v.get("duration", 0) < 8: continue
            f = best_file(v)
            if not f: continue
            name = f"{pref}-{vid}"; raw = f"/tmp/{vid}.mp4"
            out = os.path.join(CLIPS, name + ".mp4"); poster = os.path.join(CLIPS, name + ".jpg")
            urllib.request.urlretrieve(f["link"], raw)
            start = 1 if v["duration"] >= 17 else 0; dur = min(15, v["duration"] - start)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-t", str(dur), "-i", raw, "-an",
                            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
                            "-c:v", "libx264", "-crf", "21", "-preset", "veryfast", "-pix_fmt", "yuv420p",
                            "-movflags", "+faststart", out], check=True)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "1", "-i", out, "-frames:v", "1", "-q:v", "3", poster], check=True)
            os.remove(raw)
            autore = (v.get("user") or {}).get("name", "")
            cat.append(dict(file=f"clips/{name}.mp4", poster=f"clips/{name}.jpg", dur=round(dur, 1),
                            soggetto=f"(da verificare) {slug(v.get('url'))}", ambientazione="da verificare",
                            palette="da verificare", luce="da verificare", tono="dark",
                            fonte=f"Pexels (licenza Pexels, uso libero) – autore: {autore} – scaricato automaticamente il {datetime.date.today():%d/%m/%Y} (ricerca: {r['cerca']})",
                            originale=os.path.basename(urllib.parse.urlparse(f['link']).path), pexels_id=v["id"],
                            pexels_url=v.get("url", ""), da_verificare=True))
            ids.add(vid); need -= 1; added.append((vid, name, slug(v.get("url"))))
            print("Aggiunta", name)
    json.dump(cat, open(CAT, "w"), indent=1, ensure_ascii=False)
    if added:
        lines = open(CODES).read().split("\n")
        last = max(i for i, l in enumerate(lines) if l.startswith("| ") and not l.startswith("| Codice"))
        lines[last + 1:last + 1] = [f"| {vid} | {name} | (da verificare) {s} |" for vid, name, s in added]
        open(CODES, "w").write("\n".join(lines))
    json.dump({"richieste": []}, open(REQ, "w"), indent=1)
    print(f"Totale aggiunte: {len(added)}")

if __name__ == "__main__":
    main()
