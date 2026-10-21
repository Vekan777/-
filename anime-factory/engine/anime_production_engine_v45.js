/* Anime Production Engine: shared modular 2D production kernel.
 * V45 implements deterministic story/relations/camera/combat plans and
 * asset validation. V46-V50 have explicit interfaces, NOT imaginary features.
 * Works offline in a browser, and as pure JS in Node.js regression tests.
 */
const AnimeProductionEngineV45=(()=>{
 'use strict';
 const VERSION='45.0.0';
 const DOMAINS=Object.freeze({
  story:'ready',world:'ready',relationships:'ready',combat:'ready',
  characters:'ready',artAssets:'ready',camera:'ready',
  animation:'v46_integration',voice:'v47_integration',
  lipSync:'v47_integration',sound:'v47_integration',
  editing:'v48_integration',seasonRender:'v48_integration',
  unifiedApp:'v49_integration',deepQA:'v50_gate',threeD:'separate_after_v50'
 });
 const REL=['friendship','love','trust','betrayal','reconciliation'];
 const SCENES=['opening','friendship','romance','betrayal','fight','ending',
  'dialogue','reconciliation','quiet','intimacy'];
 function norm(n,min,max,alt){const a=Number(n);return Number.isFinite(a)?Math.min(max,Math.max(min,a)):alt;}
 function text(t,max=160){return typeof t==='string'?t.slice(0,max):'';}
 function clone(s){return JSON.parse(JSON.stringify(s));}
 function normalizeAsset(input){
  const a=input&&typeof input==='object'?input:{};
  const out={id:text(a.id,80),kind:text(a.kind,20),name:text(a.name,160),
   rights:text(a.rights,500),width:norm(a.width,1,8192,640),
   height:norm(a.height,1,8192,960),alpha:a.alpha===true,
   layers:Array.isArray(a.layers)?a.layers.map(x=>({
    name:text(x.name,48),pivot:{
      x:norm(x.pivot?.x,-300,300,0),y:norm(x.pivot?.y,-300,300,0)},
    active:x.active!==false
   })):[]};
  return out;
 }
 function buildWorld(project){
  return {title:text(project?.title||'Новый сериал',200),
   seed:norm(project?.seed,0,4294967295,6060),
   lore:Array.isArray(project?.lore)?clone(project.lore):[],
   locations:[...new Set((project?.episodes||[]).flatMap(ep=>
    (ep.scenes||[]).map(sc=>text(sc.place,160))).filter(Boolean))],
   characters:(project?.characters||[]).map(c=>({
    id:text(c.id,80),name:text(c.name,160),
    role:text(c.role,80),goal:text(c.goal,500),secret:text(c.secret,500)
   }))};
 }
 function relationshipTimeline(project){
  let affection=norm(project?.episodes?.[0]?.affection,0,100,25);
  let trust=norm(project?.episodes?.[0]?.trust,0,100,50);
  const sequence=[];
  for(const ep of project?.episodes||[]){
   for(const s of ep.scenes||[]){
    const kind=text(s.kind,35);
    const was={trust,affection};
    if(kind==='friendship'){trust=norm(trust+4,0,100,trust);}
    if(kind==='romance'){affection=norm(affection+5,0,100,affection);}
    if(kind==='betrayal'){trust=norm(trust-20,0,100,trust);}
    if(kind==='reconciliation'){trust=norm(trust+11,0,100,trust);}
    sequence.push({episode:ep.number,scene:text(s.title,120),
      type:kind,prior:was,after:{trust,affection}});
   }
  }
  return sequence;
 }
 function framePlan(project,epIndex=0){
  const ep=project?.episodes?.[epIndex];
  if(!ep)return {episode:epIndex+1,duration:0,shots:[]};
  let at=0;
  const shots=[];
  for(const sc of ep.scenes||[]){
   const duration=norm(sc.duration,0.1,3600,5);
   const actor=sc.kind==='romance'?'partner':'hero';
   const camera=text(sc.camera||'Средний план',180);
   shots.push({id:shots.length+1,scene:text(sc.title,160),
     kind:text(sc.kind,40),location:text(sc.place,160),
     actor,camera,start:Number(at.toFixed(3)),
     end:Number((at+duration).toFixed(3)),seconds:duration});
   at+=duration;
  }
  return {episode:ep.number,title:text(ep.title,160),
    duration:Number(at.toFixed(3)),shots};
 }
 function combatPlan(scene){
  if(scene?.kind!=='fight')return [];
  const data=Array.isArray(scene?.combatV17?.beats)?scene.combatV17.beats:[];
  const fallback=Array.isArray(scene?.beats)?scene.beats:[];
  return (data.length?data:fallback).map((b,index)=>{
   const item=typeof b==='object'&&b?b:{label:String(b)};
   return {index:index+1,label:text(item.label||item.name||item.text||String(b),180),
    actor:text(item.actor||'hero',20),
    result:['hit','block','dodge','miss'].includes(item.outcome)?item.outcome:'unresolved',
    authoritative:false};
  });
 }
 function validate(project,assets=[]){
  const errors=[],warnings=[];
  if(!project||!Array.isArray(project.episodes)||!project.episodes.length)
   errors.push('Нет сцен или серий');
  if(!Array.isArray(project?.characters)||project.characters.length<2)
   errors.push('Для аниме-эпизода необходимы как минимум два персонажа');
  const cast=new Set((project?.characters||[]).map(c=>text(c.name)));
  for(const [ei,e] of (project?.episodes||[]).entries()){
   if(!Array.isArray(e.scenes)||!e.scenes.length)
    errors.push('Серия '+(ei+1)+' не содержит сцен');
   for(const [si,s] of (e.scenes||[]).entries()){
    const label='Серия '+(ei+1)+', сцена '+(si+1)+': ';
    if(!s.title)warnings.push(label+'нет названия');
    if(!Number.isFinite(Number(s.duration))||Number(s.duration)<=0)
     errors.push(label+'некорректная длительность');
    if(s.kind==='fight'&&!Array.isArray(s.beats))
     warnings.push(label+'нет списка фаз боя');
    for(const line of s.lines||[]){
     if(!cast.has(line.speaker))warnings.push(label+'неизвестный голос '+text(line.speaker));
    }
   }
  }
  for(const a of assets.map(normalizeAsset)){
   if(!a.rights.trim())warnings.push('Нет указания прав на материал '+a.name);
   if(a.width>8192||a.height>8192)errors.push('Материал слишком велик '+a.name);
   for(const layer of a.layers){
    if(!Number.isFinite(layer.pivot.x)||!Number.isFinite(layer.pivot.y))
     errors.push('Ошибка pivot '+a.name+'/'+layer.name);
   }
  }
  const topology=relationshipTimeline(project||{});
  for(const e of topology){
   if(e.type==='romance'&&e.after.affection<e.prior.affection)
    errors.push('Некорректная дуга отношений');
  }
  return {ok:errors.length===0,errors,warnings,episodeCount:project?.episodes?.length||0,
   characterCount:project?.characters?.length||0};
 }
 function snapshot(project,assets=[]){
  const world=buildWorld(project);
  const videos=(project?.episodes||[]).map((e,i)=>framePlan(project,i));
  const relationship=relationshipTimeline(project);
  const audit=validate(project,assets);
  return {schema:'AnimeProductionEngine/V45',version:VERSION,
   domains:DOMAINS,world,episodes:videos,relationships:relationship,
   assets:assets.map(normalizeAsset),audit,
   note:'Production plan only. Video/audio pipelines V46–V50 have separate acceptance gates.'};
 }
 return Object.freeze({VERSION,DOMAINS,REL,SCENES,
  buildWorld,relationshipTimeline,framePlan,combatPlan,validate,snapshot,normalizeAsset});
})();
