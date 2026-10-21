/* V49 UNIFIED PRODUCTION DESK — single guided surface around REAL
 * V20 story, V45 art, V46 animation, V47 audio and V48 episode pipeline.
 * Never declare finished based on the existence of a tab or mock records.
 * Small review ledger in P; full JSON backup stays an explicit user action.
 */
const v49Stages=[
 {id:'story',label:'Сценарий и канон',page:'story-v20',fallback:'bible'},
 {id:'art',label:'Персонажи и локации',page:'art-assets-v45'},
 {id:'animate',label:'2D движение / клипы',page:'animation-v46'},
 {id:'voice',label:'Голоса / музыка / губы',page:'voice-v47'},
 {id:'subtitles',label:'Субтитры / монтаж',page:'subtitles-v37',fallback:'episode-v48'},
 {id:'release',label:'Рендер серий / MP4',page:'episode-v48'}
];
let v49Episode=0,v49DraftedReport=null;
function v49Data(){
 if(!P.productionV49||typeof P.productionV49!=='object'||Array.isArray(P.productionV49))
  P.productionV49={reviews:{},notes:''};
 if(!P.productionV49.reviews||typeof P.productionV49.reviews!=='object')
  P.productionV49.reviews={};
 if(typeof P.productionV49.notes!=='string')P.productionV49.notes='';
 return P.productionV49;
}
function v49IssuesForEpisode(ep,index){
 const issues=[],counts={story:0,art:0,animate:0,voice:0,subtitles:0,release:0};
 const add=(stage,severity,message)=>{
  counts[stage]++;issues.push({stage,severity,message,episode:index+1});
 };
 if(!ep.scenes?.length)add('story','error','Нет сцен');
 if(!ep.title?.trim())add('story','error','Не задано название');
 if(!ep.storyV20?.wound?.trim())add('story','review','Не описано состояние героя после событий');
 if(!ep.storyV20?.payoff?.trim())add('story','review','Не описаны последствия сюжетных событий');
 const plan=v35Plan(ep);
 if(!Number.isFinite(plan.duration)||plan.duration<=0)add('release','error','Неправильная длительность серии');
 if(!Array.isArray(P.characters)||P.characters.length<2)add('art','error','Для сцены нужны минимум два персонажа');
 const cast=P.characters||[];
 for(const c of cast.slice(0,2)){
  const rig=c.productionRig,parts=rig?.parts||{};
  const count=['legs','cape','torso','arms','face','hair','weapon'].filter(n=>parts[n]?.image).length;
  if(count<7)add('art','review',c.name+': '+count+'/7 подготовленных PNG-слоёв, остаётся процедурная рисовка');
  if(count&&!(rig?.rights||'').trim())
   add('art','review',c.name+': не зафиксировано происхождение арта');
 }
 let animated=0,voiced=0,captioned=0,locationArt=0;
 for(const [j,scene] of ep.scenes.entries()){
  const tracks=scene.animationV46?.tracks||{};
  if(['hero','partner'].some(role=>Object.values(tracks[role]||{}).some(arr=>Array.isArray(arr)&&arr.length>=2)))
   animated++;
  const a=scene.audioV36||{};
  if(a.voice?.embeddedV47)voiced++;
  if((scene.subtitlesV37?.cues||[]).some(c=>c.text&&c.end>c.start))captioned++;
  if(scene.bgV45?.image)locationArt++;
  if(scene.bgV45?.image&&!scene.bgV45.rights?.trim())
   add('art','review','Сцена '+(j+1)+': у фона не указаны права');
  for(const slot of ['voice','music','fx']){
   if(a[slot]?.name&&!a[slot]?.embeddedV47)
    add('voice','review','Сцена '+(j+1)+': '+slot+' есть в описании, но не переносится с JSON');
  }
 }
 if(ep.scenes?.length){
  if(!animated)add('animate','review','Нет ≥2 ключей V46 на треке — движение может быть статичным');
  if(!voiced)add('voice','review','Не добавлены переносимые голосовые дорожки');
  if(!captioned)add('subtitles','review','Нет субтитров V37');
  if(!locationArt)add('art','review','Нет собственных импортированных локаций; используется процедурный фон');
 }
 const completed={story:counts.story===0,art:counts.art===0,
  animate:counts.animate===0,voice:counts.voice===0,
  subtitles:counts.subtitles===0,release:counts.release===0};
 return {number:ep.number,title:ep.title,duration:plan.duration,
  scenes:ep.scenes?.length||0,animated,voiced,captioned,locationArt,
  completed,issues};
}
function v49Audit(){
 if(!P)return {version:49,problems:[{severity:'error',message:'Проект не загружен'}]};
 const report=P.episodes.map(v49IssuesForEpisode);
 const all=report.flatMap(x=>x.issues),errors=all.filter(x=>x.severity==='error').length,
  warnings=all.filter(x=>x.severity==='review').length;
 // This is an engineering/delivery checklist, NOT an artistic certification.
 return {schema:'AIAnimeFactory/UnifiedStudioV49/1',version:49,
  title:P.title,episodes:report,characterCount:P.characters.length,
  errors,warnings,canRender:errors===0,requiresHumanReview:true,
  workflow:v49Stages.map(s=>({id:s.id,label:s.label})),
  criteria:'Technical readiness does not guarantee professional anime-quality or content licensing.',
  issues:all};
}
function v49Route(stage){
 const next=v49Stages.find(x=>x.id===stage);
 if(!next)return;
 const target=$$('nav.tabs [data-page]').find(b=>b.dataset.page===next.page)?
  next.page:next.fallback||next.page;
 show(target);
}
function v49Render(){
 if(!P)return;
 const audit=v49Audit();v49DraftedReport=audit;
 const reviews=v49Data().reviews;
 const selected=P.episodes[v49Episode]||P.episodes[0];
 $('v49-summary').textContent=P.title+' · '+P.episodes.length+' серий · '+
  audit.characterCount+' персонажей · '+audit.errors+' блокирующих ошибок / '+
  audit.warnings+' замечаний к ручной проверке';
 const select=$('v49-episode'),old=String(v49Episode);
 select.innerHTML=P.episodes.map((e,i)=>'<option value="'+i+'">'+
  (i+1)+'. '+escapeHTML(e.title)+'</option>').join('');
 select.value=old;
 const row=audit.episodes[v49Episode];
 const meta=reviews[String(v49Episode)]||{};
 $('v49-stage-list').innerHTML=v49Stages.map(stage=>{
  const n=row.issues.filter(issue=>issue.stage===stage.id).length;
  const approved=!!meta[stage.id];
  const status=n?'Замечаний: '+n:approved?'Проверено автором':'Нужна ручная приёмка';
  return '<div class="card" style="padding:12px;margin:8px 0">'+
    '<strong>'+escapeHTML(stage.label)+'</strong> · '+escapeHTML(status)+
    '<div class="flex">'+
    '<button data-v49-open="'+stage.id+'">Открыть редактор</button>'+
    '<label><input type="checkbox" data-v49-ok="'+stage.id+'" '+
      (approved?'checked':'')+'> Я лично проверил этот этап</label></div></div>';
 }).join('');
 for(const b of $$('[data-v49-open]'))b.onclick=()=>v49Route(b.dataset.v49Open);
 for(const box of $$('[data-v49-ok]'))box.onchange=()=>{
  const data=v49Data(),index=String(v49Episode);
  if(!data.reviews[index])data.reviews[index]={};
  data.reviews[index][box.dataset.v49Ok]=box.checked;
  save();v49Render();
 };
 $('v49-report').textContent='Серия '+(v49Episode+1)+' — '+row.title+
  ' · '+row.duration.toFixed(1)+' с · '+row.scenes+' сцен\n\n'+
  (row.issues.map(issue=>'['+issue.severity.toUpperCase()+'] '+
    issue.message).join('\n')||'Структурных замечаний нет. Нужна ручная художественная проверка.')+
  '\n\nИз всех этапов отмечено автором: '+
  v49Stages.filter(s=>meta[s.id]).length+'/'+v49Stages.length+
  '\n\nВажно: статус не является автоматической гарантией профессионального качества.';
 $('v49-notes').value=v49Data().notes;
 const blocking=audit.errors;
 $('v49-record').disabled=!!blocking;
 $('v49-readiness').textContent=blocking?
  'Блокирующие замечания — исправьте их перед выпуском.':
  'Нет блокирующих технических замечаний; перед публикацией проверьте изображения, звук, сюжет и права вручную.';
}
function v49Show(){
 if(!P)return;
 v49Episode=Math.max(0,Math.min(P.episodes.length-1,v49Episode));
 v49Render();
}
function v49Backup(){
 if(!P)return;
 download('V49_FULL_UNIFIED_BACKUP_WITH_AUDIO_AND_ART.json',
  new Blob([JSON.stringify(P,null,2)],{type:'application/json;charset=utf-8'}));
 notify('V49: сохранён ПОЛНЫЙ проект. Проверьте файл на диске.');
}
function v49ChecklistExport(){
 const audit=v49Audit(),reviews=v49Data().reviews;
 download('V49_PRODUCTION_READINESS.json',
  new Blob([JSON.stringify({...audit,reviews,
   manualNotes:v49Data().notes},null,2)],{type:'application/json;charset=utf-8'}));
}
function v49SelectEpisode(){
 v49Episode=Number($('v49-episode').value)||0;
 v49Render();
}
function v49QuickRender(){
 const ep=P.episodes[v49Episode];if(!ep)return;
 if(!v49Audit().canRender){notify('V49: исправьте блокирующие замечания.');return;}
 // Re-use the exact V48/V36 render contract; no fake combined video.
 show('episode-v48');
 $('v48-episode').value=String(v49Episode);
 $('v48-episode').dispatchEvent(new Event('change'));
 notify('V49: выбран эпизод '+ep.number+'; проверьте параметры и запишите WebM.');
}
function v49SaveNotes(){
 v49Data().notes=$('v49-notes').value.slice(0,8000);
 save();notify('V49: режиссёрские и художественные замечания сохранены.');
}
$('v49-episode').onchange=v49SelectEpisode;
$('v49-export-project').onclick=v49Backup;
$('v49-import-project').onclick=()=>$('project-file').click();
$('v49-export-checklist').onclick=v49ChecklistExport;
$('v49-record').onclick=v49QuickRender;
$('v49-save-notes').onclick=v49SaveNotes;
window.v49UnifiedBridge=Object.freeze({
 audit:()=>v49Audit(),
 fullProject:()=>JSON.parse(JSON.stringify(P)),
 select:index=>{v49Episode=Math.max(0,Math.min(P.episodes.length-1,index));v49Render();return v49Episode;},
 route:stage=>v49Route(stage)
});
