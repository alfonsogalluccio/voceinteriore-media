"""Video verticale 9:16 VoceInteriore2025: scene di testo su alba con zoom lento + pad audio originale."""
import sys, subprocess, os, json; sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from brand import *
def run(c): subprocess.run(c, shell=True, check=True, stderr=subprocess.DEVNULL)
def make(scenes, out, seed=5, tmp="/home/claude/vtmp"):
    os.makedirs(tmp, exist_ok=True); W, H, FPS = 1080, 1920, 30
    total = sum(s["dur"] for s in scenes)
    background(1296, 2304, seed, 0.95).save(f"{tmp}/bg.png")
    ft = Image.new("RGBA", (W, H), (0,0,0,0)); brand_footer(ft, H - 230); ft.save(f"{tmp}/footer.png")
    t0 = 0; parts = []
    for i, s in enumerate(scenes):
        ov = Image.new("RGBA", (W, H), (0,0,0,0))
        if s.get("kicker"):
            spaced(ov, s["kicker"].upper(), SANS, 30, W//2, 560, track=8); ornament(ov, W//2, 625)
        y0, y1 = text_block(ov, s["text"], SERIF_I, s.get("size", 88), W//2, s.get("cy", 900), 900)
        if s.get("sub"): spaced(ov, s["sub"].upper(), SANS, 30, W//2, y1 + 50, track=6)
        if s.get("small"): text_block(ov, s["small"], SANS_B, 40, W//2, 1480, 860, fill=CREAM)
        ov.save(f"{tmp}/t{i}.png"); n = int(s["dur"] * FPS); d = s["dur"]
        fin = 0 if i == 0 else 0.5
        flt = (f"[0]zoompan=z='1+0.10*((on+{int(t0*FPS)})/{int(total*FPS)})':d={n}:s={W}x{H}:fps={FPS}"
               f":x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2',format=rgba[b];"
               f"[1]format=rgba,fade=in:st={fin}:d=0.7:alpha=1,fade=out:st={d-0.7}:d=0.6:alpha=1[t];"
               f"[b][t]overlay[x];[x][2]overlay,format=yuv420p")
        if i == 0: flt += ",fade=in:st=0:d=0.4"
        if i == len(scenes)-1: flt += f",fade=out:st={d-0.5}:d=0.5"
        part = f"{tmp}/p{i}.mp4"
        run(f"ffmpeg -y -loop 1 -framerate {FPS} -i {tmp}/bg.png -loop 1 -framerate {FPS} -i {tmp}/t{i}.png "
            f"-i {tmp}/footer.png -filter_complex \"{flt}\" -frames:v {n} -c:v libx264 -crf 19 -preset veryfast "
            f"-pix_fmt yuv420p {tmp}/p{i}.tmp.mp4"); os.rename(f"{tmp}/p{i}.tmp.mp4", part); parts.append(part)
        t0 += d
    open(f"{tmp}/list.txt","w").write("".join(f"file '{p}'\n" for p in parts))
    run(f"ffmpeg -y -f concat -safe 0 -i {tmp}/list.txt -c copy {tmp}/v.mp4")
    # pianoforte originale sintetizzato (nessun diritto d'autore)
    import piano; piano.render(total, f"{tmp}/a.wav", seed=seed)
    run(f"ffmpeg -y -i {tmp}/v.mp4 -i {tmp}/a.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -af loudnorm=I=-16:TP=-1.5:LRA=11 -shortest -movflags +faststart {out}.tmp.mp4")
    os.rename(f"{out}.tmp.mp4", out)
if __name__ == "__main__":
    make(json.load(open(sys.argv[1])), sys.argv[2])
