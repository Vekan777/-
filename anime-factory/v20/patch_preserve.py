#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebuilt V20.3 preservation patch over genuine V19 HTML.
Adds lossless extensions import metadata; keeps V19 animation renderer unchanged.
This does not replace the original historical V20 browser-only download.
"""
from __future__ import annotations
import argparse
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
OPEN="function migrate(raw){"
NEXT="function ep(){"
SIGNATURE="v203PreservationRebuilt"

JS = r"""
function preserve203Key(x){
  if(!x||typeof x!=='object')return null;
  if(x.id!==undefined)return 'id:'+String(x.id);
  if(x.title!==undefined)return 'title:'+String(x.title)+'|'+String(x.kind||'');
  if(x.name!==undefined)return 'name:'+String(x.name);
  if(x.number!==undefined)return 'num:'+String(x.number);
  if(x.t!==undefined)return 'time:'+String(Number(x.t));
  return null;
}
function preserve203Missing(into,source,depth){
  if(depth>30||!source||typeof source!=='object'||!into||typeof into!=='object')return;
  if(Array.isArray(source)){
    if(!Array.isArray(into))return;
    const visited=new Set();
    source.forEach((old,i)=>{
      const key=preserve203Key(old);
      let n=-1;
      if(key!==null)n=into.findIndex((v,j)=>!visited.has(j)&&preserve203Key(v)===key);
      if(n<0 && key===null && source.length===into.length && i<into.length)n=i;
      if(n>=0){visited.add(n);preserve203Missing(into[n],old,depth+1);}
    });
    return;
  }
  if(Array.isArray(into))return;
  Object.keys(source).forEach(k=>{
    if(k==='__proto__'||k==='constructor'||k==='prototype')return;
    if(!Object.prototype.hasOwnProperty.call(into,k)){
      Object.defineProperty(into,k,{value:source[k],writable:true,enumerable:true,configurable:true});
    } else preserve203Missing(into[k],source[k],depth+1);
  });
}
function migrate(raw){
  const migrated=migrateOriginalV19(raw);
  preserve203Missing(migrated,raw,0);
  migrated.legacyOriginal=raw;
  migrated.v203PreservationRebuilt={base:'V19',status:'candidate',preservesUnknownFields:true};
  return migrated;
}
"""

def patch(text):
    if SIGNATURE in text:
        raise ValueError("Already patched")
    if text.count(OPEN)!=1 or text.count(NEXT)!=1:
        raise ValueError("Unexpected V19 layout")
    if "AIAnimeFactoryProject" not in text or "combatV19" not in text:
        raise ValueError("Wrong source")
    result=text.replace(OPEN,"function migrateOriginalV19(raw){",1)
    result=result.replace(NEXT,JS+"\n"+NEXT,1)
    assert SIGNATURE in result and "function migrateOriginalV19(raw){" in result
    return result

def test():
    text=SOURCE.read_text(encoding="utf-8")
    converted=patch(text)
    assert converted.count("function migrateOriginalV19(raw){")==1
    assert "function preserve203Missing(" in converted
    assert "legacyOriginal=raw" in converted
    assert "combatV19" in converted
    assert len(converted)>len(text)
    print("PRESERVATION PATCH STATIC TEST PASS")
    print("NOTE: no Windows browser/renders tested")

def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--source",default=str(SOURCE))
    cli.add_argument("--output")
    cli.add_argument("--selftest",action="store_true")
    a=cli.parse_args()
    if a.selftest:
        test();return
    path=Path(a.source)
    dest=Path(a.output or path.with_name("AI_Anime_Factory_V20_3_PRESERVATION.html"))
    if dest.resolve()==path.resolve():
        raise ValueError("Never overwrite V19 original")
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(patch(path.read_text(encoding="utf-8")),encoding="utf-8")
    print(dest)

if __name__=="__main__":
    main()
