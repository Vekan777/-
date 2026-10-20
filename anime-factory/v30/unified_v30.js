/* AI Anime Factory V30 — unified, non-destructive continuity and integrity QA.
   Every version V19–V29 is preserved. Only explicit baseline/save actions
   add V30 metadata; no audit rewrites the canon, battles or any scene.
*/
function v30Stable(v,depth=0){
 if(depth>40)return '"[depth-limit]"';
 if(v===null||typeof v!=='object')return JSON.stringify(v)??'null';
 if(Array.isArray(v))return '['+v.map(x=>v30Stable(x,depth+1)).join(',')+']';
 return '{'+Object.keys(v).filter(k=>k!=='__proto__').sort().map(k=>
  JSON.stringify(k)+':'+v30Stable(v[k],depth+1)).join(',')+'}';
}
function v30Hash(value){
 const s=v30Stable(value);
 let h=2166136261;
 for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619);}
 return (h>>>0).toString(16).padStart(8,'0')+':'+s.length;
}
function v30ProjectView(project){
 const p=project||P;
 if(!p)return {metadata:{},cast:[],episodes:[]};
 const characters=Array.isArray(p.characters)?p.characters:[];
 const episodes=Array.isArray(p.episodes)?p.episodes:[];
 // Exclude exactly the V30 review metadata, not any earlier version fields.
 const extra={...p};
 delete extra.unifiedV30;delete extra.characters;delete extra.episodes;
 delete extra.version;
 return {
  metadata:{digest:v30Hash(extra),title:p.title||'',loreDigest:v30Hash(p.lore||[])},
  cast:characters.map((c,i)=>({
   index:i,id:String(c.id??''),name:String(c.name??''),
   digest:v30Hash(c)})),
  episodes:episodes.map((e,i)=>({
   index:i,number:e.number,title:e.title||'',digest:v30Hash(
    Object.fromEntries(Object.entries(e).filter(([k])=>k!=='scenes'))),
   scenes:(Array.isArray(e.scenes)?e.scenes:[]).map((s,j)=>({
    index:j,title:String(s.title||''),kind:String(s.kind||''),
    digest:v30Hash(s)
   }))
  }))
 };
}
function v30Snapshot(){
 if(!P)return;
 const baseline=v30ProjectView(P);
 // Make it impossible to replace the baseline silently through audit.
 P.unifiedV30={schema:'AIAnimeFactoryV30Baseline/1',
  capturedAt:new Date().toISOString(),baseline};
 save();
 v30Run();
 notify('V30: контрольная точка сюжета и персонажей сохранена.');
}
function v30Issue(list,level,category,message,ei=null,si=null){
 list.push({level,category,message,episode:ei,scene:si});
}
function v30Compare(now,old,issues){
 if(!old){v30Issue(issues,'info','эталон','Контрольная точка ещё не создана: сохраните резерв JSON и зафиксируйте эталон.');return;}
 if(old.metadata?.digest!==now.metadata.digest)
  v30Issue(issues,'warning','проект','Метаданные проекта, правила мира или титры изменились со времени контрольной точки.');
 if(old.metadata?.loreDigest!==now.metadata.loreDigest)
  v30Issue(issues,'warning','канон','Свод правил мира изменён: проверьте согласованность способностей и цены призыва.');
 const oldCast=old.cast||[],nowCast=now.cast||[];
 if(nowCast.length<oldCast.length)
  v30Issue(issues,'error','персонажи','Уменьшилось число персонажей: '+oldCast.length+' → '+nowCast.length);
 else if(nowCast.length>oldCast.length)
  v30Issue(issues,'info','персонажи','Добавлены персонажи: '+oldCast.length+' → '+nowCast.length);
 for(const [i,c] of oldCast.entries()){
  const match=nowCast.find(x=>x.id===c.id)||nowCast[i];
  if(!match){v30Issue(issues,'error','персонажи','Исчез персонаж: '+c.name);continue;}
  if(match.digest!==c.digest)
   v30Issue(issues,'warning','персонажи','Изменены данные героя «'+c.name+'»: сверить характер, биографию, силу и внешний вид.');
 }
 const oldEpisodes=old.episodes||[],nowEpisodes=now.episodes||[];
 if(nowEpisodes.length<oldEpisodes.length)
  v30Issue(issues,'error','сезон','Уменьшилось число серий: '+oldEpisodes.length+' → '+nowEpisodes.length);
 for(const [i,e] of oldEpisodes.entries()){
  const present=nowEpisodes[i];
  if(!present){v30Issue(issues,'error','сезон','Удалена серия '+(i+1)+' «'+e.title+'»',i);continue;}
  if(e.digest!==present.digest)
   v30Issue(issues,'warning','сюжет','Изменены структура/сюжет/последствия серии «'+e.title+'».',i);
  const a=e.scenes||[],b=present.scenes||[];
  if(b.length<a.length)v30Issue(issues,'error','сцены',
   'В серии «'+e.title+'» стало меньше сцен: '+a.length+' → '+b.length,i);
  for(const [j,sc] of a.entries()){
   if(!b[j]){v30Issue(issues,'error','сцены','Исчезла сцена «'+sc.title+'».',i,j);continue;}
   if(sc.digest!==b[j].digest)v30Issue(issues,'warning','сцены',
    'Изменилась сцена «'+sc.title+'» (текст, бой, звук или визуальные настройки).',i,j);
  }
 }
}
function v30Audit(){
 if(!P)return [];
 const issues=[],snapshot=v30ProjectView(P);
 const old=P.unifiedV30?.baseline||null;
 v30Compare(snapshot,old,issues);
 // Reuse the existing canon and continuity checks; do not invent a plot.
 try{for(const item of v20ContinuityQA())
  v30Issue(issues,item.severity==='error'?'error':'warning',
   'преемственность V20',item.message);}catch(e){
  v30Issue(issues,'error','анализ сюжета','Ошибка анализа V20: '+String(e.message||e));}
 // Historical renderer and motion QA must remain visible in one place.
 for(const [category,fn] of [
  ['визуал V21',v21VisualQA],['актёры V22',v22ActingQA],
  ['персонажи V23',v23CharacterQA],['движения V24',v24MotionQA],
  ['бой V25',v25QA],['камера V26',v26QA],['мир V27',v27QA],
  ['взаимодействие V28',v28QA],['ритм V29',v29QA]
 ]){
  try{for(const problem of fn())v30Issue(issues,'warning',category,String(problem));}
  catch(e){v30Issue(issues,'error',category,'Анализ завершился ошибкой: '+String(e.message||e));}
 }
 // Structural diagnostics are separately indexed so failures are clickable.
 const ids=new Set();
 for(const [i,c] of (P.characters||[]).entries()){
  const id=String(c.id??'');
  if(ids.has(id))v30Issue(issues,'error','персонажи','Повтор ID персонажа '+id);
  ids.add(id);
  if(!String(c.name||'').trim())
   v30Issue(issues,'error','персонажи','Персонаж '+(i+1)+' без имени.');
 }
 for(const [i,e] of (P.episodes||[]).entries()){
  if(!Array.isArray(e.scenes)||!e.scenes.length){
   v30Issue(issues,'error','сцены','Серия '+(i+1)+' не содержит сцен.',i);continue;
  }
  for(const [j,s] of e.scenes.entries()){
   if(!Number.isFinite(Number(s.duration))||Number(s.duration)<=0)
    v30Issue(issues,'error','тайминг','Сцена «'+s.title+'»: некорректная длительность.',i,j);
   if(s.kind==='fight'&&!s.combatV17)
    v30Issue(issues,'warning','бой','Боевая сцена «'+s.title+'»: проверьте события V17.',i,j);
   if(typeof s.narration==='string'&&!s.narration.trim())
    v30Issue(issues,'info','текст','Сцена «'+s.title+'» без закадрового текста.',i,j);
  }
 }
 return issues;
}
function v30Counts(issues){
 return {error:issues.filter(x=>x.level==='error').length,
  warning:issues.filter(x=>x.level==='warning').length,
  info:issues.filter(x=>x.level==='info').length};
}
function v30Report(issues=v30Audit()){
 const counts=v30Counts(issues),lines=[
  'AI ANIME FACTORY V30 — ОБЪЕДИНЁННАЯ ПРОВЕРКА КАЧЕСТВА',
  'Проект: '+(P?.title||'не открыт'),
  'Серий: '+(P?.episodes?.length||0),
  'Сцен: '+(P?.episodes||[]).reduce((n,e)=>n+(e.scenes?.length||0),0),
  'Персонажей: '+(P?.characters?.length||0),
  'Эталон: '+(P?.unifiedV30?.capturedAt||'нет'),
  'Ошибок: '+counts.error+'; предупреждений: '+counts.warning+
   '; сведений: '+counts.info,''];
 for(const x of issues)lines.push('['+x.level.toUpperCase()+'] '+x.category+
  (x.episode==null?'':' / серия '+(x.episode+1))+
  (x.scene==null?'':' / сцена '+(x.scene+1))+': '+x.message);
 if(!issues.length)lines.push('Автоматических замечаний не найдено.');
 lines.push('','Проверка основана на кодовых эвристиках и контрольных хешах.',
  'Она не доказывает художественное качество или отсутствие сюжетных противоречий.',
  'В V30 нет автоматического удаления/переписывания сцен или канона.');
 return lines.join('\n');
}
function v30Run(){
 if(!P)return;
 const issues=v30Audit(),count=v30Counts(issues);
 $('v30-summary').textContent='Ошибок: '+count.error+
  ' · предупреждений: '+count.warning+' · замечаний: '+count.info+
  ' · эталон: '+(P.unifiedV30?.capturedAt||'не создан');
 const filter=$('v30-filter').value;
 const filtered=issues.filter(x=>filter==='all'||x.level===filter);
 const colors={error:'#ffbbb0',warning:'#f5d39a',info:'#bad8f4'};
 $('v30-results').innerHTML=filtered.length?filtered.slice(0,300).map((x,i)=>
  '<div class="note" style="margin:6px 0;color:'+colors[x.level]+'">'+
  '<b>'+escapeHTML(x.level.toUpperCase()+' · '+x.category)+'</b>: '+
  escapeHTML(x.message)+
  (x.episode!=null?'<button type="button" data-v30-episode="'+x.episode+
   '" data-v30-scene="'+(x.scene??0)+'">Открыть сцену</button>':'')+'</div>'
 ).join(''):'<p class="muted">По этому фильтру замечаний нет.</p>';
 $('v30-results').querySelectorAll('button[data-v30-episode]').forEach(b=>{
  b.onclick=()=>{
   selectScene(Number(b.dataset.v30Episode),Number(b.dataset.v30Scene));
   show('script');
  };
 });
 $('v30-stage').textContent=P.episodes.map(e=>'Серия '+e.number+
  ' · '+e.title+' · сцен '+(e.scenes?.length||0)).join('\n');
 v30Frame();
}
function v30Frame(){
 if(!P)return;
 const s=scene(),t=s.duration*(Number($('v30-position').value)||0)/100;
 drawScene($('v30-preview'),s,t,false);
 $('v30-caption').textContent='Серия '+(epIndex+1)+' · '+s.title+
  ' · '+t.toFixed(2)+' с · реальный рендер V29.';
}
function v30Backup(){
 if(!P)return;
 download('AI_ANIME_V30_COMPLETE_PROJECT_BACKUP.json',
  new Blob([JSON.stringify(P,null,2)],{type:'application/json;charset=utf-8'}));
 notify('V30: скачан полный JSON проекта.');
}
function v30DownloadReport(){
 if(!P)return;
 download('AI_ANIME_V30_AUDIT_REPORT_RU.txt',
  new Blob([v30Report()],{type:'text/plain;charset=utf-8'}));
}
function v30Manifest(){
 if(!P)return;
 const data={schema:'AIAnimeFactoryV30Continuity/1',
  baseline:P.unifiedV30?.baseline||null,
  capturedAt:P.unifiedV30?.capturedAt||null,
  current:v30ProjectView(P),issues:v30Audit()};
 download('AI_ANIME_V30_INTEGRITY_REPORT.json',
  new Blob([JSON.stringify(data,null,2)],{type:'application/json;charset=utf-8'}));
}
async function v30Sheet(){
 if(!P)return;await preloadArtwork();
 const e=ep(),s=e.scenes[scIndex];
 const board=document.createElement('canvas'),scratch=document.createElement('canvas');
 board.width=1280;board.height=720;scratch.width=640;scratch.height=360;
 const g=board.getContext('2d');
 for(const [i,pct] of [.12,.35,.62,.88].entries()){
  drawScene(scratch,s,s.duration*pct,false);
  const x=(i%2)*640,y=Math.floor(i/2)*360;g.drawImage(scratch,x,y);
  g.fillStyle='rgba(4,10,23,.82)';g.fillRect(x+7,y+8,230,26);
  g.fillStyle='#e6dbc9';g.font='bold 13px Arial';
  g.fillText('V30 КАДР '+(i+1)+' / '+Math.round(pct*100)+'%',x+16,y+26);
 }
 download('V30_SCENE_CONTACT_SHEET_'+slug(s.title)+'.png',await blobPNG(board));
 notify('V30: четыре контрольных кадра сохранены.');
}
$('v30-run').onclick=v30Run;
$('v30-snapshot').onclick=v30Snapshot;
$('v30-backup').onclick=v30Backup;
$('v30-report').onclick=v30DownloadReport;
$('v30-manifest').onclick=v30Manifest;
$('v30-filter').onchange=v30Run;
$('v30-position').oninput=v30Frame;
$('v30-sheet').onclick=async()=>{try{await v30Sheet();}catch(e){notify('V30 PNG: '+e.message);}};
