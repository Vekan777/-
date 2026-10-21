/* V50 FINAL QUALITY GATE — deterministic 2D project review, no fabricated
 * promises of professional results. All V19–V49 render and story systems stay
 * untouched; this module only audits and records user-owned signoff.
 */
const v50Checks=[
 {id:'story',label:'Сюжет, канон и преемственность'},
 {id:'art',label:'Изображения, персонажи, права'},
 {id:'movement',label:'Позы, движение и боевые исходы'},
 {id:'audio',label:'Голоса, музыка и синхронизация губ'},
 {id:'text',label:'Субтитры, титры и таймкоды'},
 {id:'delivery',label:'Экспорт, резервные копии и видео'},
 {id:'human',label:'Ручная художественная приёмка'}
];
let v50Selected=0;
function v50ReviewData(){
 if(!P.productionV50||typeof P.productionV50!=='object')
  P.productionV50={episodeReviews:{},notes:'',qaAccepted:false};
 if(!P.productionV50.episodeReviews||typeof P.productionV50.episodeReviews!=='object')
  P.productionV50.episodeReviews={};
 if(typeof P.productionV50.notes!=='string')P.productionV50.notes='';
 return P.productionV50;
}
function v50SafeImage(src){return typeof src==='string'&&/^data:image\/(png|jpeg|webp);base64,[A-Za-z0-9+/=]+$/.test(src);}
function v50SafeAudio(src){return typeof src==='string'&&/^data:audio\/[a-zA-Z0-9.+-]+;base64,[A-Za-z0-9+/=]+$/.test(src);}
function v50AuditProject(project){
 const errors=[],warnings=[],details=[],add=(stage,severity,location,problem)=>{
  const row={stage,severity,location,problem};
  (severity==='error'?errors:warnings).push(row);
  details.push(row);
 };
 if(!project||!Array.isArray(project.episodes)||!project.episodes.length){
  add('story','error','Проект','Нет эпизодов');
  return {schema:'AnimeFactory/V50/DeepAudit/1',version:50,errors,warnings,
    details,passed:false,manualAcceptanceRequired:true};
 }
 const ids=new Set(),names=new Set(),cast=project.characters||[];
 for(const [ci,c] of cast.entries()){
  const name=String(c?.name||'').trim(),id=String(c?.id??'');
  if(!name)add('story','error','Персонаж '+(ci+1),'Имя отсутствует');
  if(names.has(name))add('story','error','Персонаж '+(ci+1),'Повтор имени '+name);
  if(ids.has(id))add('story','error','Персонаж '+(ci+1),'Повтор ID '+id);
  ids.add(id);names.add(name);
  const rig=c?.productionRig;
  let count=0;
  for(const part of ['legs','cape','torso','arms','face','hair','weapon']){
   const image=rig?.parts?.[part]?.image;
   if(image){
    count++;
    if(!v50SafeImage(image))add('art','error',name+'/'+part,'Слой не является корректно оформленным PNG/JPEG/WebP data URL');
   }
  }
  if(!count)add('art','review',name,'Нет собственных cutout-слоёв — остаётся процедурная рисовка');
  if(count<7&&count>0)add('art','review',name,'Загружено '+count+'/7 слоёв, проверить контуры и позы');
  if(count&&!(rig?.rights||'').trim())add('art','review',name,'Нет записанных сведений об источнике изображения');
 }
 let totalSeconds=0,sceneCount=0,filledVoice=0,animatedScenes=0,subtitled=0,storyCount=0;
 const facts=project.storyV20?.facts||[];
 if(!Array.isArray(facts))add('story','error','Библия','Список сюжетных фактов повреждён');
 for(const [ei,ep] of project.episodes.entries()){
  const label='Серия '+(ei+1)+' — '+String(ep.title||'');
  if(!ep.scenes?.length){add('story','error',label,'Серия без сцен');continue;}
  if(!ep.title?.trim())add('story','error',label,'Нет названия');
  if(!ep.storyV20?.wound?.trim())add('story','review',label,'Не зафиксированы травмы/состояние героя');
  if(!ep.storyV20?.payoff?.trim())add('story','review',label,'Не указан результат развития сюжета');
  if(ep.storyV20)storyCount++;
  let duration=0;
  for(const [si,s] of ep.scenes.entries()){
   const where=label+' / сцена '+(si+1)+' '+String(s.title||'');
   sceneCount++;
   const length=Number(s.duration);
   if(!Number.isFinite(length)||length<=0||length>3600)
    add('delivery','error',where,'Неправильная или недопустимо большая длительность');
   else {duration+=length;totalSeconds+=length;}
   if(!s.title?.trim())add('story','error',where,'Нет названия сцены');
   if(!s.kind)add('story','review',where,'Не выбран тип сюжетного события');
   if(s.kind==='fight'&&!Array.isArray(s.beats))
    add('movement','error',where,'Потеряны исходные боевые события');
   if(s.bgV45?.image&&!v50SafeImage(s.bgV45.image))
    add('art','error',where,'Фоновый рисунок повреждён');
   if(s.bgV45?.image&&!s.bgV45.rights?.trim())
    add('art','review',where,'Не отмечены права на фон');
   let moving=false;
   for(const role of ['hero','partner'])for(const part of ['legs','cape','torso','arms','face','hair','weapon']){
    const keys=s.animationV46?.tracks?.[role]?.[part];
    if(!Array.isArray(keys))continue;
    if(keys.length>=2)moving=true;
    let prev=-1;
    for(const frame of keys){
     const t=Number(frame?.t);
     if(!Number.isFinite(t)||t<0||t>1||t<=prev)
      add('movement','error',where,role+'/'+part+': временные ключи повреждены или повторены');
     for(const field of ['x','y','angle','scale'])
      if(!Number.isFinite(Number(frame[field])))add('movement','error',where,role+'/'+part+': '+field+' не число');
     if(Number(frame.scale)<.3||Number(frame.scale)>2)
      add('movement','review',where,role+'/'+part+': необычный масштаб');
     prev=t;
    }
   }
   if(moving)animatedScenes++;
   const tracks=s.audioV36||{};
   for(const slot of ['voice','music','fx']){
    const a=tracks[slot]||{};
    if(a.embeddedV47){
     if(!v50SafeAudio(a.embeddedV47))
      add('audio','error',where,slot+': аудиоданные не являются корректным data URL');
     else if(slot==='voice')filledVoice++;
     if(a.embeddedV47.length>2_100_000)
      add('audio','review',where,slot+': слишком большой аудиоклип для localStorage');
    }else if(a.name){
     add('audio','review',where,slot+': файл указан, но его нет в переносимом JSON');
    }
    if(a.gain!==undefined&&(!Number.isFinite(Number(a.gain))||a.gain<0||a.gain>2))
     add('audio','error',where,slot+': коэффициент громкости повреждён');
    if(a.offset!==undefined&&(!Number.isFinite(Number(a.offset))||a.offset<0||a.offset>120))
     add('audio','error',where,slot+': смещение аудио повреждено');
    if(slot==='voice'&&a.waveV47&&!Array.isArray(a.waveV47))
     add('audio','error',where,'Повреждена амплитудная дорожка рта');
    if(slot==='voice'&&Array.isArray(a.waveV47)&&a.waveV47.some(q=>!Number.isFinite(Number(q))||q<0||q>1))
     add('audio','error',where,'Сигнал для синхронизации рта вне диапазона [0,1]');
   }
   const cues=s.subtitlesV37?.cues||[];
   if(Array.isArray(cues)){
    if(cues.length)subtitled++;
    let prev=-1;
    for(const cue of cues){
     const start=Number(cue.start),end=Number(cue.end);
     if(!Number.isFinite(start)||!Number.isFinite(end)||start<0||end<=start||end>length+.01)
      add('text','error',where,'Неверный таймкод субтитра');
     if(start<prev)add('text','review',where,'Непоследовательный порядок субтитров');
     prev=start;
    }
   }else add('text','error',where,'Повреждён формат субтитров');
  }
  if(duration>3600)add('delivery','review',label,'Продолжительность больше часа — пакетный рендер может быть долгим');
 }
 if(!animatedScenes)add('movement','review','Проект','Не найдено ни одной 2D-сцены с несколькими ручными ключами V46');
 if(!filledVoice)add('audio','review','Проект','Нет ни одной переносимой голосовой дорожки V47');
 if(!subtitled)add('text','review','Проект','Нет ни одной сцены с ручными субтитрами V37');
 const conclusion=errors.length?'blocked':'technical-review';
 return {schema:'AnimeFactory/V50/DeepAudit/1',version:50,
  project:String(project.title||''),characters:cast.length,episodes:project.episodes.length,
  sceneCount,storyCount,totalSeconds:Number(totalSeconds.toFixed(2)),
  animatedScenes,voiceScenes:filledVoice,subtitleScenes:subtitled,
  errors,warnings,details,passed:errors.length===0,status:conclusion,
  manualAcceptanceRequired:true,
  limitations:[
   'Автоматическое тестирование не подтверждает профессиональный художественный стиль.',
   'V46 поддерживает 2D-cutout ключи, но не гарантирует покадровое аниме студийного уровня.',
   'V47 связывает открытие рта с амплитудой звука, а не распознаёт фонемы.',
   'Для публикации нужны готовые авторские материалы и проверенные права на их использование.',
   'Пакетный MP4 требует Python + Chromium/Playwright + FFmpeg на Windows.',
   'Восстановление рендера осуществляется только по границе завершённой серии.'
  ]};
}
function v50SelectedEpisode(){return P?.episodes?.[v50Selected]||null;}
function v50Show(){
 if(!P)return;
 const ep=$('v50-episode'),old=String(v50Selected);
 ep.innerHTML=P.episodes.map((e,i)=>'<option value="'+i+'">'+
  (i+1)+'. '+escapeHTML(e.title)+'</option>').join('');
 ep.value=[...ep.options].some(o=>o.value===old)?old:'0';
 const audit=v50AuditProject(P);
 const review=v50ReviewData(),selectedReview=review.episodeReviews[String(v50Selected)]||{};
 $('v50-summary').textContent=audit.project+' · '+audit.episodes+' серий · '+
  audit.sceneCount+' сцен · '+audit.errors.length+' критических ошибок / '+
  audit.warnings.length+' замечаний';
 $('v50-status').textContent=audit.passed?
  'Нет блокирующих структурных ошибок. Для выпуска нужна РУЧНАЯ приёмка каждой серии и контроль реального видео.':
  'Найдены блокирующие ошибки. Исправьте их в рабочих редакторах до выпуска.';
 $('v50-evidence').textContent='Рисованные движения в '+audit.animatedScenes+
  ' сценах · озвучка в '+audit.voiceScenes+' сценах · субтитры в '+
  audit.subtitleScenes+' сценах.\n'+
  'Это подсчёт материалов, не независимая оценка художественного качества.';
 $('v50-checklist').innerHTML=v50Checks.map(k=>{
  const checked=!!selectedReview[k.id];
  const issues=audit.details.filter(x=>x.stage===k.id);
  return '<label style="display:block;margin:8px 0"><input type="checkbox" data-v50-review="'+k.id+
   '" '+(checked?'checked':'')+'> '+escapeHTML(k.label)+' — '+issues.length+
   ' обнаружено автоматически; проверено мною: '+(checked?'да':'нет')+'</label>';
 }).join('');
 for(const el of $$('[data-v50-review]'))el.onchange=()=>{
  const r=v50ReviewData();
  if(!r.episodeReviews[String(v50Selected)])r.episodeReviews[String(v50Selected)]={};
  r.episodeReviews[String(v50Selected)][el.dataset.v50Review]=el.checked;
  save();v50Show();
 };
 $('v50-notes').value=review.notes;
 $('v50-report').textContent=audit.details.map(a=>'['+a.severity+'] '+a.location+
  ' — '+a.problem).join('\n')||
  'Автоматические блокирующие ошибки и предупреждения не найдены.\nОднако требуется ручная проверка художественного результата.';
 const done=P.episodes.every((ep,i)=>
  v50Checks.every(k=>review.episodeReviews[String(i)]?.[k.id]));
 $('v50-signoff').textContent='Ручная приёмка: '+
  P.episodes.filter((e,i)=>v50Checks.every(k=>review.episodeReviews[String(i)]?.[k.id])).length+
  '/'+P.episodes.length+' серий. '+
  (done&&audit.passed?'Все ручные этапы отмечены; качество видео и права проверьте отдельно.':
    'Финальный профессиональный выпуск НЕ подтверждён.');
}
function v50SaveNotes(){
 v50ReviewData().notes=$('v50-notes').value.slice(0,12000);
 save();notify('V50: итоговые замечания сохранены в полном JSON.');
}
function v50Report(){
 const report=v50AuditProject(P),review=v50ReviewData();
 return {...report,authorReviews:review.episodeReviews,authorNotes:review.notes,
  disclaimer:'Автоматический отчёт не является художественным сертификатом или лицензией.'};
}
function v50Export(){
 download('V50_FINAL_DEEP_QA_REPORT.json',
  new Blob([JSON.stringify(v50Report(),null,2)],{type:'application/json;charset=utf-8'}));
}
function v50Backup(){
 download('V50_FINAL_FULL_PROJECT_BACKUP.json',
  new Blob([JSON.stringify(P,null,2)],{type:'application/json;charset=utf-8'}));
 notify('V50: полный проект (арт, аудио, движения, сюжет) сохранён на диск.');
}
function v50GoToStage(){
 show('unified-v49');$('v49-episode').value=String(v50Selected);
 $('v49-episode').dispatchEvent(new Event('change'));
}
function v50VisitRender(){
 show('episode-v48');$('v48-episode').value=String(v50Selected);
 $('v48-episode').dispatchEvent(new Event('change'));
}
$('v50-episode').onchange=()=>{v50Selected=Number($('v50-episode').value)||0;v50Show();};
$('v50-notes-save').onclick=v50SaveNotes;
$('v50-export').onclick=v50Export;
$('v50-full-backup').onclick=v50Backup;
$('v50-import').onclick=()=>$('project-file').click();
$('v50-go-stages').onclick=v50GoToStage;
$('v50-go-render').onclick=v50VisitRender;
window.v50FinalQA=Object.freeze({
 audit:()=>v50AuditProject(P),
 report:()=>v50Report(),
 auditForeign:data=>v50AuditProject(data),
 currentProject:()=>JSON.parse(JSON.stringify(P))
});
