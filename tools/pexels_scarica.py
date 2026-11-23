"""Scarica nuovi video da Pexels (licenza Pexels, uso libero) e li aggiunge alla libreria clips/.
Gira dentro GitHub Actions (.github/workflows/scarica-clip.yml) con il segreto PEXELS_API_KEY.

Richieste: clips/richieste.json
  {"richieste": [{"cerca": "man hoodie from behind", "quanti": 3, "prefisso": "uomo"}]}
Per ogni richiesta cerca video verticali, salta quelli già in libreria (CODICI_PEXELS.md e catalogo.json),
taglia 15 s in 1080x1920 senza audio, crea il poster, aggiunge la voce a catalogo.json con "da_verificare": true
e la riga a CODICI_PEXELS.md. Alla fine svuota le richieste.
Le clip "da_verificare" vanno guardate (poster e fotogrammi) e completate in italiano prima di usarle."""
import json, os, re, subprocess, sys, urllib.parse, urllib.request, urllib.error, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIPS = os.path.join(ROOT, "clips"); CAT = os.path.join(CLIPS, "catalogo.json")
REQ = os.path.join(CLIPS, "richieste.json"); CODES = os.path.join(CLIPS, "CODICI_PEXELS.md")
KEY = os.environ.get("PEXELS_API_KEY", "")
PXB = os.environ.get("PIXABAY_API_KEY", "")   # Pexels ha sospeso le nuove chiavi (23/11/2026): si usa Pixabay
MAX_PER_RUN = 10
LOG = os.path.join(CLIPS, "ultimo_download.log"); _log = []
def log(*a):
    m = " ".join(str(x) for x in a); print(m, flush=True); _log.append(m)
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

def api(url):
    r = urllib.request.Request(url, headers={"Authorization": KEY, "User-Agent": "voceinteriore-clip/1.0"})
    with urllib.request.urlopen(r, timeout=60) as f: return json.load(f)

def known_ids():
    ids = set()
    if os.path.exists(CODES):
        ids |= set(re.findall(r"\b(\d{5,9})\b", open(CODES).read()))   # tabella e scartati
        ids |= set(re.findall(r"\b(pxb\d+)\b", open(CODES).read()))   # Pixabay
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

def pixabay_search(query, tag=None):
    """Cerca su Pixabay e restituisce video nel formato usato sotto (come Pexels)."""
    q = urllib.parse.quote(query)
    rq = urllib.request.Request(f"https://pixabay.com/api/videos/?key={PXB}&q={q}&per_page=50&safesearch=true", headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(rq, timeout=60) as f: data = json.load(f)
    except urllib.error.HTTPError as e:
        log("Errore API Pixabay:", e.code, e.read()[:200]); return []
    log(f"Pixabay '{query}': {data.get('totalHits')} risultati, {len(data.get('hits', []))} in questa pagina")
    out = []
    tag = [t.lower() for t in (tag or [query.split()[0]])]
    for h in data.get("hits", []):
        tags = {t.strip().lower() for t in h.get("tags", "").split(",")}
        if not any(t in tags for t in tag): continue      # Pixabay restituisce anche risultati poco pertinenti
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
            videos = pixabay_search(r["cerca"], r.get("tag"))
            log(f"  pertinenti (tag {r.get('tag') or r['cerca'].split()[0]}): {len(videos)}")
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
            try:
                subprocess.run(["curl", "-sSfL", "--max-time", "300", "-A", UA, "-o", raw, f["link"]], check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                log("Download fallito", vid, f["width"], "x", f["height"], e.stderr.decode()[:200]); continue
            start = 1 if v["duration"] >= 17 else 0; dur = min(15, v["duration"] - start)
            ok = subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-t", str(dur), "-i", raw, "-an",
                            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
                            "-c:v", "libx264", "-crf", "21", "-maxrate", "6M", "-bufsize", "12M", "-preset", "veryfast", "-pix_fmt", "yuv420p",
                            "-movflags", "+faststart", out], capture_output=True)
            if ok.returncode != 0:
                log("ffmpeg fallito", vid, ok.stderr.decode()[-300:]); os.path.exists(out) and os.remove(out); continue
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
            log("Aggiunta", name, f"({f['width']}x{f['height']})")
    json.dump(cat, open(CAT, "w"), indent=1, ensure_ascii=False)
    if added:
        lines = open(CODES).read().split("\n")
        last = max(i for i, l in enumerate(lines) if l.startswith("| ") and not l.startswith("| Codice"))
        lines[last + 1:last + 1] = [f"| {vid} | {name} | (da verificare) {s} |" for vid, name, s in added]   # pxb… = Pixabay
        open(CODES, "w").write("\n".join(lines))
    json.dump({"richieste": []}, open(REQ, "w"), indent=1)
    log(f"Totale aggiunte: {len(added)}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback; log("ERRORE:", repr(e)); log(traceback.format_exc()[-1500:])
    finally:
        open(LOG, "w").write(f"{datetime.datetime.now():%d/%m/%Y %H:%M} UTC\n" + "\n".join(_log).replace(PXB or "§", "***").replace(KEY or "§", "***") + "\n")
