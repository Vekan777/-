#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI Rescue Factory V7 Unified: integrity, legacy import, migration and CLI.

Python >=3.10; no mandatory third-party dependencies or cloud services.
Never executes files received from AI or imported archives.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

from engine import Engine, RescueError, safe_path, target, sha_file, sha_bytes

RELEASE = "7.0"
MANIFEST = "_v7/manifest.json"
LIMIT_FILE = 2 * 1024**3
LIMIT_TOTAL = 8 * 1024**3
LIMIT_COUNT = 10000


def inspect_bundle(path):
    """Check full V7 package by CRC32 and SHA256, no extraction."""
    with zipfile.ZipFile(path, "r") as z:
        infos = z.infolist()
        if len(infos) > LIMIT_COUNT:
            raise RescueError("Archive too many entries")
        names, total = set(), 0
        for info in infos:
            if info.is_dir():
                raise RescueError("Unexpected directory entry")
            name = info.filename
            if name != MANIFEST:
                safe_path(name)
            key = name.casefold()
            if key in names:
                raise RescueError("Windows filename collision")
            names.add(key)
            if info.flag_bits & 0x01:
                raise RescueError("Encrypted ZIP entries are not supported")
            if info.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
                raise RescueError("Unsupported compression method")
            if ((info.external_attr >> 16) & 0o170000) == 0o120000:
                raise RescueError("Symlink ZIP entry not supported")
            total += info.file_size
            if info.file_size > LIMIT_FILE or total > LIMIT_TOTAL:
                raise RescueError("Excessive archive expansion")
        if MANIFEST not in z.namelist():
            raise RescueError("V7 manifest missing")
        if z.testzip() is not None:
            raise RescueError("ZIP CRC32 failure")
        data = json.loads(z.read(MANIFEST))
        if data.get("format") != "AIRescueUnified/7":
            raise RescueError("Incorrect V7 manifest format")
        expected = set()
        for row in data.get("files", []):
            name = safe_path(row["path"])
            key = name.casefold()
            if key in expected:
                raise RescueError("Duplicate in V7 manifest")
            expected.add(key)
            if name not in z.namelist():
                raise RescueError("Missing V7 file: " + name)
            size, digest = 0, hashlib.sha256()
            with z.open(name) as input_file:
                for part in iter(lambda: input_file.read(1024 * 1024), b""):
                    digest.update(part)
                    size += len(part)
            if size != row["size"] or digest.hexdigest() != row["sha256"]:
                raise RescueError("V7 SHA256 mismatch: " + name)
        if names - {MANIFEST.casefold()} != expected:
            raise RescueError("Unexpected V7 files")
        return {"files":len(expected),"version":data.get("version"),"bytes":total}


def import_legacy_file(home, archive):
    """Keep an older ZIP byte-for-byte; do not extract or execute it."""
    path = Path(archive)
    if not path.is_file() or path.is_symlink():
        raise RescueError("A regular ZIP file is required")
    if path.suffix.lower() != ".zip":
        raise RescueError("Only ZIP imports allowed")
    if path.stat().st_size > LIMIT_TOTAL:
        raise RescueError("Archive exceeds configured limits")
    # General ZIP CRC check; older versions may have different manifests.
    with zipfile.ZipFile(path) as z:
        if len(z.infolist()) > LIMIT_COUNT:
            raise RescueError("Too many ZIP entries")
        for i in z.infolist():
            if i.is_dir():
                continue
            safe_path(i.filename)
            if i.file_size > LIMIT_FILE:
                raise RescueError("ZIP entry too large")
        if z.testzip():
            raise RescueError("Imported archive CRC failure")
    digest = sha_file(path)
    destination = Path(home).resolve() / "legacy-imports"
    destination.mkdir(parents=True, exist_ok=True)
    final = destination / (digest[:16] + "_" + path.name)
    if final.exists():
        if sha_file(final) != digest:
            raise RescueError("Legacy ZIP filename checksum collision")
        return final
    with path.open("rb") as inp, final.open("xb") as out:
        shutil.copyfileobj(inp, out, 1024 * 1024)
    if sha_file(final) != digest:
        final.unlink(missing_ok=True)
        raise RescueError("Legacy import copy checksum failure")
    return final


