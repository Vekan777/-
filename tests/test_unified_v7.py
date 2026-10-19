"""V7 integration tests for real Windows/Linux runners."""
from __future__ import annotations
import importlib.util
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "rescue-engine"))
from engine import Engine, RescueError, sha_file  # noqa: E402

v7spec = importlib.util.spec_from_file_location(
    "unified_v7", ROOT / "rescue-engine" / "unified_v7.py"
)
v7 = importlib.util.module_from_spec(v7spec)
v7spec.loader.exec_module(v7)


class V7UnifiedTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.engine = Engine(self.root, "v7")
        self.addCleanup(self.engine.connection.close)

    def test_migration_is_lossless_and_repeatable(self):
        old = self.root / "old"
        (old / "world").mkdir(parents=True)
        (old / "world" / "plot.json").write_text(
            json.dumps({"characters": ["Акира"], "skills": ["Призыв душ"]},
                       ensure_ascii=False), encoding="utf-8"
        )
        self.assertEqual(v7.migrate_files(self.engine, old), 1)
        self.assertEqual(v7.migrate_files(self.engine, old), 0)
        self.assertEqual((self.engine.files / "world" / "plot.json").read_bytes(),
                         (old / "world" / "plot.json").read_bytes())
        self.assertTrue(list(self.engine.backups.glob("before-legacy-import-*.zip")))

    def test_migration_rejects_collision_without_overwrite(self):
        old = self.root / "old"
        old.mkdir()
        (old / "story.txt").write_text("old story", encoding="utf-8")
        (self.engine.files / "story.txt").write_text("modified", encoding="utf-8")
        with self.assertRaises(RescueError):
            v7.migrate_files(self.engine, old)
        self.assertEqual((self.engine.files / "story.txt").read_text(), "modified")

    def test_import_legacy_keeps_original_bytes(self):
        oldzip = self.root / "v3.zip"
        with zipfile.ZipFile(oldzip, "w") as z:
            z.writestr("one.txt", "1")
        preserved = v7.import_legacy_file(self.root, oldzip)
        self.assertEqual(preserved.read_bytes(), oldzip.read_bytes())
        self.assertEqual(v7.import_legacy_file(self.root, oldzip), preserved)

    def test_path_traversal_in_legacy_zip_blocked(self):
        oldzip = self.root / "evil.zip"
        with zipfile.ZipFile(oldzip, "w") as z:
            z.writestr("../dangerous.exe", b"test")
        with self.assertRaises(RescueError):
            v7.import_legacy_file(self.root, oldzip)

    def test_bundle_verifier_detects_crc_tampering(self):
        target = self.root / "unified.zip"
        with zipfile.ZipFile(target, "w") as z:
            data = b"test"
            import hashlib
            z.writestr("world.txt", data)
            z.writestr(v7.MANIFEST, json.dumps({
                "format": "AIRescueUnified/7",
                "version": "7.0",
                "files": [{"path": "world.txt", "size": 4,
                           "sha256": hashlib.sha256(data).hexdigest()}]
            }))
        self.assertEqual(v7.inspect_bundle(target)["files"], 1)
        raw = bytearray(target.read_bytes())
        pos = raw.find(b"PK\x01\x02")
        self.assertGreaterEqual(pos, 0)
        raw[pos+16] ^= 1
        broken = self.root / "corrupt.zip"
        broken.write_bytes(raw)
        with self.assertRaises((RescueError, zipfile.BadZipFile)):
            v7.inspect_bundle(broken)

    def test_bundle_verifier_rejects_missing_files(self):
        target = self.root / "unlisted.zip"
        with zipfile.ZipFile(target, "w") as z:
            z.writestr("file.txt", b"content")
            z.writestr(v7.MANIFEST, '{"format":"AIRescueUnified/7","files":[]}')
        with self.assertRaises(RescueError):
            v7.inspect_bundle(target)


if __name__ == "__main__":
    unittest.main()
