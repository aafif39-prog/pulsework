# T.LOW "First Braces Appointment" - Meta-safe layout (v4).
# Same edit as build2.py; graphics moved into the Meta Reels/Stories safe area:
#   Meta UI covers the top ~14% (y<270) and bottom ~35% (y>1250) -> all text/graphics live in y 262..1250.
#   Banner = compact card at the top (drawn at 3x and downscaled for smooth edges).
import json, subprocess, os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
END_START, TOTAL = 38.7, 45.0
HOOK_END = 2.7
SAFE_TOP, SAFE_BOTTOM = 262, 1240
os.makedirs("work", exist_ok=True)
FD = "/usr/share/fonts/opentype/inter/"
NAVY = (12, 35, 84); BLUE = (21, 94, 214); CYAN = (40, 190, 210); LIME = (198, 232, 58); WHITE = (255, 255, 255)
PHONE = "+60 17 613 9754"
SKIP_VIDEO = os.environ.get("SKIP_VIDEO") == "1"

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-2000:]); raise SystemExit(cmd)
def F(name, size): return ImageFont.truetype(FD + name, size)

# ---------------- shots (unchanged from build2.py) ----------------
cuts = [
    (0.0, 2.7, "155823", 1.0, "c"), (2.7, 5.26, "160005", 1.0, "b"), (5.26, 7.9, "155823", 5.0, "c"),
    (7.9, 10.0, "160321", 2.8, "c"), (10.0, 12.45, "160005", 6.0, "b"), (12.45, 16.43, "160728", 0.0, "b"),
    (16.43, 18.5, "160728", 5.0, "b"), (18.5, 20.8, "160728", 7.5, "b"), (20.8, 22.8, "160710", 0.3, "land"),
    (22.8, 25.2, "160955", 1.0, "b"), (25.2, 28.86, "161452", 1.0, "b"), (28.86, 32.66, "161530", 1.0, "b"),
    (32.66, 36.0, "161452", 6.0, "b"), (36.0, END_START, "160005", 11.0, "b"),
]
grade = "eq=contrast=1.06:brightness=0.015:saturation=1.08,unsharp=5:5:0.4"
if not SKIP_VIDEO:
    parts = []
    for i, (a, b, src, sin, fr) in enumerate(cuts):
        if fr == "land":
            geo = "scale=-2:2208,crop=1080:1920:2391:150"
        else:
            y = "ih-oh" if fr == "b" else "(ih-oh)/2"
            geo = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}:(iw-ow)/2:{y}"
        out = f"work/q{i:02d}.mp4"
        run(f"ffmpeg -v error -y -ss {sin} -i raw/{src}.mp4 -t {b-a:.3f} -an -vf \"fps={FPS},{geo},setsar=1,{grade},format=yuv420p\" "
            f"-c:v libx264 -preset fast -crf 16 {out}")
        parts.append(out)
    d = TOTAL - END_START
    run(f"ffmpeg -v error -y -ss 4 -i raw/160005.mp4 -t {d:.3f} -an -vf \"fps={FPS},"
        f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,"
        f"gblur=sigma=28,eq=brightness=-0.06:saturation=0.8,format=yuv420p\" "
        f"-c:v libx264 -preset fast -crf 16 work/qend.mp4")
    parts.append("work/qend.mp4")
    open("work/list2.txt", "w").write("".join(f"file '{os.path.basename(p)}'\n" for p in parts))
    run("ffmpeg -v error -y -f concat -safe 0 -i work/list2.txt -c copy work/base2.mp4")

# ---------------- logo (white background removed) ----------------
logo = Image.open("brand/logo_crop.png").convert("RGBA")
px = logo.load()
for y in range(logo.height):
    for x in range(logo.width):
        r, g, b_, a = px[x, y]
        m = min(r, g, b_)
        if m > 235: px[x, y] = (r, g, b_, 0)
        elif m > 200: px[x, y] = (r, g, b_, int(255 * (235 - m) / 35))
