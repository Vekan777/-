/* Anime Production Engine V46 — actual layered-cutout keyframe animation.
 * Binds to original pose16Sample() used by the real V15/V45 renderer and
 * V36 MediaRecorder. Old v16 choreography and V25 outcomes are untouched.
 */
const v46Parts=['legs','cape','torso','arms','face','hair','weapon'];
const v46Roles=['hero','partner'];
const v46OriginalPose16=pose16Sample;
const v46Neutral={x:0,y:0,angle:0,scale:1,ease:'smooth'};
const v46Actions={
 walk:{legs:[0,-24,26,-18,0],torso:[0,4,-3,4,0],arms:[0,17,-19,14,0],
  cape:[0,-7,9,-5,0],hair:[0,4,-5,5,0],face:[0,0,0,0,0],weapon:[0,3,-4,3,0]},
 guard:{legs:[0,-6,-9,-6,0],torso:[0,-8,-13,-8,0],arms:[0,-36,-61,-36,0],
  cape:[0,5,10,5,0],hair:[0,3,-5,3,0],face:[0,-5,-7,-5,0],weapon:[0,-12,-29,-12,0]},
 strike:{legs:[0,7,-16,12,0],torso:[0,-15,18,8,0],arms:[0,-44,75,15,0],
  cape:[0,8,-23,-12,0],hair:[0,3,-16,-8,0],face:[0,-7,8,4,0],weapon:[0,-65,89,18,0]},
 bow:{legs:[0,-3,-3,-3,0],torso:[0,12,40,18,0],arms:[0,12,24,14,0],
  cape:[0,8,18,8,0],hair:[0,3,13,5,0],face:[0,8,30,14,0],weapon:[0,0,0,0,0]},
 warmth:{legs:[0,0,0,0,0],torso:[0,-7,9,-6,0],arms:[0,15,34,10,0],
  cape:[0,3,-8,3,0],hair:[0,-3,8,-3,0],face:[0,-7,12,-5,0],weapon:[0,0,0,0,0]}
};
let v46Playback=false,v46RAF=0,v46Stamp=0,v46Time=0,v46CurrentSceneKey='';
function v46Clamp(n,min,max,fallback=0){
 const v=Number(n);return Number.isFinite(v)?Math.max(min,Math.min(max,v)):fallback;
}
function v46Animation(s){
 if(!s.animationV46||typeof s.animationV46!=='object'||Array.isArray(s.animationV46))
  s.animationV46={enabled:true,tracks:{hero:{},partner:{}}};
 const data=s.animationV46;
 if(!data.tracks||typeof data.tracks!=='object')data.tracks={hero:{},partner:{}};
 for(const role of v46Roles){
  if(!data.tracks[role]||typeof data.tracks[role]!=='object')data.tracks[role]={};
 }
 data.enabled=data.enabled!==false;
 return data;
}
function v46Keys(s,role,part){
 const root=v46Animation(s);
 if(!Array.isArray(root.tracks[role][part]))root.tracks[role][part]=[];
 return root.tracks[role][part];
}
function v46NormalizedKey(k){
 return {t:v46Clamp(k.t,0,1),x:v46Clamp(k.x,-70,70),
  y:v46Clamp(k.y,-70,70),angle:v46Clamp(k.angle,-100,100),
  scale:v46Clamp(k.scale,.6,1.4,1),
  ease:['linear','smooth','hold'].includes(k.ease)?k.ease:'smooth'};
}
function v46Interpolate(list,fraction){
 if(!list.length)return {...v46Neutral,t:fraction};
 const f=v46Clamp(fraction,0,1);
 const frames=list.map(v46NormalizedKey).sort((a,b)=>a.t-b.t);
 if(f<=frames[0].t)return {...frames[0],t:f};
 for(let i=1;i<frames.length;i++){
  const a=frames[i-1],b=frames[i];if(f>b.t)continue;
  let t=v46Clamp((f-a.t)/Math.max(.00001,b.t-a.t),0,1);
  if(a.ease==='hold')t=0;
  if(a.ease==='smooth')t=t*t*(3-2*t);
  return {t:f,ease:a.ease,
   x:a.x+(b.x-a.x)*t,y:a.y+(b.y-a.y)*t,
   angle:a.angle+(b.angle-a.angle)*t,
   scale:a.scale+(b.scale-a.scale)*t};
 }
 return {...frames[frames.length-1],t:f};
}
function v46LayerMotion(s,role,part,sec){
 if(!v46Animation(s).enabled)return {...v46Neutral};
 const track=v46Keys(s,role,part);
 if(!track.length)return {...v46Neutral};
 return v46Interpolate(track,sec/Math.max(.01,s.duration));
}
// Real extension of the original renderer. This changes actual actor geometry,
// not a composite filter; the V45 images and procedural fallback both use it.
pose16Sample=function(s,role,part,sec){
 const base=v46OriginalPose16(s,role,part,sec);
 if(!v46Parts.includes(part)||!v46Roles.includes(role))return base;
 const extra=v46LayerMotion(s,role,part,sec);
 return {...base,x:base.x+extra.x,y:base.y+extra.y,
  angle:base.angle+extra.angle,
  scale:v46Clamp(base.scale*extra.scale,.3,2,1)};
};
function v46PresetAnimation(name){
 if(!Object.prototype.hasOwnProperty.call(v46Actions,name))throw Error('Unknown clip');
 const matrix=v46Actions[name];
 return Object.fromEntries(v46Parts.map(part=>{
  const angles=matrix[part],times=[0,.22,.48,.74,1];
  return [part,times.map((t,i)=>v46NormalizedKey({
   t,angle:angles[i],x:part==='legs'&&name==='walk'?[0,-8,0,9,0][i]:
     part==='arms'&&name==='strike'?[0,-6,22,8,0][i]:0,
   y:part==='torso'&&name==='bow'?[0,3,9,2,0][i]:0,
   scale:1,ease:'smooth'}))];
 }));
}
function v46Episode(){
 if(!P)return null;
 return P.episodes[Number($('v46-episode').value)||0]||P.episodes[0]||null;
}
function v46Scene(){return v46Episode()?.scenes?.[Number($('v46-scene').value)||0]||null;}
function v46Fields(){
 const s=v46Scene();if(!s)return;
 const role=$('v46-role').value,part=$('v46-part').value;
 const now=v46Time,keys=v46Keys(s,role,part),candidate=keys.find(k=>Math.abs(k.t-now)<.008);
 const value=candidate||v46Interpolate(keys,now);
 for(const n of ['x','y','angle','scale'])$('v46-'+n).value=
  Number(value[n]).toFixed(n==='scale'?2:1);
 $('v46-ease').value=value.ease||'smooth';
 $('v46-key-list').innerHTML=keys.map(k=>
  '<option value="'+k.t+'">'+Math.round(k.t*100)+'% · '+k.angle+'°</option>').join('');
 $('v46-enabled').checked=v46Animation(s).enabled;
 $('v46-key-count').textContent=keys.length+' ключей · '+Math.round(now*100)+'%';
}
function v46Show(){
 if(!P)return;v46Pause();
 const select=$('v46-episode'),old=select.value;
 select.innerHTML=P.episodes.map((e,i)=>
  '<option value="'+i+'">Серия '+e.number+' — '+escapeHTML(e.title)+'</option>').join('');
 select.value=[...select.options].some(o=>o.value===old)?old:String(epIndex);
 if(!select.value&&P.episodes.length)select.value='0';
 v46Scenes();
}
function v46Scenes(){
 v46Pause();
 const s=$('v46-scene'),ep=v46Episode(),old=s.value;
 s.innerHTML=(ep?.scenes||[]).map((scene,i)=>
  '<option value="'+i+'">'+(i+1)+'. '+escapeHTML(scene.title)+'</option>').join('');
 s.value=[...s.options].some(o=>o.value===old)?old:String(scIndex);
 v46Time=0;v46Fields();v46ClipsUI();v46Render();
}
function v46SaveKey(){
 const s=v46Scene();if(!s)return;
 const role=$('v46-role').value,part=$('v46-part').value,keys=v46Keys(s,role,part);
 const value={t:v46Time,ease:$('v46-ease').value};
 for(const name of ['x','y','angle','scale'])value[name]=Number($('v46-'+name).value);
 const key=v46NormalizedKey(value);
 const i=keys.findIndex(k=>Math.abs(k.t-key.t)<.008);
 if(i>=0)keys[i]=key;else keys.push(key);
 keys.sort((a,b)=>a.t-b.t);
 v46Animation(s).enabled=true;save();v46Fields();v46Render();
 notify('V46: реальный ключ '+part+' сохранён.');
}
function v46DeleteKey(){
 const s=v46Scene();if(!s)return;
 const arr=v46Keys(s,$('v46-role').value,$('v46-part').value);
 const idx=arr.findIndex(k=>Math.abs(k.t-v46Time)<.008);
 if(idx<0){notify('V46: на этом времени нет ключа для удаления.');return;}
 arr.splice(idx,1);save();v46Fields();v46Render();
}
function v46ApplyAction(){
 const s=v46Scene();if(!s)return;
 const action=$('v46-action').value,role=$('v46-role').value;
 const data=v46Animation(s);
 data.tracks[role]=v46PresetAnimation(action);
 data.enabled=true;save();v46Fields();v46Render();
 notify('V46: записаны 35 реальных ключей на семи частях рига.');
}
function v46Clips(){if(!Array.isArray(P.animationClipsV46))P.animationClipsV46=[];return P.animationClipsV46;}
function v46ClipsUI(){
 if(!P)return;
 const select=$('v46-clip'),old=select.value;
 select.innerHTML=v46Clips().map((c,i)=>'<option value="'+i+'">'+
  escapeHTML(c.name||'Клип '+(i+1))+'</option>').join('');
 select.value=[...select.options].some(o=>o.value===old)?old:'0';
 $('v46-clip-count').textContent=v46Clips().length+' сохранённых клипов';
}
function v46SaveClip(){
 const s=v46Scene();if(!s)return;
 const role=$('v46-role').value,tracks=v46Animation(s).tracks[role];
 const name=$('v46-clip-name').value.trim().slice(0,80)||'Анимация '+s.title;
 const clip={name,source:s.title,role,
  tracks:JSON.parse(JSON.stringify(Object.fromEntries(v46Parts.map(n=>[n,tracks[n]||[]]))))};
 v46Clips().push(clip);
 if(v46Clips().length>100)v46Clips().shift();
 save();v46ClipsUI();notify('V46: клип сохранён в проекте.');
}
function v46ApplyClip(){
 const s=v46Scene(),clip=v46Clips()[Number($('v46-clip').value)];
 if(!s||!clip)return;
 const role=$('v46-role').value,root=v46Animation(s);
 root.tracks[role]=Object.fromEntries(v46Parts.map(n=>
  [n,Array.isArray(clip.tracks[n])?clip.tracks[n].map(v46NormalizedKey):[]]));
 root.enabled=true;save();v46Fields();v46Render();
 notify('V46: клип перенесён в сцену без изменения канона.');
}
function v46Audit(){
 const s=v46Scene(),errors=[];
 if(!s)return errors;
 const root=v46Animation(s);
 for(const role of v46Roles)for(const part of v46Parts){
  let prev=-1;
  for(const k of root.tracks[role][part]||[]){
   if(k.t<=prev)errors.push(role+'/'+part+' — дублированное или непоследовательное время');
   for(const name of ['x','y','angle','scale','t'])
    if(!Number.isFinite(Number(k[name])))errors.push(role+'/'+part+' — некорректный '+name);
   prev=k.t;
  }
 }
 return errors;
}
function v46Render(){
 const s=v46Scene();if(!s)return;
 const sec=Math.max(0,s.duration)*v46Time,canvas=$('v46-preview');
 // Onion skin: two truthful neighboring frames composed over current frame.
 const g=canvas.getContext('2d');
 drawScene(canvas,s,sec);
 if($('v46-onion').checked){
  const scratch=document.createElement('canvas');
  scratch.width=canvas.width;scratch.height=canvas.height;
  const delta=Math.min(.2,s.duration*.055);
  for(const [step,opacity] of [[-delta,.17],[delta,.17]]){
   drawScene(scratch,s,Math.max(0,Math.min(s.duration,sec+step)));
   g.save();g.globalAlpha=opacity;g.drawImage(scratch,0,0);g.restore();
  }
 }
 $('v46-position').value=Math.round(v46Time*1000);
 $('v46-timestamp').textContent=s.title+' · '+sec.toFixed(2)+' / '+
  s.duration.toFixed(2)+' сек.';
}
function v46Pause(){
 v46Playback=false;v46Stamp=0;
 if(v46RAF){cancelAnimationFrame(v46RAF);v46RAF=0;}
 if($('v46-play'))$('v46-play').textContent='Воспроизвести';
}
function v46Tick(stamp){
 if(!v46Playback)return;
 const dt=v46Stamp?Math.min(.15,(stamp-v46Stamp)/1000):0;
 v46Stamp=stamp;
 const s=v46Scene();
 v46Time=Math.min(1,v46Time+dt/Math.max(.1,s.duration));
 v46Render();v46Fields();
 if(v46Time>=1){v46Pause();return;}
 v46RAF=requestAnimationFrame(v46Tick);
}
function v46Toggle(){
 if(v46Playback){v46Pause();return;}
 if(!v46Scene())return;
 if(v46Time>=1)v46Time=0;
 v46Playback=true;v46Stamp=0;
 $('v46-play').textContent='Пауза';
 v46RAF=requestAnimationFrame(v46Tick);
}
async function v46Evidence(){
 await preloadArtwork();
 const s=v46Scene();if(!s)return;
 const one=document.createElement('canvas'),sheet=document.createElement('canvas');
 one.width=640;one.height=360;sheet.width=1280;sheet.height=720;
 const ctx=sheet.getContext('2d'),times=[.09,.33,.62,.91];
 for(let i=0;i<4;i++){
  drawScene(one,s,s.duration*times[i]);
  ctx.drawImage(one,(i%2)*640,Math.floor(i/2)*360);
 }
 download('V46_FOUR_REAL_KEYFRAME_POSES.png',await blobPNG(sheet));
}
function v46Manifest(){
 if(!P)return {};
 return {schema:'AIAnimeFactory/AnimationV46/1',version:46,
  clips:v46Clips(),
  episodes:P.episodes.map(ep=>({title:ep.title,scenes:ep.scenes.map(s=>
   ({title:s.title,duration:s.duration,animation:v46Animation(s)}))})),
  note:'Native V16 preserved, V45 cutout parts truly animated by pose16Sample.'};
}
$('v46-episode').onchange=v46Scenes;
$('v46-scene').onchange=()=>{v46Pause();v46Time=0;v46Fields();v46Render();};
$('v46-role').onchange=()=>{v46Fields();v46Render();};
$('v46-part').onchange=()=>{v46Fields();v46Render();};
$('v46-enabled').onchange=()=>{const s=v46Scene();if(!s)return;v46Animation(s).enabled=$('v46-enabled').checked;save();v46Render();};
$('v46-action-apply').onclick=v46ApplyAction;
$('v46-key-save').onclick=v46SaveKey;
$('v46-key-remove').onclick=v46DeleteKey;
$('v46-clip-save').onclick=v46SaveClip;
$('v46-clip-apply').onclick=v46ApplyClip;
$('v46-position').oninput=()=>{v46Pause();v46Time=Number($('v46-position').value)/1000;v46Fields();v46Render();};
$('v46-key-list').onchange=()=>{v46Pause();v46Time=Number($('v46-key-list').value);v46Fields();v46Render();};
$('v46-onion').onchange=v46Render;
$('v46-play').onclick=v46Toggle;
$('v46-first').onclick=()=>{v46Pause();v46Time=0;v46Fields();v46Render();};
$('v46-frame').onclick=async()=>{try{await v46Evidence();}catch(e){notify('V46 PNG: '+e.message);}};
$('v46-json').onclick=()=>download('V46_ANIMATION_LIBRARY.json',
 new Blob([JSON.stringify(v46Manifest(),null,2)],{type:'application/json;charset=utf-8'}));
$('v46-audit').onclick=()=>{
 const issues=v46Audit();
 $('v46-report').textContent=issues.length?issues.join('\n'):
 'V46: числовые границы, порядок ключей и наличие рига проверены. Это не оценка художественного качества.';
};
