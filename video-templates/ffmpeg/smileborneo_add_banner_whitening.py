# Smile Borneo - add a Meta-safe top banner (from the Nov-26 static) to an already-edited video.
import subprocess, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

W, H = 1080, 1920
SRC, OUT = "raw/video.mp4", "SmileBorneo_Whitening_VideoAds_NOV26_MetaSafe.mp4"
B_IN, B_OUT = 0.4, 49.3           # banner on screen (video's own logo end screen starts ~49.4s)
SAFE_TOP = 262
FD = "/usr/share/fonts/opentype/inter/"
GREEN = (3, 82, 76)      # #03524C headline green
PINK = (242, 127, 156)   # #F27F9C price box
PINK2 = (232, 101, 138)
YELLOW = (247, 212, 26)  # #F7D41A footer yellow
WHITE = (255, 255, 255)
def F(n, s): return ImageFont.truetype(FD + n, s)
def run(c): subprocess.run(c, shell=True, check=True)

# ---- logo cut-out (white background removed) ----
st = Image.open("raw/static.jpg").convert("RGB")
lg = st.crop((398, 22, 672, 108))
a = np.asarray(lg).astype(float)
mn = a.min(2)
alpha = np.clip((250 - mn) / 45, 0, 1)
rgb = np.where(alpha[..., None] > 0.02, (a - 255 * (1 - alpha[..., None])) / np.maximum(alpha[..., None], 1e-3), a)
logo = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype(np.uint8), "RGBA")
logo = logo.crop(logo.getbbox())
def logo_w(w):
    return logo.resize((w, int(logo.height * w / logo.width)), Image.LANCZOS)

def shadowed(im, blur=16, off=8, alpha=110, pad=30):
    out = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 255)); sh.putalpha(im.split()[3].point(lambda v: v * alpha // 255))
    out.alpha_composite(sh, (pad, pad + off)); out = out.filter(ImageFilter.GaussianBlur(blur))
    out.alpha_composite(im, (pad, pad)); return out

# ---- banner card, drawn at 3x ----
CW, CH, S = 1000, 250, 3
cw, ch = CW * S, CH * S
def sF(n, s): return F(n, s * S)
mask = Image.new("L", (cw, ch), 0)
ImageDraw.Draw(mask).rounded_rectangle((0, 0, cw - 1, ch - 1), 30 * S, fill=255)
body = Image.new("RGBA", (cw, ch)); bd = ImageDraw.Draw(body)
for y in range(ch):
    k = y / ch
    bd.line((0, y, cw, y), fill=tuple(int(a + (b - a) * k) for a, b in zip((255, 255, 255), (222, 245, 241))) + (255,))
def wy(x, base, amp, ph): return base + amp * math.sin(2 * math.pi * x / cw * 1.05 + ph)
for poly_base, amp, ph, col, al in ((ch - 30 * S, 7 * S, 0.4, YELLOW, 120), (ch - 20 * S, 6 * S, 0.9, YELLOW, 255)):
    m = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(m).polygon([(x, wy(x, poly_base, amp, ph)) for x in range(0, cw + 1, 4)] + [(cw, ch), (0, ch)], fill=al)
    body.paste(Image.new("RGBA", (cw, ch), col + (255,)), (0, 0), m)
card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0)); card.paste(body, (0, 0), mask)
d = ImageDraw.Draw(card)
# top row: headline on the right of the logo (logo pasted after downscale)
d.text((970 * S, 46 * S), "TEETH WHITENING", font=sF("Inter-Black.otf", 40), fill=GREEN, anchor="rm")
# left: price block (the hero)
px0, py0, px1, py1 = 26 * S, 84 * S, 440 * S, 214 * S
d.rounded_rectangle((px0, py0, px1, py1), 24 * S, fill=PINK2)
fp, fr, fc = sF("Inter-Black.otf", 74), sF("Inter-Black.otf", 34), sF("Inter-ExtraBold.otf", 24)
pw, rw, cw2 = d.textlength("269", font=fp), d.textlength("RM", font=fr), d.textlength("/cycle", font=fc)
x = (px0 + px1 - (rw + 8 * S + pw + 8 * S + cw2)) / 2
d.text((x, py0 + 38 * S), "RM", font=fr, fill=WHITE); x += rw + 8 * S
d.text((x, py0 + 20 * S), "269", font=fp, fill=WHITE); x += pw + 8 * S
d.text((x, py0 + 54 * S), "/cycle", font=fc, fill=WHITE)
# right: perks checklist (2 x 2)
perks = ["Scaling & polishing", "Cleaner teeth", "Healthier gums", "Fresher breath"]
fpk = sF("Inter-ExtraBold.otf", 22)
cx0, cy0, colw, rowh = 462 * S, 100 * S, 272 * S, 58 * S
for i, p in enumerate(perks):
    x = cx0 + (i % 2) * colw; y = cy0 + (i // 2) * rowh
    r = 15 * S
    d.ellipse((x, y, x + 2 * r, y + 2 * r), fill=GREEN)
    d.line([(x + 8 * S, y + 15 * S), (x + 13 * S, y + 21 * S), (x + 23 * S, y + 9 * S)], fill=YELLOW, width=4 * S, joint="curve")
    d.text((x + 2 * r + 10 * S, y + r), p, font=fpk, fill=GREEN, anchor="lm")
rim = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
ImageDraw.Draw(rim).rounded_rectangle((S, S, cw - 1 - S, ch - 1 - S), 30 * S, outline=(255, 255, 255, 170), width=2 * S)
card.alpha_composite(rim)
card = card.resize((CW, CH), Image.LANCZOS)
card.alpha_composite(logo_w(210), (28, 20))
bn = shadowed(card)
bn.save("work/banner.png")
BX, BY = (W - bn.width) // 2, SAFE_TOP - 30

# ---- composite: drop in + fade, out before the logo end screen; audio untouched ----
dur = B_OUT - B_IN
ease = f"{BY}-60*pow(1-min(max((t-{B_IN})/0.5,0),1),3)"
SHIFT = 200
fc = (f"[0:v]split[a][b];[a]gblur=sigma=30,eq=brightness=-0.1[bg];[b]crop={W}:{H-SHIFT}:0:0[fg];[bg][fg]overlay=0:{SHIFT}[sh];"
      f"[1:v]format=rgba,fade=t=in:st={B_IN}:d=0.35:alpha=1,fade=t=out:st={B_OUT-0.35}:d=0.35:alpha=1[bn];"
      f"[sh][bn]overlay=x={BX}:y='{ease}':enable='between(t,{B_IN},{B_OUT})'[v]")
run(f"ffmpeg -v error -y -i {SRC} -loop 1 -framerate 30 -t {B_OUT} -i work/banner.png -filter_complex \"{fc}\" "
    f"-map \"[v]\" -map 0:a -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -c:a copy -movflags +faststart {OUT}")
print("done", OUT)
