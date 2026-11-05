# Aesthetic explainer style (Remotion)

A minimal "product explainer" look, first used for I-SIHAT Bukit Jalil (Nov 2026). Everything stays inside the Meta-safe area (y 262–1250).

- **Intro title** (0–3.6s): small grey line, then a huge Inter Black word with the brand mark, then an Instrument Serif italic accent line. Each line blurs in with a stagger.
- **Step progress**: thin 7-segment bar at y≈274 (done = white, current = brand colour filling up), plus a mono pill "STEP 0X / 07" and a mono label.
- **Captions**: one line at a time (≤24 characters), bottom edge at y=1240. Each word blurs in on its own timing. `*word*` = bold gold keyword, `~word~` = Instrument Serif italic.
- **Frosted cards** above the head (y≈372): white at 84% opacity with backdrop blur, radius 32. Mono header with a dot. Rows get selected (teal tint + border + check that pops) on the spoken word. They spring in and blur out.
- **Number tiles**: dashed translucent tiles with serif numerals and mono labels. The active tile fills with teal.
- **Picture-in-picture**: the footage springs from full screen into a rounded card on a dark teal stage. Captions sit under the card, a list card sits below, then it springs back to full screen.
- **End card**: blurred footage under a light frosted wash, logo, big word, serif price, dark WhatsApp pill, mono clinic/branch line.
- **Audio**: template voice chain (fixed gain), clinic music at volume 0.28 with light sidechain ducking, soft pops on cards/selections, whooshes on PiP moves.

Fonts in `public/`: Inter (OTF), Instrument Serif Italic (`@fontsource/instrument-serif`, woff2), JetBrains Mono (`mono.ttf`).
Workflow: `python3 prep.py` (footage, voice, captions.json), then `MUSIC_DUR=<len> python3 music_sfx.py`, then render muted with Remotion and mix with ffmpeg (see ../README.md).