logo = logo.crop(logo.getbbox())
logo.save("work/logo.png")
def logo_w(w): return logo.resize((w, int(logo.height * w / logo.width)), Image.LANCZOS)

def shadowed(im, blur=14, off=6, alpha=90, pad=30):
    out = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    a = im.split()[3].point(lambda v: v * alpha // 255)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 255)); sh.putalpha(a)
    out.alpha_composite(sh, (pad, pad + off))
    out = out.filter(ImageFilter.GaussianBlur(blur))
    out.alpha_composite(im, (pad, pad))
    return out

def card(lw, px_, py_, radius, S=3):
    lg = logo_w(lw)
    w, h = lg.width + 2 * px_, lg.height + 2 * py_
    big = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    ImageDraw.Draw(big).rounded_rectangle((0, 0, w * S - 1, h * S - 1), radius * S, fill=(255, 255, 255, 245))
    im = big.resize((w, h), Image.LANCZOS)
    im.alpha_composite(lg, (px_, py_))
    return shadowed(im)
card(230, 24, 14, 24).save("work/logo_small.png")

# ---------------- hook (two boxed lines) ----------------
def boxed(lines, font, size, fg, bg, padx=34, pady=18, gap=6, radius=22, S=3):
    f = F(font, size * S)
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    boxes = []
    for s in lines:
        l, t, r, b = tmp.textbbox((0, 0), s, font=f)
        boxes.append((s, r - l, l))
    asc, desc = f.getmetrics()
    lh = asc + desc - 6 * S
    wmax = max(b[1] for b in boxes) + 2 * padx * S
    hh = len(lines) * (lh + 2 * pady * S) + (len(lines) - 1) * gap * S
    im = Image.new("RGBA", (wmax, hh), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    y = 0
    for s, tw, l in boxes:
        bw = tw + 2 * padx * S
        x0 = (wmax - bw) // 2
        d.rounded_rectangle((x0, y, x0 + bw, y + lh + 2 * pady * S), radius * S, fill=bg)
        d.text((x0 + padx * S - l, y + pady * S - 4 * S), s, font=f, fill=fg)
        y += lh + 2 * pady * S + gap * S
    im = im.resize((wmax // S, hh // S), Image.LANCZOS)
    return shadowed(im, blur=16, off=8, alpha=110)
h1 = boxed(["Getting braces soon?"], "Inter-ExtraBold.otf", 56, NAVY, WHITE)
h2 = boxed(["Here's what REALLY", "happens on Day 1"], "Inter-Black.otf", 78, NAVY, LIME)
h1.save("work/hook1.png"); h2.save("work/hook2.png")
LOGO_Y = SAFE_TOP - 20
HOOK1_Y = 390
HOOK2_Y = HOOK1_Y + h1.height - 40

# ---------------- top banner card (3x supersampled) ----------------
CW, CH, S = 1000, 300, 3
cw, ch = CW * S, CH * S
def sF(name, size): return F(name, size * S)
mask = Image.new("L", (cw, ch), 0)
ImageDraw.Draw(mask).rounded_rectangle((0, 0, cw - 1, ch - 1), 30 * S, fill=255)
body = Image.new("RGBA", (cw, ch)); bd = ImageDraw.Draw(body)
for y in range(ch):
    k = y / ch
    bd.line((0, y, cw, y), fill=tuple(int(a + (b - a) * k) for a, b in zip((246, 251, 255), (214, 232, 255))) + (255,))
def wy(x, base, amp, ph): return base + amp * math.sin(2 * math.pi * x / cw * 1.05 + ph)
grad = Image.new("RGBA", (cw, ch)); gd = ImageDraw.Draw(grad)
for x in range(cw):
    k = x / cw
    gd.line((x, 0, x, ch), fill=tuple(int(a + (b - a) * k) for a, b in zip(CYAN, BLUE)) + (255,))
ma = Image.new("L", (cw, ch), 0); ImageDraw.Draw(ma).polygon([(x, wy(x, ch - 30 * S, 7 * S, 0.4)) for x in range(0, cw + 1, 4)] + [(cw, ch), (0, ch)], fill=110)
mb = Image.new("L", (cw, ch), 0); ImageDraw.Draw(mb).polygon([(x, wy(x, ch - 20 * S, 6 * S, 0.9)) for x in range(0, cw + 1, 4)] + [(cw, ch), (0, ch)], fill=255)
body.paste(grad, (0, 0), ma); body.paste(grad, (0, 0), mb)
cim = Image.new("RGBA", (cw, ch), (0, 0, 0, 0)); cim.paste(body, (0, 0), mask)
d = ImageDraw.Draw(cim)
# left column - HEADLINE / PRICE: change per campaign
d.text((28 * S, 64 * S), "BRACES", font=sF("Inter-Black.otf", 92), fill=NAVY)
bx0, by0, bx1, by1 = 34 * S, 178 * S, 470 * S, 256 * S
d.rounded_rectangle((bx0, by0, bx1, by1), 20 * S, fill=NAVY)
f_from, f_price, f_mo = sF("Inter-Bold.otf", 24), sF("Inter-Black.otf", 60), sF("Inter-ExtraBold.otf", 28)
fw, pw, mw = d.textlength("FROM", font=f_from), d.textlength("RM150", font=f_price), d.textlength("/month", font=f_mo)
x = bx0 + (bx1 - bx0 - (fw + 14 * S + pw + 10 * S + mw)) / 2
d.text((x, by0 + 30 * S), "FROM", font=f_from, fill=LIME); x += fw + 14 * S
d.text((x, by0 + 6 * S), "RM150", font=f_price, fill=WHITE); x += pw + 10 * S
d.text((x, by0 + 29 * S), "/month", font=f_mo, fill=LIME)
# right column: before / after (cropped from the Sep ad), side by side
src = Image.open("brand/ad.jpg").convert("RGBA")
def photo(box, label, w):
    p = src.crop(box); p = p.resize((w, int(p.height * w / p.width)), Image.LANCZOS)
    fr = Image.new("RGBA", (w + 6 * S, p.height + 6 * S), (0, 0, 0, 0))
    m = Image.new("L", p.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, p.width - 1, p.height - 1), 16 * S, fill=255)
    ImageDraw.Draw(fr).rounded_rectangle((0, 0, fr.width - 1, fr.height - 1), 19 * S, fill=WHITE)
    fr.paste(p, (3 * S, 3 * S), m)
    dd = ImageDraw.Draw(fr); lf = sF("Inter-ExtraBold.otf", 18)
    lw_ = dd.textlength(label, font=lf)
    dd.rounded_rectangle((12 * S, 10 * S, 12 * S + lw_ + 22 * S, 40 * S), 15 * S, fill=LIME if label == "AFTER" else WHITE)
    dd.text((23 * S, 13 * S), label, font=lf, fill=NAVY)
    return fr
pw_ = 236 * S
pb = photo((85, 805, 520, 1075), "BEFORE", pw_)
pa = photo((560, 805, 998, 1075), "AFTER", pw_)
yy = 22 * S
cim.alpha_composite(pb, (cw - 2 * pb.width - 40 * S, yy))
cim.alpha_composite(pa, (cw - pa.width - 26 * S, yy))
rim = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
ImageDraw.Draw(rim).rounded_rectangle((S, S, cw - 1 - S, ch - 1 - S), 30 * S, outline=(255, 255, 255, 170), width=2 * S)
cim.alpha_composite(rim)
cim = cim.resize((CW, CH), Image.LANCZOS)
lg_ = logo_w(140); cim.alpha_composite(lg_, (34, 14))
px_mid = (CW - 2 * pb.width // S - 40 + CW - 26) // 2
ImageDraw.Draw(cim).text((px_mid, 22 + pb.height // S + 12), f"WhatsApp {PHONE}", font=F("Inter-Bold.otf", 26), fill=NAVY, anchor="ma")
bn = shadowed(cim, blur=16, off=8, alpha=110, pad=30)
bn.save("work/banner.png")
BANNER_X, BANNER_Y = (W - bn.width) // 2, SAFE_TOP - 30

# ---------------- end card (fits y 270..1250) ----------------
ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dr = ImageDraw.Draw(ov)
dr.rectangle((0, 0, W, H), fill=(8, 22, 56, 135))
big = card(500, 50, 36, 44)
ov.alpha_composite(big, ((W - big.width) // 2, 285))
def ctext(y, s, size, font="Inter-Bold.otf", fill=WHITE):
    f = F(font, size); w = dr.textlength(s, font=f)
    dr.text(((W - w) / 2, y), s, font=f, fill=fill)
ctext(640, "Your braces journey", 62, "InterDisplay-ExtraBold.otf")
ctext(716, "starts with one visit.", 62, "InterDisplay-ExtraBold.otf")
ctext(808, "Braces from RM150/month", 42, "Inter-Bold.otf", LIME)
f = F("Inter-Bold.otf", 42); f2 = F("Inter-Black.otf", 50)
s1, s2 = "WhatsApp to book", PHONE
w1, w2 = dr.textlength(s1, font=f), dr.textlength(s2, font=f2)
bw_ = max(w1, w2) + 120; x0 = (W - bw_) / 2
btn = Image.new("RGBA", (int(bw_) * 3, 156 * 3), (0, 0, 0, 0))
ImageDraw.Draw(btn).rounded_rectangle((0, 0, btn.width - 1, btn.height - 1), 40 * 3, fill=LIME)
ov.alpha_composite(btn.resize((int(bw_), 156), Image.LANCZOS), (int(x0), 886))
dr.text(((W - w1) / 2, 902), s1, font=f, fill=NAVY)
dr.text(((W - w2) / 2, 960), s2, font=f2, fill=NAVY)
ctext(1072, "www.tlowdentalclinic.com", 38, "Inter-SemiBold.otf")
ctext(1122, "SS2, Petaling Jaya", 34, "Inter-Medium.otf", (215, 225, 240))
ctext(1190, "Follow for more dental tips", 36, "Inter-SemiBold.otf", LIME)
ov.save("work/endcard2.png")

# ---------------- subtitles (bottom edge at y=1240, above Meta's CTA/caption area) ----------------
words = [w for s in json.load(open("transcript.json")) for w in s["words"]]
fix = {"bracket": "brackets", "color.": "colour!", "what's": "WhatsApp", "happens": "us",
       "appointments?": "appointment."}
toks = []
for i, w in enumerate(words):
    t = w["w"].strip()
    if t == "are" and i and words[i - 1]["w"].strip() == "you":
        toks[-1]["t"] = "you're"; continue
    if t == "-ray.":
        toks[-1]["e"] = w["e"]; continue
    if t == "x": t = "X-ray."
    elif t in fix: t = fix[t]
    toks.append({"t": t, "s": w["s"], "e": w["e"]})
toks = [t for t in toks if t["s"] < END_START]
chunks, cur = [], []
for tk in toks:
    if cur and (len(cur) >= 4 or cur[-1]["t"][-1] in ",.?!" or tk["s"] - cur[-1]["e"] > 0.6):
        chunks.append(cur); cur = []
    cur.append(tk)
chunks.append(cur)
def ts(x): return f"{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}"
hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: SubB,Inter ExtraBold,68,&H00FFFFFF,&H00FFFFFF,&H00401A08,&H78000000,0,0,0,0,100,100,0,0,1,5,3,2,90,150,{H-SAFE_BOTTOM},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
HL = "&H00D2BE28&"
ev = []
for ci, ch_ in enumerate(chunks):
    nxt = chunks[ci + 1][0]["s"] if ci + 1 < len(chunks) else END_START
    cend = min(ch_[-1]["e"] + 0.35, nxt)
    for wi, w in enumerate(ch_):
        a = ch_[0]["s"] if wi == 0 else w["s"]
        b = ch_[wi + 1]["s"] if wi + 1 < len(ch_) else cend
        a = max(a, HOOK_END)
        if b <= a: continue
        txt = " ".join((f"{{\\c{HL}}}{x['t']}{{\\c&H00FFFFFF&}}" if j == wi else x["t"]) for j, x in enumerate(ch_))
        pop = "{\\fscx92\\fscy92\\t(0,90,\\fscx100\\fscy100)}" if wi == 0 else ""
        ev.append(f"Dialogue: 1,{ts(a)},{ts(b)},SubB,,0,0,0,,{pop}{txt}")
open("work/subs2.ass", "w").write(hdr + "\n".join(ev) + "\n")
print("\n".join(" ".join(x["t"] for x in c) for c in chunks))

# ---------------- composite ----------------
ease_b = f"{BANNER_Y}-60*pow(1-min(max((t-{HOOK_END})/0.5,0),1),3)"
def pop(t0): return f"pow(1-min(max((t-{t0})/0.3,0),1),3)"
fc = (
    f"[0:v]subtitles=work/subs2.ass:fontsdir={FD}[s];"
    f"[1:v]format=rgba,fade=t=out:st={HOOK_END-0.3}:d=0.3:alpha=1[lg];"
    f"[s][lg]overlay=x=(W-w)/2:y={LOGO_Y}:enable='lt(t,{HOOK_END})'[a];"
    f"[2:v]format=rgba,fade=t=in:st=0.05:d=0.25:alpha=1,fade=t=out:st={HOOK_END-0.3}:d=0.3:alpha=1[h1];"
    f"[3:v]format=rgba,fade=t=in:st=0.35:d=0.25:alpha=1,fade=t=out:st={HOOK_END-0.3}:d=0.3:alpha=1[h2];"
    f"[a][h1]overlay=x=(W-w)/2:y='{HOOK1_Y}+40*{pop(0.05)}':enable='lt(t,{HOOK_END})'[b];"
    f"[b][h2]overlay=x=(W-w)/2:y='{HOOK2_Y}+40*{pop(0.35)}':enable='lt(t,{HOOK_END})'[c];"
    f"[4:v]format=rgba,fade=t=in:st={HOOK_END}:d=0.35:alpha=1[bn];"
    f"[c][bn]overlay=x={BANNER_X}:y='{ease_b}':enable='between(t,{HOOK_END},{END_START})'[d];"
    f"[5:v]format=rgba,fade=t=in:st=0:d=0.5:alpha=1[ec];"
    f"[d][ec]overlay=0:0:enable='gte(t,{END_START})'[v];"
    f"[6:a]highpass=f=80,afftdn=nf=-25,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,"
    f"loudnorm=I=-14:TP=-1.5:LRA=9,aresample=44100,aformat=channel_layouts=stereo,asplit=2[vo][vosc];"
    f"[7:a]volume=0.19,aformat=channel_layouts=stereo[mu];"
    f"[mu][vosc]sidechaincompress=threshold=0.04:ratio=4:attack=30:release=400[mud];"
    f"[vo][mud]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.89,"
    f"atrim=0:{TOTAL},afade=t=out:st={TOTAL-1.5}:d=1.5[au]"
)
hd = HOOK_END
OUT = "TLow_First_Braces_Appointment_v4_MetaSafe.mp4"
run(f"ffmpeg -v error -y -i work/base2.mp4 -i work/logo_small.png "
    f"-loop 1 -framerate {FPS} -t {hd} -i work/hook1.png -loop 1 -framerate {FPS} -t {hd} -i work/hook2.png "
    f"-loop 1 -framerate {FPS} -t {END_START} -i work/banner.png "
    f"-loop 1 -framerate {FPS} -t {TOTAL-END_START} -itsoffset {END_START} -i work/endcard2.png "
    f"-i raw/voiceover.m4a -i work/music.wav "
    f"-filter_complex \"{fc}\" -map \"[v]\" -map \"[au]\" -t {TOTAL} "
    f"-c:v libx264 -preset medium -crf 18 -profile:v high -pix_fmt yuv420p -r {FPS} "
    f"-c:a aac -b:a 192k -ar 48000 -movflags +faststart {OUT}")
print("done", OUT)
