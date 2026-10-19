#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Optional AI job proposal generator. Nothing proposed is executed automatically."""
from __future__ import annotations
import json
import os
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

from engine import FORMAT, RescueError, safe_path

MAX_RESPONSE = 4 * 1024**2

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise RescueError("Provider redirect denied")

def endpoint_ok(url, provider):
    u = urllib.parse.urlsplit(url)
    local = u.hostname in ("localhost", "127.0.0.1", "::1")
    if u.username or u.password or u.fragment:
        raise RescueError("Credentials are forbidden in endpoint URL")
    if u.scheme not in ("http","https") or not u.hostname:
        raise RescueError("Bad endpoint URL")
    if u.scheme == "http" and not local:
        raise RescueError("Remote endpoints require HTTPS")
    if provider == "ollama" and not local:
        raise RescueError("Ollama endpoint must be local")

def request_model(provider, model, endpoint, task):
    system = ("Return ONLY valid JSON with format ArtifactBridgeJob/1, project and files. "
              "Each file contains path and content strings. Never include passwords or secrets. "
              "Files must have relative names. Never suggest auto-running the code.")
    if provider == "ollama":
        url = endpoint or "http://127.0.0.1:11434/api/generate"
        payload = {"model":model,"prompt":system+"\n"+task,"stream":False,"format":"json"}
    else:
        url = endpoint or "https://api.openai.com/v1/chat/completions"
        payload = {"model":model,"messages":[
            {"role":"system","content":system},
            {"role":"user","content":task}],"temperature":0.1}
    endpoint_ok(url, provider)
    headers = {"Content-Type":"application/json"}
    key = os.environ.get("AI_RESCUE_API_KEY","")
    if provider == "compatible" and key:
        headers["Authorization"]="Bearer "+key
    req = urllib.request.Request(url,
            data=json.dumps(payload,ensure_ascii=False).encode("utf-8"),
            headers=headers, method="POST")
    opener = urllib.request.build_opener(NoRedirect())
    with opener.open(req,timeout=120) as res:
        raw = res.read(MAX_RESPONSE+1)
    if len(raw)>MAX_RESPONSE:
        raise RescueError("Provider response too long")
    response = json.loads(raw)
    body = (response.get("response","") if provider=="ollama"
            else response["choices"][0]["message"]["content"])
    body = body.strip()
    if body.startswith(chr(96)*3):
        body = re.sub(r"^\x60{3}(?:json)?\s*|\s*\x60{3}$","",body).strip()
    return json.loads(body)

def generate_and_save(home, task_file, provider="offline",
                      model="qwen2.5-coder:1.5b", endpoint=""):
    path = Path(task_file)
    if path.stat().st_size>64000:
        raise RescueError("Task >64KB")
    task = path.read_text(encoding="utf-8-sig")
    if provider=="offline":
        job={"format":FORMAT,"project":"AI Rescue",
             "files":[{"path":"docs/REQUEST.txt","content":task}]}
    elif provider in ("ollama","compatible"):
        job=request_model(provider,model,endpoint,task)
    else:
        raise RescueError("Unknown provider")
    if not isinstance(job,dict) or job.get("format")!=FORMAT:
        raise RescueError("Unexpected model response")
    files=job.get("files")
    if not isinstance(files,list) or len(files)>200:
        raise RescueError("Unexpected file list")
    for file in files:
        safe_path(file.get("path"))
        if not isinstance(file.get("content"),str):
            raise RescueError("Only text proposals supported in this mode")
    folder=Path(home)/"proposals"
    folder.mkdir(parents=True,exist_ok=True)
    out=folder/("proposal-"+str(time.time_ns())+".json")
    out.write_text(json.dumps(job,ensure_ascii=False,indent=2),encoding="utf-8")
    return out
