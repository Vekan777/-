#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Versioned CLI launcher. Bundled per-edition with engine.py."""
import argparse
import json
import sys
from pathlib import Path

from engine import Engine, RescueError, read_job, selftest

HOME = Path(__file__).resolve().parent
EDITION = json.loads((HOME / "edition.json").read_text(encoding="utf-8"))
VERSION = int(EDITION["version"])
CAPS = {
    1: ("doctor", "release", "status", "selftest"),
    2: ("doctor", "release", "status", "backup", "verify", "restore", "selftest"),
    3: ("doctor", "release", "status", "backup", "verify", "restore", "job", "selftest"),
    4: ("doctor", "release", "status", "backup", "verify", "restore", "job", "ai", "selftest"),
    5: ("doctor", "release", "status", "backup", "verify", "restore", "job", "ai", "queue",
        "once", "recover", "worker", "selftest"),
    6: ("doctor", "release", "status", "backup", "verify", "restore", "job", "ai", "queue",
        "once", "recover", "worker", "selftest"),
}


def main():
    p = argparse.ArgumentParser(description="AI Rescue Factory V" + str(VERSION))
    p.add_argument("action", choices=CAPS[VERSION])
    p.add_argument("path", nargs="?")
    p.add_argument("other", nargs="?")
    p.add_argument("--allow-replace", action="store_true")
    p.add_argument("--project", default="default")
    p.add_argument("--provider", default="offline", choices=["offline", "ollama", "compatible"])
    p.add_argument("--model", default="qwen2.5-coder:1.5b")
    p.add_argument("--endpoint", default="")
    args = p.parse_args()
    if args.action == "selftest":
        selftest()
        return
    if args.action == "doctor":
        import shutil
        print("AI Rescue Factory V" + str(VERSION))
        for cmd in ("python", "git", "ffmpeg", "ollama"):
            print(cmd + ":", shutil.which(cmd) or "not found")
        return
    engine = Engine(HOME, args.project)
    if args.action == "status":
        print("Project", args.project, "files", len(engine.scan()))
    elif args.action == "release":
        print(engine.snapshot())
    elif args.action == "backup":
        print(engine.snapshot(engine.backups, "backup"))
    elif args.action == "verify":
        if not args.path:
            p.error("verify requires ZIP path")
        print(engine.verify(args.path))
    elif args.action == "restore":
        if not args.path or not args.other:
            p.error("restore requires ZIP and new target folder")
        print(engine.restore(args.path, args.other))
    elif args.action == "job":
        if not args.path:
            p.error("job requires job JSON path")
        print("Applied", engine.apply(read_job(args.path),
                                     permit_replace=args.allow_replace))
    elif args.action == "ai":
        if not args.path:
            p.error("ai requires task TXT path")
        from ai_pipeline import generate_and_save
        print(generate_and_save(HOME, args.path, args.provider, args.model,
                                args.endpoint))
    elif args.action == "queue":
        if not args.path:
            p.error("queue requires job JSON path")
        print(engine.enqueue(args.path))
    elif args.action == "once":
        print(engine.once(permit_replace=args.allow_replace))
    elif args.action == "recover":
        print("Recovered", engine.recover(age=0))
    elif args.action == "worker":
        import time
        try:
            while True:
                engine.once(permit_replace=args.allow_replace)
                time.sleep(15)
        except KeyboardInterrupt:
            print("Stopped")


if __name__ == "__main__":
    try:
        main()
    except (RescueError, ValueError, OSError) as ex:
        print("ERROR:", str(ex), file=sys.stderr)
        raise SystemExit(1)
