/* V48: Episode Production studio, deterministic season manifests, SRT/VTT,
   end cards, production checks and per-episode checkpoint previews.
   Heavy batch MP4 is performed by the bundled Playwright+FFmpeg CLI.
   No 1800-frame memory accumulation or ZIP of every PNG.
*/
const v48EpisodeKey='AI_ANIME_FACTORY_V48_RENDER_PROGRESS';
const v48OldV35Frame=v35Frame;
let v48Running=false,v48At=0,v48RAF=0,v48Stamp=0;
function v48Settings(){
 if(!P.productionV48||typeof P.productionV48!=='object')
  P.productionV48={credits:true,creditSeconds:2,studio:'AI Anime Factory',fps:6,width:640};
 const v=P.productionV48;
 v.creditSeconds=clamp(Number(v.creditSeconds)||2,.5,8);
 v.width=[640,960,1280].includes(Number(v.width))?Number(v.width):640;
 v.fps=[6,12,24].includes(Number(v.fps))?Number(v.fps):6;
 v.studio=String(v.studio||'AI Anime Factory').slice(0,130);
 v.credits=v.credits!==false;
 return v;
}
function v48DrawCredits(canvas,episode,sec){
 const cfg=v48Settings(),p=v35Plan(episode);
 if(!cfg.credits||!p.rows.length||sec<p.duration-cfg.creditSeconds)return;
 const elapsed=clamp((sec-(p.duration-cfg.creditSeconds))/Math.min(.5,cfg.creditSeconds/3),0,1);
 const ctx=canvas.getContext('2d'),w=canvas.width,h=canvas.height,s=w/640;
 ctx.save();ctx.globalAlpha=.86*elapsed;
 ctx.fillStyle='#040916';ctx.fillRect(0,0,w,h);
 ctx.textAlign='center';ctx.textBaseline='middle';
 ctx.fillStyle='#f6e2a9';ctx.font='bold '+Math.round(29*s)+'px Arial';
 ctx.fillText('КОНЕЦ СЕРИИ '+episode.number,w/2,h*.33);
 ctx.fillStyle='#fff';ctx.font=Math.round(20*s)+'px Arial';
 ctx.fillText(String(episode.title||'').slice(0,42),w/2,h*.48);
 ctx.font=Math.round(13*s)+'px Arial';
 ctx.fillText(cfg.studio.slice(0,75),w/2,h*.67);
 ctx.restore();
}
v35Frame=function(canvas,episode,sec){
 const result=v48OldV35Frame(canvas,episode,sec);
 v48DrawCredits(canvas,episode,sec);
 return result;
};
function v48Select(){return P?.episodes?.[Number($('v48-episode').value)||0]||null;}
function v48Resume(){
 try{return JSON.parse(localStorage.getItem(v48EpisodeKey)||'{}');}
 catch(_){return {};}
}
function v48ProgressMark(index,value){
 const progress=v48Resume();
 progress[String(index)]={...value,at:new Date().toISOString()};
 try{localStorage.setItem(v48EpisodeKey,JSON.stringify(progress));}
 catch(_){notify('V48: недостаточно места для контрольной записи.');}
}
function v48Manifest(){
 const cfg=v48Settings();
 return {format:'AIAnimeFactoryEpisodeProduction/V48',version:48,
   series:P.title,creditSettings:{...cfg},
   characters:P.characters.map(c=>({id:c.id,name:c.name,rights:c.productionRig?.rights||''})),
   episodes:P.episodes.map((e,i)=>{
    const p=v35Plan(e),cues=v37Timeline(e).cues;
    return {index:i,number:e.number,title:e.title,
      duration:p.duration,scenes:p.rows.map(r=>({
        title:r.title,kind:r.kind,start:r.start,end:r.end,
        location:r.scene.place,camera:r.scene.camera})),
      subtitles:cues.length,
      audio:p.rows.flatMap(r=>['voice','music','fx'].map(slot=>{
        const c=v47Of(r.scene,slot);return {scene:r.title,slot,
          name:c.name,embedded:!!c.embeddedV47,gain:c.gain,offset:c.offset};
      }))};
   }),progress:v48Resume(),
   notes:['WebM recording runs in real time via V36 MediaRecorder.',
     'For sequential resumed episodes and H264 MP4 use scripts/render_anime_v48.py + FFmpeg.',
     'No claim of 20-minute episodes rendered in this browser smoke test.']};
}
function v48Audit(){
 const issues=[];
 if(!P?.episodes?.length)return ['Нет эпизодов'];
 for(const [i,e] of P.episodes.entries()){
  const p=v35Plan(e);
  if(!p.rows.length||p.duration<=0)issues.push('Серия '+(i+1)+' без сцен');
  if(p.duration>3600)issues.push('Серия '+(i+1)+' дольше часа: используйте пакетный рендер');
  for(const r of p.rows){
   if(!r.scene.title)issues.push('Серия '+(i+1)+' содержит безымянную сцену');
   for(const slot of ['voice','music','fx']){
    const c=v47Of(r.scene,slot);
    if(c.name&&!c.embeddedV47&&!v36Buffer(r.scene,slot))
      issues.push('Серия '+(i+1)+', '+r.title+': '+slot+' не встроен в JSON');
   }
  }
 }
 return issues;
}
function v48Show(){
 if(!P)return;
 v48Pause();v48Settings();
 const sel=$('v48-episode'),old=sel.value;
 sel.innerHTML=P.episodes.map((e,i)=>'<option value="'+i+'">'+
  e.number+'. '+escapeHTML(e.title)+'</option>').join('');
 sel.value=[...sel.options].some(o=>o.value===old)?old:'0';
 const cfg=v48Settings();
 $('v48-fps').value=String(cfg.fps);
 $('v48-width').value=String(cfg.width);
 $('v48-credits').checked=cfg.credits;
 $('v48-credit-seconds').value=cfg.creditSeconds;
 $('v48-studio').value=cfg.studio;
 v48Draw();
}
function v48Save(){
 const cfg=v48Settings();
 cfg.fps=Number($('v48-fps').value)||6;
 cfg.width=Number($('v48-width').value)||640;
 cfg.credits=$('v48-credits').checked;
 cfg.creditSeconds=clamp(Number($('v48-credit-seconds').value),.5,8);
 cfg.studio=$('v48-studio').value.slice(0,130);
 save();v48Draw();notify('V48: параметры экспорта сохранены в полном проекте.');
}
function v48Pause(){
 v48Running=false;v48Stamp=0;
 if(v48RAF){cancelAnimationFrame(v48RAF);v48RAF=0;}
 if($('v48-play'))$('v48-play').textContent='Воспроизвести';
}
function v48Draw(){
 const e=v48Select();if(!e)return;
 const p=v35Plan(e);
 v48At=clamp(v48At,0,p.duration);
 v35Frame($('v48-preview'),e,v48At);
 // V37 subtitles remain legible over the end card as a separate text layer.
 v37Paint($('v48-preview'),e,v48At);
 $('v48-timestamp').textContent='Эпизод '+e.number+' / '+P.episodes.length+
  ' • '+v48At.toFixed(2)+' / '+p.duration.toFixed(2)+' сек' +
  ' • '+v37Timeline(e).cues.length+' субтитров';
 $('v48-position').value=p.duration?Math.round(v48At/p.duration*1000):0;
 const check=v48Resume();
 $('v48-report').textContent='ОБЪЕДИНЕНИЕ V48 · '+P.title+'\n'+
  P.episodes.map((ep,i)=>{
   const d=v35Plan(ep).duration,pr=check[String(i)]||{};
   return 'Серия '+(i+1)+' — '+ep.title+' ('+d.toFixed(1)+' с), '+
    (pr.status||'не записывалась');
  }).join('\n')+'\n\n'+
  (v48Audit().join('\n')||'Данные структуры серий: без критических замечаний.');
}
function v48Tick(stamp){
 if(!v48Running)return;
 const delta=v48Stamp?Math.min(.12,(stamp-v48Stamp)/1000):0;
 v48Stamp=stamp;
 const p=v35Plan(v48Select());
 v48At=Math.min(p.duration,v48At+delta);
 v48Draw();
 if(v48At>=p.duration){v48Pause();return;}
 v48RAF=requestAnimationFrame(v48Tick);
}
function v48Toggle(){
 if(v48Running){v48Pause();return;}
 const e=v48Select();if(!e)return;
 const p=v35Plan(e);if(v48At>=p.duration)v48At=0;
 v48Running=true;v48Stamp=0;
 $('v48-play').textContent='Пауза';
 v48RAF=requestAnimationFrame(v48Tick);
}
async function v48FourFrames(){
 await preloadArtwork();
 const e=v48Select();if(!e)return;
 const p=v35Plan(e);
 const sheet=document.createElement('canvas'),small=document.createElement('canvas');
 sheet.width=1280;sheet.height=720;small.width=640;small.height=360;
 const ctx=sheet.getContext('2d');
 for(const [i,frac] of [.06,.36,.67,.98].entries()){
  const sec=p.duration*frac;
  v35Frame(small,e,sec);v37Paint(small,e,sec);
  ctx.drawImage(small,(i%2)*640,Math.floor(i/2)*360);
 }
 download('V48_REAL_EPISODE_STORYBOARD.png',await blobPNG(sheet));
}
function v48Subs(format){
 const ep=v48Select();if(!ep)return;
 download('V48_EPISODE_'+ep.number+'_SUBTITLES.'+format,
  new Blob([v37SubtitleFile(ep,format)],{type:'text/plain;charset=utf-8'}));
}
function v48ShotList(){
 const ep=v48Select();if(!ep)return;
 const data=v48Manifest().episodes[Number($('v48-episode').value)||0];
 download('V48_EPISODE_'+ep.number+'_SHOT_PLAN.json',
  new Blob([JSON.stringify(data,null,2)],{type:'application/json;charset=utf-8'}));
}
async function v48RecordOne(){
 const ep=v48Select(),idx=Number($('v48-episode').value)||0;
 if(!ep||v36Active||v36Recorder)return;
 v48Save();
 const issues=v48Audit();if(issues.length)notify('V48: замечаний '+issues.length+'. Проверьте отчёт.');
 v48ProgressMark(idx,{status:'запись запущена',duration:v35Plan(ep).duration});
 $('v36-episode').value=String(idx);
 v36Scenes();
 $('v36-fps').value=String(v48Settings().fps);
 // Original audio/video export remains authoritative and handles V47 restore.
 await v36Start(true);
 if(!v36Active)v48ProgressMark(idx,{status:'ошибка запуска'});
}
function v48ExportProject(){
 download('V48_PORTABLE_SEASON_PROJECT.json',
  new Blob([JSON.stringify(P,null,2)],{type:'application/json;charset=utf-8'}));
}
$('v48-episode').onchange=()=>{v48Pause();v48At=0;v48Draw();};
$('v48-position').oninput=()=>{v48Pause();v48At=v35Plan(v48Select()).duration*
 Number($('v48-position').value)/1000;v48Draw();};
