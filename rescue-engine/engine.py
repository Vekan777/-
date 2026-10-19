#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI Rescue Factory: offline artifact builder, V1-V6 unified engine.
Python >=3.10, standard library only. Never executes imported project code.
"""
from __future__ import annotations

import argparse
import ast
import base64
import hashlib
import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile
import time
import unicodedata
import zipfile
from pathlib import Path

FORMAT = "ArtifactBridgeJob/1"
MANIFEST = "_rescue_manifest.json"
MAX_FILES = 10000
MAX_FILE = 2 * 1024**3
MAX_TOTAL = 8 * 1024**3
MAX_JOB = 16 * 1024**2
RESERVED = {"CON", "PRN", "AUX", "NUL"} | {
    p + str(n) for p in ("COM", "LPT") for n in range(1, 10)
}


class RescueError(Exception):
    pass


def safe_path(raw):
    if not isinstance(raw, str):
        raise RescueError("Filename must be text")
    name = raw.replace("\\", "/")
    if not name or len(name) > 240 or name.startswith("/") or ":" in name:
        raise RescueError("Absolute/empty/long path")
    parts = name.split("/")
    for part in parts:
        if (part in ("", ".", "..") or part.rstrip(" .") != part or
                re.search(r'[\x00-\x1f<>:"|?*]', part) or
                part.split(".")[0].upper() in RESERVED):
            raise RescueError("Unsafe filename: " + raw)
    if name.casefold() == MANIFEST.casefold():
        raise RescueError("Reserved manifest path")
    return name


def normalize(name):
    return unicodedata.normalize("NFC", name).casefold()


def target(root, name):
    root = Path(root).resolve()
    resolved = root.joinpath(*safe_path(name).split("/"))
    if not resolved.resolve().is_relative_to(root):
        raise RescueError("Symlink/path escapes workspace")
    return resolved


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for part in iter(lambda: f.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def stamp():
    return time.strftime("%Y%m%d-%H%M%S") + "-" + str(time.time_ns() % 1000000000)


def read_job(filepath):
    path = Path(filepath)
    if path.stat().st_size > MAX_JOB:
        raise RescueError("Job size above 16 MiB")
    obj = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(obj, dict) or obj.get("format") != FORMAT:
        raise RescueError("Expected ArtifactBridgeJob/1")
    rows = obj.get("files")
    if not isinstance(rows, list) or len(rows) > MAX_FILES:
        raise RescueError("Invalid files array")
    seen, total, result = set(), 0, []
    for r in rows:
        if not isinstance(r, dict):
            raise RescueError("Invalid file record")
        name = safe_path(r.get("path"))
        key = normalize(name)
        if key in seen:
            raise RescueError("Duplicate Windows filenames")
        seen.add(key)
        mode = r.get("mode", "create")
        if mode not in ("create", "replace"):
            raise RescueError("Unsupported write mode")
        if isinstance(r.get("content"), str):
            data = r["content"].encode("utf-8")
        elif isinstance(r.get("base64"), str):
            data = base64.b64decode(r["base64"], validate=True)
        else:
            raise RescueError("Missing content for " + name)
        total += len(data)
        if len(data) > MAX_FILE or total > MAX_TOTAL:
            raise RescueError("Job exceeds limits")
        sha = sha_bytes(data)
        if r.get("sha256") and r["sha256"].lower() != sha:
            raise RescueError("Input SHA256 differs")
        old = r.get("expected_sha256")
        if mode == "replace":
            if not isinstance(old, str) or not re.fullmatch("[a-fA-F0-9]{64}", old):
                raise RescueError("Replacement requires expected_sha256")
            old = old.lower()
        if name.lower().endswith(".py"):
            ast.parse(data.decode("utf-8-sig"), filename=name)
        if name.lower().endswith(".json"):
            json.loads(data.decode("utf-8-sig"))
        result.append((name, data, mode, old, sha))
    return result


class Engine:
    def __init__(self, home, project="default"):
        p = safe_path(project)
        if "/" in p:
            raise RescueError("Project name must be one component")
        self.home = Path(home).expanduser().resolve()
        self.project = p
        self.files = self.home / "workspace" / p / "files"
        self.internal = self.home / ".rescue_state" / p
        self.jobs = self.internal / "jobs"
        self.backups = self.home / "backups" / p
        self.releases = self.home / "releases" / p
        for folder in (self.files, self.jobs, self.backups, self.releases):
            folder.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.internal / "queue.sqlite3", timeout=30,
                                           isolation_level=None)
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("PRAGMA busy_timeout=30000")
        self.connection.execute("PRAGMA synchronous=FULL")
        self.connection.executescript("""
        CREATE TABLE IF NOT EXISTS tasks(
          id TEXT PRIMARY KEY, digest TEXT NOT NULL, state TEXT NOT NULL,
          attempts INTEGER NOT NULL, maximum INTEGER NOT NULL,
          due REAL NOT NULL, started REAL, message TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS events(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          timestamp REAL NOT NULL, task_id TEXT, action TEXT, details TEXT
        );
        """)

    def event(self, task_id, action, message=""):
        self.connection.execute(
            "INSERT INTO events(timestamp,task_id,action,details) VALUES(?,?,?,?)",
            (time.time(), task_id, action, str(message)[:2000]))

    def scan(self):
        result, total, seen = [], 0, set()
        for path in self.files.rglob("*"):
            if path.is_symlink():
                raise RescueError("Symbolic link in workspace")
            if not path.is_file():
                continue
            name = safe_path(path.relative_to(self.files).as_posix())
            if not path.resolve().is_relative_to(self.files.resolve()):
                raise RescueError("Escaped workspace")
            if normalize(name) in seen:
                raise RescueError("Case-insensitive filename collision")
            seen.add(normalize(name))
            size = path.stat().st_size
            total += size
            if size > MAX_FILE or total > MAX_TOTAL:
                raise RescueError("Workspace too large")
            result.append((name, path))
        if len(result) > MAX_FILES:
            raise RescueError("Too many files")
        return sorted(result)

    def snapshot(self, folder=None, label="release"):
        where = Path(folder or self.releases)
        where.mkdir(parents=True, exist_ok=True)
        destination = where / (label + "-" + stamp() + ".zip")
        files = self.scan()
        manifest = {
            "format": "AIRescueManifest/6",
            "project": self.project,
            "label": label,
            "files": [{"path": name, "size": path.stat().st_size,
                       "sha256": sha_file(path)} for name, path in files]
        }
        temp = destination.with_suffix(".partial")
        try:
            with zipfile.ZipFile(temp, "w", compression=zipfile.ZIP_DEFLATED,
                                 compresslevel=6, allowZip64=True) as z:
                for name, path in files:
                    z.write(path, arcname=name)
                z.writestr(MANIFEST, json.dumps(manifest, ensure_ascii=False, indent=2))
            self.verify(temp)
            os.replace(temp, destination)
            return destination
        finally:
            temp.unlink(missing_ok=True)

    @staticmethod
    def verify(path):
        with zipfile.ZipFile(path) as z:
            infos = z.infolist()
            if len(infos) > MAX_FILES + 1:
                raise RescueError("Excessive archive entries")
            names, total = set(), 0
            for info in infos:
                if info.is_dir():
                    raise RescueError("Directory records not expected")
                if info.filename != MANIFEST:
                    safe_path(info.filename)
                key = normalize(info.filename)
                if key in names:
                    raise RescueError("Duplicate archive filenames")
                names.add(key)
                total += info.file_size
                if info.file_size > MAX_FILE or total > MAX_TOTAL:
                    raise RescueError("ZIP bomb / archive too large")
                if info.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
                    raise RescueError("Unsupported compression")
                if ((info.external_attr >> 16) & 0o170000) == 0o120000:
                    raise RescueError("ZIP symlink forbidden")
            if z.testzip():
                raise RescueError("ZIP CRC32 failure")
            if MANIFEST not in z.namelist():
                raise RescueError("Manifest absent")
            doc = json.loads(z.read(MANIFEST))
            if doc.get("format") != "AIRescueManifest/6":
                raise RescueError("Unknown manifest version")
            expected = set()
            for entry in doc["files"]:
                name = safe_path(entry["path"])
                expected.add(normalize(name))
                if name not in z.namelist():
                    raise RescueError("Manifest path missing")
                h, count = hashlib.sha256(), 0
                with z.open(name) as f:
                    for block in iter(lambda: f.read(1024*1024), b""):
                        h.update(block)
                        count += len(block)
                if h.hexdigest() != entry["sha256"] or count != entry["size"]:
                    raise RescueError("SHA256/size mismatch: " + name)
            if names - {normalize(MANIFEST)} != expected:
                raise RescueError("Unlisted files in ZIP")
            return len(infos)

    def restore(self, archive, destination):
        self.verify(archive)
        dest = Path(destination).expanduser().resolve()
        if dest.exists():
            raise RescueError("Restore target must be a new folder")
        dest.mkdir(parents=True)
        try:
            with zipfile.ZipFile(archive) as z:
                for info in z.infolist():
                    if info.filename == MANIFEST:
                        continue
                    p = target(dest, info.filename)
                    p.parent.mkdir(parents=True, exist_ok=True)
                    with z.open(info) as inp, p.open("xb") as out:
                        shutil.copyfileobj(inp, out, 1024 * 1024)
            return dest
        except Exception:
            shutil.rmtree(dest, ignore_errors=True)
            raise

    def apply(self, entries, permit_replace=False):
        before = {normalize(n): n for n, _ in self.scan()}
        todo = []
        for name, data, mode, old_sha, new_sha in entries:
            colliding = before.get(normalize(name))
            if colliding and colliding != name:
                raise RescueError("Case collision: " + name)
            p = target(self.files, name)
            if p.exists():
                if not p.is_file():
                    raise RescueError("Non-file target")
                actual = sha_file(p)
                if actual == new_sha:
                    continue
                if mode != "replace" or not permit_replace:
                    raise RescueError("Overwrite not approved: " + name)
                if actual != old_sha:
                    raise RescueError("Old content SHA256 changed: " + name)
            elif mode != "create":
                raise RescueError("Missing file for replacement: " + name)
            todo.append((name, data, p, mode))
        if not todo:
            return 0
        if any(mode == "replace" for _, _, _, mode in todo):
            self.snapshot(self.backups, "before-replace")
        with tempfile.TemporaryDirectory(prefix="rescue-", dir=self.internal) as td:
            scratch = Path(td)
            originals = scratch / "originals"
            incoming = scratch / "incoming"
            restored = []
            for name, data, p, mode in todo:
                staged = target(incoming, name)
                staged.parent.mkdir(parents=True, exist_ok=True)
                staged.write_bytes(data)
                if sha_file(staged) != sha_bytes(data):
                    raise RescueError("Staging verification failed")
                if mode == "replace":
                    prior = target(originals, name)
                    prior.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(p, prior)
            try:
                for name, data, p, mode in todo:
                    p.parent.mkdir(parents=True, exist_ok=True)
                    staged = target(incoming, name)
                    if mode == "create":
                        try:
                            os.link(staged, p)  # no overwrite
                        except FileExistsError:
                            if not p.is_file() or sha_file(p) != sha_bytes(data):
                                raise RescueError("Concurrent create conflict")
                    else:
                        os.replace(staged, p)
                    restored.append((name, p, mode))
            except Exception:
                for name, p, mode in reversed(restored):
                    if mode == "create":
                        p.unlink(missing_ok=True)
                    else:
                        shutil.copy2(target(originals, name), p)
                raise
        return len(todo)

    def enqueue(self, job_file, maximum=3):
        path = Path(job_file)
        if path.stat().st_size > MAX_JOB:
            raise RescueError("Job too large")
        raw = path.read_bytes()
        read_job(job_file)
        digest = sha_bytes(raw)
        id_ = digest[:32]
        dest = self.jobs / (id_ + ".json")
        if not dest.exists():
            with dest.open("xb") as f:
                f.write(raw)
                f.flush()
                os.fsync(f.fileno())
        if sha_file(dest) != digest:
            raise RescueError("Queued job hash mismatch")
        self.connection.execute(
            "INSERT OR IGNORE INTO tasks(id,digest,state,attempts,maximum,due) "
            "VALUES(?,?, 'queued',0,?,?)",
            (id_, digest, max(1, min(int(maximum), 10)), time.time()))
        self.event(id_, "enqueued")
        return id_

    def recover(self, age=300):
        old = time.time() - age
        rows = self.connection.execute(
            "SELECT id,attempts,maximum FROM tasks WHERE state='running' AND started<?",
            (old,)).fetchall()
        for id_, attempts, maximum in rows:
            state = "retry" if attempts < maximum else "failed"
            self.connection.execute(
                "UPDATE tasks SET state=?,due=?,started=NULL WHERE id=?",
                (state, time.time(), id_))
            self.event(id_, "recovery", state)
        return len(rows)

    def once(self, permit_replace=False):
        self.recover()
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            row = self.connection.execute(
                "SELECT id,digest,attempts,maximum FROM tasks "
                "WHERE state IN ('queued','retry') AND due<=? "
                "ORDER BY due LIMIT 1", (time.time(),)).fetchone()
            if row:
                self.connection.execute(
                    "UPDATE tasks SET state='running',started=?,attempts=attempts+1 "
                    "WHERE id=?", (time.time(), row[0]))
            self.connection.execute("COMMIT")
        except Exception:
            self.connection.execute("ROLLBACK")
            raise
        if not row:
            return None
        id_, digest, attempts, maximum = row
        try:
            path = self.jobs / (id_ + ".json")
            if sha_file(path) != digest:
                raise RescueError("Queued job checksum changed")
            changed = self.apply(read_job(path), permit_replace=permit_replace)
            archive = self.snapshot(self.backups, "after-job")
            self.connection.execute(
                "UPDATE tasks SET state='done',message=? WHERE id=?",
                (f"{changed} changes; {archive.name}", id_))
            self.event(id_, "done", str(changed))
        except Exception as exc:
            terminal = isinstance(exc, RescueError) or attempts+1>=maximum
            state = "failed" if terminal else "retry"
            delay = 0 if terminal else min(900, 15*2**attempts)
            self.connection.execute(
                "UPDATE tasks SET state=?,due=?,message=? WHERE id=?",
                (state, time.time()+delay, str(exc)[:1800], id_))
            self.event(id_, state, str(exc))
        return id_

    def tasks(self):
        return self.connection.execute(
            "SELECT id,state,attempts,maximum,message FROM tasks ORDER BY rowid DESC"
        ).fetchall()

    def audit(self):
        errors = []
        for name, p in self.scan():
            try:
                if name.endswith(".py"):
                    ast.parse(p.read_text(encoding="utf-8-sig"), filename=name)
                elif name.endswith(".json"):
                    json.loads(p.read_text(encoding="utf-8-sig"))
            except (SyntaxError, ValueError, UnicodeError) as exc:
                errors.append(f"{name}: {exc}")
        return errors


def selftest():
    with tempfile.TemporaryDirectory(prefix="rescue-v6-") as temp:
        home = Path(temp)
        e = Engine(home, "test")
        j = home / "test.json"
        j.write_text(json.dumps({"format": FORMAT, "files": [
            {"path": "src/main.py", "content": "print('hello')\n"},
            {"path": "metadata/info.json", "content": '{"ok":true}'}
        ]}), encoding="utf-8")
        first = e.enqueue(j)
        assert first == e.enqueue(j)
        assert e.once() == first
        assert e.tasks()[0][1] == "done"
        assert e.once() is None
        snap = e.snapshot(label="test")
        assert e.verify(snap) == 3
        restored = e.restore(snap, home / "restored")
        assert (restored / "src/main.py").read_text() == "print('hello')\n"
        old_sha = sha_file(e.files / "src/main.py")
        j.write_text(json.dumps({"format": FORMAT, "files": [
            {"path": "src/main.py", "mode": "replace",
             "expected_sha256": old_sha, "content": "print('better')\n"}
        ]}), encoding="utf-8")
        second = e.enqueue(j)
        assert e.once(permit_replace=True) == second
        assert e.tasks()[0][1] == "done"
        assert (e.files / "src/main.py").read_text() == "print('better')\n"
        assert list(e.backups.glob("before-replace-*.zip"))
        j.write_text(json.dumps({"format": FORMAT, "files": [
            {"path": "recovered.txt", "content": "after crash"}]}), encoding="utf-8")
        third = e.enqueue(j)
        e.connection.execute(
            "UPDATE tasks SET state='running',started=1,attempts=1 WHERE id=?", (third,))
        assert e.recover(age=0) == 1
        assert e.once() == third
        assert (e.files / "recovered.txt").read_text() == "after crash"
        assert e.audit() == []
        for unsafe in ("../secret.txt", "C:/boot.ini", "CON.txt", "folder/../oops"):
            try:
                safe_path(unsafe)
                raise AssertionError("Unsafe path accepted")
            except RescueError:
                pass
        e.connection.close()
    print("SELFTEST PASS: queue, idempotency, backup, SHA256, ZIP, restore, recovery")


def main():
    p = argparse.ArgumentParser(description="AI Rescue Factory V6")
    p.add_argument("--home", default=str(Path(__file__).resolve().parent))
    p.add_argument("--project", default="default")
    sub = p.add_subparsers(dest="cmd", required=True)
    for cmd in ("selftest", "init", "status", "audit", "release", "backup",
                "once", "recover", "tasks", "doctor"):
        sub.add_parser(cmd)
    cmd = sub.add_parser("enqueue")
    cmd.add_argument("job")
    cmd = sub.add_parser("verify")
    cmd.add_argument("archive")
    cmd = sub.add_parser("restore")
    cmd.add_argument("archive")
    cmd.add_argument("destination")
    cmd = sub.add_parser("add")
    cmd.add_argument("source")
    cmd.add_argument("destination")
    cmd = sub.add_parser("worker")
    cmd.add_argument("--interval", type=float, default=15)
    args = p.parse_args()
    if args.cmd == "selftest":
        selftest()
        return
    if args.cmd == "doctor":
        for tool in ("python", "git", "ffmpeg", "ollama", "node"):
            print(tool, shutil.which(tool) or "NOT FOUND")
        print(sys.version)
        return
    e = Engine(args.home, args.project)
    if args.cmd == "init":
        print(e.files)
    elif args.cmd == "status":
        print(e.scan())
    elif args.cmd == "audit":
        errs = e.audit()
        print("\n".join(errs) or "AUDIT PASS")
        if errs:
            raise SystemExit(2)
    elif args.cmd == "release":
        print(e.snapshot())
    elif args.cmd == "backup":
        print(e.snapshot(e.backups, "manual"))
    elif args.cmd == "once":
        print(e.once())
    elif args.cmd == "recover":
        print("Recovered", e.recover(age=0))
    elif args.cmd == "tasks":
        for line in e.tasks():
            print(*line, sep=" | ")
    elif args.cmd == "enqueue":
        print("Queued", e.enqueue(args.job))
    elif args.cmd == "verify":
        print("Verified", Engine.verify(args.archive), "files")
    elif args.cmd == "restore":
        print("Restored", e.restore(args.archive, args.destination))
    elif args.cmd == "add":
        src = Path(args.source)
        if not src.is_file() or src.is_symlink():
            raise RescueError("Expected normal source file")
        dest = target(e.files, args.destination)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with src.open("rb") as i, dest.open("xb") as o:
            shutil.copyfileobj(i, o, 1024*1024)
        print(dest)
    elif args.cmd == "worker":
        if args.interval < 1:
            raise RescueError("Interval must be at least 1 second")
        try:
            while True:
                e.once()
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("Worker stopped")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(type(exc).__name__ + ": " + str(exc), file=sys.stderr)
        raise SystemExit(1)
