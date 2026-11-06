import shutil
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
PHONE = "017-744 6302"   # I-SIHAT WhatsApp (as in the other I-SIHAT videos)
SKIP_VIDEO = os.environ.get("SKIP_VIDEO") == "1"

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-3000:]); raise SystemExit(cmd)
def F(name, size): return ImageFont.truetype(FD + name, size)

# ---------------- shots: (clip, in, out, look) ----------------
# look: "w" wide, "z" punch-in 1.12 (hides jump cuts), "push" slow push-in (B-roll), "c" close-up
SPAN = (0.25, 57.7)  # one continuous clip
segs = [("qna", 0.25, 57.7, "w")]
# timeline position of each segment
tl, t = [], 0.0
for s in segs:
    tl.append((t, t + s[2] - s[1])); t += s[2] - s[1]
END_START = round(t, 3)
TOTAL = END_START + END_LEN
TOP_SUB = set()  # captions always at the bottom of the safe area

grade = "eq=contrast=1.06:brightness=0.015:saturation=1.08,unsharp=5:5:0.4"
def geo(look, dur):
    base = f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}"
    if look == "w":
        return base
    z, face = look  # zoom so the face lands at y~880
    ch_, cw_ = int(H / z) // 2 * 2, int(W / z) // 2 * 2
    y0 = int(max(0, min(face - 880 / z, H - ch_)))
    return f"{base},crop={cw_}:{ch_}:(iw-ow)/2:{y0},scale={W}:{H}:flags=lanczos"

if not SKIP_VIDEO:
    # 1) clean each clip's voice once, so cuts share the same processing
    for c in sorted({s[0] for s in segs}):
        run(f"ffmpeg -v error -y -i raw/{c}.mov -vn -ac 1 -ar 48000 "
            f"-af \"highpass=f=80,afftdn=nf=-25,loudnorm=I=-18:TP=-2:LRA=9\" work/a_{c}.wav")
    parts, aparts = [], []
    for i, (c, a, b, look) in enumerate(segs):
        d = b - a
        out = f"work/s{i:02d}.mp4"
        run(f"ffmpeg -v error -y -ss {a} -i raw/{c}.mov -t {d:.3f} -an -vf \"fps={FPS},{geo(look, d)},setsar=1,{grade},format=yuv420p\" "
            f"-c:v libx264 -preset fast -crf 16 {out}")
        aout = f"work/s{i:02d}.wav"
        run(f"ffmpeg -v error -y -ss {a} -i work/a_{c}.wav -t {d:.3f} -af \"afade=t=in:d=0.02,afade=t=out:st={d-0.04:.3f}:d=0.04\" {aout}")
        parts.append(out); aparts.append(aout)
    # end-card background: blurred last frames of the cost shot
    run(f"ffmpeg -v error -y -ss 40.0 -i raw/qna.mov -t {END_LEN} -an -vf \"fps={FPS},"
        f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,"
        f"gblur=sigma=28,eq=brightness=-0.06:saturation=0.8,format=yuv420p,tpad=stop_mode=clone:stop_duration=4\" "
        f"-t {END_LEN} -c:v libx264 -preset fast -crf 16 work/send.mp4")
    parts.append("work/send.mp4")
    open("work/vlist.txt", "w").write("".join(f"file '{os.path.basename(p)}'\n" for p in parts))
    open("work/alist.txt", "w").write("".join(f"file '{os.path.basename(p)}'\n" for p in aparts))
    run("ffmpeg -v error -y -f concat -safe 0 -i work/vlist.txt -c copy work/base.mp4")
    VOICE = ("highpass=f=85,aresample=48000,arnndn=m=models/sh.rnnn:mix=0.92,afftdn=nr=8:nf=-45,"
             "equalizer=f=250:t=q:w=1.2:g=-2.5,equalizer=f=3200:t=q:w=1.0:g=3,highshelf=f=9000:g=2,deesser=i=0.35,"
             "acompressor=threshold=-22dB:ratio=2.5:attack=8:release=150:makeup=2,agate=threshold=0.012:range=0.08:ratio=3:attack=5:release=250")
    run(f"ffmpeg -v error -y -i raw/qna.mov -vn -ac 1 -af \"{VOICE}\" -ar 48000 work/a_qna.wav")  # RNNoise voice clean-up
    run(f"ffmpeg -v error -y -ss {SPAN[0]} -i work/a_qna.wav -t {SPAN[1]-SPAN[0]:.3f} -af \"afade=t=out:st={SPAN[1]-SPAN[0]-0.08:.3f}:d=0.08\" work/voice.wav")

