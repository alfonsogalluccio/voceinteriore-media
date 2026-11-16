"""Analizza la libreria musicale: tempo, beat, energia, umore e miglior finestra per video brevi."""
import librosa, numpy as np, json, sys, os, glob
def analyze(path, win=12.0):
    y, sr = librosa.load(path, sr=22050, mono=True)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units="time")
    tempo = float(np.atleast_1d(tempo)[0])
    rms = librosa.feature.rms(y=y, hop_length=512)[0]; t = librosa.times_like(rms, sr=sr, hop_length=512)
    cent = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
    dur = len(y) / sr; best, bs = 0, -1
    # finestra: energia alta, crescita nei primi secondi, evitando i primi 5 s e il finale
    for s in np.arange(5, max(6, dur - win - 6), 0.5):
        m = (t >= s) & (t < s + win)
        if m.sum() == 0: continue
        e = rms[m]; n = len(e)
        score = e.mean() + 0.6 * (e[n//3:].mean() - e[:n//6].mean()) + 0.3 * e[:n//6].mean()
        if score > bs: bs, best = score, s
    # aggancia al beat più vicino
    if len(beats): best = float(beats[np.argmin(np.abs(beats - best))])
    energy = float(rms.mean())
    mood = "epico" if (energy > 0.16 and tempo > 100) else ("luminoso" if cent > 2200 else "emozionale")
    return dict(file=os.path.basename(path), dur=round(dur,1), tempo=round(tempo,1), energy=round(energy,3),
                brightness=round(cent), mood=mood, best_start=round(best,2),
                beats=[round(float(b),3) for b in beats])
if __name__ == "__main__":
    lib = [analyze(p) for p in sorted(glob.glob(os.path.join(sys.argv[1], "*.mp3")))]
    json.dump(lib, open(sys.argv[2], "w"), indent=1)
    for x in lib: print(f'{x["file"][:45]:45} {x["dur"]:6} bpm={x["tempo"]:6} E={x["energy"]} C={x["brightness"]} {x["mood"]} start={x["best_start"]}')
