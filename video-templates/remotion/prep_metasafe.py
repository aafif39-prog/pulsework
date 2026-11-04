# VIDEO 2 "Metal vs Ceramic Braces" - prep for the Meta-safe Remotion render.
# Based on prep.py from the template; captions rebuilt from word timings (speech is English).
import json, subprocess, shutil, os
P = "rem/public/"
os.makedirs(P, exist_ok=True)
def run(c): subprocess.run(c, shell=True, check=True)

KEEP = [(0.3, 5.6), (21.2, 57.3)]  # cut the first take of "This one is metal..." (retake at 21.2s)
def out_t(t):
    o = 0
    for a, b in KEEP:
        if a <= t < b: return o + (t - a)
        o += b - a
    return o
SPEECH = round(sum(b - a for a, b in KEEP), 3)

# ---- captions: English words with timings, max 4 per chunk ----
segs = json.load(open("transcript_src_en.json"))
words = []
for s in segs:
    for w in s["words"]:
        t = w["w"].strip()
        if not any(a <= w["s"] < b for a, b in KEEP): continue
        if t.startswith("-") and words:  # "budget" + "-friendly"
            words[-1]["t"] += t; words[-1]["e"] = round(out_t(min(w["e"], 57.29)), 3); continue
        words.append({"t": t, "s": round(out_t(w["s"]), 3), "e": round(out_t(min(w["e"], 57.29)), 3)})
words[0]["t"] = "Metal"
chunks, cur = [], []
for w in words:
    if cur and (len(cur) >= 4 or cur[-1]["t"][-1] in ",.?!" or w["s"] - cur[-1]["e"] > 0.6):
        chunks.append(cur); cur = []
    cur.append(w)
chunks.append(cur)
for i, c in enumerate(chunks):
    nxt = chunks[i + 1][0]["s"] if i + 1 < len(chunks) else SPEECH
    c[-1]["e"] = min(c[-1]["e"] + 0.3, nxt)
json.dump({"speech": SPEECH, "chunks": chunks}, open(P + "captions.json", "w"), indent=1)
for c in chunks: print(f'{c[0]["s"]:6.2f} ' + " ".join(w["t"] for w in c))
print("speech", SPEECH)

# ---- voice (template VOICE_CHAIN, fixed gain to -14 LUFS) ----
VOICE_CHAIN = ("highpass=f=90,anlmdn=s=7:p=0.002:r=0.006,afftdn=nr=12:nf=-42,"
               "acompressor=threshold=-20dB:ratio=3:attack=5:release=120,"
               "agate=threshold=0.025:range=0.05:ratio=4:attack=4:release=300:knee=2,lowpass=f=12000")
fc = ";".join(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={b-a-0.03}:d=0.03[a{i}]" for i, (a, b) in enumerate(KEEP))
fc += ";" + "".join(f"[a{i}]" for i in range(len(KEEP))) + f"concat=n={len(KEEP)}:v=0:a=1,{VOICE_CHAIN}[o]"
run(f'ffmpeg -v error -y -i raw/src.mp4 -filter_complex "{fc}" -map "[o]" -ar 48000 -ac 2 work/voice_pre.wav')
r = subprocess.run("ffmpeg -i work/voice_pre.wav -af ebur128 -f null -", shell=True, capture_output=True, text=True).stderr
I = float([l for l in r.splitlines() if " I:" in l][-1].split()[1])
run(f'ffmpeg -v error -y -i work/voice_pre.wav -af "volume={-14-I:.2f}dB,alimiter=limit=0.89" work/voice.wav')
print(f"voice: measured {I} LUFS -> -14")

# ---- footage + B-roll (1080x1920) ----
shutil.copy("raw/src.mp4", P + "src.mp4")
grade = "eq=contrast=1.06:brightness=0.015:saturation=1.08,unsharp=5:5:0.4"
def broll(name, src, ss, geo, d=5):
    run(f'ffmpeg -v error -y -ss {ss} -i raw/{src}.mp4 -t {d} -an -vf "fps=30,{geo},setsar=1,{grade},format=yuv420p" -c:v libx264 -crf 17 -preset fast {P}{name}')
B = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920:(iw-ow)/2:ih-oh"
broll("b_wire.mp4", "160710", 0.3, "scale=-2:2208,crop=1080:1920:2391:150")
broll("b_place.mp4", "160728", 5.0, B)
broll("b_model.mp4", "161530", 1.0, B)
broll("b_clinic.mp4", "160005", 11.0, B)
# close-up cards (880x774)
run(f'ffmpeg -v error -y -ss 11.6 -i raw/isihat_ceramic.mp4 -t 3.2 -an -vf "fps=30,crop=880:774:100:330,format=yuv420p" -c:v libx264 -crf 17 {P}c_ceramic.mp4')
run(f'ffmpeg -v error -y -ss 7.5 -i raw/160728.mp4 -t 4.5 -an -vf "fps=30,crop=440:500:380:1220,transpose=2,scale=880:774:force_original_aspect_ratio=increase,crop=880:774,format=yuv420p" -c:v libx264 -crf 17 {P}c_metal.mp4')
# brand images (logo cut-out + Meta-safe top banner from build3_metasafe.py)
shutil.copy("work/logo.png", P + "logo.png")
shutil.copy("work/banner.png", P + "banner.png")
for f in ["Inter-ExtraBold.otf", "Inter-Black.otf", "Inter-Bold.otf", "Inter-SemiBold.otf", "InterDisplay-ExtraBold.otf"]:
    shutil.copy("/usr/share/fonts/opentype/inter/" + f, P + f)
print("prep ok")
