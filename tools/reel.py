"""Reel/Short/TikTok dinamico VoceInteriore2025.
Testo che appare parola per parola a tempo di musica, sfondo in movimento con particelle di luce,
musica vera dalla libreria (estratto migliore, agganciato ai beat)."""
import sys, os, json, subprocess, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from brand import *
import scenes as SCN
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H, FPS = 1080, 1920, 30

def layout_words(text, fpath, size, maxw, cx, cy, lh=1.2):
    d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    while True:
        f = font(fpath, size); lines = wrap(d, text, f, maxw)
        if len(lines) * size * lh < H * 0.42 or size < 40: break
        size -= 4
    total_h = len(lines) * size * lh; y0 = cy - total_h / 2; words = []
    space = d.textlength(" ", font=f)
    for i, ln in enumerate(lines):
        x = cx - d.textlength(ln, font=f) / 2
        for wd in ln.split(" "):
            words.append((wd, x, y0 + i * size * lh)); x += d.textlength(wd, font=f) + space
    return f, words, y0 + total_h

def ease(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3

class Scene:
    def __init__(self, s, t0, t1):
        self.t0, self.t1 = t0, t1; self.s = s
        style = s.get("style", "body")
        size = {"hook": 104, "body": 88, "verse": 84, "cta": 96, "caption": 58}[style]
        fp = SERIF_I if style in ("verse", "body", "hook") else SERIF
        if style == "caption":   # sottotitolo stile "divisa FORTE": piccolo, bianco, centro-basso
            fp = SANS_B; s = dict(s); s.setdefault("cy", 1380)
        text = s["text"]
        if s.get("font") == "impact":   # registro "forte": maiuscolo d'impatto, *parole* in oro
            fp = SANS_X; text = text.upper(); size = int(size * 0.8)
        self.hl = {w.strip(".,;:!?«»\"'") for m in __import__("re").findall(r"\*([^*]+)\*", text) for w in m.split()}
        text = text.replace("*", "")
        self.f, self.words, self.ybot = layout_words(text, fp, s.get("size", size), 900, W/2, s.get("cy", 880))
        self.reveal = s.get("reveal", min(1.4, 0.18 * len(self.words)))
        self.s = s
    def draw(self, t):
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
        lt = t - self.t0; out = 1 - ease((t - (self.t1 - 0.35)) / 0.35) if t > self.t1 - 0.35 else 1
        n = len(self.words)
        for i, (wd, x, y) in enumerate(self.words):
            if self.s.get("instant") and i < 3: a = out
            else: a = ease((lt - self.reveal * i / max(1, n)) / 0.28) * out
            if a <= 0: continue
            dy = (1 - a) * 22
            col = GOLD if wd.strip(".,;:!?«»\"'") in self.hl else CREAM
            d.text((x, y + dy), wd, font=self.f, fill=col + (int(255 * a),))
        if self.s.get("kicker"):
            a = ease(lt / 0.3) * out; tmp = Image.new("RGBA", (W, H), (0,0,0,0))
            spaced(tmp, self.s["kicker"].upper(), SANS, 32, W//2, self.s.get("cy", 880) - 260, fill=GOLD, track=8)
            ornament(tmp, W//2, self.s.get("cy", 880) - 200)
            tmp.putalpha(tmp.getchannel("A").point(lambda v: int(v * a))); layer.alpha_composite(tmp)
        if self.s.get("sub"):
            a = ease((lt - self.reveal) / 0.4) * out; tmp = Image.new("RGBA", (W, H), (0,0,0,0))
            spaced(tmp, self.s["sub"].upper(), SANS, 32, W//2, int(self.ybot + 40), fill=GOLD, track=6)
            tmp.putalpha(tmp.getchannel("A").point(lambda v: int(v * a))); layer.alpha_composite(tmp)
        if self.s.get("small"):
            a = ease((lt - self.reveal - 0.2) / 0.4) * out; tmp = Image.new("RGBA", (W, H), (0,0,0,0))
            text_block(tmp, self.s["small"], SANS_B, 44, W//2, 1430, 860, fill=CREAM)
            tmp.putalpha(tmp.getchannel("A").point(lambda v: int(v * a))); layer.alpha_composite(tmp)
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sh.putalpha(layer.getchannel("A").point(lambda v: int(v * 0.55)))
        sh = sh.filter(ImageFilter.GaussianBlur(8)); base = Image.new("RGBA", (W, H), (0,0,0,0))
        base.alpha_composite(sh, (0, 3)); base.alpha_composite(layer); return base

def particles(rng, n=38):
    return dict(x=rng.random(n) * W, y=rng.random(n) * H, r=2 + rng.random(n) * 7,
                vy=-(8 + rng.random(n) * 30), vx=rng.normal(0, 6, n), ph=rng.random(n) * 6.28)

def render(spec, out, music_dir, lib, tmp="/home/claude/rtmp"):
    os.makedirs(tmp, exist_ok=True); rng = np.random.default_rng(spec.get("seed", 1))
    track = next(x for x in lib if x["file"] == spec["music"])
    start = spec.get("music_start", track["best_start"]); total = spec["dur"]
    beats = [b - start for b in track["beats"] if start <= b <= start + total]
    # tempi delle scene agganciati ai beat
    cuts = [0.0]
    for c in spec["cuts"]:
        # con la voce narrante i tagli devono seguire la voce: "snap_beats": false li lascia dove sono
        cuts.append(min(beats, key=lambda b: abs(b - c)) if beats and spec.get("snap_beats", True) else c)
    cuts.append(total)
    scenes = [Scene(s, cuts[i], cuts[i+1]) for i, s in enumerate(spec["scenes"])]
    bgspec = spec.get("bg", {"concept": "cielo", "palette": spec.get("palette", "alba")})
    bg, meta = SCN.render(bgspec, 1296, 2304, spec.get("seed", 1))
    if meta.get("tono") == "light" or bgspec.get("concept") != "cielo":
        # velatura per leggere il testo chiaro su qualsiasi sfondo
        import numpy as _np
        a = _np.array(bg, _np.float32) * (0.55 if meta.get("tono") == "light" else 0.78); bg = Image.fromarray(a.clip(0, 255).astype(_np.uint8))
    meta.update(layout="video")
    clip = None
    if "clip" in bgspec:
        cp = os.path.join(SCN.ROOT, bgspec["clip"])
        # "slow": rallenta la clip (es. 1.5); "pingpong": true la fa scorrere avanti e indietro, così nei Reel
        # lunghi (35-45 s) una clip da 12-15 s non "salta" quando ricomincia
        if bgspec.get("slow") or bgspec.get("pingpong"):
            k = bgspec.get("slow", 1.0); lp = f"{tmp}/clip_loop.mp4"
            fc = f"[0:v]setpts={k}*PTS,split[a][b];[b]reverse[r];[a][r]concat=n=2:v=1[v]" if bgspec.get("pingpong") else f"[0:v]setpts={k}*PTS[v]"
            subprocess.run(f'ffmpeg -v error -y -i "{cp}" -an -filter_complex "{fc}" -map "[v]" -c:v libx264 -crf 16 -preset veryfast "{lp}"', shell=True, check=True)
            cp = lp
        # "grade": "bn" = divisa del registro FORTE: bianco e nero morbido, contrasto un po' più alto
        grade = ",hue=s=0.08,eq=contrast=1.15:brightness=-0.02" if bgspec.get("grade") == "bn" else ""
        clip = subprocess.Popen(f'ffmpeg -v error -stream_loop -1 -i "{cp}" -vf "scale={W}:{H},fps={FPS}{grade}" -f rawvideo -pix_fmt rgb24 -',
                                shell=True, stdout=subprocess.PIPE, stdin=subprocess.DEVNULL)
        dk = bgspec.get("darken", 0.38)
    foot = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ornament(foot, W // 2, H - 252, half=40, fill=CREAM); spaced(foot, "VOCEINTERIORE2025", SANS_B, 26, W // 2, H - 230, fill=CREAM, track=7)
    P = particles(rng); N = int(total * FPS)
    beat_frames = set(int(b * FPS) for b in beats)
    ff = subprocess.Popen(f"ffmpeg -v error -y -f rawvideo -pix_fmt rgb24 -s {W}x{H} -r {FPS} -i - "
                          f"-c:v libx264 -crf 18 -preset veryfast -pix_fmt yuv420p {tmp}/v.mp4", shell=True, stdin=subprocess.PIPE)
    pulse = 0.0
    for fi in range(N):
        t = fi / FPS
        if fi in beat_frames: pulse = 1.0
        pulse *= 0.86
        z = 1 + 0.09 * t / total
        cw, ch = 1296 / z * (W / 1296) * 1.2, 2304 / z * (H / 2304) * 1.2
        cx, cy = 648 + 18 * np.sin(t * 0.4), 1152 - 30 * t / total
        if clip:
            raw = clip.stdout.read(W * H * 3)
            fr = np.frombuffer(raw, np.uint8).reshape(H, W, 3).astype(np.float32) * (1 - dk)
            frame = Image.fromarray(fr.astype(np.uint8)).convert("RGBA")
        else:
            frame = bg.crop((int(cx - cw/2), int(cy - ch/2), int(cx + cw/2), int(cy + ch/2))).resize((W, H), Image.BILINEAR).convert("RGBA")
        # particelle di luce che salgono
        if spec.get("particles", True):   # nel registro FORTE si spengono ("particles": false)
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
            ys = (P["y"] + P["vy"] * t) % H; xs = (P["x"] + P["vx"] * t) % W
            for x, y, r, ph in zip(xs, ys, P["r"], P["ph"]):
                a = int((90 + 70 * np.sin(t * 1.5 + ph)) * (0.4 + 0.6 * y / H) * (1 + 0.6 * pulse))
                d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 230, 180, min(255, a)))
            frame.alpha_composite(lay.filter(ImageFilter.GaussianBlur(3)))
        for sc in scenes:
            if sc.t0 <= t < sc.t1: frame.alpha_composite(sc.draw(t))
        frame.alpha_composite(foot)
        if fi >= N - 12: frame = Image.blend(frame, Image.new("RGBA", (W, H), (0, 0, 0, 255)), (fi - (N - 12)) / 12 * 0.9)
        ff.stdin.write(frame.convert("RGB").tobytes())
    ff.stdin.close(); ff.wait()
    if clip: clip.kill()
    mp = os.path.join(music_dir, spec["music"])
    if spec.get("voice"):
        # voce narrante (ElevenLabs) sopra la musica abbassata
        vd = int(spec.get("voice_delay", 0.6) * 1000); mv = spec.get("music_vol_with_voice", 0.22)
        subprocess.run(f'ffmpeg -v error -y -i {tmp}/v.mp4 -ss {start} -t {total} -i "{mp}" -i "{spec["voice"]}" '
                       f'-filter_complex "[1:a]volume={mv},afade=in:d=0.15,afade=out:st={total-1.2}:d=1.2[m];'
                       f'[2:a]adelay={vd}|{vd},apad[v];[m][v]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]" '
                       f'-map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -t {total} -movflags +faststart "{out}.tmp.mp4"', shell=True, check=True)
    else:
        subprocess.run(f'ffmpeg -v error -y -i {tmp}/v.mp4 -ss {start} -t {total} -i "{mp}" -map 0:v -map 1:a -c:v copy '
                       f'-af "afade=in:d=0.15,afade=out:st={total-1.2}:d=1.2,loudnorm=I=-14:TP=-1.5:LRA=11" -c:a aac -b:a 192k '
                       f'-shortest -movflags +faststart "{out}.tmp.mp4"', shell=True, check=True)
    os.rename(out + ".tmp.mp4", out)
    return cuts, meta

if __name__ == "__main__":
    spec = json.load(open(sys.argv[1])); lib = json.load(open(os.path.join(sys.argv[3], "library.json")))
    print(render(spec, sys.argv[2], sys.argv[3], lib)[0])
