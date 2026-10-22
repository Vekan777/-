"""Verify CRC and per-member SHA-256 for C8 Rev16.7 downloaded ZIP."""
from pathlib import Path
from zipfile import ZipFile
import sys, json, hashlib

def verify(path):
    with ZipFile(path) as z:
        bad=z.testzip()
        if bad: raise ValueError('CRC_ERROR '+bad)
        manifest=json.loads(z.read('MANIFEST_SHA256.json'))
        expected={e['path'] for e in manifest['files']}
        found={n for n in z.namelist() if not n.endswith('/')}-{'MANIFEST_SHA256.json'}
        if found!=expected: raise ValueError('Member inventory mismatch')
        for e in manifest['files']:
            if '..' in Path(e['path']).parts or e['path'].startswith('/'):
                raise ValueError('Unsafe member')
            data=z.read(e['path'])
            if len(data)!=e['size'] or hashlib.sha256(data).hexdigest()!=e['sha256']:
                raise ValueError('File digest mismatch: '+e['path'])
        return {'pass':True,'files':len(expected),'production_gate':manifest['production_gate']}
if __name__=='__main__':
    print(json.dumps(verify(sys.argv[1]),indent=2))
