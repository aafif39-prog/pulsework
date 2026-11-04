# I-SIHAT Dental Care (Cheras) - Invisalign talking-head Reel.
# Adapted from the T.LOW template (build2.py): same layout/motion, I-SIHAT branding.
import json, subprocess, os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
HOOK_END = 2.6
END_LEN = 4.0
BANNER_H = 500
BANNER_Y = H - BANNER_H
os.makedirs("work", exist_ok=True)
FD = "/usr/share/fonts/opentype/inter/"
# I-SIHAT brand colours (sampled from the brand poster)
DEEP = (8, 52, 65)       # #083441 headline / outline
GREEN = (10, 75, 55)     # #0A4B37 footer green
TEAL = (46, 156, 147)    # #2E9C93 logo teal
MINT = (198, 238, 205)   # light green
GOLD = (242, 187, 68)    # #F2BB44 headline gold
WHITE = (255, 255, 255)
PHONE = "017-744 6302"   # same WhatsApp as the I-SIHAT Cheras video
SKIP_VIDEO = os.environ.get("SKIP_VIDEO") == "1"

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-3000:]); raise SystemExit(cmd)
def F(name, size): return ImageFont.truetype(FD + name, size)

# ---------------- shots: (clip, in, out, look) ----------------
# look: "w" wide, "z" punch-in 1.12 (hides jump cuts), "push" slow push-in (B-roll), "c" close-up
segs = [  # Shah Alam - Braces Q&A with Dr Khalish
    ("c1", 0.60, 2.85, "w"),    # Q1 read (under hook): Berapa lama kena pakai?
    ("c1", 6.65, 11.00, "z"),   # Ia bergantung pada kes...
    ("c1", 11.45, 15.85, "w"),  # 1-2 tahun
    ("c2", 0.55, 2.40, "w"),    # Q2 Sakit ke pakai braces ni?
    ("c2", 6.60, 12.75, "z"),   # tak ada jarum...
    ("c2", 13.35, 21.45, "w"),  # ngilu 4-5 hari
    ("c2", 21.95, 24.20, "z"),  # gigi dah start bergerak
    ("c4", 1.60, 4.10, "w"),    # Q3 boleh walk in je ke?
    ("c4", 4.30, 11.15, "z"),   # book appointment dulu...
    ("c4", 11.35, 14.70, "w"),  # tak perlu tunggu lama
    ("c5", 3.15, 5.80, "w"),    # Q4 boleh bayar ansuran ke?
    ("c5", 5.85, 13.85, "z"),   # installment plan dari RM150 sebulan
    ("c3", 0.00, 5.05, "stand"),  # Nak pasang braces?... WhatsApp kami.
    ("c3", 5.20, 6.90, "stand"),  # We are ready to help you.
    ("c3", 7.45, 10.40, "stand"), # I'm Dr Khalish. See you guys soon.
]
# timeline position of each segment
tl, t = [], 0.0
for s in segs:
    tl.append((t, t + s[2] - s[1])); t += s[2] - s[1]
END_START = round(t, 3)
TOTAL = END_START + END_LEN
TOP_SUB = set()  # captions always at the bottom of the safe area

grade = "eq=contrast=1.06:brightness=0.015:saturation=1.08,unsharp=5:5:0.4"
SRC_H = 1974      # 464x848 sources scaled to 1080 wide
FACE_Y = 1170     # seated doctor's face (y in the scaled source)
def geo(look, dur):
    if look == "stand":  # standing shot: head is near the top -> shift down 330px, blurred fill behind
        return (f"scale={W}:-2,split[a][b];[a]crop={W}:{H}:0:0,gblur=sigma=30,eq=brightness=-0.12[bg];"
                f"[b]crop={W}:{H-330}:0:0[fg];[bg][fg]overlay=0:330")
    z, target = (1.35, 840) if look == "w" else (1.55, 830)  # seated: zoom so the face sits at y~830
    ch_ = int(H / z) // 2 * 2; cw_ = int(W / z) // 2 * 2
    y0 = int(max(0, min(FACE_Y - target / z, SRC_H - ch_)))
    return f"scale={W}:-2,crop={cw_}:{ch_}:(iw-ow)/2:{y0},scale={W}:{H}:flags=lanczos"

