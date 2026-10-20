/* AI Anime Factory V35 — REAL EPISODE ASSEMBLY.
   Uses V19–V34 drawScene for every source frame. Story, events and
   original scene durations remain authoritative and untouched.
   Per-scene outgoing dissolves create a deterministic combined timeline.
*/
function v35Of(s){
 if(!s.assemblyV35||typeof s.assemblyV35!=='object'||Array.isArray(s.assemblyV35))
  s.assemblyV35={};
 const a=s.assemblyV35;
 a.transition=Number.isFinite(Number(a.transition))?clamp(Number(a.transition),0,1.5):.35;
 a.enabled=a.enabled!==false;
 return a;
}
function v35Duration(s){return Math.max(.05,Number(s?.duration)||.05);}
function v35Transition(s,next){
 if(!next)return 0;
 const o=v35Of(s);
 return o.enabled?Math.min(o.transition,v35Duration(s)/3,v35Duration(next)/3,1.5):0;
}
function v35Plan(episode){
 const scenes=Array.isArray(episode?.scenes)?episode.scenes:[];
 let cursor=0;
 const rows=scenes.map((s,i)=>{
  const d=v35Duration(s),next=scenes[i+1],cross=v35Transition(s,next);
  const row={index:i,title:String(s.title||'Сцена '+(i+1)),
   scene:s,start:cursor,end:cursor+d,duration:d,outgoing:cross,
   kind:s.kind};
  cursor+=d-cross;
  return row;
 });
 return {episode:episode?.number??0,rows,duration:rows.length?rows[rows.length-1].end:0};
}
function v35Find(episode,sec){
 const plan=v35Plan(episode),t=clamp(Number(sec)||0,0,plan.duration);
 let index=0;
 for(let i=1;i<plan.rows.length;i++)
  if(t>=plan.rows[i].start)index=i;
 return {plan,t,index,row:plan.rows[index]||null,
  previous:plan.rows[index-1]||null};
}
function v35Frame(canvas,episode,sec){
 const g=canvas.getContext('2d'),w=canvas.width,h=canvas.height;
 g.clearRect(0,0,w,h);
 const state=v35Find(episode,sec),row=state.row;
 if(!row)return state;
 const prior=state.previous,overlap=prior?prior.outgoing:0;
 const inTime=state.t-row.start;
 const isBlend=overlap>.001&&inTime<overlap&&prior;
 if(isBlend){
  drawScene(v35Scratch(w,h),prior.scene,
   clamp(state.t-prior.start,0,prior.duration),false);
  g.drawImage(v35Canvas,0,0);
  drawScene(v35Scratch(w,h),row.scene,clamp(inTime,0,row.duration),false);
  g.save();g.globalAlpha=clamp(inTime/overlap,0,1);
  g.drawImage(v35Canvas,0,0);g.restore();
 }else{
  drawScene(canvas,row.scene,clamp(inTime,0,row.duration),false);
 }
 return state;
}
let v35Canvas=null;
function v35Scratch(w,h){
 if(!v35Canvas)v35Canvas=document.createElement('canvas');
 if(v35Canvas.width!==w)v35Canvas.width=w;
 if(v35Canvas.height!==h)v35Canvas.height=h;
 return v35Canvas;
}
function v35Episode(){
 if(!P)return null;
 const i=Number($('v35-episode').value)||0;
 return P.episodes[i]||P.episodes[0]||null;
}
function v35SelectedScene(){
 const e=v35Episode();if(!e)return null;
 return e.scenes[Number($('v35-scene').value)||0]||e.scenes[0]||null;
}
function v35Audit(){
 const issues=[];
 if(!P)return ['Проект ещё не открыт.'];
 for(const e of P.episodes){
  const list=e.scenes||[];
  if(!list.length){issues.push('Серия '+e.number+': отсутствуют сцены.');continue;}
  const plan=v35Plan(e);
  let totalSource=0,totalOverlap=0;
  for(let i=0;i<list.length;i++){
   const s=list[i],d=Number(s.duration),row=plan.rows[i];
   if(!Number.isFinite(d)||d<=0)
    issues.push('Серия '+e.number+', '+s.title+': некорректная длительность.');
   if(d<.5)issues.push('Серия '+e.number+', '+s.title+': сцена короче 0.5 секунды.');
   if(d>90)issues.push('Серия '+e.number+', '+s.title+': очень длинная сцена, проверьте темп.');
   if(v35Of(s).transition>row.outgoing+.02&&i<list.length-1)
    issues.push('Серия '+e.number+', '+s.title+
     ': переход автоматически ограничен третью длины соседних сцен.');
   if(i===list.length-1&&v35Of(s).transition>0)
    issues.push('Серия '+e.number+': переход из последней сцены не используется.');
   totalSource+=row.duration;totalOverlap+=row.outgoing;
  }
  if(Math.abs(plan.duration-(totalSource-totalOverlap))>.001)
   issues.push('Серия '+e.number+': ошибка расчёта временной шкалы.');
  try{
   for(const remark of v34Review()){
    if(remark.startsWith('Серия '+e.number+','))issues.push(remark);
   }
  }catch(error){issues.push('Ошибка проверки стыков V34: '+error.message);}
 }
 return issues;
}
function v35Report(){
 if(!P)return 'Нет проекта.';
 const lines=['AI ANIME FACTORY V35 — СБОРКА СЕРИЙ / ПРОДАКШН',
  P.title,'Источники V19–V34 и длительности сцен не переписываются.',''];
 for(const e of P.episodes){
  const plan=v35Plan(e);
  lines.push('Серия '+e.number+' — '+e.title+' · общая длина '+plan.duration.toFixed(2)+' с');
  for(const r of plan.rows)
   lines.push(' '+String(r.index+1).padStart(2,'0')+' · '+r.title+
    ' · начало '+r.start.toFixed(2)+' с · длительность '+r.duration.toFixed(2)+
    ' с · наложение '+r.outgoing.toFixed(2)+' с');
  lines.push('');
 }
 lines.push('ПРОВЕРКА ПРОДАКШНА:',...(v35Audit().length?v35Audit():
  ['Предупреждений по эвристическим правилам нет.']),
  '','Сборка в браузере показывает последовательность видео без смешивания звуковых дорожек.',
  'Это 2D-аниматик, а не финальный аудиовизуальный монтаж в MP4.');
 return lines.join('\n');
}
function v35Manifest(){
 if(!P)return {};
 return {format:'AIAnimeFactoryEpisodeAssembly/35',version:35,title:P.title,
  episodes:P.episodes.map(e=>{
   const p=v35Plan(e);
   return {number:e.number,title:e.title,totalSeconds:p.duration,
    scenes:p.rows.map(r=>({index:r.index,title:r.title,kind:r.kind,
     startSeconds:r.start,durationSeconds:r.duration,
     endSeconds:r.end,overlapSeconds:r.outgoing}))};
  }),warnings:v35Audit()};
}
let v35Playing=false,v35At=0,v35Stamp=0,v35RAF=0;
function v35Pause(){
 v35Playing=false;
 if(v35RAF){cancelAnimationFrame(v35RAF);v35RAF=0;}
 v35Stamp=0;
 if($('v35-play'))$('v35-play').textContent='Воспроизвести';
}
function v35Clock(stamp){
 if(!v35Playing)return;
 const dt=v35Stamp?Math.min((stamp-v35Stamp)/1000,.14):0;
 v35Stamp=stamp;
 const episode=v35Episode(),plan=v35Plan(episode);
 v35At=Math.min(plan.duration,v35At+dt);
 v35Render();
 if(v35At>=plan.duration){v35Pause();return;}
 v35RAF=requestAnimationFrame(v35Clock);
}
function v35Toggle(){
 if(v35Playing){v35Pause();return;}
 const e=v35Episode(),p=v35Plan(e);
 if(!p.rows.length)return;
 if(v35At>=p.duration)v35At=0;
 v35Playing=true;v35Stamp=0;
 $('v35-play').textContent='Пауза';
 v35RAF=requestAnimationFrame(v35Clock);
}
function v35Seek(sec){
 const plan=v35Plan(v35Episode());
 v35At=clamp(Number(sec)||0,0,plan.duration);v35Render();
}
function v35Render(){
 const e=v35Episode(),plan=v35Plan(e);
 if(!e||!plan.rows.length)return;
 const state=v35Frame($('v35-preview'),e,v35At);
 const next=state.row?.index??0;
 $('v35-progress').value=plan.duration?Math.round(v35At/plan.duration*1000):0;
 $('v35-time').textContent=v35At.toFixed(2)+' / '+plan.duration.toFixed(2)+
  ' с · сцена '+(next+1)+'/'+plan.rows.length+
  ' · '+(state.row?.title||'');
 $('v35-sequence').textContent=plan.rows.map(r=>
  (r.index===next?'▶ ':'  ')+(r.index+1)+'. '+r.title+
  ' · '+r.start.toFixed(2)+'–'+r.end.toFixed(2)+
  ' с · переход '+r.outgoing.toFixed(2)+' с').join('\n');
}
function v35Show(){
 if(!P)return;
 v35Pause();
 const select=$('v35-episode'),old=select.value;
 select.innerHTML=P.episodes.map((e,i)=>
  '<option value="'+i+'">Серия '+e.number+' — '+escapeHTML(e.title)+'</option>').join('');
 select.value=[...select.options].some(o=>o.value===old)?old:String(epIndex);
 if(!select.value&&P.episodes.length)select.value='0';
 v35SceneList();
}
function v35SceneList(){
 v35Pause();
 const e=v35Episode();
 const select=$('v35-scene'),old=select.value;
 select.innerHTML=(e?.scenes||[]).map((s,i)=>
  '<option value="'+i+'">'+(i+1)+' — '+escapeHTML(s.title)+'</option>').join('');
 select.value=[...select.options].some(o=>o.value===old)?old:'0';
 v35SceneControls();v35At=0;v35Render();
}
function v35SceneControls(){
 const scene=v35SelectedScene();if(!scene)return;
 const o=v35Of(scene);
 $('v35-enabled').checked=o.enabled;
 $('v35-transition').value=Math.round(o.transition*100);
 $('v35-transition-n').textContent=o.transition.toFixed(2);
}
function v35Save(){
 const s=v35SelectedScene();if(!s)return;
 const o=v35Of(s);
 o.enabled=$('v35-enabled').checked;
 o.transition=clamp((Number($('v35-transition').value)||0)/100,0,1.5);
 save();v35Render();v35SceneControls();
 notify('V35: наложение соседних сцен сохранено без изменения сюжетных кадров.');
}
async function v35Sheet(){
 await preloadArtwork();
 const e=v35Episode(),p=v35Plan(e);if(!p.rows.length)return;
 const frame=document.createElement('canvas'),board=document.createElement('canvas');
 frame.width=640;frame.height=360;board.width=1920;board.height=720;
 const g=board.getContext('2d');
 const midpoint=p.duration*.5;
 const cut=p.rows[1]?.start??midpoint;
 const times=[0,p.duration*.16,Math.max(0,cut-.07),
  Math.min(p.duration,cut+.07),p.duration*.78,Math.max(0,p.duration-.001)];
 for(const [i,t] of times.entries()){
  const state=v35Frame(frame,e,t);
  const x=(i%3)*640,y=Math.floor(i/3)*360;g.drawImage(frame,x,y);
  g.fillStyle='rgba(3,10,23,.86)';g.fillRect(x+8,y+8,310,28);
  g.fillStyle='#f5e3c8';g.font='bold 13px Arial';
  g.fillText('V35 '+(i+1)+' / '+t.toFixed(2)+' с / сцена '+(state.index+1),x+16,y+27);
 }
 download('V35_EPISODE_SIX_FRAMES_'+slug(e.title)+'.png',await blobPNG(board));
 notify('V35: шесть реальных кадров из последовательности серии экспортированы.');
}
$('v35-episode').onchange=v35SceneList;
$('v35-scene').onchange=v35SceneControls;
$('v35-transition').oninput=e=>{$('v35-transition-n').textContent=(Number(e.target.value)/100).toFixed(2);};
$('v35-progress').oninput=e=>v35Seek(v35Plan(v35Episode()).duration*Number(e.target.value)/1000);
$('v35-play').onclick=v35Toggle;
$('v35-start').onclick=()=>{v35Pause();v35Seek(0);};
$('v35-save').onclick=v35Save;
$('v35-audit').onclick=()=>{$('v35-audit-result').textContent=v35Audit().join('\n')||
 'Эвристических замечаний по сценам и монтажным стыкам не обнаружено.';};
$('v35-report').onclick=()=>download('V35_EPISODE_ASSEMBLY_RU.txt',
 new Blob([v35Report()],{type:'text/plain;charset=utf-8'}));
$('v35-json').onclick=()=>download('V35_EPISODE_ASSEMBLY.json',
 new Blob([JSON.stringify(v35Manifest(),null,2)],{type:'application/json;charset=utf-8'}));
$('v35-sheet').onclick=async()=>{try{await v35Sheet();}catch(err){notify('V35 PNG: '+err.message);}};
