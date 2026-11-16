"""Pianoforte sintetizzato originale (nessun diritto d'autore): arpeggi dolci + melodia, con riverbero."""
import numpy as np, sys, wave
SR = 44100
def note_freq(n): return 440 * 2 ** ((n - 69) / 12)
def piano(midi, dur, vel=0.5):
    f = note_freq(midi); t = np.arange(int(SR * (dur + 2.5))) / SR
    B = 0.0004; s = np.zeros_like(t)
    for k in range(1, 9):
        fk = f * k * np.sqrt(1 + B * k * k)
        if fk > 9000: break
        decay = np.exp(-t * (0.9 + 0.55 * k) * (f / 260) ** 0.35)
        s += (0.6 ** (k - 1)) * np.sin(2 * np.pi * fk * t + k) * decay
    att = np.minimum(1, t / 0.006)
    rel = np.where(t > dur, np.exp(-(t - dur) * 3.0), 1)
    return s * att * rel * vel
def render(total, out, bpm=72, seed=3):
    rng = np.random.default_rng(seed)
    beat = 60 / bpm; e = beat / 2
    # Do maggiore: C  G/B  Am  F  (Fsus→C finale)
    chords = [(48, [60, 64, 67]), (47, [59, 62, 67]), (45, [57, 60, 64]), (41, [57, 60, 65]),
              (48, [60, 64, 67]), (43, [59, 62, 67]), (45, [57, 60, 64]), (41, [57, 60, 65])]
    melody = [76, 74, 72, 74, 76, 79, 76, 74, 72, 71, 72, 69, 72, 74, 72, 72]
    buf = np.zeros(int(SR * (total + 4)))
    def add(m, at, dur, v):
        if at >= total: return
        x = piano(m, dur, v); i = int(at * SR); n = min(len(x), len(buf) - i); buf[i:i+n] += x[:n]
    bar = 4 * beat; t = 0.0; ci = 0
    while t < total:
        bass, tri = chords[ci % len(chords)]
        add(bass, t, bar, 0.42); add(bass + 12, t, bar, 0.18)
        patt = [tri[0], tri[1], tri[2], tri[1] + 12, tri[2], tri[1], tri[0] + 12, tri[2]]
        for j, m in enumerate(patt):
            add(m, t + j * e + rng.normal(0, 0.008), e * 1.6, 0.16 + 0.04 * rng.random())
        for j in range(2):
            mi = melody[(ci * 2 + j) % len(melody)]
            add(mi, t + j * 2 * beat + 0.02, 2 * beat, 0.30)
        t += bar; ci += 1
    # riverbero (convoluzione con coda di rumore decadente)
    ir_t = np.arange(int(SR * 2.2)) / SR
    ir = rng.normal(0, 1, len(ir_t)) * np.exp(-ir_t * 3.2); ir[0] = 0; ir /= np.abs(ir).sum() / 6
    wet = np.fft.irfft(np.fft.rfft(buf, len(buf) + len(ir)) * np.fft.rfft(ir, len(buf) + len(ir)))[:len(buf)]
    mix = 0.75 * buf + 0.35 * wet
    mix = mix[:int(SR * total)]
    fade = int(SR * 2.5); mix[-fade:] *= np.linspace(1, 0, fade) ** 1.5
    mix[:int(SR*0.05)] *= np.linspace(0, 1, int(SR*0.05))
    mix = mix / np.abs(mix).max() * 0.7
    st = np.stack([mix, np.roll(mix, int(SR * 0.012))], 1)
    with wave.open(out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())
if __name__ == "__main__":
    render(float(sys.argv[1]), sys.argv[2])
