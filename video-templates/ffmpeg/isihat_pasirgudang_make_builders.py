# Generates the two Pasir Gudang builders from the Setapak builder (single continuous clip, time-based pills, RNNoise voice).
import re
BASE = open("/home/user/isihat_setapak/build_setapak.py").read()

CONFIGS = {
    "qna": dict(
        clip="qna", span=(0.25, 57.70), endbg=40.0,
        hook=('["Anda tanya,"]', '["Doktor jawab!"]'),
        pills='''[(4.36, 12.6, "Q1", "Apa fungsi braces?"), (12.76, 21.4, "Q2", "Berapa lama pakai braces?"),
         (22.48, 37.3, "Q3", "Sakit ke masa pasang?"), (37.52, 48.8, "Q4", "Boleh walk in ke?"),
         (49.04, 57.5, "Q5", "Bayaran macam mana?")]''',
        end=("Ada soalan braces?", "WhatsApp kami dulu."),
        fix="{51.76: \"I-SIHAT\"}",
        out="ISIHAT_PasirGudang_Braces_QnA_v1.mp4"),
    "pg": dict(
        clip="pg", span=(0.0, 67.30), endbg=20.0,
        hook=('["3 salah faham"]', '["tentang braces!"]'),
        pills='''[(6.94, 10.1, "1", "Braces untuk budak je?"), (10.14, 21.2, "1", "Dewasa pun boleh pakai!"),
         (21.36, 24.95, "2", "Lepas pasang tak perlu datang?"), (25.02, 42.6, "2", "Kena datang setiap bulan!"),
         (43.10, 46.9, "3", "Tak perlu retainer?"), (47.18, 59.7, "3", "Retainer paling penting!"),
         (60.0, 67.2, "WA", "WhatsApp untuk tanya")]''',
        end=("Ada soalan braces?", "Doktor sedia bantu."),
        fix="{15.68: \"gusi\", 23.2: \"pasang\", 22.8: \"lepas\", 41.02: \"progress\", 64.18: \"I-SIHAT.\"}",
        out="ISIHAT_PasirGudang_Braces_3SalahFaham_v1.mp4"),
}

def build(name, c):
    s = BASE
    def rep(a, b, regex=False):
        nonlocal s
        if regex:
            s2 = re.sub(a, b, s, count=1, flags=re.S)
            assert s2 != s, a; s = s2
        else:
            assert a in s, a[:70]; s = s.replace(a, b)
    rep('PHONE = "017-744 6302"   # I-SIHAT WhatsApp (as in the other I-SIHAT videos)', 'PHONE = "017-744 6302"   # I-SIHAT WhatsApp (as in the other I-SIHAT videos)')
    rep(r'SPAN = \(0\.30, 47\.80\).*?\n\]\n', f'''SPAN = {c["span"]}  # one continuous clip
segs = [("{c["clip"]}", {c["span"][0]}, {c["span"][1]}, "w")]
''', regex=True)
    s = s.replace("raw/setapak.mov", f"raw/{c['clip']}.mov").replace("a_setapak.wav", f"a_{c['clip']}.wav")
    rep(f"-ss 48.3 -i raw/{c['clip']}.mov -t {{END_LEN}}", f"-ss {c['endbg']} -i raw/{c['clip']}.mov -t {{END_LEN}}")
    rep(r'h1 = boxed\(\["Metal atau ceramic\?"\]', f'h1 = boxed({c["hook"][0]}', regex=True)
    rep(r'h2 = boxed\(\["Ni beza dia!"\]', f'h2 = boxed({c["hook"][1]}', regex=True)
    rep(r'PILLS = \[\(4\.9.*?\)\]\n', f'PILLS = {c["pills"]}\n', regex=True)
    rep('ctext(660, "Metal atau ceramic?"', f'ctext(660, "{c["end"][0]}"')
    rep('ctext(740, "Doktor bantu pilih."', f'ctext(740, "{c["end"][1]}"')
    rep("I-SIHAT Dental Care · Setapak", "I-SIHAT Dental Care · Pasir Gudang")
    rep('tr = json.load(open("work/transcripts_p.json"))["setapak"]', f'tr = json.load(open("work/transcripts.json"))["{c["clip"]}"]')
    rep(r'FIX = \{0\.67.*?\}', f'FIX = {c["fix"]}', regex=True)
    rep('OUT = "ISIHAT_Setapak_Braces_MetalVsCeramic_v3.mp4"', f'OUT = "{c["out"]}"')
    open(f"build_{name}.py", "w").write(s)
    print("wrote", f"build_{name}.py")

for n, c in CONFIGS.items():
    build(n, c)