if not SKIP_VIDEO:
    # 1) clean each clip's voice once, so cuts share the same processing
    for c in sorted({s[0] for s in segs}):
        run(f"ffmpeg -v error -y -i raw/{c}.mp4 -vn -ac 1 -ar 48000 "
            f"-af \"highpass=f=80,afftdn=nf=-25,loudnorm=I=-18:TP=-2:LRA=9\" work/a_{c}.wav")
    parts, aparts = [], []
    for i, (c, a, b, look) in enumerate(segs):
        d = b - a
        out = f"work/s{i:02d}.mp4"
        run(f"ffmpeg -v error -y -ss {a} -i raw/{c}.mp4 -t {d:.3f} -an -vf \"fps={FPS},{geo(look, d)},setsar=1,{grade},format=yuv420p\" "
            f"-c:v libx264 -preset fast -crf 16 {out}")
        aout = f"work/s{i:02d}.wav"
        run(f"ffmpeg -v error -y -ss {a} -i work/a_{c}.wav -t {d:.3f} -af \"afade=t=in:d=0.02,afade=t=out:st={d-0.04:.3f}:d=0.04\" {aout}")
        parts.append(out); aparts.append(aout)
    # end-card background: blurred last frames of the cost shot
    run(f"ffmpeg -v error -y -ss 9 -i raw/c1.mp4 -t {END_LEN} -an -vf \"fps={FPS},"
        f"{geo('w', END_LEN)},setsar=1,"
        f"gblur=sigma=28,eq=brightness=-0.06:saturation=0.8,format=yuv420p,tpad=stop_mode=clone:stop_duration=4\" "
        f"-t {END_LEN} -c:v libx264 -preset fast -crf 16 work/send.mp4")
    parts.append("work/send.mp4")
    open("work/vlist.txt", "w").write("".join(f"file '{os.path.basename(p)}'\n" for p in parts))
    open("work/alist.txt", "w").write("".join(f"file '{os.path.basename(p)}'\n" for p in aparts))
    run("ffmpeg -v error -y -f concat -safe 0 -i work/vlist.txt -c copy work/base.mp4")
    run("ffmpeg -v error -y -f concat -safe 0 -i work/alist.txt -c copy work/voice.wav")

# ---------------- B-roll cutaways (I-SIHAT footage; clean top area of the Oct-26 braces ads) ----------------
# (timeline start, duration, source, source in, crop x:y:w:h)
BROLL = [
    (4.2, 1.8, "broll/ads_oct26_1.mp4", 17.0, "562:1000:259:0"),   # 3D bracket close-up  - "jenis braces"
    (15.5, 1.9, "broll/ads_oct26_1.mp4", 29.0, "562:1000:259:0"),  # modern braces in mouth - "tak ada jarum"
    (21.0, 2.6, "broll/ads_oct26_1.mp4", 14.1, "562:1000:259:0"),  # smile with metal braces - "ngilu sikit"
    (27.1, 2.25, "broll/ads_oct26_3.mp4", 19.0, "562:1000:259:0"), # brackets moving teeth - "gigi dah start bergerak"
    (32.6, 1.8, "raw/c3.mp4", 12.6, "iw:ih:0:0"),                   # I-SIHAT wall logo - "klinik I-SIHAT"
    (36.3, 1.9, "broll/ads_oct26_1.mp4", 31.0, "562:1000:259:0"),  # digital X-ray / scan - "full consultation"
]
if not SKIP_VIDEO or not os.path.exists("work/base_b.mp4"):
    ins, fcb, last = "", "", "0:v"
    for k, (t0, d, src, sin, crop) in enumerate(BROLL):
        cw_, ch_, cx, cy = crop.split(":")
        geo_b = (f"crop={cw_}:{ch_}:{cx}:{cy}," if crop != "iw:ih:0:0" else "") + \
                f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}"
        run(f"ffmpeg -v error -y -ss {sin} -i {src} -t {d} -an -vf \"fps={FPS},{geo_b},"
            f"scale=w='trunc({W}*(1+0.05*t/{d})/2)*2':h=-2:eval=frame,crop={W}:{H},setsar=1,{grade},format=yuv420p\" "
            f"-c:v libx264 -preset fast -crf 16 work/br{k}.mp4")
        ins += f" -i work/br{k}.mp4"
        fcb += (f"[{k+1}:v]setpts=PTS-STARTPTS+{t0}/TB,format=yuv420p,fade=t=in:st={t0}:d=0.12:alpha=1[b{k}];"
                f"[{last}][b{k}]overlay=0:0:eof_action=pass:enable='between(t,{t0},{t0+d})'[o{k}];")
        last = f"o{k}"
    run(f"ffmpeg -v error -y -i work/base.mp4{ins} -filter_complex \"{fcb[:-1].rsplit('[', 1)[0]}[vb]\" -map \"[vb]\" "
        f"-c:v libx264 -preset fast -crf 16 -pix_fmt yuv420p work/base_b.mp4")

