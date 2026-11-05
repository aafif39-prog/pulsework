# I-SIHAT Bukit Jalil - "aesthetic" motion style. Prep: footage, cleaned voice, captions.json, logo.
import json, subprocess
from PIL import Image
def run(c): subprocess.run(c, shell=True, check=True)
P = "rem/public/"
CLIPS = [("c6986", 0.15, 20.55), ("c6992", 0.00, 11.65), ("c6993", 0.00, 4.40)]
offs, t = [], 0.0
for c, a, b in CLIPS:
    offs.append(t); t += b - a
SPEECH = round(t, 3)

# ---- footage (1080x1920, 30fps, light grade) + voice (template chain, fixed gain to -14 LUFS) ----
grade = "eq=contrast=1.05:brightness=0.02:saturation=1.05,unsharp=5:5:0.35"
vparts = []
for i, (c, a, b) in enumerate(CLIPS):
    run(f'ffmpeg -v error -y -ss {a} -i raw/{c}.mov -t {b-a:.3f} -an -vf "fps=30,scale=1080:1920:force_original_aspect_ratio=increase,'
        f'crop=1080:1920,setsar=1,{grade},format=yuv420p" -c:v libx264 -crf 16 -preset fast work/v{i}.mp4')
    vparts.append(f"work/v{i}.mp4")
open("work/vlist.txt", "w").write("".join(f"file '{p.split('/')[-1]}'\n" for p in vparts))
run("ffmpeg -v error -y -f concat -safe 0 -i work/vlist.txt -c copy " + P + "src.mp4")
VOICE = ("highpass=f=90,anlmdn=s=7:p=0.002:r=0.006,afftdn=nr=12:nf=-42,"
         "acompressor=threshold=-20dB:ratio=3:attack=5:release=120,"
         "agate=threshold=0.02:range=0.06:ratio=4:attack=4:release=300:knee=2,lowpass=f=12000")
ins = " ".join(f"-ss {a} -t {b-a:.3f} -i raw/{c}.mov" for c, a, b in CLIPS)
fc = "".join(f"[{i}:a]aresample=48000,ac=1,afade=t=in:d=0.02,afade=t=out:st={b-a-0.04:.3f}:d=0.04[a{i}];" for i, (c, a, b) in enumerate(CLIPS))
fc = fc.replace(",ac=1", ",aformat=channel_layouts=mono")
fc += "".join(f"[a{i}]" for i in range(len(CLIPS))) + f"concat=n={len(CLIPS)}:v=0:a=1,{VOICE}[o]"
run(f'ffmpeg -v error -y {ins} -filter_complex "{fc}" -map "[o]" -ar 48000 -ac 2 work/voice_pre.wav')
r = subprocess.run("ffmpeg -i work/voice_pre.wav -af ebur128 -f null -", shell=True, capture_output=True, text=True).stderr
I = float([l for l in r.splitlines() if " I:" in l][-1].split()[1])
run(f'ffmpeg -v error -y -i work/voice_pre.wav -af "volume={-14.5-I:.2f}dB,alimiter=limit=0.89" work/voice.wav')
print("voice", I, "->", -14.5)

