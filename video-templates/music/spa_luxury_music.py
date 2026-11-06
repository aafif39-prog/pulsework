# Original "luxury spa" background track for the Dr Glow / Mediwira HIFU ad. Fully synthesised (no samples, no copyright).
# 88 BPM so bar 9 (24.55s) lands on the contact card (cut at 24.5s): the progression resolves there and rings out.
import wave, numpy as np
from scipy.signal import fftconvolve, butter, sosfilt

SR = 48000; BPM = 88; BEAT = 60 / BPM; BAR = 4 * BEAT
DUR = 26.53
N = int(SR * DUR); L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(21)
def midi(n): return 440 * 2 ** ((n - 69) / 12)
def lp(x, fc, o=2): return sosfilt(butter(o, fc, fs=SR, output="sos"), x)
def hp(x, fc, o=2): return sosfilt(butter(o, fc, "highpass", fs=SR, output="sos"), x)
def add(t, sig, g, pan=0.5):
    i = int(t * SR)
    if i >= N or i < 0: return
    sig = sig[: N - i]
    L[i:i + len(sig)] += sig * g * (1 - pan) * 1.4; R[i:i + len(sig)] += sig * g * pan * 1.4

# Fmaj7 - G6 - Em7 - Am9 (dreamy, warm), final bar resolves on Fmaj9
prog = [(41, [57, 60, 64, 65, 69]), (43, [59, 62, 64, 67, 71]), (40, [55, 59, 62, 64, 67]), (45, [57, 60, 64, 67, 71])]
final = (41, [57, 60, 64, 67, 69, 72])

def piano(f, dur=3.0, vel=1.0):  # felt piano: few harmonics, soft attack, two-stage decay
    n = int(dur * SR); t = np.arange(n) / SR
    s = sum(a * np.sin(2 * np.pi * f * k * t * (1 + 0.0004 * k)) * np.exp(-t * (1.6 + 1.1 * k)) for k, a in zip(range(1, 6), (1, .45, .22, .1, .05)))
    s *= np.minimum(t / 0.008, 1) * (0.7 * np.exp(-t * 1.2) + 0.3 * np.exp(-t * 0.35))
    return lp(s, 3800) * vel
def pad(notes, dur):
    n = int(dur * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for m in notes:
        for d in (-0.1, 0.0, 0.1):
            f = midi(m) * 2 ** (d / 12)
            s += np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) + 0.2 * np.sin(4 * np.pi * f * t)
    a = np.minimum(t / 1.4, 1) * np.minimum((dur - t) / 1.0, 1)
    return lp(s * a * (0.8 + 0.2 * np.sin(2 * np.pi * 0.15 * t)), 1800) / (len(notes) * 3)
def bell(f, dur=2.5):
    n = int(dur * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * f * t + 1.8 * np.exp(-t * 3) * np.sin(2 * np.pi * 2.76 * f * t)) * np.exp(-t * 2.0) * np.minimum(t / 0.003, 1)
def kick():
    n = int(0.35 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(46 + 50 * np.exp(-t * 30)) / SR) * np.exp(-t * 8)
def shaker():
    n = int(0.1 * SR); t = np.arange(n) / SR
    return hp(rng.standard_normal(n), 6500) * np.minimum(t / 0.02, 1) * np.exp(-t * 35)
def swell(dur=1.6):  # soft reverse-noise swell into a cut
    n = int(dur * SR); t = np.arange(n) / SR
    return lp(hp(rng.standard_normal(n), 900), 5000) * (t / dur) ** 3

nbars = 9
for b in range(nbars):
    t0 = b * BAR
    root, ch = prog[b % 4]
    add(t0, pad(ch, BAR + 1.0), 0.55)
    # piano: chord on 1, gentle arpeggio
    for k, m in enumerate(ch[:4]):
        add(t0 + 0.012 * k, piano(midi(m), 3.2, 0.13), 1, 0.35 + 0.1 * k)
    arp = [ch[1] + 12, ch[2] + 12, ch[3] + 12, ch[4] + 12, ch[3] + 12, ch[2] + 12]
    for i, m in enumerate(arp):
        add(t0 + (1 + i * 0.5) * BEAT, piano(midi(m), 1.8, 0.07 if b >= 1 else 0.05), 1, 0.3 + 0.4 * (i % 2))
    # bass from bar 2
    if b >= 1:
        n_ = int(BAR * SR); tt = np.arange(n_) / SR
        add(t0, np.sin(2 * np.pi * midi(root) * tt) * np.exp(-tt * 0.9) * np.minimum(tt / 0.02, 1), 0.2)
    # light pulse in the middle section (bars 3-8)
    if 2 <= b <= 7:
        for beat in range(4):
            tb = t0 + beat * BEAT
            if beat in (0, 2): add(tb, kick(), 0.16)
            for q in (0, 0.5):
                add(tb + q * BEAT, shaker(), 0.012 if q else 0.006, 0.65)
    # sparkle every 2 bars
    if b % 2 == 1:
        add(t0 + 2 * BEAT, bell(midi(ch[-1] + 12)), 0.035, 0.75)
# accents on the main cuts
for tc in (6.73, 14.1, 18.67):
    add(tc - 1.6, swell(1.6), 0.05)
    add(tc, bell(midi(81)), 0.03, 0.3)
# resolve on the contact card (bar 9 = 24.55s): long Fmaj9 + bell
tf = 9 * BAR
add(tf - 1.6, swell(1.6), 0.06)
root, ch = final
for k, m in enumerate(ch):
    add(tf + 0.02 * k, piano(midi(m), 4.0, 0.12), 1, 0.3 + 0.08 * k)
add(tf, pad(ch, DUR - tf + 0.5), 0.6)
nf = int((DUR - tf + 0.5) * SR); tt = np.arange(nf) / SR
add(tf, np.sin(2 * np.pi * midi(root) * tt) * np.exp(-tt * 0.7), 0.2)
add(tf + 0.05, bell(midi(84), 3.0), 0.04, 0.6)

# reverb (stereo, ~2.6s) + master
irn = int(2.6 * SR); tt = np.arange(irn) / SR
ir = [lp(rng.standard_normal(irn) * np.exp(-tt * 2.3), 6000) for _ in range(2)]
ir = [x / np.sqrt((x ** 2).sum()) for x in ir]
L = L + 0.45 * fftconvolve(L, ir[0])[:N]; R = R + 0.45 * fftconvolve(R, ir[1])[:N]
L, R = hp(L, 35), hp(R, 35)
t = np.arange(N) / SR
fade = np.minimum(t / 0.8, 1) * np.clip((DUR - t) / 1.2, 0, 1)
L *= fade; R *= fade
pk = max(abs(L).max(), abs(R).max())
L = np.tanh(L / pk * 1.05) * 0.85; R = np.tanh(R / pk * 1.05) * 0.85
with wave.open("work/music.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.stack([L, R], 1) * 32767).astype(np.int16).tobytes())
print("ok", DUR, "bar", round(BAR, 3), "resolve at", round(tf, 2))
