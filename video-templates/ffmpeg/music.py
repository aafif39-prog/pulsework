# Original, procedurally generated background track (no samples, no copyright).
# Same as the T.LOW template; length comes from MUSIC_DUR (seconds).
import os, wave
import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt

SR = 44100
BPM = 96
BEAT = 60 / BPM
BAR = 4 * BEAT
DUR = float(os.environ.get("MUSIC_DUR", "46"))
N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)

def midi(n): return 440 * 2 ** ((n - 69) / 12)
def env(n, a, d_rate):
    t = np.arange(n) / SR
    e = np.exp(-t * d_rate)
    ai = int(a * SR)
    if ai > 0: e[:ai] *= np.linspace(0, 1, ai)
    return e
def add(buf, start, sig, gain=1.0):
    i = int(start * SR)
    if i >= N: return
    sig = sig[: N - i]
    buf[i:i + len(sig)] += sig * gain
def lp(x, fc, order=2): return sosfilt(butter(order, fc, fs=SR, output="sos"), x)
def hp(x, fc, order=2): return sosfilt(butter(order, fc, "highpass", fs=SR, output="sos"), x)

# D major: I - V - vi - IV with added 9ths
prog = [(50, [62, 66, 69, 76]), (45, [61, 64, 69, 71]), (47, [62, 66, 71, 73]), (43, [62, 67, 71, 74])]
nbars = int(DUR / BAR) + 1

def keys(f, dur, vel):
    n = int(dur * SR); t = np.arange(n) / SR
    idx = 1.6 * np.exp(-t * 6)
    s = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t))
    s += 0.25 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 8)
    return s * env(n, 0.004, 2.2) * vel
def pad(notes, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.zeros(n)
    for m in notes:
        for det in (-0.12, 0.12):
            f = midi(m + det)
            s += np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)
    a = np.minimum(t / 0.8, 1) * np.minimum((dur - t) / 0.6, 1)
    return lp(s * a, 1800) / len(notes)
def pluck(f, dur=0.5):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t * 18)
    return s * env(n, 0.002, 7)
def kick():
    n = int(0.35 * SR); t = np.arange(n) / SR
    f = 48 + 70 * np.exp(-t * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
def snap():
    n = int(0.25 * SR)
    return lp(hp(rng.standard_normal(n), 1400) * env(n, 0.001, 22), 7000)
def hat():
    n = int(0.08 * SR)
    return hp(rng.standard_normal(n), 7000) * env(n, 0.001, 55)

for b in range(nbars):
    t0 = b * BAR
    root, ch = prog[b % 4]
    p = pad(ch, BAR + 0.4)
    add(L, t0, p, 0.10); add(R, t0, p, 0.10)
    for off, vel in ((0, 0.16), (1.5 * BEAT, 0.11), (3 * BEAT, 0.09)):
        for k, m in enumerate(ch[:3]):
            s = keys(midi(m), 1.6, vel)
            add(L, t0 + off + 0.006 * k, s, 0.9 if k % 2 else 0.7)
            add(R, t0 + off + 0.006 * k, s, 0.7 if k % 2 else 0.9)
    if b >= 1:
        for off in (0, 2.5 * BEAT, 3 * BEAT):
            n = int(0.9 * BEAT * SR); t = np.arange(n) / SR
            s = np.sin(2 * np.pi * midi(root) * t) * env(n, 0.006, 3.5)
            add(L, t0 + off, s, 0.22); add(R, t0 + off, s, 0.22)
    if b >= 2:
        arp = [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[3] + 12, ch[2] + 12, ch[1] + 12, ch[3] + 12, ch[2] + 12]
        for i, m in enumerate(arp):
            s = pluck(midi(m)); pan = 0.35 + 0.3 * (i % 2)
            add(L, t0 + i * BEAT / 2, s, 0.05 * (1 - pan) * 2)
            add(R, t0 + i * BEAT / 2, s, 0.05 * pan * 2)
        for beat in range(4):
            tb = t0 + beat * BEAT
            if beat in (0, 2):
                k = kick(); add(L, tb, k, 0.30); add(R, tb, k, 0.30)
            else:
                s = snap(); add(L, tb, s, 0.05); add(R, tb, s, 0.05)
            for h in (0, 0.5):
                s = hat(); g = 0.022 if h else 0.012
                add(L, tb + h * BEAT, s, g * 0.8); add(R, tb + h * BEAT, s, g * 1.2)

irn = int(1.9 * SR); tt = np.arange(irn) / SR
irL = lp(rng.standard_normal(irn) * np.exp(-tt * 3.2), 5000)
irR = lp(rng.standard_normal(irn) * np.exp(-tt * 3.2), 5000)
irL /= np.sqrt((irL ** 2).sum()); irR /= np.sqrt((irR ** 2).sum())
L = L + 0.35 * fftconvolve(L, irL)[:N]; R = R + 0.35 * fftconvolve(R, irR)[:N]
L = hp(L, 35); R = hp(R, 35)
t = np.arange(N) / SR
fade = np.minimum(t / 1.0, 1) * np.clip((DUR - t) / 2.5, 0, 1)
L *= fade; R *= fade
peak = max(abs(L).max(), abs(R).max())
L = np.tanh(L / peak * 1.1) * 0.85; R = np.tanh(R / peak * 1.1) * 0.85
pcm = (np.stack([L, R], 1) * 32767).astype(np.int16)
os.makedirs("work", exist_ok=True)
with wave.open("work/music.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())

# --- subtle generated SFX: soft whoosh + small pop ---
def save(name, x):
    x = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(f"work/{name}.wav", "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(x.tobytes())
n = int(0.55 * SR); t = np.arange(n) / SR
noise = rng.standard_normal(n)
sweep = np.concatenate([lp(noise[i:i + 2205], 600 + 5000 * (i / n)) for i in range(0, n, 2205)])[:n]
save("whoosh", sweep * np.sin(np.pi * t / t[-1]) ** 2 * 0.5)
n = int(0.12 * SR); t = np.arange(n) / SR
f = 900 * np.exp(-t * 30) + 400
save("pop", np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 40) * 0.6)
print("music ok", DUR)