# ---- captions: (clip index, start, end, text). *word* = gold keyword, ~word~ = italic serif accent ----
LINES = [
    (0, 0.24, 2.20, "Ramai ingat bila dah pakai *braces*"),
    (0, 2.20, 3.40, "dah boleh ~santai~ je."),
    (0, 3.94, 4.80, "Sebenarnya *tak.*"),
    (0, 5.08, 7.50, "*Appointment* pun sangat ~penting~ tau."),
    (0, 7.60, 8.80, "Apa yang perlu you all tahu"),
    (0, 8.80, 9.90, "bila datang ke *klinik.*"),
    (0, 10.14, 12.38, "*Pertama,* check ~pergerakan gigi.~"),
    (0, 12.84, 14.95, "*Kedua,* adjust braces juga perlu"),
    (0, 15.24, 16.30, "dan semestinya"),
    (0, 16.30, 18.44, "rawatan berjalan dengan ~baik~ lah."),
    (0, 18.60, 20.40, "So, jangan *skip appointment* ye."),
    (1, 0.05, 1.27, "Dengan *I-SIHAT* ni,"),
    (1, 1.27, 3.05, "kita ada banyak *branch*"),
    (1, 3.05, 4.95, "di ~Lembah Klang.~"),
    (1, 5.37, 7.11, "Jadi korang boleh pilih"),
    (1, 7.11, 8.80, "*cawangan* yang ~dekat,~"),
    (1, 8.87, 11.60, "supaya senang nak datang *appointment.*"),
    (2, 0.05, 1.97, "Kalau korang nak pasang *braces*"),
    (2, 1.97, 2.90, "atau nak ~konsultasi,~"),
    (2, 2.90, 4.30, "*WhatsApp* kami sekarang."),
]
lines = []
for ci, a, b, text in LINES:
    c, ca, cb = CLIPS[ci]
    s0 = offs[ci] + a - ca if ci == 0 else offs[ci] + a
    s1 = offs[ci] + b - ca if ci == 0 else offs[ci] + b
    toks = text.split()
    # parse markers spanning several words
    out, mode = [], ""
    for tok in toks:
        if tok.startswith("*"): mode = "key"; tok = tok[1:]
        elif tok.startswith("~"): mode = "serif"; tok = tok[1:]
        cur = mode
        end = False
        if tok.endswith("*") or tok.rstrip(".,?").endswith("*"):
            tok = tok.replace("*", ""); end = True
        if tok.endswith("~") or tok.rstrip(".,?").endswith("~"):
            tok = tok.replace("~", ""); end = True
        out.append({"t": tok, "style": cur})
        if end: mode = ""
    n = len(out)
    for k, w in enumerate(out):
        w["s"] = round(s0 + (s1 - s0) * 0.85 * k / max(n, 1), 3)
    lines.append({"s": round(s0, 3), "e": round(s1, 3), "words": out})
# split long lines so each caption fits on one line (<= 24 chars)
split = []
for l in lines:
    txt = " ".join(w["t"] for w in l["words"])
    if len(txt) <= 24 or len(l["words"]) < 3:
        split.append(l); continue
    best, bi = 1e9, 1
    for k in range(1, len(l["words"])):
        left = len(" ".join(w["t"] for w in l["words"][:k]))
        if abs(left - len(txt) / 2) < best: best, bi = abs(left - len(txt) / 2), k
    w2 = l["words"][bi:]
    split.append({"s": l["s"], "e": w2[0]["s"], "words": l["words"][:bi]})
    split.append({"s": w2[0]["s"], "e": l["e"], "words": w2})
lines = split
for i, l in enumerate(lines):  # hold each line until the next starts (max +0.4s)
    nxt = lines[i + 1]["s"] if i + 1 < len(lines) else SPEECH
    l["e"] = round(min(max(l["e"], l["s"] + 0.6) + 0.35, nxt), 3)
json.dump({"speech": SPEECH, "offs": offs, "lines": lines}, open(P + "captions.json", "w"), indent=1)
for l in lines: print(f'{l["s"]:6.2f}-{l["e"]:6.2f} ' + " ".join((w["t"] + ("*" if w["style"] == "key" else "~" if w["style"] == "serif" else "")) for w in l["words"]))
print("speech", SPEECH, "offs", offs)

# ---- logo (from the I-SIHAT kit) ----
Image.open("/home/user/isihat/brand/logo_isihat.png").save(P + "logo.png")
lg = Image.open("/home/user/isihat/brand/logo_isihat.png").convert("RGBA")
lg.crop((0, 0, int(lg.height * 0.78), lg.height)).save(P + "tooth.png")  # tooth mark only