$('v48-play').onclick=v48Toggle;
$('v48-first').onclick=()=>{v48Pause();v48At=0;v48Draw();};
$('v48-save').onclick=v48Save;
$('v48-frames').onclick=async()=>{try{await v48FourFrames();}catch(e){notify('V48 PNG: '+e.message);}};
$('v48-srt').onclick=()=>v48Subs('srt');
$('v48-vtt').onclick=()=>v48Subs('vtt');
$('v48-shot').onclick=v48ShotList;
$('v48-manifest').onclick=()=>download('V48_SEASON_MANIFEST.json',
 new Blob([JSON.stringify(v48Manifest(),null,2)],{type:'application/json;charset=utf-8'}));
$('v48-project').onclick=v48ExportProject;
$('v48-record').onclick=v48RecordOne;

/* Narrow export bridge. No private variables are accessed by Playwright.
   Read-only catalog/subtitle methods; QA truncation is explicitly test-only.
*/
window.v48BatchBridge=Object.freeze({
 count:()=>P?.episodes?.length||0,
 episode:i=>{
  const ep=P?.episodes?.[i];if(!ep)throw Error('Episode not found '+i);
  const p=v35Plan(ep);
  return {title:ep.title,number:ep.number,duration:p.duration,
   scenes:p.rows.length,subtitles:v37Timeline(ep).cues.length};
 },
 subtitles:(i,format)=>{
  const ep=P?.episodes?.[i];if(!ep)throw Error('Episode not found');
  if(!['srt','vtt'].includes(format))throw Error('Unsupported subtitle type');
  return v37SubtitleFile(ep,format);
 },
 testShorten:()=>{
  if(!P||P.episodes.length<2)throw Error('QA requires two episodes');
  P.episodes=P.episodes.slice(0,2);
  for(const ep of P.episodes){
   ep.scenes=ep.scenes.slice(0,1);
   ep.scenes[0].duration=2.7;
   if(ep.scenes[0].audioV36?.voice?.embeddedV47)
    ep.scenes[0].audioV36.voice.offset=0;
  }
  P.version=48;save();
  return P.episodes.length;
 }
});
