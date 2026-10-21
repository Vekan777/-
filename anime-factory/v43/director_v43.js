/* AI Anime Factory V43 — true action-aware cinematography on canonical V25 beats.
 * Uses existing V19/V25 outcomes only; it does not create or change attacks.
 * No manual randomness, no 3D, no character sprite rewrite.
 */
const v43Profiles={
 duel:{zoom:53,focus:57,recoil:40,tempo:62,tilt:18,shot:'medium'},
 heroic:{zoom:75,focus:76,recoil:68,tempo:78,tilt:38,shot:'close'},
 wide:{zoom:19,focus:23,recoil:12,tempo:38,tilt:5,shot:'wide'}
};
const v43BaseFrame=v38Frame;
let v43Clock=0,v43Playing=false,v43Stamp=0,v43RAF=0;
function v43Of(s){
 if(!s.directorV43||typeof s.directorV43!=='object'||Array.isArray(s.directorV43))
  s.directorV43={};
 const out=s.directorV43;
 if(!Object.prototype.hasOwnProperty.call(v43Profiles,out.profile))out.profile='duel';
 const defaults=v43Profiles[out.profile];
 if(!['wide','medium','close'].includes(out.shot))out.shot=defaults.shot;
 for(const name of ['zoom','focus','recoil','tempo','tilt']){
  const x=Number(out[name]);
  out[name]=Number.isFinite(x)?clamp(x,0,100):defaults[name];
 }
 out.enabled=out.enabled!==false;
 out.reducedMotion=out.reducedMotion===true;
 return out;
}
function v43Easing(t){const x=clamp(t,0,1);return x*x*(3-2*x);}
function v43DirectorState(s,t){
 const opt=v43Of(s);
 const idle={enabled:false,zoom:1,shiftX:0,shiftY:0,angle:0,
  event:'idle',actor:null,impact:0,beat:null};
 if(!opt.enabled||s.kind!=='fight')return idle;
 const local=clamp(t,0,Math.max(.01,s.duration)),normal=local/Math.max(.01,s.duration);
 const e=v25Contact(s,local);
 const base=opt.shot==='wide'?1.017:opt.shot==='close'?1.085:1.04;
 const slide=(.018+.035*opt.focus/100);
 const prepar=e.active?clamp(e.anticipation||0,0,1):0;
 const attack=e.active?clamp(e.release||0,0,1):0;
 const actualHit=e.active&&e.outcome==='hit'?clamp(e.contact||0,0,1):0;
 const actualBlock=e.active&&e.outcome==='block'?clamp(e.contact||0,0,1):0;
 const actualDodge=e.active&&e.outcome==='dodge'?clamp(e.defense||0,0,1):0;
 const impact=Math.max(actualHit,actualBlock);
 const pose=v43Easing(Math.min(1,normal*7))*v43Easing(Math.min(1,(1-normal)*7));
 const breathe=Math.sin(normal*Math.PI*2)*.008*pose;
 const direction=e.actor==='partner'?-1:1;
 const focusDirection=e.outcome==='hit'||e.outcome==='block'?
  -direction:direction;
 const surge=attack*(.02+.03*opt.tempo/100)+impact*.035+actualDodge*.022;
 const emphasis=opt.zoom/100;
 const cameraZoom=clamp(base+emphasis*(.09*prepar+.08*surge+.14*impact+.075*actualDodge)+breathe,1,1.28);
 // Camera is a deterministic virtual crop around the already-painted 2D stage.
 const focus=slide*opt.focus/100*pose*(.45+.55*attack);
 const shiftX=focusDirection*focus;
 const shake=opt.reducedMotion?0:opt.recoil/100;
 const shiftY=Math.sin(local*31)*actualHit*.012*shake+
  Math.sin(local*25)*actualBlock*.007*shake;
 const tilt=opt.reducedMotion?0:
  direction*Math.PI/180*(opt.tilt/100)*(actualDodge*2.1+actualHit*1.4);
 return {enabled:true,zoom:cameraZoom,shiftX,shiftY,angle:tilt,
  event:e.active?e.outcome:'idle',actor:e.actor||null,
  impact,beat:e};
}
function v43Shot(canvas,episode,second){
 const state=v43BaseFrame(canvas,episode,second),row=state?.row;
 if(!row)return state;
 const options=v43DirectorState(row.scene,Math.max(0,state.t-row.start));
 if(!options.enabled)return state;
 const w=canvas.width,h=canvas.height,ctx=canvas.getContext('2d');
 if(!v43Shot.scratch)v43Shot.scratch=document.createElement('canvas');
 const tmp=v43Shot.scratch;
 if(tmp.width!==w)tmp.width=w;
 if(tmp.height!==h)tmp.height=h;
 const cg=tmp.getContext('2d');cg.clearRect(0,0,w,h);
 cg.drawImage(canvas,0,0);
 ctx.save();ctx.clearRect(0,0,w,h);ctx.fillStyle='#08101a';ctx.fillRect(0,0,w,h);
 ctx.translate(w/2+options.shiftX*w,h/2+options.shiftY*h);
 ctx.rotate(options.angle);ctx.scale(options.zoom,options.zoom);
 ctx.drawImage(tmp,-w/2,-h/2,w,h);
 ctx.restore();
 // Subtitles must stay fixed/readable, unaffected by crop, tilt or recoil.
 v37Paint(canvas,episode,second);
 return state;
}
v38Frame=function(canvas,episode,second){return v43Shot(canvas,episode,second);};
function v43Episode(){
 if(!P)return null;
 return P.episodes[Number($('v43-episode').value)||0]||P.episodes[0]||null;
}
function v43Scene(){
 const ep=v43Episode();return ep?.scenes?.[Number($('v43-scene').value)||0]||null;
}
function v43Show(){
 if(!P)return;v43Pause();
 const el=$('v43-episode'),old=el.value;
 el.innerHTML=P.episodes.map((ep,i)=>'<option value="'+i+'">Серия '+ep.number+
  ' — '+escapeHTML(ep.title)+'</option>').join('');
 el.value=[...el.options].some(o=>o.value===old)?old:String(epIndex);
 if(!el.value&&P.episodes.length)el.value='0';
 v43Scenes();
}
function v43Scenes(){
 v43Pause();const ep=v43Episode(),el=$('v43-scene'),old=el.value;
 el.innerHTML=(ep?.scenes||[]).map((s,i)=>'<option value="'+i+'">'+(i+1)+'. '+
  escapeHTML(s.title)+(s.kind==='fight'?' · Бой':'')+'</option>').join('');
 const firstFight=ep?.scenes?.findIndex(s=>s.kind==='fight')??-1;
 el.value=[...el.options].some(o=>o.value===old)?old:String(firstFight>=0?firstFight:0);
 v43Controls();v43SeekScene();v43Render();
}
function v43Controls(){
 const s=v43Scene();if(!s)return;
 const opt=v43Of(s);
 $('v43-enabled').checked=opt.enabled;
 $('v43-reduced').checked=opt.reducedMotion;
 $('v43-profile').value=opt.profile;
 $('v43-shot').value=opt.shot;
 for(const name of ['zoom','focus','recoil','tempo','tilt']){
  $('v43-'+name).value=opt[name];
  $('v43-label-'+name).textContent=String(opt[name]);
 }
}
function v43SeekScene(){
 const ep=v43Episode();if(!ep)return;
 const plan=v35Plan(ep),index=Number($('v43-scene').value)||0;
 const row=plan.rows.find(r=>r.index===index);
 v43Clock=row?row.start+Math.min(row.duration*.36,Math.max(.2,row.duration*.5)):0;
}
function v43Preset(){
 const s=v43Scene();if(!s)return;
 const opt=v43Of(s),preset=$('v43-profile').value;
 Object.assign(opt,v43Profiles[preset],{profile:preset,enabled:true});
 save();v43Controls();v43Render();
}
function v43Save(){
 const s=v43Scene();if(!s)return;
 const opt=v43Of(s);
 opt.enabled=$('v43-enabled').checked;
 opt.reducedMotion=$('v43-reduced').checked;
 opt.profile=$('v43-profile').value;opt.shot=$('v43-shot').value;
 for(const name of ['zoom','focus','recoil','tempo','tilt'])
  opt[name]=Number($('v43-'+name).value);
 save();v43Render();
 notify('V43: постановка камеры сохранена; боевые события и сюжет не изменены.');
}
function v43Render(){
 const ep=v43Episode(),plan=v35Plan(ep);
 if(!ep||!plan.rows.length)return;
 v43Clock=clamp(v43Clock,0,plan.duration);
 const canvas=$('v43-preview'),state=v38Frame(canvas,ep,v43Clock),row=state?.row;
 const local=row?Math.max(0,v43Clock-row.start):0;
 const info=row?v43DirectorState(row.scene,local):null;
 $('v43-time').textContent=v43Clock.toFixed(2)+' / '+plan.duration.toFixed(2)+
  ' c · '+(row?.title||'')+
  ' · '+(info?.event||'idle')+' · '+(info?.zoom||1).toFixed(3)+'×';
 $('v43-seek').value=plan.duration?Math.round(1000*v43Clock/plan.duration):0;
}
function v43Pause(){
 v43Playing=false;v43Stamp=0;
 if(v43RAF){cancelAnimationFrame(v43RAF);v43RAF=0;}
 if($('v43-play'))$('v43-play').textContent='Воспроизвести';
}
function v43Tick(time){
 if(!v43Playing)return;
 const dt=v43Stamp?Math.min(.15,(time-v43Stamp)/1000):0;
 v43Stamp=time;
 v43Clock=Math.min(v35Plan(v43Episode()).duration,v43Clock+dt);
 v43Render();
 if(v43Clock>=v35Plan(v43Episode()).duration){v43Pause();return;}
 v43RAF=requestAnimationFrame(v43Tick);
}
function v43Toggle(){
 if(v43Playing){v43Pause();return;}
 const plan=v35Plan(v43Episode());if(!plan.rows.length)return;
 if(v43Clock>=plan.duration)v43Clock=0;
 v43Playing=true;v43Stamp=0;$('v43-play').textContent='Пауза';
 v43RAF=requestAnimationFrame(v43Tick);
}
function v43Manifest(){
 if(!P)return {};
 return {format:'AIAnimeFactoryActionCamera/43',version:43,
  episodes:P.episodes.map(ep=>({number:ep.number,title:ep.title,
   scenes:ep.scenes.map((s,i)=>({index:i,title:s.title,kind:s.kind,
    direction:{...v43Of(s)}}))})),
  note:'All V19-V42 narrative/actor/combat/audio/subtitles remain authoritative.'};
}
function v43Audit(){
 const result=[];if(!P)return result;
 for(const ep of P.episodes)for(const s of ep.scenes){
  const opt=v43Of(s);
  if(!opt.enabled||s.kind!=='fight')continue;
  const pre='Серия '+ep.number+', '+s.title+': ';
  if(opt.recoil>86&&!opt.reducedMotion)
   result.push(pre+'очень сильный толчок камеры может вызывать дискомфорт.');
  if(opt.zoom>90&&opt.shot==='close')
   result.push(pre+'слишком крупное приближение может обрезать бойцов.');
  if(opt.tempo<20)
   result.push(pre+'низкая выразительность боевого ритма.');
 }
 return result;
}
async function v43Evidence(){
 await preloadArtwork();
 const ep=v43Episode(),plan=v35Plan(ep);
 if(!ep||!plan.rows.length)return;
 const one=document.createElement('canvas'),sheet=document.createElement('canvas');
 one.width=640;one.height=360;sheet.width=1280;sheet.height=720;
 const ctx=sheet.getContext('2d');
 for(let i=0;i<4;i++){
  const second=plan.duration*(i+.5)/4;
  v38Frame(one,ep,second);
  ctx.drawImage(one,(i%2)*640,Math.floor(i/2)*360);
 }
 download('V43_ACTION_CAMERA_FOUR_REAL_FRAMES_'+slug(ep.title)+'.png',
  await blobPNG(sheet));
}
$('v43-episode').onchange=v43Scenes;
$('v43-scene').onchange=()=>{v43Controls();v43SeekScene();v43Render();};
$('v43-profile').onchange=v43Preset;
$('v43-enabled').onchange=v43Save;
$('v43-reduced').onchange=v43Save;
$('v43-shot').onchange=v43Save;
for(const name of ['zoom','focus','recoil','tempo','tilt']){
 $('v43-'+name).oninput=()=>{
  $('v43-label-'+name).textContent=$('v43-'+name).value;
  v43Render();
 };
}
$('v43-save').onclick=v43Save;
$('v43-play').onclick=v43Toggle;
$('v43-first').onclick=()=>{v43Pause();v43Clock=0;v43Render();};
$('v43-seek').oninput=e=>{
 v43Pause();v43Clock=v35Plan(v43Episode()).duration*Number(e.target.value)/1000;
 v43Render();
};
$('v43-sheet').onclick=async()=>{try{await v43Evidence();}catch(e){notify('V43 PNG: '+e.message);}};
$('v43-json').onclick=()=>download('V43_ACTION_CAMERA.json',
 new Blob([JSON.stringify(v43Manifest(),null,2)],{type:'application/json;charset=utf-8'}));
$('v43-audit').onclick=()=>{$('v43-report').textContent=v43Audit().join('\n')||
 'V43: предупреждений по постановке боя не найдено.';};
