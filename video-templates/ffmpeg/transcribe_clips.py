import json, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8")
res = {}
for c in ["7170","7179","7180","7181","7182"]:
    subprocess.run(f"ffmpeg -v error -y -i raw/{c}.MOV -ac 1 -ar 16000 -f s16le work/{c}.pcm", shell=True, check=True)
    a = np.fromfile(f"work/{c}.pcm", dtype=np.int16).astype(np.float32)/32768
    print("==", c, "rms", float(np.sqrt((a**2).mean())))
    segs, info = m.transcribe(a, word_timestamps=True, vad_filter=True, language="en", initial_prompt="Invisalign clear aligners at I-SIHAT Dental Care. Trays, attachments, braces.")
    out=[]
    for s in segs:
        print(f"[{s.start:.2f}-{s.end:.2f}] {s.text}")
        out.append({"start":s.start,"end":s.end,"text":s.text,"words":[{"w":w.word,"s":w.start,"e":w.end} for w in s.words]})
    res[c]=out
json.dump(res, open("work/transcripts.json","w"), indent=1)
