"""Optional *real* Russian forced alignment. Never substitute lip-flap for phonemes."""
import argparse
import hashlib
import json
import shutil
import subprocess
import time
import wave
from pathlib import Path


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for part in iter(lambda:f.read(1024*1024),b''):h.update(part)
    return h.hexdigest()


def align(wav,text,out,model='russian_mfa',dictionary='russian_mfa',timeout=900):
    wav=Path(wav).resolve(); text=Path(text).resolve(); out=Path(out).resolve()
    issues=[]
    if not wav.is_file() or wav.suffix.lower()!='.wav': issues.append('valid_WAV_missing')
    if not text.is_file() or text.suffix.lower()!='.txt' or not text.read_text(encoding='utf-8').strip():
        issues.append('transcript_missing')
    if not shutil.which('mfa'):issues.append('MFA_executable_not_installed')
    secs=None
    if not issues:
        try:
            with wave.open(str(wav),'rb') as f:
                secs=f.getnframes()/f.getframerate()
                if secs<=0:issues.append('empty_audio')
        except (wave.Error,ZeroDivisionError):issues.append('unsupported_or_invalid_WAV')
    command=['mfa','align_one',str(wav),str(text),dictionary,model,str(out),'--output_format','long_textgrid']
    report={"alignment_status":"BLOCKED_NOT_ALIGNED","errors":issues,
            "command":command,"model":model,"dictionary":dictionary,"audio_duration_s":secs,
            "phoneme_timing_validated":False,"audio_sha256":sha(wav) if wav.is_file() else None,
            "transcript_sha256":sha(text) if text.is_file() else None}
    if issues:return report
    out.parent.mkdir(parents=True,exist_ok=True)
    # No shell, no downloads, no mutation outside the explicit output.
    try:
        start=time.monotonic()
        completed=subprocess.run(command,timeout=timeout,capture_output=True,text=True,check=False)
        report['elapsed_s']=round(time.monotonic()-start,2)
        report['exit_code']=completed.returncode
        report['stderr_tail']=completed.stderr[-1500:]
        if completed.returncode==0 and out.is_file() and out.stat().st_size>200:
            report['alignment_status']='GENERATED_REQUIRES_PHONEME_QA'
            report['textgrid_sha256']=sha(out)
        else:
            report['errors'].append('MFA_process_failed_or_empty_output')
    except subprocess.TimeoutExpired:
        report['errors'].append('MFA_timeout')
    except OSError as e:
        report['errors'].append('MFA_os_error:'+str(e))
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('wav');p.add_argument('transcript');p.add_argument('--output',default='output/forced_alignment.TextGrid')
    p.add_argument('--report',default='output/REV15_ALIGNMENT_QA.json')
    p.add_argument('--acoustic-model',default='russian_mfa')
    p.add_argument('--dictionary',default='russian_mfa')
    args=p.parse_args()
    report=align(args.wav,args.transcript,args.output,args.acoustic_model,args.dictionary)
    rp=Path(args.report);rp.parent.mkdir(parents=True,exist_ok=True)
    rp.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