# ---------------- logo ----------------
logo = Image.open("brand/logo_isihat.png").convert("RGBA")
def logo_w(w):
    im = logo.resize((w, int(logo.height * w / logo.width)), Image.LANCZOS)
    r, g, b_, a = im.split()
    a = a.filter(ImageFilter.GaussianBlur(0.6)).point(lambda v: min(255, int(v * 1.15)))
    im = Image.merge("RGBA", (r, g, b_, a))
    return im.filter(ImageFilter.UnsharpMask(radius=1.0, percent=40, threshold=3))

def shadowed(im, blur=14, off=6, alpha=90, pad=30):
    out = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    a = im.split()[3].point(lambda v: v * alpha // 255)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 255)); sh.putalpha(a)
    out.alpha_composite(sh, (pad, pad + off))
    out = out.filter(ImageFilter.GaussianBlur(blur))
    out.alpha_composite(im, (pad, pad))
    return out

def card(lw, px_, py_, radius):
    lg = logo_w(lw)
    im = Image.new("RGBA", (lg.width + 2 * px_, lg.height + 2 * py_), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius, fill=(255, 255, 255, 245))
    im.alpha_composite(lg, (px_, py_))
    return shadowed(im)
card(260, 26, 18, 26).save("work/logo_small.png")

# ---------------- hook (two boxed lines) ----------------
def boxed(lines, font, size, fg, bg, padx=34, pady=18, gap=6, radius=22):
    f = F(font, size)
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    boxes = []
    for s in lines:
        l, t_, r, b = tmp.textbbox((0, 0), s, font=f)
        boxes.append((s, r - l, l))
    asc, desc = f.getmetrics()
    lh = asc + desc - 6
    wmax = max(b[1] for b in boxes) + 2 * padx
    hh = len(lines) * (lh + 2 * pady) + (len(lines) - 1) * gap
    im = Image.new("RGBA", (wmax, hh), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    y = 0
    for s, tw, l in boxes:
        bw = tw + 2 * padx
        x0 = (wmax - bw) // 2
        d.rounded_rectangle((x0, y, x0 + bw, y + lh + 2 * pady), radius, fill=bg)
        d.text((x0 + padx - l, y + pady - 4), s, font=f, fill=fg)
        y += lh + 2 * pady + gap
    return shadowed(im, blur=16, off=8, alpha=110)

# HOOK TEXT
h1 = boxed(["Anda tanya, Dr Khalish jawab"], "Inter-ExtraBold.otf", 54, DEEP, WHITE)
h2 = boxed(["Edisi BRACES"], "Inter-Black.otf", 92, DEEP, GOLD)
h1.save("work/hook1.png"); h2.save("work/hook2.png")
HOOK1_Y = 380
HOOK2_Y = HOOK1_Y + h1.height - 40

# ---------------- key-point pills (numbered reasons) ----------------
def pill(num, text):
    fn, ft = F("Inter-Black.otf", 50 if len(num) == 1 else 34), F("Inter-ExtraBold.otf", 48)
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    tw = tmp.textlength(text, font=ft)
    hgt = 92; cw = 92
    im = Image.new("RGBA", (int(cw + 28 + tw + 40), hgt), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, im.width - 1, hgt - 1), hgt // 2, fill=(255, 255, 255, 248))
    d.ellipse((6, 6, cw - 6, hgt - 6), fill=TEAL)
    nw = d.textlength(num, font=fn)
    nb = d.textbbox((0, 0), num, font=fn)
    d.text(((cw - nw) / 2, (hgt - (nb[3] + nb[1])) / 2), num, font=fn, fill=WHITE)
    d.text((cw + 20, 17), text, font=ft, fill=DEEP)
    return shadowed(im, blur=12, off=6, alpha=100, pad=24)
# (segment index the pill starts on, segment index it ends after, number, text)
PILLS = [(0, 2, "Q1", "Berapa lama pakai braces?"), (3, 6, "Q2", "Sakit ke pakai braces?"),
         (7, 9, "Q3", "Boleh walk in ke?"), (10, 11, "Q4", "Boleh bayar ansuran ke?")]
pill_ev = []
for k, (s0, s1, n, txt) in enumerate(PILLS):
    im = pill(n, txt); fn = f"work/pill{k}.png"; im.save(fn)
    pill_ev.append((fn, max(tl[s0][0] + 0.15, HOOK_END + 0.1), tl[s1][1] - 0.1, (W - im.width) // 2, 520))

# ---------------- top banner card (Meta safe zone: y 270-1250) ----------------
# Meta Reels/Stories UI covers the top ~14% and bottom ~35%, so the banner sits under the header.
# Drawn at 3x and downscaled so the rounded edges and the wave strip are anti-aliased.
CW, CH, S = 1000, 250, 3
cw, ch = CW * S, CH * S
def sF(name, size): return F(name, size * S)
m = Image.new("L", (cw, ch), 0)
ImageDraw.Draw(m).rounded_rectangle((0, 0, cw - 1, ch - 1), 30 * S, fill=255)
body = Image.new("RGBA", (cw, ch))
bd = ImageDraw.Draw(body)
for y in range(ch):
    k = y / ch
    c = tuple(int(a + (b - a) * k) for a, b in zip((250, 255, 250), (218, 244, 224)))
    bd.line((0, y, cw, y), fill=c + (255,))
# soft wave strip along the bottom: thin cyan-teal accent, then the green band
def wy(x, base, amp, ph): return base + amp * math.sin(2 * math.pi * x / cw * 1.05 + ph)
poly_a = [(x, wy(x, ch - 30 * S, 7 * S, 0.4)) for x in range(0, cw + 1, 4)] + [(cw, ch), (0, ch)]
poly_b = [(x, wy(x, ch - 20 * S, 6 * S, 0.9)) for x in range(0, cw + 1, 4)] + [(cw, ch), (0, ch)]
grad = Image.new("RGBA", (cw, ch)); gd = ImageDraw.Draw(grad)
for x in range(cw):
    k = x / cw
    gd.line((x, 0, x, ch), fill=tuple(int(a + (b - a) * k) for a, b in zip(TEAL, GREEN)) + (255,))
ma = Image.new("L", (cw, ch), 0); ImageDraw.Draw(ma).polygon(poly_a, fill=110)
mb = Image.new("L", (cw, ch), 0); ImageDraw.Draw(mb).polygon(poly_b, fill=255)
body.paste(grad, (0, 0), ma)
body.paste(grad, (0, 0), mb)
card_im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
card_im.paste(body, (0, 0), m)
d = ImageDraw.Draw(card_im)
hs = 100
while d.textlength("BRACES", font=sF("Inter-Black.otf", hs)) > 520 * S: hs -= 2
d.text((30 * S, 74 * S), "BRACES", font=sF("Inter-Black.otf", hs), fill=DEEP)
bx0, by0, bx1, by1 = 590 * S, 32 * S, 970 * S, 176 * S
d.rounded_rectangle((bx0, by0, bx1, by1), 24 * S, fill=GREEN)
fb = sF("Inter-Black.otf", 40)
for txt, yy, col in (("Dari RM150", by0 + 22 * S, WHITE), ("sebulan", by0 + 76 * S, GOLD)):
    d.text(((bx0 + bx1 - d.textlength(txt, font=fb)) / 2, yy), txt, font=fb, fill=col)
card_im = card_im.resize((CW, CH), Image.LANCZOS)
card_im.alpha_composite(logo_w(200), (34, 20))
# thin light rim so the card edge reads cleanly on busy backgrounds
rim = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
ImageDraw.Draw(rim).rounded_rectangle((S, S, cw - 1 - S, ch - 1 - S), 30 * S, outline=(255, 255, 255, 170), width=2 * S)
card_im.alpha_composite(rim.resize((CW, CH), Image.LANCZOS))
bn = shadowed(card_im, blur=16, off=8, alpha=110, pad=30)
bn.save("work/banner.png")
BANNER_X, BANNER_Y = (W - bn.width) // 2, 262 - 30

# ---------------- end card ----------------
ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dr = ImageDraw.Draw(ov)
dr.rectangle((0, 0, W, H), fill=(6, 40, 44, 140))
big = card(520, 52, 40, 44)
ov.alpha_composite(big, ((W - big.width) // 2, 290))
def ctext(y, s, size, font="Inter-Bold.otf", fill=WHITE):
    f = F(font, size); w = dr.textlength(s, font=f)
    dr.text(((W - w) / 2, y), s, font=f, fill=fill)
ctext(660, "Nak pasang braces?", 64, "InterDisplay-ExtraBold.otf")
ctext(740, "Book konsultasi dulu.", 64, "InterDisplay-ExtraBold.otf")
ctext(840, "Braces dari RM150 sebulan", 42, "Inter-Bold.otf", GOLD)
f = F("Inter-Bold.otf", 42); f2 = F("Inter-Black.otf", 54)
s1, s2 = "WhatsApp untuk book", PHONE
w1, w2 = dr.textlength(s1, font=f), dr.textlength(s2, font=f2)
pw_ = max(w1, w2) + 120; x0 = (W - pw_) / 2
dr.rounded_rectangle((x0, 920, x0 + pw_, 1080), 40, fill=GOLD)
dr.text(((W - w1) / 2, 938), s1, font=f, fill=DEEP)
dr.text(((W - w2) / 2, 996), s2, font=f2, fill=DEEP)
ctext(1110, "I-SIHAT Dental Care · Shah Alam", 38, "Inter-SemiBold.otf")
ctext(1160, "Kuala Lumpur  ·  Selangor  ·  Johor Bahru", 32, "Inter-Medium.otf", (215, 235, 230))
ctext(1208, "Follow untuk lebih tips gigi", 34, "Inter-SemiBold.otf", GOLD)
ov.save("work/endcard.png")

# ---------------- subtitles ----------------
tr = json.load(open("work/transcripts.json"))
# fix misheard / unclear words: (clip, original) -> replacement ("" drops the word)
fix = {("c1", "Anggaranya"): "Anggarannya", ("c2", "pasien"): "patient", ("c2", "nilu"): "ngilu",
       ("c2", "-nilu"): "-ngilu", ("c4", "buka"): "book", ("c5", "hansuran?"): "ansuran?",
       ("c5", "hansuran"): "ansuran", ("c3", "Dr."): "Dr"}
toks = []
for i, (c, a, b, look) in enumerate(segs):
    t0 = tl[i][0]
    for s in tr[c]:
        for w in s["words"]:
            mid = (w["s"] + w["e"]) / 2
            if not (a <= mid < b): continue
            txt = w["w"].strip()
            txt = fix.get((c, txt), txt)
            if not txt:
                toks[-1]["e"] = t0 + min(w["e"], b) - a; continue
            if txt.startswith("-") and toks and toks[-1]["seg"] == i:  # "Cepat" + "-cepat", "4" + "-5", "I" + "-SIHAT"
                toks[-1]["t"] += txt; toks[-1]["e"] = t0 + min(w["e"], b) - a; continue
            toks.append({"t": txt, "s": t0 + max(w["s"], a) - a, "e": t0 + min(w["e"], b) - a, "seg": i})
# chunk: max 4 words, break after punctuation and at shot changes
chunks, cur = [], []
for k, tk in enumerate(toks):
    if cur and (tk["seg"] != cur[-1]["seg"] or len(cur) >= 4 or cur[-1]["t"][-1] in ",.?!"
                or sum(len(x["t"]) + 1 for x in cur) + len(tk["t"]) > 24  # Malay words are long: keep one line
                or tk["s"] - cur[-1]["e"] > 0.6):
        chunks.append(cur); cur = []
    cur.append(tk)
chunks.append(cur)
# merge a lone trailing word ("ni?", "lain?") into the previous line
merged = []
for c in chunks:
    if merged and len(c) == 1 and c[0]["seg"] == merged[-1][-1]["seg"] and len(merged[-1]) <= 4 and sum(len(x["t"]) + 1 for x in merged[-1] + c) <= 27 \
            and c[0]["s"] - merged[-1][-1]["e"] < 0.6:
        merged[-1] = merged[-1] + c
    else:
        merged.append(c)
chunks = merged

def ts(x): return f"{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}"
hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: SubB,Inter ExtraBold,68,&H00FFFFFF,&H00FFFFFF,&H00413408,&H78000000,0,0,0,0,100,100,0,0,1,5,3,2,90,150,{H-1240},1
Style: SubT,Inter ExtraBold,68,&H00FFFFFF,&H00FFFFFF,&H00413408,&H78000000,0,0,0,0,100,100,0,0,1,5,3,8,90,140,330,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
HL = "&H0044BBF2&"  # gold #F2BB44
ev = []
for ci, ch in enumerate(chunks):
    nxt = chunks[ci + 1][0]["s"] if ci + 1 < len(chunks) else END_START
    segend = tl[ch[-1]["seg"]][1]
    cend = min(ch[-1]["e"] + 0.35, nxt, segend)
    st = "SubB"
    for wi, w in enumerate(ch):
        a = ch[0]["s"] if wi == 0 else w["s"]
        b = ch[wi + 1]["s"] if wi + 1 < len(ch) else cend
        a = max(a, HOOK_END)  # no captions under the hook boxes
        if b <= a: continue
        txt = " ".join((f"{{\\c{HL}}}{x['t']}{{\\c&H00FFFFFF&}}" if j == wi else x["t"]) for j, x in enumerate(ch))
        pop = "{\\fscx92\\fscy92\\t(0,90,\\fscx100\\fscy100)}" if wi == 0 else ""
        ev.append(f"Dialogue: 1,{ts(a)},{ts(b)},{st},,0,0,0,,{pop}{txt}")
open("work/subs.ass", "w").write(hdr + "\n".join(ev) + "\n")
print("\n".join(" ".join(x["t"] for x in ch) for ch in chunks))

# ---------------- composite ----------------
ease_b = f"{BANNER_Y}-60*pow(1-min(max((t-{HOOK_END})/0.5,0),1),3)"
def pop(t0): return f"pow(1-min(max((t-{t0})/0.3,0),1),3)"
inputs = [f"-i work/base_b.mp4", "-i work/logo_small.png",
          f"-loop 1 -framerate {FPS} -t {HOOK_END} -i work/hook1.png",
          f"-loop 1 -framerate {FPS} -t {HOOK_END} -i work/hook2.png",
          f"-loop 1 -framerate {FPS} -t {END_START} -i work/banner.png",
          f"-loop 1 -framerate {FPS} -t {END_LEN} -itsoffset {END_START} -i work/endcard.png",
          "-i work/voice.wav", "-i work/music.wav", "-i work/whoosh.wav", "-i work/pop.wav"]
fc = (
    f"[0:v]subtitles=work/subs.ass:fontsdir={FD}[s];"
    f"[1:v]format=rgba,fade=t=out:st={HOOK_END-0.3}:d=0.3:alpha=1[lg];"
    f"[s][lg]overlay=x=(W-w)/2:y=262:enable='lt(t,{HOOK_END})'[a];"
    f"[2:v]format=rgba,fade=t=in:st=0.05:d=0.25:alpha=1,fade=t=out:st={HOOK_END-0.3}:d=0.3:alpha=1[h1];"
    f"[3:v]format=rgba,fade=t=in:st=0.35:d=0.25:alpha=1,fade=t=out:st={HOOK_END-0.3}:d=0.3:alpha=1[h2];"
    f"[a][h1]overlay=x=(W-w)/2:y='{HOOK1_Y}+40*{pop(0.05)}':enable='lt(t,{HOOK_END})'[b];"
    f"[b][h2]overlay=x=(W-w)/2:y='{HOOK2_Y}+40*{pop(0.35)}':enable='lt(t,{HOOK_END})'[c];"
    f"[4:v]format=rgba,fade=t=in:st={HOOK_END}:d=0.35:alpha=1[bn];"
    f"[c][bn]overlay=x={BANNER_X}:y='{ease_b}':enable='between(t,{HOOK_END},{END_START})'[v0];"
)
last = "v0"
for k, (fn, a, b, x, y) in enumerate(pill_ev):
    inputs.append(f"-loop 1 -framerate {FPS} -t {b-a+0.1:.2f} -itsoffset {a:.2f} -i {fn}")
    idx = 10 + k
    fc += (f"[{idx}:v]format=rgba,fade=t=in:st={a:.2f}:d=0.2:alpha=1,fade=t=out:st={b-0.2:.2f}:d=0.2:alpha=1[p{k}];"
           f"[{last}][p{k}]overlay=x={x}:y='{y}+30*{pop(round(a,2))}':enable='between(t,{a:.2f},{b:.2f})'[v{k+1}];")
    last = f"v{k+1}"
fc += f"[5:v]format=rgba,fade=t=in:st={END_START}:d=0.5:alpha=1[ec];[{last}][ec]overlay=0:0:enable='gte(t,{END_START})'[v];"
# SFX: whoosh on hook + banner, pop on each pill
sfx_times = [("w", 0.02), ("w", HOOK_END - 0.1)] + [("p", a) for _, a, _, _, _ in pill_ev] + [("w", END_START - 0.1)]
nw = sum(1 for k, _ in sfx_times if k == "w"); npp = len(sfx_times) - nw
fc += f"[8:a]asplit={nw}" + "".join(f"[w{i}]" for i in range(nw)) + ";"
fc += f"[9:a]asplit={npp}" + "".join(f"[q{i}]" for i in range(npp)) + ";"
sl, wi, pi = [], 0, 0
for kind, at in sfx_times:
    ms = int(at * 1000)
    if kind == "w":
        fc += f"[w{wi}]adelay={ms}|{ms},volume=0.22[x{len(sl)}];"; wi += 1
    else:
        fc += f"[q{pi}]adelay={ms}|{ms},volume=0.20[x{len(sl)}];"; pi += 1
    sl.append(f"[x{len(sl)}]")
fc += "".join(sl) + f"amix=inputs={len(sl)}:normalize=0,aformat=channel_layouts=stereo[sfx];"
fc += (
    f"[6:a]acompressor=threshold=-20dB:ratio=3:attack=5:release=120,"
    f"loudnorm=I=-14.8:TP=-1.5:LRA=9,aresample=44100,aformat=channel_layouts=stereo,asplit=2[vo][vosc];"
    f"[7:a]volume=0.19,aformat=channel_layouts=stereo[mu];"
    f"[mu][vosc]sidechaincompress=threshold=0.04:ratio=4:attack=30:release=400[mud];"
    f"[vo][mud][sfx]amix=inputs=3:duration=longest:normalize=0,alimiter=limit=0.89,"
    f"atrim=0:{TOTAL},afade=t=out:st={TOTAL-1.5}:d=1.5[au]"
)
OUT = "ISIHAT_ShahAlam_Braces_QnA_v2.mp4"
run(f"ffmpeg -v error -y {' '.join(inputs)} -filter_complex \"{fc}\" -map \"[v]\" -map \"[au]\" -t {TOTAL} "
    f"-c:v libx264 -preset medium -crf 18 -profile:v high -pix_fmt yuv420p -r {FPS} "
    f"-c:a aac -b:a 192k -ar 48000 -movflags +faststart {OUT}")
print("done", OUT, TOTAL)
