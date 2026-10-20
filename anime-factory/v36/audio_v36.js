/* AI Anime Factory V36 — additive audio/episode export.
   Audio metadata is in scene.audioV36; decoded file bytes stay in browser RAM.
   Timeline is exclusively the V35 plan. No scene durations or story are rewritten.
*/
const v36Assets=new WeakMap();
let v36Context=null,v36Master=null,v36Media=null;
let v36Sources=[],v36Active=false,v36At=0,v36Zero=0,v36RAF=0,v36Recorder=null;
function v36Of(scene){
 if(!scene.audioV36||typeof scene.audioV36!=='object'||Array.isArray(scene.audioV36))
  scene.audioV36={};
 for(const slot of ['voice','music','fx']){
  if(!scene.audioV36[slot]||typeof scene.audioV36[slot]!=='object')
   scene.audioV36[slot]={};
  const s=scene.audioV36[slot];
  s.name=String(s.name||'').slice(0,250);
  s.gain=Number.isFinite(Number(s.gain))?clamp(Number(s.gain),0,2):1;
  s.offset=Number.isFinite(Number(s.offset))?clamp(Number(s.offset),0,120):0;
 }
 return scene.audioV36;
}
function v36Episode(){
 if(!P)return null;
 return P.episodes[Number($('v36-episode').value)||0]||P.episodes[0]||null;
}
function v36Scene(){
 const e=v36Episode();return e?.scenes?.[Number($('v36-scene').value)||0]||null;
}
function v36Slot(){return $('v36-slot').value||'voice';}
function v36Buffer(scene,slot){return v36Assets.get(scene)?.[slot]||null;}
function v36Audio(){
 if(v36Context)return v36Context;
 const Factory=window.AudioContext||window.webkitAudioContext;
 if(!Factory)throw new Error('Web Audio API недоступен; используйте Chrome/Edge.');
 v36Context=new Factory();
 v36Master=v36Context.createGain();
 v36Master.gain.value=.75;
 v36Media=v36Context.createMediaStreamDestination();
 v36Master.connect(v36Media);
 v36Master.connect(v36Context.destination);
 return v36Context;
}
function v36Stop(){
 if(v36Active&&v36Context)v36At=Math.max(0,v36Context.currentTime-v36Zero);
 v36Active=false;
 if(v36RAF){cancelAnimationFrame(v36RAF);v36RAF=0;}
 for(const s of v36Sources){try{s.stop();}catch(_e){}try{s.disconnect();}catch(_e){}}
 v36Sources=[];
 if(v36Recorder&&v36Recorder.state!=='inactive'){
  try{v36Recorder.stop();}catch(_e){}
 }
 v36Recorder=null;
 if($('v36-play'))$('v36-play').textContent='Слушать + смотреть';
 if($('v36-export'))$('v36-export').disabled=false;
}
function v36Envelope(row,previous,clipStart,time){
 const fin=Math.max(.025,previous?.outgoing||0);
 const fout=Math.max(.025,row.outgoing||0);
 const a=clamp((time-clipStart)/fin,0,1);
 const b=clamp((row.end-time)/fout,0,1);
 return Math.min(a,b);
}
function v36Schedule(episode,from){
 const plan=v35Plan(episode),ctx=v36Context;
 for(const row of plan.rows){
  const previous=plan.rows[row.index-1]||null;
  for(const slot of ['music','fx','voice']){
   const cfg=v36Of(row.scene)[slot],buffer=v36Buffer(row.scene,slot);
   if(!cfg.name||!buffer||buffer.name!==cfg.name||!buffer.audio.duration)continue;
   const clipStart=row.start+cfg.offset;
   const clipEnd=slot==='music'?row.end:Math.min(row.end,clipStart+buffer.audio.duration);
   const first=Math.max(from,clipStart),last=clipEnd;
   if(first>=last-0.0001)continue;
   const src=ctx.createBufferSource(),gain=ctx.createGain();
   src.buffer=buffer.audio;src.loop=slot==='music';
   src.connect(gain);gain.connect(v36Master);
   const offset=first-clipStart;
   const sampleOffset=src.loop?offset%buffer.audio.duration:offset;
   const pts=[first,clipStart+Math.max(.025,previous?.outgoing||0),
    row.end-Math.max(.025,row.outgoing||0),last].filter(t=>t>first+.00001&&t<last+.00001);
   pts.push(last);pts.sort((a,b)=>a-b);
   const vol=t=>cfg.gain*v36Envelope(row,previous,clipStart,t);
   gain.gain.setValueAtTime(vol(first),v36Zero+first);
   for(const t of pts)gain.gain.linearRampToValueAtTime(vol(t),v36Zero+t);
   src.start(v36Zero+first,sampleOffset);
   src.stop(v36Zero+last+.002);
   v36Sources.push(src);
  }
 }
}
function v36Draw(){
 const ep=v36Episode(),plan=v35Plan(ep);
 if(!ep||!plan.rows.length)return;
 v36At=clamp(v36At,0,plan.duration);
 const state=v35Frame($('v36-preview'),ep,v36At);
 $('v36-position').value=plan.duration?Math.round(v36At/plan.duration*1000):0;
 $('v36-clock').textContent=v36At.toFixed(2)+' / '+plan.duration.toFixed(2)+
  ' с · сцена '+((state.row?.index??0)+1)+'/'+plan.rows.length+
  ' · '+(state.row?.title||'');
}
function v36Tick(){
 if(!v36Active)return;
 const plan=v35Plan(v36Episode());
 v36At=clamp(v36Context.currentTime-v36Zero,0,plan.duration);
 v36Draw();
 if(v36At>=plan.duration){v36Stop();return;}
 v36RAF=requestAnimationFrame(v36Tick);
}
async function v36Start(record){
 if(v36Active)return;
 const ep=v36Episode(),plan=v35Plan(ep);
 if(!ep||!plan.rows.length){notify('V36: нет сцен для экспорта.');return;}
 if(record&&(!window.MediaRecorder||!$('v36-preview').captureStream)){
  notify('Запись WebM недоступна в этом браузере.');return;
 }
 try{
  const ctx=v36Audio();
  await ctx.resume();
  await preloadArtwork();
  if(record)v36At=0;
  if(v36At>=plan.duration)v36At=0;
  v36Draw();
  const lead=.18;
  v36Zero=ctx.currentTime+lead-v36At;
  if(record){
   const canvasStream=$('v36-preview').captureStream(Number($('v36-fps').value)||6);
   const tracks=[...canvasStream.getVideoTracks(),...v36Media.stream.getAudioTracks()];
   const stream=new MediaStream(tracks);
   const mime=['video/webm;codecs=vp8,opus','video/webm;codecs=vp9,opus',
    'video/webm'].find(t=>MediaRecorder.isTypeSupported(t));
   if(!mime)throw new Error('MediaRecorder не поддерживает WebM/Opus.');
   const rec=new MediaRecorder(stream,{mimeType:mime,videoBitsPerSecond:1200000});
   const chunks=[];
   rec.ondataavailable=e=>{if(e.data.size)chunks.push(e.data);};
   rec.onerror=e=>notify('Ошибка записи V36: '+(e.error?.message||'MediaRecorder'));
   rec.onstop=()=>{
    for(const track of canvasStream.getTracks())track.stop();
    const blob=new Blob(chunks,{type:mime});
    if(blob.size>512){
     download('V36_EPISODE_'+slug(ep.title)+'.webm',blob);
     notify('V36: реальная серия WebM готова ('+blob.size+' байт). MP4: CONVERT_MP4_WINDOWS.bat.');
    }else notify('V36: запись не сохранила видеоданные.');
   };
   rec.start(1000);v36Recorder=rec;$('v36-export').disabled=true;
  }
  v36Schedule(ep,v36At);
  v36Active=true;
  $('v36-play').textContent='Остановить';
  v36RAF=requestAnimationFrame(v36Tick);
 }catch(err){
  v36Stop();
  notify('V36 Audio/Video: '+err.message);
 }
}
function v36Show(){
 if(!P)return;
 v36Stop();
 const sel=$('v36-episode'),old=sel.value;
 sel.innerHTML=P.episodes.map((e,i)=>
  '<option value="'+i+'">Серия '+e.number+' — '+escapeHTML(e.title)+'</option>').join('');
 sel.value=[...sel.options].some(o=>o.value===old)?old:String(epIndex);
 if(!sel.value&&P.episodes.length)sel.value='0';
 v36Scenes();
}
function v36Scenes(){
 v36Stop();
 const ep=v36Episode(),sel=$('v36-scene'),old=sel.value;
 sel.innerHTML=(ep?.scenes||[]).map((s,i)=>
  '<option value="'+i+'">'+(i+1)+'. '+escapeHTML(s.title)+'</option>').join('');
 sel.value=[...sel.options].some(o=>o.value===old)?old:'0';
 v36At=0;v36Controls();v36Draw();
}
function v36Controls(){
 const scene=v36Scene();if(!scene)return;
 const slot=v36Slot(),cfg=v36Of(scene)[slot],attached=v36Buffer(scene,slot);
 $('v36-gain').value=Math.round(cfg.gain*100);
 $('v36-gain-value').textContent=cfg.gain.toFixed(2);
 $('v36-offset').value=Math.round(cfg.offset*100);
 $('v36-asset').textContent=cfg.name?
  cfg.name+' · '+(attached&&attached.name===cfg.name?'аудио подключено':'необходимо повторно выбрать файл'):
  'Файл не выбран. Музыка повторяется до конца сцены, речь и эффекты — нет.';
 $('v36-audiofile').value='';
}
async function v36Attach(event){
 const scene=v36Scene(),slot=v36Slot(),file=event.target.files?.[0];
 if(!scene||!file)return;
 if(file.size>150*1024*1024){notify('Аудиофайл больше 150 МБ — выбран другой файл.');return;}
 try{
  const ctx=v36Audio(),bytes=await file.arrayBuffer();
  const decoded=await ctx.decodeAudioData(bytes);
  if(!decoded.duration||!Number.isFinite(decoded.duration))
   throw new Error('Аудиофайл не удалось декодировать.');
  if(!v36Assets.has(scene))v36Assets.set(scene,{});
  v36Assets.get(scene)[slot]={name:file.name,audio:decoded};
  v36Of(scene)[slot].name=file.name;
  save();v36Controls();
  notify('V36: '+slot+' — '+file.name+' ('+decoded.duration.toFixed(2)+' с)');
 }catch(err){notify('Ошибка аудиодекодирования: '+err.message);}
}
function v36Save(){
 const scene=v36Scene();if(!scene)return;
 const cfg=v36Of(scene)[v36Slot()];
 cfg.gain=clamp(Number($('v36-gain').value)/100,0,2);
 cfg.offset=clamp(Number($('v36-offset').value)/100,0,120);
 save();v36Controls();notify('V36: громкость и сдвиг звука сохранены.');
}
function v36Audit(){
 const issues=[];
 if(!P)return ['Проект не создан.'];
 for(const ep of P.episodes){
  const plan=v35Plan(ep);
  for(const row of plan.rows)for(const slot of ['voice','music','fx']){
   const cfg=v36Of(row.scene)[slot],asset=v36Buffer(row.scene,slot);
   const label='Серия '+ep.number+', сцена '+(row.index+1)+', '+slot+': ';
   if(cfg.name&&(!asset||asset.name!==cfg.name))
    issues.push(label+'файл '+cfg.name+' не подключён в текущем сеансе.');
   if(asset&&asset.name===cfg.name&&slot!=='music'&&
      cfg.offset+asset.audio.duration<row.duration-.02)
    issues.push(label+'звука меньше длительности сцены, после файла будет тишина.');
   if(cfg.offset>=row.duration&&cfg.name)
    issues.push(label+'сдвиг начинается после конца сцены.');
  }
 }
 return issues;
}
function v36Manifest(){
 if(!P)return {};
 return {format:'AIAnimeFactoryAudioEpisode/36',version:36,
  assembly:v35Manifest(),
  audio:P.episodes.map(e=>({number:e.number,title:e.title,
   scenes:(e.scenes||[]).map((s,i)=>({index:i,title:s.title,
    slots:Object.fromEntries(['voice','music','fx'].map(slot=>{
     const cfg=v36Of(s)[slot],loaded=v36Buffer(s,slot);
     return [slot,{name:cfg.name,gain:cfg.gain,offsetSeconds:cfg.offset,
       loadedInBrowser:Boolean(loaded&&loaded.name===cfg.name),
       loop:slot==='music'}];
    }))}))})),
  notes:['Звуковые файлы не встроены в JSON и HTML; переподключите их после перезагрузки.',
   'Временная шкала берётся из V35 без изменения оригинальных длительностей.'],
  warnings:v36Audit()};
}
$('v36-episode').onchange=v36Scenes;
$('v36-scene').onchange=()=>{v36Stop();v36Controls();};
$('v36-slot').onchange=()=>{v36Stop();v36Controls();};
$('v36-audiofile').onchange=v36Attach;
$('v36-gain').oninput=()=>{$('v36-gain-value').textContent=(Number($('v36-gain').value)/100).toFixed(2);};
$('v36-save').onclick=v36Save;
$('v36-position').oninput=e=>{v36Stop();v36At=v35Plan(v36Episode()).duration*Number(e.target.value)/1000;v36Draw();};
$('v36-play').onclick=()=>{if(v36Active)v36Stop();else v36Start(false);};
$('v36-stop').onclick=()=>{v36Stop();v36At=0;v36Draw();};
$('v36-export').onclick=()=>v36Start(true);
$('v36-audit').onclick=()=>{$('v36-result').textContent=v36Audit().join('\n')||
 'В V36 нет предупреждений по загруженным аудиофайлам.';};
$('v36-json').onclick=()=>download('V36_AUDIO_EPISODE.json',
 new Blob([JSON.stringify(v36Manifest(),null,2)],{type:'application/json;charset=utf-8'}));
