"""Integration and security regression tests for AI Rescue Factory V6."""
import hashlib
import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "rescue-engine" / "engine.py"
SPEC = importlib.util.spec_from_file_location("rescue_engine", SOURCE)
rescue = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rescue)


class RescueTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.engine = rescue.Engine(self.home, "test")

    def job(self, entries):
        file = self.home / "job.json"
        file.write_text(json.dumps({"format": rescue.FORMAT, "files": entries}),
                        encoding="utf-8")
        return file

    def test_guard_path(self):
        for path in ("../file", "dir/../f", "C:/system", "CON.txt",
                     "trailing. ", "a//b", "/root", "NUL"):
            with self.subTest(path=path), self.assertRaises(rescue.RescueError):
                rescue.safe_path(path)

    def test_create_and_snapshot(self):
        self.engine.apply(rescue.read_job(self.job([
            {"path": "docs/Тест.txt", "content": "Привет"},
            {"path": "config/app.json", "content": '{"version":1}'}
        ])))
        z = self.engine.snapshot(label="test")
        self.assertEqual(self.engine.verify(z), 3)
        out = self.engine.restore(z, self.home / "restore")
        self.assertEqual((out / "docs/Тест.txt").read_text(encoding="utf-8"), "Привет")

    def test_replace_requires_sha(self):
        self.engine.apply(rescue.read_job(self.job([
            {"path": "one.txt", "content": "old"}
        ])))
        invalid = self.job([{"path": "one.txt", "mode": "replace",
                            "expected_sha256": "0"*64, "content": "new"}])
        with self.assertRaises(rescue.RescueError):
            self.engine.apply(rescue.read_job(invalid), permit_replace=True)
        self.assertEqual((self.engine.files / "one.txt").read_text(), "old")
        source_hash = hashlib.sha256(b"old").hexdigest()
        valid = self.job([{"path": "one.txt", "mode": "replace",
                          "expected_sha256": source_hash, "content": "new"}])
        with self.assertRaises(rescue.RescueError):
            self.engine.apply(rescue.read_job(valid))
        self.engine.apply(rescue.read_job(valid), permit_replace=True)
        self.assertEqual((self.engine.files / "one.txt").read_text(), "new")
        self.assertTrue(list(self.engine.backups.glob("before-replace-*.zip")))

    def test_same_job_deduplicates(self):
        file = self.job([{"path": "scripts/hello.py", "content": "print('hi')"}])
        id1 = self.engine.enqueue(file)
        self.assertEqual(id1, self.engine.enqueue(file))
        self.assertEqual(self.engine.once(), id1)
        self.assertIsNone(self.engine.once())
        self.assertEqual(self.engine.tasks()[0][1], "done")

    def test_resume(self):
        file = self.job([{"path": "log.txt", "content": "back"}])
        id_ = self.engine.enqueue(file)
        self.engine.connection.execute(
            "UPDATE tasks SET state='running',started=1,attempts=1 WHERE id=?",
            (id_,))
        self.assertEqual(self.engine.recover(age=0), 1)
        self.assertEqual(self.engine.once(), id_)
        self.assertEqual((self.engine.files / "log.txt").read_text(), "back")

    def test_prevent_clashes(self):
        with self.assertRaises(rescue.RescueError):
            rescue.read_job(self.job([
                {"path": "Readme.md", "content": "a"},
                {"path": "readme.md", "content": "b"}
            ]))

    def test_archive_damage(self):
        self.engine.apply(rescue.read_job(self.job([
            {"path": "a.txt", "content": "123456789"}
        ])))
        good = self.engine.snapshot(label="checksum")
        corrupted = self.home / "broken.zip"
        raw = bytearray(good.read_bytes())
        with zipfile.ZipFile(good) as f:
            entry = f.getinfo("a.txt")
            position = entry.header_offset + 30 + len(entry.filename.encode())
            raw[position] ^= 1
        corrupted.write_bytes(raw)
        with self.assertRaises((zipfile.BadZipFile, rescue.RescueError, ValueError)):
            self.engine.verify(corrupted)

    def test_no_arbitrary_code_execution(self):
        file = self.job([
            {"path": "danger.py", "content": "raise RuntimeError('NOT EXECUTED')\n"}
        ])
        self.engine.apply(rescue.read_job(file))
        self.assertTrue((self.engine.files / "danger.py").exists())


if __name__ == "__main__":
    unittest.main()
