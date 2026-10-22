"""C8 Rev16.5 release verifier: checks CRC, member sizes and SHA-256 before launching."""
from pathlib import Path
from zipfile import ZipFile
import json
import hashlib
import sys

def verify(path: Path):
    with ZipFile(path) as z:
        damaged = z.testzip()
        if damaged:
            raise ValueError("Corrupt ZIP member: " + damaged)
        manifest = json.loads(z.read("MANIFEST_SHA256.json"))
        entries = manifest["files"]
        expected_names = {e["path"] for e in entries}
        received_names = set(z.namelist()) - {"MANIFEST_SHA256.json"}
        if expected_names != received_names:
            raise ValueError("Manifest and archive entry names differ")
        for entry in entries:
            contents = z.read(entry["path"])
            if len(contents) != entry["size"]:
                raise ValueError("Size mismatch: " + entry["path"])
            if hashlib.sha256(contents).hexdigest() != entry["sha256"]:
                raise ValueError("SHA256 mismatch: " + entry["path"])
        return {
            "passed": True,
            "archive_members": len(entries) + 1,
            "studio_release_gate": manifest["qa"]["production"]
        }

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python verify_zip.py path-to-release.zip")
    print(json.dumps(verify(Path(sys.argv[1])), indent=2))
