/* AI Anime Factory V47: actual portable audio and waveform-driven 2D lip animation.
 * Audio bytes live in scene.audioV36[slot].embeddedV47 inside full project JSON.
 * AudioBuffer is lazily re-created after reload. Never call text-heuristic mouth
 * when a valid waveform is present. Not phoneme/ASR forced alignment.
 */
const v47OldMouth=mouth;
const v47Slots=['voice','music','fx'];
const v47MaxClip=1500000;
let v47Seen=0,v47Busy=false;
function v47AudioBytes(bytes){
 const input=new Uint8Array(bytes),pieces=[];
 for(let i=0;i<input.length;i+=16384){
  const piece=input.subarray(i,i+16384);
  let t='';for(const x of piece)t+=String.fromCharCode(x);
  pieces.push(t);
 }
 return btoa(pieces.join(''));
}
function v47DecodeBytes(encoded){
 const str=atob(encoded),data=new Uint8Array(str.length);
 for(let i=0;i<str.length;i++)data[i]=str.charCodeAt(i);
 return data.buffer;
}
function v47Wave(buffer,rate=50){
 if(!buffer?.numberOfChannels)return [];
 const audio=buffer.getChannelData(0),hop=Math.max(1,Math.floor(buffer.sampleRate/rate));
 const points=[];
 for(let at=0;at<audio.length;at+=hop){
  let sum=0,count=0;
  for(let i=at;i<Math.min(audio.length,at+hop);i++){sum+=audio[i]*audio[i];count++;}
  points.push(Math.sqrt(sum/Math.max(1,count)));
  if(points.length>=rate*600)break; // 10-minute voice cap, never unbounded arrays
 }
 const ordered=[...points].sort((a,b)=>a-b),p95=ordered[Math.min(ordered.length-1,Math.floor(ordered.length*.95))]||.01;
 return points.map(x=>Number(clamp(x/(p95*.87),0,1).toFixed(3)));
}
function v47Of(scene,slot){
 const cfg=v36Of(scene)[slot];
 if(cfg.embeddedV47&&typeof cfg.embeddedV47!=='string')cfg.embeddedV47='';
 if(!Array.isArray(cfg.waveV47))cfg.waveV47=[];
 cfg.mouthEnabledV47=cfg.mouthEnabledV47!==false;
 cfg.mouthX=clamp(Number(cfg.mouthX)||0,-45,45);
 cfg.mouthY=clamp(Number(cfg.mouthY)||0,-45,45);
 cfg.speakerV47=String(cfg.speakerV47||P?.characters?.[0]?.name||'').slice(0,160);
 return cfg;
}
async function v47KeepAudio(scene,slot,file){
 if(!scene||!v47Slots.includes(slot)||!file)return;
 if(file.size>v47MaxClip)throw Error('Для переносимого проекта ограничение 1,5 МБ на аудиоклип. Используйте сжатый OGG/MP3 или разделите запись.');
 if(!['audio/wav','audio/x-wav','audio/wave','audio/mpeg','audio/mp3','audio/ogg','audio/webm','audio/mp4',''].includes(file.type))
  throw Error('Поддерживаются WAV/MP3/OGG/WebM/M4A, если их может декодировать браузер.');
 const input=await file.arrayBuffer(),context=v36Audio();
 const decoded=await context.decodeAudioData(input.slice(0));
 if(!decoded.duration||decoded.duration>600)throw Error('Длительность клипа должна быть от 0 до 600 секунд.');
 const cfg=v47Of(scene,slot),prev={...cfg};
 const existing=v36Assets.get(scene)||{};
 const old=existing[slot];
 const mime=file.type||'audio/wav';
 const embedded='data:'+mime+';base64,'+v47AudioBytes(input);
 const wave=slot==='voice'?v47Wave(decoded):[];
 cfg.embeddedV47=embedded;
 cfg.waveV47=wave;
 cfg.sampleRateV47=50;
 cfg.name=file.name.slice(0,250);
 cfg.durationV47=decoded.duration;
 existing[slot]={name:cfg.name,audio:decoded};
 v36Assets.set(scene,existing);
 // LocalStorage is small. Always verify persisted audio, never claim success if
 // the browser quota rejected the save. File export remains available.
 const serialized=JSON.stringify(P);
 try{
  localStorage.setItem(storageKey,serialized);
  const copy=localStorage.getItem(storageKey);
  if(!copy||copy.length!==serialized.length)throw Error('Browser storage readback mismatch');
 }catch(e){
  Object.assign(cfg,prev);
  if(old)existing[slot]=old;else delete existing[slot];
  throw Error('Недостаточно места в локальном хранилище. Сохраните проект JSON; уменьшите число/размер аудиоклипов. '+e.message);
 }
 return {name:cfg.name,duration:decoded.duration,bytes:input.byteLength,points:wave.length};
}
async function v47RestoreScene(scene){
 if(!scene)return;
 const context=v36Audio(),meta=v36Of(scene);
 for(const slot of v47Slots){
  const cfg=v47Of(scene,slot);
  const existing=v36Buffer(scene,slot);
  if(existing?.name===cfg.name)continue;
  if(!/^data:audio\/[\w.+-]+;base64,/.test(cfg.embeddedV47||''))continue;
  try{
   const encoded=cfg.embeddedV47.split(',',2)[1];
   if(encoded.length>v47MaxClip*1.4)throw Error('Stored audio exceeds safe import limit');
   const audio=await context.decodeAudioData(v47DecodeBytes(encoded));
   const found=v36Assets.get(scene)||{};
   found[slot]={name:cfg.name,audio};
   v36Assets.set(scene,found);
   if(slot==='voice'&&!cfg.waveV47.length)cfg.waveV47=v47Wave(audio);
  }catch(err){notify('V47: аудио '+cfg.name+' не восстановлено: '+err.message);}
 }
}
async function v47RestoreEpisode(ep){
 for(const s of ep?.scenes||[])await v47RestoreScene(s);
}
const v47PriorMouth=mouth;
mouth=function(s,c,sec){
 const cfg=v47Of(s,'voice');
 const wav=cfg.waveV47;
 if(!cfg.name||!cfg.mouthEnabledV47||!wav.length)return v47PriorMouth(s,c,sec);
 if(cfg.speakerV47!==c.name)return 0;
 const line=activeLine(s,sec);
 if(line&&line.speaker!==c.name)return 0;
 const t=sec-cfg.offset;
 if(t<0||t>=wav.length/(cfg.sampleRateV47||50))return 0;
 const x=t*(cfg.sampleRateV47||50),i=Math.floor(x),fract=x-i;
 const a=Number(wav[i])||0,b=Number(wav[i+1]??a)||0;
 // RMS amplitude is authentic sound energy aligned to clip timing.
 return clamp(a+(b-a)*fract,0,1);
};
function v47PaintMouthOnCutout(ctx,s,c,t){
 const cfg=v47Of(s,'voice');
 if(!cfg.mouthEnabledV47||!cfg.waveV47?.length||
     !productionOf(c).parts.face?.image)return;
 const opening=mouth(s,c,t);
 const x=cfg.mouthX,y=cfg.mouthY;
 ctx.save();ctx.translate(x,-195+y);
 ctx.fillStyle='#32172b';ctx.strokeStyle='#b77b86';
 ctx.lineWidth=1.7;ctx.beginPath();
 ctx.ellipse(0,0,7+opening*2,1.1+opening*8,0,0,Math.PI*2);
 ctx.fill();ctx.stroke();ctx.restore();
}
function v47Episode(){
 if(!P)return null;
 return P.episodes[Number($('v47-episode').value)||0]||P.episodes[0]||null;
}
function v47Scene(){return v47Episode()?.scenes?.[Number($('v47-scene').value)||0]||null;}
function v47View(){
 if(!P)return;
 const ep=$('v47-episode'),old=ep.value;
 ep.innerHTML=P.episodes.map((e,i)=>'<option value="'+i+'">Серия '+e.number+
  ' — '+escapeHTML(e.title)+'</option>').join('');
 ep.value=[...ep.options].some(o=>o.value===old)?old:String(epIndex);
 if(!ep.value&&P.episodes.length)ep.value='0';
 v47Scenes();
}
function v47Scenes(){
 const scenes=$('v47-scene'),old=scenes.value,ep=v47Episode();
 scenes.innerHTML=(ep?.scenes||[]).map((s,i)=>'<option value="'+i+'">'+(i+1)+
  '. '+escapeHTML(s.title)+'</option>').join('');
 scenes.value=[...scenes.options].some(o=>o.value===old)?old:'0';
 v47Controls();
}
function v47Controls(){
 const scene=v47Scene();if(!scene)return;
 const slot=$('v47-slot').value,cfg=v47Of(scene,slot);
 const actor=$('v47-speaker');
 actor.innerHTML=P.characters.map((c,i)=>'<option value="'+i+'">'+escapeHTML(c.name)+'</option>').join('');
 const who=P.characters.findIndex(c=>c.name===cfg.speakerV47);
 actor.value=String(who>=0?who:0);
 $('v47-gain').value=Math.round(cfg.gain*100);
 $('v47-offset').value=Math.round(cfg.offset*100);
 $('v47-mouth-on').checked=cfg.mouthEnabledV47;
 $('v47-mouth-x').value=cfg.mouthX;$('v47-mouth-y').value=cfg.mouthY;
 $('v47-state').textContent=cfg.embeddedV47?
  cfg.name+' · сохранено '+Math.round(cfg.embeddedV47.length*.75/1024)+' КБ внутри JSON'+
  (v36Buffer(scene,slot)?.name===cfg.name?' · декодировано':' · восстановление при записи'):
  'Нет переносимого файла для этого слота. Можно загрузить WAV/MP3/OGG.';
 v47Preview();
}
function v47Save(){
 const scene=v47Scene();if(!scene)return;
 const cfg=v47Of(scene,$('v47-slot').value);
 cfg.gain=clamp(Number($('v47-gain').value)/100,0,2);
 cfg.offset=clamp(Number($('v47-offset').value)/100,0,120);
 cfg.mouthEnabledV47=$('v47-mouth-on').checked;
 cfg.mouthX=clamp(Number($('v47-mouth-x').value),-45,45);
 cfg.mouthY=clamp(Number($('v47-mouth-y').value),-45,45);
 cfg.speakerV47=P.characters[Number($('v47-speaker').value)]?.name||cfg.speakerV47;
 save();v47Controls();
 notify('V47: смешивание, персонаж и синхронизация губ сохранены.');
}
async function v47Attach(){
 if(v47Busy)return;
 const scene=v47Scene(),file=$('v47-file').files?.[0];
 if(!scene||!file)return;
 v47Busy=true;
 try{
  const result=await v47KeepAudio(scene,$('v47-slot').value,file);
  v47Controls();
  notify('V47: звук '+result.name+' и '+result.points+' отсчётов рта сохранены в проекте.');
 }catch(err){notify('V47: '+err.message);}
 finally{v47Busy=false;$('v47-file').value='';}
}
$('v36-audiofile').onchange=async event=>{
 const scene=v36Scene(),file=event.target.files?.[0];
 if(!scene||!file)return;
 try{
  await v47KeepAudio(scene,v36Slot(),file);
  v36Controls();
  notify('V47: WAV/MP3/OGG встроен в переносимый JSON; звук доступен после перезапуска.');
 }catch(err){notify('V47 аудио: '+err.message);}
};
const v47LegacyControls=v36Controls;
v36Controls=function(){
 const scene=v36Scene();
 if(scene){
  const cfg=v47Of(scene,v36Slot());
  if(cfg.embeddedV47&&!v36Buffer(scene,v36Slot())){
   v47LegacyControls();
   $('v36-asset').textContent=cfg.name+' · встроен в JSON, восстановится при запуске';
   return;
  }
 }
 return v47LegacyControls();
};
const v47LegacyAudioManifest=v36Manifest;
v36Manifest=function(){
 const report=v47LegacyAudioManifest();
 report.version=47;
 report.embeddedPortableAudio=true;
 report.notes=['Аудиобайты хранятся в полном JSON-проекте в scene.audioV36.<slot>.embeddedV47.',
  'Синхронизация рта по громкости WAV/MP3, не фонемная расшифровка.'];
 return report;
};
function v47Preview(){
 const s=v47Scene();if(!s)return;
 const sec=s.duration*Number($('v47-timeline').value)/1000;
 drawScene($('v47-preview'),s,sec);
 const cfg=v47Of(s,'voice'),actor=P.characters.find(c=>c.name===cfg.speakerV47)||P.characters[0];
 const opening=mouth(s,actor,sec);
 $('v47-time').textContent=sec.toFixed(2)+' / '+s.duration.toFixed(2)+
  ' сек · реальное открытие рта '+opening.toFixed(3)+
  ' · '+(cfg.waveV47.length?'амплитуда звука':'старый текстовый черновик');
}
function v47Audit(){
 const issues=[];
 for(const ep of P?.episodes||[])for(const s of ep.scenes||[]){
  for(const slot of v47Slots){
   const cfg=v47Of(s,slot);
   if(cfg.name&&!cfg.embeddedV47)issues.push(ep.title+'/'+s.title+' '+slot+': файл не переносится в JSON');
   if(cfg.embeddedV47?.length>v47MaxClip*1.4)
    issues.push(ep.title+'/'+s.title+' '+slot+': слишком большой звуковой клип');
  }
 }
 $('v47-report').textContent=issues.join('\n')||
  'V47: аудиофайлы прикреплены к JSON. Учтите квоту локального хранилища; сохраните резерв на диске.';
}
$('v47-episode').onchange=v47Scenes;
$('v47-scene').onchange=v47Controls;
$('v47-slot').onchange=v47Controls;
$('v47-file').onchange=v47Attach;
$('v47-save').onclick=v47Save;
$('v47-timeline').oninput=v47Preview;
$('v47-audit').onclick=v47Audit;
$('v47-project').onclick=()=>download('V47_PORTABLE_PROJECT_WITH_AUDIO.json',
 new Blob([JSON.stringify(P,null,2)],{type:'application/json;charset=utf-8'}));
$('v47-manifest').onclick=()=>download('V47_AUDIO_LIPSYNC_MANIFEST.json',
 new Blob([JSON.stringify(v36Manifest(),null,2)],{type:'application/json;charset=utf-8'}));