# ---------------- B-roll cutaways (I-SIHAT footage; clean top area of the Oct-26 braces ads) ----------------
# (timeline start, duration, source, source in, speed, crop w:h:x:y)
# Each cutaway covers a jump cut in the talking head (hides it), starts/ends on a phrase break,
# never sits on a question read, and dissolves in/out (XF seconds).
XF = 0.35
BROLL = [
]
CARD = None
if not BROLL and not CARD:
    if not SKIP_VIDEO or not os.path.exists("work/base_b.mp4"):
        shutil.copy("work/base.mp4", "work/base_b.mp4")
elif not SKIP_VIDEO or not os.path.exists("work/base_b.mp4"):
    ins, fcb, last = "", "", "0:v"
    for k, (t0, d, src, sin, sp, crop) in enumerate(BROLL):
        cw_, ch_, cx, cy = crop.split(":")
        geo_b = (f"crop={cw_}:{ch_}:{cx}:{cy}," if crop != "iw:ih:0:0" else "") + \
                f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}"
        slow = f"setpts={1/sp:.4f}*PTS,framerate=fps={FPS}:interp_start=0:interp_end=255," if sp != 1.0 else ""
        run(f"ffmpeg -v error -y -ss {sin} -i {src} -t {d*sp+0.1:.2f} -an -vf \"{slow}fps={FPS},{geo_b},"
            f"scale=w='trunc({W}*(1+0.04*t/{d})/2)*2':h=-2:eval=frame,crop={W}:{H},setsar=1,{grade},format=yuv420p\" "
            f"-t {d} -c:v libx264 -preset fast -crf 16 work/br{k}.mp4")
        ins += f" -i work/br{k}.mp4"
        fcb += (f"[{k+1}:v]format=yuva420p,fade=t=in:st=0:d={XF}:alpha=1,fade=t=out:st={d-XF}:d={XF}:alpha=1,"
                f"setpts=PTS-STARTPTS+{t0}/TB[b{k}];"
                f"[{last}][b{k}]overlay=0:0:eof_action=pass:enable='between(t,{t0},{t0+d})'[o{k}];")
        last = f"o{k}"
    t0, d, png, cy = CARD
    k = len(BROLL)
    ins += f" -loop 1 -framerate {FPS} -t {d} -i work/dim.png -loop 1 -framerate {FPS} -t {d} -i {png}"
    fcb += (f"[{k+1}:v]format=yuva420p,fade=t=in:st=0:d={XF}:alpha=1,fade=t=out:st={d-XF}:d={XF}:alpha=1,setpts=PTS-STARTPTS+{t0}/TB[dm];"
            f"[{k+2}:v]format=rgba,scale=w='trunc(iw*(1+0.06*t/{d})/2)*2':h=-2:eval=frame,"
            f"fade=t=in:st=0:d={XF}:alpha=1,fade=t=out:st={d-XF}:d={XF}:alpha=1,setpts=PTS-STARTPTS+{t0}/TB[cd];"
            f"[{last}][dm]overlay=0:0:eof_action=pass:enable='between(t,{t0},{t0+d})'[od];"
            f"[od][cd]overlay=x=(W-w)/2:y={cy}-h/2:eval=frame:eof_action=pass:enable='between(t,{t0},{t0+d})'[oc];")
    last = "oc"
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
h1 = boxed(["Anda tanya,"], "Inter-ExtraBold.otf", 58, DEEP, WHITE)
h2 = boxed(["Doktor jawab!"], "Inter-Black.otf", 78, DEEP, GOLD)
h1.save("work/hook1.png"); h2.save("work/hook2.png")
HOOK1_Y = 365
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
# (start, end, label, text) - key points under the banner
PILLS = [(4.36, 12.6, "Q1", "Apa fungsi braces?"), (12.76, 21.4, "Q2", "Berapa lama pakai braces?"),
         (22.48, 37.3, "Q3", "Sakit ke masa pasang?"), (37.52, 48.8, "Q4", "Boleh walk in ke?"),
         (49.04, 57.5, "Q5", "Bayaran macam mana?")]
