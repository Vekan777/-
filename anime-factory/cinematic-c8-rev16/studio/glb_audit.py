#!/usr/bin/env python3
"""Simple standalone glTF 2.0 GLB structural audit for exported C8 Rev16 character assets."""
import argparse, json, struct, hashlib
from pathlib import Path
def audit(path):
    b=Path(path).read_bytes()
    if len(b)<20 or b[:4]!=b'glTF':raise ValueError("GLB header missing")
    version,length=struct.unpack_from("<II",b,4)
    if version!=2 or length!=len(b):raise ValueError("GLB truncated/incompatible")
    size,chunk=struct.unpack_from("<I4s",b,12)
    if chunk!=b"JSON":raise ValueError("Missing JSON chunk")
    d=json.loads(b[20:20+size])
    p=[q for m in d.get("meshes",[]) for q in m.get("primitives",[])]
    result={
       "sha256":hashlib.sha256(b).hexdigest(),
       "skin_count":len(d.get("skins",[])),
       "max_facial_morph_targets":max([len(q.get("targets",[])) for q in p] or [0]),
       "embedded_image_count":len(d.get("images",[])),
       "animation_count":len(d.get("animations",[])),
       "pass":len(d.get("skins",[]))>=2 and len(d.get("images",[]))>=6 and max([len(q.get("targets",[])) for q in p] or [0])>=24,
       "artistic_gate":"PRODUCTION_BLOCKED",
       "note":"Structural pass alone does not prove professional animation quality"
    }
    return result
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("glb")
    a=p.parse_args()
    result=audit(a.glb)
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result["pass"] else 2)
