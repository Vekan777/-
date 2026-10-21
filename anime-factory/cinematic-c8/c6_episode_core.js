/* CINEMATIC C6 — season/episode/scene assembly, validation and subtitle timing.
   Original 3D C5 scene source is always retained verbatim inside each clip. */
(function(root){'use strict';
const SCHEMA='anime-c6-episode-production-v1';
const clone=x=>JSON.parse(JSON.stringify(x));
const id=()=>('clip-'+Math.random().toString(36).slice(2,11));
const clean=s=>String(s||'').trim();
function makeScene(p,name='Новая сцена',start=0,end=16){return{id:id(),name,in:start,out:end,project:clone(p)};}
function demo(p){let rootScene=clone(p), second=clone(p);second.title='Разворот боя';second.settings.cameraYaw=.55;second.settings.cameraDistance=.85;second.shots=second.shots.map(s=>({...s,camera:['close','orbit','track','low'][second.shots.indexOf(s)%4]}));
 const third=clone(p);third.title='Финальная контратака';third.settings.cameraYaw=-.4;
 return{schema:SCHEMA,version:'C6',seasonTitle:'Пепельный дозор · сезон 1 (демо)',episodes:[
 {id:'ep-01',name:'01 · Перед поединком',scenes:[makeScene(rootScene,'Встреча',0,4),makeScene(second,'Первое столкновение',4,9)]},
 {id:'ep-02',name:'02 · Контратака',scenes:[makeScene(third,'Возвращение бойца',9,13),makeScene(third,'Последний удар',13,16)]}
 ],updatedAt:'2026-10-21',manualReviews:{}};}
function runtime(scene){return scene.out-scene.in;}
function duration(ep){return ep.scenes.reduce((n,s)=>n+runtime(s),0)}
function scan(pack){let errors=[],warnings=[];
 if(!pack||typeof pack!=='object'||pack.schema!==SCHEMA)return{errors:['Неверная схема C6'],warnings:[]};
 if(!clean(pack.seasonTitle)||clean(pack.seasonTitle).length>150)errors.push('Название сезона: 1–150 символов');
 if(!Array.isArray(pack.episodes)||!pack.episodes.length||pack.episodes.length>12)return{errors:['Нужно 1–12 серий'],warnings};
 let ids=new Set();
 for(let [i,ep] of pack.episodes.entries()){
  if(!/^ep-[a-zA-Z0-9-]{1,24}$/.test(String(ep.id||''))||ids.has(ep.id))errors.push('Повторяющийся или неправильный ID серии '+(i+1));ids.add(ep.id);
  if(!clean(ep.name)||clean(ep.name).length>130)errors.push('Название серии '+(i+1));
  if(!Array.isArray(ep.scenes)||ep.scenes.length<1||ep.scenes.length>120){errors.push('В серии '+(i+1)+' должно быть 1–120 сцен');continue}
  let clipIds=new Set();
  for(let [j,s] of ep.scenes.entries()){
   let mark=`Серия ${i+1}, сцена ${j+1}`;
   if(!clean(s.id)||clipIds.has(s.id))errors.push(mark+': ID дублируется или пуст');clipIds.add(s.id);
   if(!clean(s.name)||clean(s.name).length>120)errors.push(mark+': название');
   if(!Number.isFinite(s.in)||!Number.isFinite(s.out)||s.in<0||s.out<=s.in||s.out-s.in<.2||s.out>120)errors.push(mark+': неверные границы');
   const p=s.project;
   if(!p||!['anime-c5-hybrid-3d-v1','anime-c4-hybrid-3d-v1'].includes(p.schema))errors.push(mark+': ожидается полный C5/C4 исходный JSON');
   if(!Number.isFinite(p?.duration)||s.out>p.duration+1e-6)errors.push(mark+': отрезок выходит за пределы 3D-сцены');
   if(!Array.isArray(p?.shots)||!p.shots.length||!Array.isArray(p?.subtitles))errors.push(mark+': отсутствует раскадровка или субтитры');
   if(!p?.motion?.keys?.hero||!p?.motion?.keys?.enemy)warnings.push(mark+': нет ключей C5, возможно это только C4');
   if(!p.audio?.base64&&!p.c7Voice?.enabled)warnings.push(mark+': русский голос не встроен, включите автосинтез C7 или импортируйте актёрскую дорожку');
   if(p?.models?.hero||p?.models?.enemy)warnings.push(mark+': импорт OBJ неподвижен относительно скелета; проверить анимацию вручную');
  }
  if(duration(ep)>3600)errors.push('Серия '+(i+1)+' длится больше часа');
 }
 if(JSON.stringify(pack).length>40e6)errors.push('Проект больше 40 МБ: разделите исходные медиа');
 return{errors,warnings};}
function locate(ep,time){if(!Number.isFinite(time))throw Error('Время не число');let cursor=0;for(let i=0;i<ep.scenes.length;i++){let s=ep.scenes[i],d=runtime(s);if(time<cursor+d||i===ep.scenes.length-1)return{index:i,scene:s,local:Math.min(s.out,Math.max(s.in,s.in+time-cursor)),start:cursor,end:cursor+d};cursor+=d;}throw Error('В серии нет сцен');}
function subtitles(ep){let entries=[],offset=0;for(const s of ep.scenes){for(const line of s.project.subtitles||[]){let a=Math.max(line.start,s.in),b=Math.min(line.end,s.out);if(b<=a||!clean(line.text))continue;entries.push({start:offset+a-s.in,end:offset+b-s.in,text:line.text,speaker:line.speaker||''});}offset+=runtime(s);}return entries;}
function srt(ep){let t=subtitles(ep);let fmt=x=>{let ms=Math.max(0,Math.round(x*1000)),a=Math.floor(ms/3600000),b=Math.floor(ms/60000)%60,c=Math.floor(ms/1000)%60,d=ms%1000;return `${String(a).padStart(2,'0')}:${String(b).padStart(2,'0')}:${String(c).padStart(2,'0')},${String(d).padStart(3,'0')}`};return t.map((v,i)=>`${i+1}\n${fmt(v.start)} --> ${fmt(v.end)}\n${v.text}`).join('\n\n')+'\n'}
function importC5(p){if(!p||!['anime-c5-hybrid-3d-v1','anime-c4-hybrid-3d-v1'].includes(p.schema))throw Error('Ожидается полный C5/C4 JSON');const fresh=demo(p);fresh.seasonTitle=clean(p.title)+' · сериал';fresh.episodes=[{id:'ep-01',name:'01 · '+clean(p.title),scenes:[makeScene(p,clean(p.title),0,p.duration)]}];return fresh;}
root.C6Core={SCHEMA,clone,makeScene,demo,duration,runtime,scan,locate,subtitles,srt,importC5};
})(typeof window!=='undefined'?window:globalThis);