pill_ev = []
for k, (a_, b_, n, txt) in enumerate(PILLS):
    im = pill(n, txt); fn = f"work/pill{k}.png"; im.save(fn)
    pill_ev.append((fn, a_ - SPAN[0], b_ - SPAN[0], (W - im.width) // 2, 520))  # PILLS are in source seconds

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
ctext(660, "Ada soalan braces?", 64, "InterDisplay-ExtraBold.otf")
ctext(740, "WhatsApp kami dulu.", 64, "InterDisplay-ExtraBold.otf")
ctext(840, "Braces dari RM150 sebulan", 42, "Inter-Bold.otf", GOLD)
f = F("Inter-Bold.otf", 42); f2 = F("Inter-Black.otf", 54)
s1, s2 = "WhatsApp untuk book", PHONE
w1, w2 = dr.textlength(s1, font=f), dr.textlength(s2, font=f2)
pw_ = max(w1, w2) + 120; x0 = (W - pw_) / 2
dr.rounded_rectangle((x0, 920, x0 + pw_, 1080), 40, fill=GOLD)
dr.text(((W - w1) / 2, 938), s1, font=f, fill=DEEP)
dr.text(((W - w2) / 2, 996), s2, font=f2, fill=DEEP)
ctext(1110, "I-SIHAT Dental Care · Pasir Gudang", 38, "Inter-SemiBold.otf")
ctext(1160, "Kuala Lumpur  ·  Selangor  ·  Johor Bahru", 32, "Inter-Medium.otf", (215, 235, 230))
ctext(1208, "Follow untuk lebih tips gigi", 34, "Inter-SemiBold.otf", GOLD)
ov.save("work/endcard.png")

# ---------------- subtitles ----------------
tr = json.load(open("work/transcripts.json"))["qna"]
FIX = {51.76: "I-SIHAT"}  # by word start time
seg_of = lambda x: max(i for i, (c, a, b, l) in enumerate(segs) if a - 1e-6 <= x)
toks = []
for sg in tr:
    for w in sg["words"]:
        if not (SPAN[0] <= w["s"] < SPAN[1] - 0.2): continue
        txt = FIX.get(round(w["s"], 2), w["w"].strip())
        s_, e_ = w["s"] - SPAN[0], min(w["e"], SPAN[1]) - SPAN[0]
        if txt.startswith("-") and toks:
            toks[-1]["t"] += txt; toks[-1]["e"] = e_; continue
        toks.append({"t": txt, "s": s_, "e": e_, "seg": seg_of(w["s"])})
for i in range(len(toks) - 1):  # don't split captions at shot changes (continuous speech)
    toks[i]["seg"] = 0
toks[-1]["seg"] = 0
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
    segend = END_START  # continuous speech across shots
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
    f"loudnorm=I=-13.0:TP=-1.5:LRA=9,aresample=44100,aformat=channel_layouts=stereo,asplit=2[vo][vosc];"
    f"[7:a]volume=0.30,aformat=channel_layouts=stereo[mu];"
    f"[mu][vosc]sidechaincompress=threshold=0.05:ratio=2.5:attack=40:release=500[mud];"
    f"[vo][mud][sfx]amix=inputs=3:duration=longest:normalize=0,alimiter=limit=0.89,"
    f"atrim=0:{TOTAL},afade=t=out:st={TOTAL-1.5}:d=1.5[au]"
)
OUT = "ISIHAT_PasirGudang_Braces_QnA_v1.mp4"
run(f"ffmpeg -v error -y {' '.join(inputs)} -filter_complex \"{fc}\" -map \"[v]\" -map \"[au]\" -t {TOTAL} "
    f"-c:v libx264 -preset medium -crf 18 -profile:v high -pix_fmt yuv420p -r {FPS} "
    f"-c:a aac -b:a 192k -ar 48000 -movflags +faststart {OUT}")
print("done", OUT, TOTAL)
