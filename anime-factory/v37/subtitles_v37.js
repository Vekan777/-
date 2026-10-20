/* AI Anime Factory V37 — subtitles and delivery continuity.
 * Per-scene subtitle cues live under subtitlesV37 only. Uses the exact
 * production V35 plan, including overlapping scenes and original durations.
 */
let v37At=0,v37Playing=false,v37Stamp=0,v37RAF=0;
function v37Of(scene){
 if(!scene.subtitlesV37||typeof scene.subtitlesV37!=='object'||Array.isArray(scene.subtitlesV37))
  scene.subtitlesV37={cues:[]};
 if(!Array.isArray(scene.subtitlesV37.cues))scene.subtitlesV37.cues=[];
 return scene.subtitlesV37;
}
function v37Clean(text){return String(text||'').replace(/[\x00-\x1f\x7f]+/g,' ').replace(/\s+/g,' ').trim().slice(0,240);}
function v37Cue(raw){
 const start=Number(raw?.start),end=Number(raw?.end);
 return {start:Number.isFinite(start)?clamp(start,0,3600):0,
  end:Number.isFinite(end)?clamp(end,0,3600):0,
  text:v37Clean(raw?.text),speaker:v37Clean(raw?.speaker).slice(0,64)};
}
function v37Episode(){
 if(!P)return null;
 return P.episodes[Number($('v37-episode').value)||0]||P.episodes[0]||null;
}
function v37Scene(){const e=v37Episode();return e?.scenes?.[Number($('v37-scene').value)||0]||null;}
function v37Timeline(episode){
 const plan=v35Plan(episode),cues=[];
 for(const row of plan.rows){
  const list=Array.isArray(row.scene?.subtitlesV37?.cues)?
   row.scene.subtitlesV37.cues:[];
  for(const [index,input] of list.entries()){
   const cue=v37Cue(input);
   if(!cue.text||cue.end<=cue.start||cue.start>=row.duration)continue;
   const start=row.start+cue.start,end=Math.min(row.end,row.start+cue.end);
   if(end<=start)continue;
   cues.push({index,sceneIndex:row.index,start,end,text:cue.text,
    speaker:cue.speaker,sceneTitle:row.title});
  }
 }
 cues.sort((a,b)=>a.start-b.start||a.sceneIndex-b.sceneIndex||a.index-b.index);
 return {duration:plan.duration,cues};
}
function v37Active(episode,sec){
 return v37Timeline(episode).cues.filter(c=>sec>=c.start&&sec<c.end).slice(0,2);
}
function v37Lines(ctx,text,maxWidth,maxLines){
 const words=v37Clean(text).split(' '),result=[];
 let line='';
 for(const word of words){
  const candidate=line?line+' '+word:word;
  if(ctx.measureText(candidate).width>maxWidth&&line){result.push(line);line=word;}
  else line=candidate;
 }
 if(line)result.push(line);
 if(result.length>maxLines){
  result.length=maxLines;
  let end=result[maxLines-1];
  while(end.length>1&&ctx.measureText(end+'…').width>maxWidth)end=end.slice(0,-1);
  result[maxLines-1]=end+'…';
 }
 return result;
}
function v37Paint(canvas,episode,sec){
 if(!episode)return [];
 const active=v37Active(episode,sec);
 if(!active.length)return active;
 const ctx=canvas.getContext('2d'),w=canvas.width,h=canvas.height;
 const scale=w/640;
 ctx.save();ctx.font='bold '+Math.max(13,Math.round(21*scale))+'px Arial, sans-serif';
 ctx.textBaseline='middle';ctx.textAlign='center';
 const chunks=active.flatMap(c=>v37Lines(ctx,
  (c.speaker?c.speaker+': ':'')+c.text,w*.88,2)).slice(0,3);
 if(!chunks.length){ctx.restore();return active;}
 const lh=Math.round(29*scale),boxHeight=lh*chunks.length+Math.round(15*scale);
 const y=h-Math.round(26*scale)-boxHeight;
 ctx.fillStyle='rgba(0,0,0,.82)';
 ctx.fillRect(w*.05,y,w*.90,boxHeight);
 ctx.lineWidth=Math.max(2,2.5*scale);ctx.strokeStyle='#000';
 ctx.fillStyle='#fff';
 chunks.forEach((s,i)=>{
  const baseline=y+Math.round(9*scale)+lh*(i+.5);
  ctx.strokeText(s,w/2,baseline);
  ctx.fillText(s,w/2,baseline);
 });
 ctx.restore();return active;
}
function v37DrawFrame(canvas,episode,sec){
 const result=v35Frame(canvas,episode,sec);
 v37Paint(canvas,episode,sec);
 return result;
}
function v37Show(){
 if(!P)return;
 v37Pause();
 const select=$('v37-episode'),old=select.value;
 select.innerHTML=P.episodes.map((e,i)=>
  '<option value="'+i+'">Серия '+e.number+' — '+escapeHTML(e.title)+'</option>').join('');
 select.value=[...select.options].some(o=>o.value===old)?old:String(epIndex);
 if(!select.value&&P.episodes.length)select.value='0';
 v37Scenes();
}
function v37Scenes(){
 v37Pause();
 const episode=v37Episode(),select=$('v37-scene'),old=select.value;
 select.innerHTML=(episode?.scenes||[]).map((s,i)=>
  '<option value="'+i+'">'+(i+1)+'. '+escapeHTML(s.title)+'</option>').join('');
 select.value=[...select.options].some(o=>o.value===old)?old:'0';
 v37At=0;v37SelectCue();v37Render();
}
function v37SelectCue(){
 const s=v37Scene(),sel=$('v37-cue'),old=sel.value;
 const items=s?v37Of(s).cues:[];
 sel.innerHTML='<option value="-1">Новые субтитры</option>'+items.map((c,i)=>
  '<option value="'+i+'">'+(i+1)+'. '+v37Cue(c).start.toFixed(2)+
  '–'+v37Cue(c).end.toFixed(2)+' · '+escapeHTML(v37Clean(c.text).slice(0,65))+'</option>').join('');
 sel.value=Number(old)>=0&&Number(old)<items.length?old:'-1';
 v37LoadCue();
}
function v37LoadCue(){
 const s=v37Scene(),i=Number($('v37-cue').value),cue=s&&i>=0?v37Cue(v37Of(s).cues[i]):null;
 $('v37-start').value=cue?cue.start.toFixed(2):'0';
 $('v37-end').value=cue?cue.end.toFixed(2):'2';
 $('v37-speaker').value=cue?cue.speaker:'';
 $('v37-text').value=cue?cue.text:'';
}
function v37SaveCue(){
 const s=v37Scene();
 if(!s)return;
 const duration=v35Duration(s);
 const cue=v37Cue({start:$('v37-start').value,end:$('v37-end').value,
  text:$('v37-text').value,speaker:$('v37-speaker').value});
 if(!cue.text||cue.end<=cue.start||cue.start>=duration||cue.end>duration){
  notify('V37: текст обязателен; таймкоды должны быть внутри выбранной сцены.');return;
 }
 const list=v37Of(s).cues,idx=Number($('v37-cue').value);
 if(idx>=0&&idx<list.length)list[idx]=cue;
 else{if(list.length>=300){notify('V37: максимум 300 реплик на одну сцену.');return;}list.push(cue);}
 save();v37SelectCue();v37Render();
 notify('V37: субтитры сохранены без изменения исходной сцены.');
}
function v37DeleteCue(){
 const s=v37Scene(),i=Number($('v37-cue').value);
 if(!s||i<0||i>=v37Of(s).cues.length)return;
 v37Of(s).cues.splice(i,1);save();v37SelectCue();v37Render();
}
function v37Pause(){
 v37Playing=false;v37Stamp=0;
 if(v37RAF){cancelAnimationFrame(v37RAF);v37RAF=0;}
 if($('v37-play'))$('v37-play').textContent='Воспроизвести';
}
function v37Tick(stamp){
 if(!v37Playing)return;
 const dt=v37Stamp?Math.min((stamp-v37Stamp)/1000,.15):0;
 v37Stamp=stamp;v37At=Math.min(v35Plan(v37Episode()).duration,v37At+dt);
 v37Render();
 if(v37At>=v35Plan(v37Episode()).duration){v37Pause();return;}
 v37RAF=requestAnimationFrame(v37Tick);
}
function v37Toggle(){
 if(v37Playing){v37Pause();return;}
 const e=v37Episode(),p=v35Plan(e);if(!p.rows.length)return;
 if(v37At>=p.duration)v37At=0;
 v37Playing=true;v37Stamp=0;$('v37-play').textContent='Пауза';
 v37RAF=requestAnimationFrame(v37Tick);
}
function v37Render(){
 const ep=v37Episode(),plan=v35Plan(ep);
 if(!ep||!plan.rows.length)return;
 v37At=clamp(v37At,0,plan.duration);
 const current=v37DrawFrame($('v37-preview'),ep,v37At);
 const list=v37Active(ep,v37At);
 $('v37-seek').value=plan.duration?Math.round(v37At/plan.duration*1000):0;
 $('v37-clock').textContent=v37At.toFixed(2)+' / '+plan.duration.toFixed(2)+
  ' с · сцена '+((current.row?.index??0)+1)+'/'+plan.rows.length+
  ' · активных реплик: '+list.length;
}
function v37Timestamp(seconds,srt){
 const ms=Math.max(0,Math.round(seconds*1000)),
  h=Math.floor(ms/3600000),m=Math.floor(ms/60000)%60,
  s=Math.floor(ms/1000)%60,x=ms%1000;
 const part=n=>String(n).padStart(2,'0');
 return part(h)+':'+part(m)+':'+part(s)+(srt?',':'.')+String(x).padStart(3,'0');
}
function v37SubtitleFile(episode,format){
 const entries=v37Timeline(episode).cues;
 const srt=format==='srt';
 const out=srt?[]:['WEBVTT',''];
 for(const [i,c] of entries.entries()){
  if(srt)out.push(String(i+1));
  out.push(v37Timestamp(c.start,srt)+' --> '+v37Timestamp(c.end,srt));
  out.push((c.speaker?c.speaker+': ':'')+c.text,'');
 }
 return out.join('\n')+'\n';
}
function v37Audit(){
 const out=[];
 if(!P)return ['Проект не создан.'];
 for(const ep of P.episodes){
  const plan=v35Plan(ep);
  for(const row of plan.rows){
   const cues=row.scene?.subtitlesV37?.cues||[];
   for(const [i,raw] of cues.entries()){
    const c=v37Cue(raw),tag='Серия '+ep.number+', сцена '+(row.index+1)+', реплика '+(i+1);
    if(!c.text)out.push(tag+': нет текста.');
    if(c.end<=c.start||c.end>row.duration||c.start>=row.duration)
     out.push(tag+': интервал выходит за сцену.');
    if(c.end>c.start&&c.text.length/(c.end-c.start)>20)
     out.push(tag+': слишком быстрая речь для чтения (>20 символов/сек).');
   }
  }
  const entries=v37Timeline(ep).cues;
  for(let i=1;i<entries.length;i++){
   if(entries[i].start<entries[i-1].end-.001)
    out.push('Серия '+ep.number+': субтитры могут перекрывать друг друга ('+
     entries[i-1].sceneTitle+' / '+entries[i].sceneTitle+').');
  }
 }
 return out;
}
function v37Manifest(){
 if(!P)return {};
 return {format:'AIAnimeFactorySubtitles/37',version:37,
  episodes:P.episodes.map(ep=>({number:ep.number,title:ep.title,
   ...v37Timeline(ep)})),
  preserved:'Source scene duration, dialogue story, V35 crossfades and V36 audio are unmodified.',
  warnings:v37Audit()};
}
$('v37-episode').onchange=v37Scenes;
$('v37-scene').onchange=()=>{v37Pause();v37SelectCue();v37Render();};
$('v37-cue').onchange=v37LoadCue;
$('v37-save').onclick=v37SaveCue;
$('v37-remove').onclick=v37DeleteCue;
$('v37-seek').oninput=e=>{v37Pause();v37At=v35Plan(v37Episode()).duration*Number(e.target.value)/1000;v37Render();};
$('v37-play').onclick=v37Toggle;
$('v37-first').onclick=()=>{v37Pause();v37At=0;v37Render();};
$('v37-audit').onclick=()=>{$('v37-report').textContent=v37Audit().join('\n')||
 'Ошибок субтитров по эвристическим правилам V37 не обнаружено.';};
$('v37-srt').onclick=()=>{
 const e=v37Episode();if(e)download('V37_'+slug(e.title)+'.srt',
  new Blob([v37SubtitleFile(e,'srt')],{type:'text/plain;charset=utf-8'}));
};
$('v37-vtt').onclick=()=>{
 const e=v37Episode();if(e)download('V37_'+slug(e.title)+'.vtt',
  new Blob([v37SubtitleFile(e,'vtt')],{type:'text/vtt;charset=utf-8'}));
};
$('v37-json').onclick=()=>download('V37_SUBTITLE_DELIVERY.json',
 new Blob([JSON.stringify(v37Manifest(),null,2)],{type:'application/json;charset=utf-8'}));
