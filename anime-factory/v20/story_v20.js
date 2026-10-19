/* AI Anime Factory V20 — Story & Fight Continuity extension.
   Embedded inside original V19 IIFE by build_story_v20.py.
   Requires P, epIndex, scIndex, save(), drawScene(), QA(), download(),
   blobPNG(), impact19Of(), combat17Of(), combat18Continuity().
   This is a 2D animatic quality pipeline; no neural movie rendering.
*/
function v20SafeJsonClone(value){
  return JSON.parse(JSON.stringify(value));
}
function v20CarryUnknown(dst,src,depth=0){
  if(depth>24 || !src || typeof src!=='object' || !dst || typeof dst!=='object')return;
  if(Array.isArray(src)){
    if(!Array.isArray(dst))return;
    src.forEach((item,index)=>{
      let targetIndex=index;
      if(item&&typeof item==='object'&&item.id!=null){
        const found=dst.findIndex(e=>e&&typeof e==='object'&&String(e.id)===String(item.id));
        if(found>=0)targetIndex=found;
      }
      if(targetIndex<dst.length)v20CarryUnknown(dst[targetIndex],item,depth+1);
    });
    return;
  }
  if(Array.isArray(dst))return;
  for(const key of Object.keys(src)){
    if(key==='__proto__'||key==='constructor'||key==='prototype')continue;
    if(!Object.prototype.hasOwnProperty.call(dst,key)){
      Object.defineProperty(dst,key,{value:v20SafeJsonClone(src[key]),enumerable:true,writable:true,configurable:true});
    }else v20CarryUnknown(dst[key],src[key],depth+1);
  }
}
function migrate(raw){
  const old=migrateV19Original(raw),source=raw&&typeof raw==='object'?raw:{};
  v20CarryUnknown(old,source);
  if(source.storyV20&&typeof source.storyV20==='object')old.storyV20=v20SafeJsonClone(source.storyV20);
  if(source.version===20 && source.format==='AIAnimeFactoryProject')old.legacyOriginal=source.legacyOriginal||null;
  old.version=20;
  return old;
}
function v20Ensure(){
  if(!P)return;
  P.version=20;
  if(!P.storyV20||typeof P.storyV20!=='object')P.storyV20={};
  const o=P.storyV20;
  if(!Array.isArray(o.facts))o.facts=[];
  if(typeof o.note!=='string')o.note='';
  if(!Array.isArray(o.openThreads))o.openThreads=[];
  P.episodes.forEach((e,i)=>{
    if(!e.storyV20||typeof e.storyV20!=='object')e.storyV20={};
    const st=e.storyV20;
    if(typeof st.wound!=='string')st.wound=i?'Усталость после боя':'До первой битвы';
    if(typeof st.soulCost!=='string')st.soulCost=String(e.memoryLost||'Не указана');
    if(typeof st.clue!=='string')st.clue='';
    if(typeof st.payoff!=='string')st.payoff='';
    if(typeof st.notes!=='string')st.notes='';
    if(typeof st.location!=='string')st.location=e.scenes[0]?.place||'';
    if(typeof st.memoryJournal!=='string')st.memoryJournal='';
  });
}
function v20Episode(){v20Ensure();return P.episodes[clamp(epIndex,0,P.episodes.length-1)];}
function v20CanonLines(){
  v20Ensure();
  let lines=[
   'AI ANIME FACTORY V20 — СЮЖЕТНАЯ ПРЕЕМСТВЕННОСТЬ',
   'Проект: '+P.title,'Замысел: '+P.premise,
   'Персонажи: '+P.characters.map(c=>c.name+' ('+c.role+')').join('; '),
   'Неизменные правила:'
  ];
  (P.lore||[]).forEach((rule,i)=>lines.push((i+1)+'. '+(typeof rule==='string'?rule:JSON.stringify(rule))));
  lines.push('', 'СОБЫТИЯ И ПОСЛЕДСТВИЯ');
  for(const [i,e] of P.episodes.entries()){
   const x=e.storyV20||{},fights=e.scenes.filter(s=>s.kind==='fight');
   lines.push('Серия '+(i+1)+': '+e.title+' / '+e.arc);
   lines.push('Потеря памяти: '+(e.memoryLost||'нет данных')+'; цена призыва: '+(x.soulCost||'нет данных'));
   lines.push('Ранения: '+(x.wound||'нет данных')+'; дневник памяти: '+(x.memoryJournal||'не заполнен'));
   lines.push('Доверие: '+e.trust+'; близость: '+e.affection+'; локация: '+(x.location||''));
   lines.push('Улика: '+(x.clue||'нет')+'; последствие: '+(x.payoff||'нет'));
   lines.push('Боёв: '+fights.length+'; кадровые сцены: '+e.scenes.length);
   lines.push('Режиссёрские заметки: '+(x.notes||'нет'), '');
  }
  const qa=v20ContinuityQA();
  lines.push('КРИТИЧЕСКИЕ ПУНКТЫ И КАЧЕСТВО','Найдено: '+qa.length);
  for(const e of qa)lines.push('['+e.severity+'] '+e.message);
  lines.push('', 'ОГРАНИЧЕНИЕ: автоматические замечания — эвристика, не художественная экспертиза.');
  return lines.join('\n');
}
function v20ContinuityQA(){
  v20Ensure();
  const errors=[],warn=(message,severity='warning')=>errors.push({severity,message});
  const ids=new Set(),names=new Set();
  for(const c of P.characters){
    if(ids.has(String(c.id)))warn('Персонажи: повторяющийся ID '+c.id,'error');
    ids.add(String(c.id));
    if(names.has(c.name))warn('Персонажи: повтор имени '+c.name,'error');
    names.add(c.name);
    if(!c.goal?.trim())warn(c.name+': отсутствует цель');
  }
  if(P.characters.length<3)warn('Меньше трёх персонажей — проверьте состав сцены.');
  const hasBetrayal=P.episodes.some(e=>e.scenes.some(s=>s.kind==='betrayal'));
  const hasFight=P.episodes.some(e=>e.scenes.some(s=>s.kind==='fight'));
  if(!hasBetrayal)warn('Предательство не показано ни в одной сцене.');
  if(!hasFight)warn('Нет боевых сцен для проверки ресурсов и травм.');
  let prev=null,previousMemory=new Set(),betrayalHasOccurred=false;
  for(const [i,e] of P.episodes.entries()){
    const x=e.storyV20||{},no=i+1;
    if(!e.scenes?.length){warn('Серия '+no+' без сцен','error');continue;}
    if(!String(e.memoryLost||'').trim())warn('Серия '+no+': не указано, какое воспоминание потеряно.');
    if(String(e.memoryLost||'').trim()){
      const item=String(e.memoryLost).toLocaleLowerCase('ru');
      if(previousMemory.has(item))warn('Серия '+no+': повторно потеряно то же воспоминание — проверьте сюжет.');
      previousMemory.add(item);
    }
    if(!x.wound?.trim())warn('Серия '+no+': не описано физическое состояние после боя.');
    if(!x.soulCost?.trim()&&e.scenes.some(s=>s.kind==='fight'))warn('Серия '+no+': цена призыва душ не зафиксирована.');
    if(!x.payoff?.trim())warn('Серия '+no+': последствия событий не описаны в карточке.');
    if(prev){
      if(Number(e.trust)-Number(prev.trust)>28)warn('Серия '+no+': доверие резко выросло без указанной проверки причины.');
      if(Number(e.affection)-Number(prev.affection)>30)warn('Серия '+no+': романтическое развитие слишком резко.');
      if(e.scenes[0]?.place!==prev.scenes[prev.scenes.length-1]?.place&&!x.location?.trim())warn('Серия '+no+': смена локации без указания перехода.');
    }
    if(e.scenes.some(s=>s.kind==='betrayal' && /предатель|разорван|расплат|призна|предал/iu.test(s.title+' '+s.narration))){
      if(!betrayalHasOccurred && Number(e.trust)>60)warn('Серия '+no+': предательство показано, но доверие остаётся высоким.');
      betrayalHasOccurred=true;
    }
    for(const [j,s] of e.scenes.entries()){
      if(!s.title?.trim())warn('Серия '+no+', сцена '+(j+1)+': нет названия.');
      if(s.kind==='fight'){
        const hits=impact19Events(s);
        if(!hits.length)warn('Серия '+no+', '+s.title+': не назначены удары.');
        for(const issue of impact19Issues(s))warn('Серия '+no+', '+s.title+': '+issue);
      }
    }
    prev=e;
  }
  return errors;
}
function v20ShotPlan(){
  if(!P)return '';
  v20Ensure();
  const e=v20Episode(),shots=[];
  for(const [j,s] of e.scenes.entries()){
    const attacks=s.kind==='fight'?impact19Events(s):[];
    shots.push('СЦЕНА '+(j+1)+': '+s.title,'Локация: '+s.place,'Тип: '+s.kind,
      'Длительность: '+s.duration+' сек','Камера: '+s.camera,
      'Эмоциональная задача: '+(s.narration||'Сформулировать'),
      'Срабатывание ударов: '+(attacks.map(x=>x.sec.toFixed(2)+' с / '+x.outcome).join('; ')||'нет'),'');
  }
  return shots.join('\n');
}
function renderStoryV20(){
  if(!P)return;v20Ensure();
  $('v20-episode').innerHTML=P.episodes.map((e,i)=>'<option value="'+i+'">'+(i+1)+'. '+escapeHTML(e.title)+'</option>').join('');
  $('v20-episode').value=String(epIndex);
  const e=v20Episode(),x=e.storyV20;
  for(const field of ['wound','soulCost','clue','payoff','notes','location','memoryJournal'])$('v20-'+field).value=x[field]||'';
  $('v20-memoryLost').value=e.memoryLost||'';
  $('v20-trust').value=e.trust;
  $('v20-affection').value=e.affection;
  const issues=v20ContinuityQA(),fails=issues.filter(z=>z.severity==='error').length;
  $('v20-audit').textContent='Серий: '+P.episodes.length+' | замечаний: '+issues.length+' | ошибок: '+fails+'\n\n'+
    (issues.map(z=>'['+z.severity+'] '+z.message).join('\n')||'По правилам V20 замечаний нет; художественный просмотр всё равно нужен.');
  $('v20-summary').textContent='Канон V20 • серия '+(epIndex+1)+': '+e.arc+
      '\nБоёв: '+e.scenes.filter(s=>s.kind==='fight').length+
      '; последняя локация: '+(e.scenes[e.scenes.length-1]?.place||'?')+
      '\nИмпорт V19 и старых версий не удаляет неизвестные поля исходного JSON.';
}
function v20SaveStory(){
  if(!P)return;
  v20Ensure();
  const e=v20Episode(),x=e.storyV20;
  for(const field of ['wound','soulCost','clue','payoff','notes','location','memoryJournal'])x[field]=$('v20-'+field).value.slice(0,2500);
  e.memoryLost=$('v20-memoryLost').value.slice(0,400);
  e.trust=clamp(Number($('v20-trust').value)||0,0,100);
  e.affection=clamp(Number($('v20-affection').value)||0,0,100);
  save();renderAll();renderStoryV20();notify('V20: последствия и канон серии сохранены.');
}
function v20ReadableFight(){
  if(!P)return;
  const e=v20Episode(),fight=e.scenes.find(s=>s.kind==='fight');
  if(!fight)return notify('В выбранной серии нет боя.');
  const impact=impact19Of(fight);
  Object.assign(impact,{enabled:true,profile:'balanced',windup:160,recovery:210,
    lunge:69,recoil:58,shake:34,trail:74,sparks:64});
  const data=combat17Of(fight),beats=data.beats;
  if(beats.length>1)for(let i=0;i<beats.length;i++)beats[i].t=+(0.08+i/(beats.length-1)*0.84).toFixed(4);
  fight.storyDirectionV20={preset:'readable-impact',beatsRetimed:beats.length,kind:'2d-animatic'};
  save();renderAll();
  notify('V20: боевая хореография перенастроена без удаления техник и действий.');
}
async function v20ContactSheet(){
  const e=v20Episode(),s=e.scenes.find(z=>z.kind==='fight')||e.scenes[0];
  if(!s)throw Error('В серии нет сцен.');
  await preloadArtwork();
  const out=document.createElement('canvas');
  out.width=1280;out.height=720;
  const g=out.getContext('2d'),frame=document.createElement('canvas');
  frame.width=640;frame.height=360;
  const samples=[.12,.38,.64,.9];
  samples.forEach((pct,i)=>{
    drawScene(frame,s,pct*s.duration,false);
    const x=(i%2)*640,y=Math.floor(i/2)*360;
    g.drawImage(frame,x,y);
    g.fillStyle='rgba(2,9,18,.78)';g.fillRect(x+8,y+7,185,25);
    g.fillStyle='#ffffff';g.font='bold 15px sans-serif';
    g.fillText('ПЛАН '+(i+1)+' · '+Math.round(pct*100)+'%',x+18,y+25);
  });
  download('V20_EP'+String(e.number).padStart(2,'0')+'_FOUR_SHOTS.png',await blobPNG(out));
  notify('V20: контактный лист четырёх кадров PNG создан.');
}
function v20ExportBundle(){
  if(!P)return;
  v20Ensure();
  const data=[
    {name:'PROJECT_V20.json',data:JSON.stringify(P,null,2)},
    {name:'V20_CANON_REPORT_RU.txt',data:v20CanonLines()},
    {name:'V20_SHOT_PLAN_RU.txt',data:v20ShotPlan()},
    {name:'V20_QA_REPORT.json',data:JSON.stringify(v20ContinuityQA(),null,2)},
    {name:'README_RU.txt',data:'AI Anime Factory V20 — канон, цены силы, последствия и режиссёрские планы. Откройте PROJECT_V20.json во вкладке «Импортировать JSON».\nАвтоматическое QA — эвристика, не подтверждение художественного качества.'}
  ];
  makeZip(data).then(zip=>{download('AI_ANIME_V20_STORY_BUNDLE.zip',zip);notify('V20: ZIP с каноном и JSON создан и скачан.');})
               .catch(err=>notify('V20 ZIP: '+err.message));
}
$('v20-episode').onchange=ev=>{epIndex=Number(ev.target.value)||0;scIndex=0;renderAll();renderStoryV20();};
$('v20-save').onclick=v20SaveStory;
$('v20-check').onclick=renderStoryV20;
$('v20-fight').onclick=v20ReadableFight;
$('v20-png').onclick=async()=>{try{await v20ContactSheet();}catch(err){notify('V20 PNG: '+err.message);}};
$('v20-report').onclick=()=>download('V20_CANON_REPORT_RU.txt',new Blob([v20CanonLines()],{type:'text/plain;charset=utf-8'}));
$('v20-story-zip').onclick=v20ExportBundle;
