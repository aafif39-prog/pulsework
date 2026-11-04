# Original "clinic ambience" track (template music_clinic.py): airy pads, marimba + bells, shaker, soft beat.
# Fully synthesized (no samples). DUR from MUSIC_DUR. Output: work/music_clinic.wav
import os, wave
import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt

SR = 44100; BPM = 104; BEAT = 60 / BPM; BAR = 4 * BEAT
DUR = float(os.environ.get("MUSIC_DUR", "45"))
N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(11)
def midi(n): return 440 * 2 ** ((n - 69) / 12)
def lp(x, fc): return sosfilt(butter(2, fc, fs=SR, output="sos"), x)
def hp(x, fc): return sosfilt(butter(2, fc, "highpass", fs=SR, output="sos"), x)
def add(buf, t, sig, g):
    i = int(t * SR)
    if i >= N: return
    sig = sig[: N - i]; buf[i:i + len(sig)] += sig * g
def stereo(t, sig, g, pan):
    add(L, t, sig, g * (1 - pan) * 1.4); add(R, t, sig, g * pan * 1.4)
prog = [(41, [60, 64, 67, 69, 72]), (45, [60, 64, 67, 69, 71]), (38, [60, 62, 65, 69, 72]), (46, [58, 62, 65, 69, 72])]
def pad(notes, dur):
    n = int(dur * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for m in notes:
        for d in (-0.08, 0.0, 0.08):
            f = midi(m) * 2 ** (d / 12)
            s += np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) + 0.18 * np.sin(4 * np.pi * f * t)
    lfo = 0.75 + 0.25 * np.sin(2 * np.pi * 0.2 * t)
    a = np.minimum(t / 1.2, 1) * np.minimum((dur - t) / 0.9, 1)
    return lp(s * a * lfo, 2200) / (len(notes) * 3)
def marimba(f, dur=0.6):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 9) + 0.35 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t * 30)
    return s * np.minimum(t / 0.002, 1)
def bell(f, dur=2.2):
    n = int(dur * SR); t = np.arange(n) / SR
    idx = 2.2 * np.exp(-t * 3)
    return np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * 3.5 * f * t)) * np.exp(-t * 2.2) * np.minimum(t / 0.003, 1)
def kick():
    n = int(0.3 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(50 + 60 * np.exp(-t * 30)) / SR) * np.exp(-t * 10)
def shaker():
    n = int(0.09 * SR); t = np.arange(n) / SR
    return hp(rng.standard_normal(n), 6000) * np.minimum(t / 0.015, 1) * np.exp(-t * 40)
def snap():
    n = int(0.2 * SR); t = np.arange(n) / SR
    return lp(hp(rng.standard_normal(n), 1800), 8000) * np.exp(-t * 28)
for b in range(int(DUR / BAR) + 1):
    t0 = b * BAR; root, ch = prog[b % 4]
    stereo(t0, pad(ch, BAR + 0.6), 0.55, 0.5)
    if b >= 1:
        for off in (0, 1.5 * BEAT, 2.5 * BEAT):
            n = int(0.8 * BEAT * SR); tt = np.arange(n) / SR
            stereo(t0 + off, np.sin(2 * np.pi * midi(root) * tt) * np.exp(-tt * 3) * np.minimum(tt / 0.01, 1), 0.16, 0.5)
        for k, (beat, idx) in enumerate([(0, 2), (0.75, 4), (1.5, 3), (2, 2), (2.75, 4), (3.5, 1)]):
            stereo(t0 + beat * BEAT, marimba(midi(ch[idx % len(ch)] + 12)), 0.09, 0.3 + 0.4 * (k % 2))
    if b % 2 == 0: stereo(t0 + 0.02, bell(midi(ch[-1] + 12)), 0.035, 0.7)
    if b >= 2:
        for beat in range(4):
            tb = t0 + beat * BEAT
            if beat in (0, 2): stereo(tb, kick(), 0.26, 0.5)
            if beat in (1, 3): stereo(tb, snap(), 0.035, 0.5)
            for q in range(4): stereo(tb + q * BEAT / 4, shaker(), 0.018 if q % 2 else 0.01, 0.65)
irn = int(2.4 * SR); tt = np.arange(irn) / SR; irs = []
for _ in range(2):
    ir = lp(rng.standard_normal(irn) * np.exp(-tt * 2.6), 6000); irs.append(ir / np.sqrt((ir ** 2).sum()))
L = L + 0.4 * fftconvolve(L, irs[0])[:N]; R = R + 0.4 * fftconvolve(R, irs[1])[:N]
L, R = hp(L, 40), hp(R, 40)
t = np.arange(N) / SR
fade = np.minimum(t / 1.5, 1) * np.clip((DUR - t) / 2.5, 0, 1)
L *= fade; R *= fade
pk = max(abs(L).max(), abs(R).max())
L = np.tanh(L / pk * 1.1) * 0.85; R = np.tanh(R / pk * 1.1) * 0.85
with wave.open("work/music_clinic.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.stack([L, R], 1) * 32767).astype(np.int16).tobytes())

# ---- SFX (template sfx.py), timings for this edit ----
SR2 = 48000; out = np.zeros(int(SR2 * DUR)); r2 = np.random.default_rng(3)
def whoosh(d=0.55):
    n = int(d * SR2); tt = np.arange(n) / SR2; x = r2.standard_normal(n); y = np.zeros(n)
    for i in range(0, n, 512):
        f = 400 + 3200 * (i / n); y[i:i + 512] = sosfilt(butter(2, [f * 0.6, f * 1.4], 'bandpass', fs=SR2, output='sos'), x[i:i + 512])
    return y * np.sin(np.pi * np.clip(tt / d, 0, 1)) ** 2 / np.abs(y).max()
def pop(f=700):
    n = int(0.12 * SR2); tt = np.arange(n) / SR2
    return np.sin(2 * np.pi * np.cumsum(f * (1 + 1.5 * np.exp(-tt * 60))) / SR2) * np.exp(-tt * 38)
def put(t, s, g):
    i = int(t * SR2); s = s[:len(out) - i]; out[i:i + len(s)] += s * g
put(0.07, pop(650), 0.16); put(0.33, pop(820), 0.16)      # hook lines
put(2.35, whoosh(), 0.10)                                  # banner
put(5.46, pop(760), 0.13); put(16.6, pop(760), 0.13)       # chips
put(26.52, pop(700), 0.12); put(26.79, pop(820), 0.12)     # compare cards
put(41.2, whoosh(0.6), 0.10)                               # end card
with wave.open("work/sfx.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR2)
    w.writeframes((np.clip(np.stack([out, out], 1), -1, 1) * 32767).astype(np.int16).tobytes())
print("music + sfx ok", DUR)
