# I-SIHAT Cheras Invisalign - aesthetic style. Reuses the approved cut (base.mp4 + voice.wav) from the Meta-safe build.
import json, shutil, subprocess
P = "rem/public/"
SRC = "/home/user/isihat/"
shutil.copy(SRC + "work/base.mp4", P + "src.mp4")
# voice: re-level to -14.5 LUFS (fixed gain)
r = subprocess.run(f"ffmpeg -i {SRC}work/voice.wav -af ebur128 -f null -", shell=True, capture_output=True, text=True).stderr
I = float([l for l in r.splitlines() if " I:" in l][-1].split()[1])
subprocess.run(f'ffmpeg -v error -y -i {SRC}work/voice.wav -af "highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,volume={-14.5-I:.2f}dB,alimiter=limit=0.89" -ar 48000 -ac 2 work/voice.wav', shell=True, check=True)

segs = [("7181", 0.10, 2.62), ("7181", 3.00, 9.00), ("7170", 0.30, 6.25), ("7170", 6.45, 11.60), ("7182", 0.62, 9.75),
        ("7180", 0.42, 4.75), ("7180", 5.30, 7.00), ("7180", 7.22, 11.15), ("7180", 11.27, 18.22), ("7180", 18.68, 21.86),
        ("7180", 22.30, 29.93), ("7180", 30.05, 32.80), ("7180", 33.25, 39.75), ("7180", 40.25, 44.40), ("7180", 44.70, 48.40),
        ("7179", 0.22, 2.75), ("7179", 3.28, 7.52), ("7179", 7.78, 11.88)]
tl, t = [], 0.0
for c, a, b in segs:
    tl.append(t); t += b - a
SPEECH = round(t, 3)
tr = json.load(open(SRC + "work/transcripts.json"))
fix = {("7180", "doctors"): "doctor", ("7180", "three"): "every 3", ("7180", "six"): "6", ("7180", "months"): "months.", ("7180", "twice."): ""}
KEY = {"invisalign", "invisalign.", "invisalign?", "trays", "trays,", "trays.", "cost", "cost?", "cost.", "teeth.", "braces?"}
SERIF = {"invisible", "aesthetic.", "aesthetic", "anything", "everything", "predictable", "cheaper", "clean", "transparent,", "multiple"}
toks = []
for i, (c, a, b) in enumerate(segs):
    for s in tr[c]:
        for w in s["words"]:
            if not (a <= (w["s"] + w["e"]) / 2 < b): continue
            txt = fix.get((c, w["w"].strip()), w["w"].strip())
            if not txt:
                toks[-1]["e"] = tl[i] + min(w["e"], b) - a; continue
            low = txt.lower()
            style = "key" if low in KEY else "serif" if low.strip(".,?!") in {x.strip(".,?!") for x in SERIF} else ""
            toks.append({"t": txt, "s": round(tl[i] + max(w["s"], a) - a, 3), "e": round(tl[i] + min(w["e"], b) - a, 3), "seg": i, "style": style})
# one-line captions: <= 24 chars, break on punctuation, shot change or pause
lines, cur = [], []
for tk in toks:
    txt = " ".join(x["t"] for x in cur)
    if cur and (tk["seg"] != cur[-1]["seg"] or cur[-1]["t"][-1] in ",.?!" or len(txt) + 1 + len(tk["t"]) > 24 or tk["s"] - cur[-1]["e"] > 0.6):
        lines.append(cur); cur = []
    cur.append(tk)
lines.append(cur)
merged = []
for l in lines:  # glue a lone trailing word ("back.", "months.") onto the line before
    if merged and len(l) == 1 and l[0]["seg"] == merged[-1][-1]["seg"] and merged[-1][-1]["t"][-1] not in ",.?!" \
            and len(" ".join(x["t"] for x in merged[-1] + l)) <= 28:
        merged[-1] = merged[-1] + l
    else:
        merged.append(l)
lines = merged
out = []
for i, l in enumerate(lines):
    nxt = lines[i + 1][0]["s"] if i + 1 < len(lines) else SPEECH
    out.append({"s": l[0]["s"], "e": round(min(l[-1]["e"] + 0.35, nxt), 3), "words": [{"t": w["t"], "s": w["s"], "style": w["style"]} for w in l]})
json.dump({"speech": SPEECH, "tl": tl, "lines": out}, open(P + "captions.json", "w"), indent=1)
for l in out: print(f'{l["s"]:6.2f} ' + " ".join(w["t"] + {"key": "*", "serif": "~"}.get(w["style"], "") for w in l["words"]))
print("speech", SPEECH, "voice", I)
print("tl", [round(x, 2) for x in tl])