def migrate_files(engine, old_directory):
    """Copy an old project's working files without overwriting modern files."""
    original = Path(old_directory).expanduser().resolve()
    if not original.is_dir():
        raise RescueError("Source directory missing")
    new_root = engine.files.resolve()
    if original == new_root or original.is_relative_to(new_root) or new_root.is_relative_to(original):
        raise RescueError("Old/new project folders must be disjoint")
    paths, seen, total = [], set(), 0
    for path in original.rglob("*"):
        if path.is_symlink():
            raise RescueError("Legacy symlink forbidden: " + str(path))
        if not path.is_file():
            continue
        name = safe_path(path.relative_to(original).as_posix())
        folded = name.casefold()
        if folded in seen:
            raise RescueError("Legacy Windows filename collision")
        seen.add(folded)
        total += path.stat().st_size
        if path.stat().st_size > LIMIT_FILE or total > LIMIT_TOTAL:
            raise RescueError("Legacy project exceeds configured limits")
        paths.append((name, path))
    if len(paths) > LIMIT_COUNT:
        raise RescueError("Too many legacy files")
    existing = {n.casefold(): n for n, _ in engine.scan()}
    to_add = []
    for name, path in paths:
        if name.casefold() in existing:
            other = target(engine.files, existing[name.casefold()])
            if existing[name.casefold()] != name or sha_file(other) != sha_file(path):
                raise RescueError("Legacy differs from existing file: " + name)
        else:
            to_add.append((name, path))
    if not to_add:
        return 0
    # Backup the pre-migration state so a user can return to it.
    engine.snapshot(engine.backups, "before-legacy-import")
    created = []
    try:
        for name, src in to_add:
            dest = target(engine.files, name)
            dest.parent.mkdir(parents=True, exist_ok=True)
            with src.open("rb") as inp, dest.open("xb") as out:
                shutil.copyfileobj(inp, out, 1024 * 1024)
            created.append(dest)
            if sha_file(src) != sha_file(dest):
                raise RescueError("Legacy content differs after copy")
    except Exception:
        for file in reversed(created):
            file.unlink(missing_ok=True)
        raise
    return len(created)


def selftest():
    with tempfile.TemporaryDirectory(prefix="v7-selftest-") as directory:
        home = Path(directory)
        engine = Engine(home, "test")
        try:
            prior = home / "old-project"
            (prior / "docs").mkdir(parents=True)
            (prior / "docs" / "Сюжет.txt").write_text("Главный герой сохраняет память.", encoding="utf-8")
            assert migrate_files(engine, prior) == 1
            assert migrate_files(engine, prior) == 0
            assert (engine.files / "docs" / "Сюжет.txt").read_text(encoding="utf-8") == "Главный герой сохраняет память."
            assert list(engine.backups.glob("before-legacy-import-*.zip"))
            old = home / "sample.zip"
            with zipfile.ZipFile(old, "w") as z:
                z.writestr("source.txt", "old version")
            stored = import_legacy_file(home, old)
            assert stored.exists() and sha_file(old) == sha_file(stored)
            assert import_legacy_file(home, old) == stored
            new = engine.snapshot(label="after-import")
            assert engine.verify(new) == 2
            print("V7 SELFTEST PASS: migration, repeat-safe import, legacy preservation, SHA256, backup and ZIP")
        finally:
            engine.connection.close()


def doctor(home):
    print("AI Rescue Factory V7 Unified")
    print("Python:", sys.version.split()[0], "Platform:", sys.platform)
    print("Free disk MiB:", shutil.disk_usage(Path(home).resolve()).free // 1048576)
    for program in ("python", "git", "ffmpeg", "ollama", "node"):
        print(program, shutil.which(program) or "not installed")
    print("Offline functions work without network or ChatGPT file runtime.")


def main():
    cli = argparse.ArgumentParser(description="AI Rescue Factory V7 Unified")
    cli.add_argument("--home", default=str(Path(__file__).resolve().parent.parent))
    cli.add_argument("--project", default="default")
    tasks = cli.add_subparsers(dest="action", required=True)
    for item in ("selftest", "doctor", "status", "audit", "backup", "release", "queue",
                 "worker-once", "recover"):
        cmd = tasks.add_parser(item)
        if item == "queue":
            cmd.add_argument("job")
    cmd = tasks.add_parser("bundle-verify")
    cmd.add_argument("filename")
    cmd = tasks.add_parser("verify")
    cmd.add_argument("filename")
    cmd = tasks.add_parser("restore")
    cmd.add_argument("filename")
    cmd.add_argument("destination")
    cmd = tasks.add_parser("legacy-import")
    cmd.add_argument("filename")
    cmd = tasks.add_parser("migrate-files")
    cmd.add_argument("folder")
    a = cli.parse_args()

    if a.action == "selftest":
        selftest()
        return
    if a.action == "doctor":
        doctor(a.home)
        return
    if a.action == "bundle-verify":
        print("Verified V7:", inspect_bundle(a.filename))
        return
    if a.action == "legacy-import":
        print("Preserved legacy ZIP:", import_legacy_file(a.home, a.filename))
        return

    e = Engine(a.home, a.project)
    try:
        if a.action == "status":
            print("Project", a.project, "files", len(e.scan()), "queued", len(e.tasks()))
        elif a.action == "audit":
            issues = e.audit()
            print("AUDIT PASS" if not issues else "\n".join(issues))
            if issues:
                raise SystemExit(2)
        elif a.action == "release":
            print("New verified ZIP:", e.snapshot())
        elif a.action == "backup":
            print("Verified backup:", e.snapshot(e.backups, "manual"))
        elif a.action == "verify":
            print("Archive entries verified:", e.verify(a.filename))
        elif a.action == "restore":
            print("Restored:", e.restore(a.filename, a.destination))
        elif a.action == "queue":
            print("Job ID:", e.enqueue(a.job))
        elif a.action == "worker-once":
            print("Processed:", e.once())
        elif a.action == "recover":
            print("Recovered tasks:", e.recover(age=0))
        elif a.action == "migrate-files":
            print("Legacy project files imported:", migrate_files(e, a.folder))
    finally:
        e.connection.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(type(error).__name__ + ": " + str(error), file=sys.stderr)
        raise SystemExit(1)
