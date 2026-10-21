#!/usr/bin/env python3
"""V50.2 spoken-Russian import test: 24 deterministic mock WAV clips.
Sine-wave TEST fixtures are not actor voices and are not released as such.
"""
import argparse,json,math,subprocess,sys,tempfile,wave,struct
from pathlib import Path
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--project",required=True)
    p.add_argument("--program",default="scripts/postprocess_v502.py")
    a=p.parse_args()
    src=Path(a.project).resolve()
    before=src.read_bytes()
    with tempfile.TemporaryDirectory(prefix="anime_voice_qa_") as tmp:
        root=Path(tmp)
        voices=root/"voices";voices.mkdir()
        for ep in (1,2):
            for scene in range(1,7):
                for line in (1,2):
                    filename=voices/f"e{ep:02d}_s{scene:02d}_l{line:02d}.wav"
                    n=16000 # 1.0 second WAV, unique tones only for test
                    rate=16000
                    with wave.open(str(filename),"wb") as w:
                        w.setframerate(rate);w.setnchannels(1);w.setsampwidth(2)
                        frames=bytes().join(struct.pack("<h",int(
                          10000*math.sin(2*math.pi*(220+ep*20+scene*11+line*5)*i/rate)))
                            for i in range(n))
                        w.writeframes(frames)
        output=root/"project_licensed_RU_NOT_REAL.json"
        cp=subprocess.run([sys.executable,a.program,"--project",str(src),
                           "--output",str(output),"--actor-voices",
                           str(voices),"--no-foley"],capture_output=True,text=True,
                          timeout=180)
        assert cp.returncode==0,cp.stderr[-2200:]
        obj=json.loads(output.read_text(encoding="utf-8"))
        assert obj["v502Director"]["voiceMode"]=="recorded"
        for e in obj["episodes"][:2]:
            for s in e["scenes"]:
                voice=s["audioV36"]["voice"]
                assert voice["actingStatusV501"]=="ACTOR_RECORDINGS_RIGHTS_PENDING"
                seg=voice["segmentsV501"]
                assert len(seg)==2 and seg[0]["end"]<seg[1]["start"],seg
                assert s["subtitlesV37"]["cues"][0]["start"]==.25
                assert voice["embeddedV47"].startswith("data:audio/mpeg;base64,")
        assert src.read_bytes()==before,"Original V50.1 file mutated!"
        print("PASS: 24 WAV placeholders handled, timed Russian dubbing, original file unchanged.")
if __name__=="__main__":main()
