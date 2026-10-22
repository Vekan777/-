"""Check C8 Rev16.6 ZIP CRC + per-entry SHA-256 manifest independently.
Run: python verify_archive.py /path/to/full_or_compact.zip
"""
from pathlib import Path
from zipfile import ZipFile
import hashlib
import json
import sys

def verify(path):
    with ZipFile(path) as z:
        damaged = z.testzip()
        if damaged:
            raise ValueError("CRC failed: " + damaged)
        manifest = json.loads(z.read("MANIFEST_SHA256.json"))
        expected = {x["path"] for x in manifest["files"]}
        actual = set(z.namelist()) - {"MANIFEST_SHA256.json"}
        if expected != actual:
            raise ValueError("Unexpected/missing archive entries")
        for entry in manifest["files"]:
            payload = z.read(entry["path"])
            if len(payload) != entry["size"]:
                raise ValueError("Size mismatch: " + entry["path"])
            if hashlib.sha256(payload).hexdigest() != entry["sha256"]:
                raise ValueError("Hash mismatch: " + entry["path"])
        return {"pass": True, "members": len(z.namelist()),
                "artistic_gate": manifest["studio_gate"]}

if __name__ == "__main__":
    print(json.dumps(verify(Path(sys.argv[1])), indent=2))
