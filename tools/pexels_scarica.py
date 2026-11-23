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
PXB = os.environ.get("PIXABAY_API_KEY", "")   # Pexels ha sospeso le nuove chiavi (23/11/2026): si usa Pixabay
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
    if v.get("orizzontale") is not None:          # Pixabay: file già scelto
        return v["video_files"][0]
    fs = [f for f in v.get("video_files", []) if f.get("width") and f.get("height") and f["height"] > f["width"]]
    ok = [f for f in fs if f["height"] >= 1920]
    if not ok: return None
    return min(ok, key=lambda f: f["height"])          # il più leggero che arriva a 1920

def pixabay_search(query):
    """Cerca su Pixabay e restituisce video nel formato usato sotto (come Pexels)."""
    q = urllib.parse.quote(query)
    with urllib.request.urlopen(f"https://pixabay.com/api/videos/?key={PXB}&q={q}&per_page=50&safesearch=true", timeout=60) as f:
        data = json.load(f)
    out = []
    for h in data.get("hits", []):
        vs = [x for x in (h.get("videos") or {}).values() if x.get("url") and x.get("width")]
        port = [x for x in vs if x["height"] > x["width"] and x["height"] >= 1920]
        land = [x for x in vs if x["width"] >= x["height"] and x["height"] >= 2160]   # 4K orizzontale: si ritaglia il centro
        pick = min(port, key=lambda x: x["height"]) if port else (min(land, key=lambda x: x["height"]) if land else None)
        if not pick: continue
        out.append(dict(id=f"pxb{h['id']}", duration=h.get("duration", 0), url=h.get("pageURL", ""),
                        user=dict(name=h.get("user", "")), tags=h.get("tags", ""), orizzontale=not port,
                        video_files=[dict(width=pick["width"], height=pick["height"], link=pick["url"])]))
    return out

def slug(url):
    m = re.search(r"/video/([a-z0-9-]+?)-?\d+/?$", url or "")
    return (m.group(1) if m else "").replace("-", " ")

def main():
    if not KEY and not PXB: sys.exit("Manca il segreto PIXABAY_API_KEY (o PEXELS_API_KEY)")
    req = json.load(open(REQ)).get("richieste", []) if os.path.exists(REQ) else []
    if not req: print("Nessuna richiesta"); return
    cat = json.load(open(CAT)); ids = known_ids(); added = []
    for r in req:
        need = int(r.get("quanti", 3)); pref = re.sub(r"[^a-z0-9-]", "", r.get("prefisso", "clip").lower()) or "clip"
        fonte_sito = r.get("sito") or ("pixabay" if PXB else "pexels")
        if fonte_sito == "pixabay":
            videos = pixabay_search(r["cerca"])
        else:
            q = urllib.parse.quote(r["cerca"])
            videos = api(f"https://api.pexels.com/videos/search?query={q}&orientation=portrait&per_page=40").get("videos", [])
        for v in videos:
            if need <= 0 or len(added) >= MAX_PER_RUN: break
            vid = str(v["id"])
            if vid in ids or v.get("duration", 0) < 8: continue
            f = best_file(v)
            if not f: continue
            name = f"{pref}-{vid}"; raw = f"/tmp/{vid}.mp4"
            out = os.path.join(CLIPS, name + ".mp4"); poster = os.path.join(CLIPS, name + ".jpg")
            rq = urllib.request.Request(f["link"], headers={"User-Agent": "voceinteriore-clip/1.0"})
            with urllib.request.urlopen(rq, timeout=300) as src, open(raw, "wb") as dst: dst.write(src.read())
            start = 1 if v["duration"] >= 17 else 0; dur = min(15, v["duration"] - start)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-t", str(dur), "-i", raw, "-an",
                            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
                            "-c:v", "libx264", "-crf", "21", "-preset", "veryfast", "-pix_fmt", "yuv420p",
                            "-movflags", "+faststart", out], check=True)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "1", "-i", out, "-frames:v", "1", "-q:v", "3", poster], check=True)
            os.remove(raw)
            autore = (v.get("user") or {}).get("name", "")
            cat.append(dict(file=f"clips/{name}.mp4", poster=f"clips/{name}.jpg", dur=round(dur, 1),
                            soggetto=f"(da verificare) {v.get('tags') or slug(v.get('url'))}", ambientazione="da verificare",
                            palette="da verificare", luce="da verificare", tono="dark",
                            fonte=f"{'Pixabay (Content License, uso libero)' if fonte_sito == 'pixabay' else 'Pexels (licenza Pexels, uso libero)'} – autore: {autore} – scaricato automaticamente il {datetime.date.today():%d/%m/%Y} (ricerca: {r['cerca']})",
                            originale=os.path.basename(urllib.parse.urlparse(f['link']).path), pexels_id=v["id"],
                            pexels_url=v.get("url", ""), da_verificare=True,
                            **({"ritaglio_centrale": True} if v.get("orizzontale") else {})))
            ids.add(vid); need -= 1; added.append((vid, name, slug(v.get("url"))))
            print("Aggiunta", name)
    json.dump(cat, open(CAT, "w"), indent=1, ensure_ascii=False)
    if added:
        lines = open(CODES).read().split("\n")
        last = max(i for i, l in enumerate(lines) if l.startswith("| ") and not l.startswith("| Codice"))
        lines[last + 1:last + 1] = [f"| {vid} | {name} | (da verificare) {s} |" for vid, name, s in added]   # pxb… = Pixabay
        open(CODES, "w").write("\n".join(lines))
    json.dump({"richieste": []}, open(REQ, "w"), indent=1)
    print(f"Totale aggiunte: {len(added)}")

if __name__ == "__main__":
    main()
