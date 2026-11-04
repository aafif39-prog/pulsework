# Smile Borneo - add a Meta-safe top banner (from the Nov-26 static) to an already-edited video.
import subprocess, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

W, H = 1080, 1920
SRC, OUT = "raw/video.mp4", "SmileBorneo_Braces_VideoAds_NOV26_MetaSafe.mp4"
B_IN, B_OUT = 0.4, 33.57          # banner on screen (video's own logo end screen starts at 33.57s)
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
lg = st.crop((405, 20, 680, 108))
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
CW, CH, S = 1000, 240, 3
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
# left: headline
d.text((30 * S, 74 * S), "BRACES", font=sF("Inter-Black.otf", 72), fill=GREEN)
d.text((34 * S, 164 * S), "Conventional braces", font=sF("Inter-Bold.otf", 24), fill=GREEN)
# right: two price boxes (as in the static)
x0, x1 = 455 * S, 972 * S
def pricebox(y0, y1, fill, small, price, small_col, price_col, note=None):
    d.rounded_rectangle((x0, y0, x1, y1), 22 * S, fill=fill)
    fs, fr, fp = sF("Inter-ExtraBold.otf", 19), sF("Inter-Black.otf", 26), sF("Inter-Black.otf", 50)
    # small label on the left, "RM" + number on the right
    ty = y0 + (y1 - y0) // 2
    lines = small.split("\n")
    lh = 22 * S
    sy = ty - lh * len(lines) // 2 - (9 * S if note else 0)
    for i, l in enumerate(lines):
        d.text((x0 + 22 * S, sy + i * lh), l, font=fs, fill=small_col)
    pw = d.textlength(price, font=fp); rw = d.textlength("RM", font=fr)
    px = x1 - 22 * S - pw
    d.text((px, ty - 32 * S - (8 * S if note else 0)), price, font=fp, fill=price_col)
    d.text((px - rw - 6 * S, ty - 26 * S - (8 * S if note else 0)), "RM", font=fr, fill=price_col)
    if note:
        fn = sF("Inter-Bold.otf", 16)
        d.text(((x0 + x1) / 2, y1 - 23 * S), note, font=fn, fill=WHITE, anchor="ma")
pricebox(20 * S, 98 * S, GREEN, "BOOKING\nDEPOSIT", "199", WHITE, WHITE)
pricebox(106 * S, 208 * S, PINK2, "FULL PAYMENT\nFROM", "3899", WHITE, WHITE, note="Includes 10% off, scaling & retainer")
rim = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
ImageDraw.Draw(rim).rounded_rectangle((S, S, cw - 1 - S, ch - 1 - S), 30 * S, outline=(255, 255, 255, 170), width=2 * S)
card.alpha_composite(rim)
card = card.resize((CW, CH), Image.LANCZOS)
card.alpha_composite(logo_w(205), (30, 18))
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
