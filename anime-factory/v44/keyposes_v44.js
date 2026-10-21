/* AI Anime Factory V44 — true pose control for the existing procedural 2D rig.
 * Extends draw-time V24/V39 motion and existing V24 foot placement, not
 * a screen overlay or synthesized combat event. Canon V25 contact is absolute.
 */
const v44Profiles={
 grounded:{stance:85,reach:58,guard:74,recovery:64,steps:76,secondary:48},
 agile:{stance:56,reach:82,guard:48,recovery:88,steps:91,secondary:78},
 powerful:{stance:92,reach:96,guard:80,recovery:74,steps:49,secondary:84}
};
const v44PrevDynamics=v24Dynamics,v44PrevFoot=v24FootPose;
let v44Time=0,v44Playing=false,v44Stamp=0,v44RAF=0;
function v44Of(s){
 if(!s.keyposesV44||typeof s.keyposesV44!=='object'||Array.isArray(s.keyposesV44))
  s.keyposesV44={};
 const opt=s.keyposesV44;
 if(!Object.prototype.hasOwnProperty.call(v44Profiles,opt.profile))opt.profile='grounded';
 const defaults=v44Profiles[opt.profile];
 opt.enabled=opt.enabled!==false;
 for(const name of ['stance','reach','guard','recovery','steps','secondary']){
  const num=Number(opt[name]);
  opt[name]=Number.isFinite(num)?clamp(num,0,100):defaults[name];
 }
 return opt;
}
function v44Ease(x){const a=clamp(x,0,1);return a*a*(3-2*a);}
function v44Pulse(t,center,width){
 const d=(t-center)/Math.max(.02,width);
 return Math.exp(-d*d*3);
}
function v44Pose(s,t,role){
 const opt=v44Of(s);
 const none={rootX:0,bob:0,lean:0,handX:0,handLift:0,
  headX:0,hair:0,cloth:0,strike:0,guard:0,step:0};
 if(!opt.enabled||s.kind!=='fight')return none;
 const seconds=clamp(t,0,Math.max(.1,s.duration));
 const progress=seconds/Math.max(.1,s.duration),contact=v25Contact(s,seconds);
 const attacker=contact.active&&contact.actor===role;
 const defender=contact.active&&contact.actor!==role;
 const prep=attacker?clamp(contact.anticipation,0,1):0;
 const release=attacker?clamp(contact.release,0,1):0;
 const hit=defender&&contact.outcome==='hit'?clamp(contact.contact,0,1):0;
 const block=defender&&contact.outcome==='block'?clamp(contact.defense,0,1):0;
 const dodge=defender&&contact.outcome==='dodge'?clamp(contact.defense,0,1):0;
 const planted=opt.stance/100,reach=opt.reach/100,guard=opt.guard/100;
 const recovery=opt.recovery/100,foot=opt.steps/100,follow=opt.secondary/100;
 const direction=role==='hero'?1:-1;
 const stanceTime=v44Ease(Math.min(1,progress*13))*v44Ease(Math.min(1,(1-progress)*13));
 const slow=Math.sin(seconds*2.9+(role==='partner'?1.8:0));
 // A held fighting stance exists even outside the peaks of the canonical
 // attack, making the new pose visible at arbitrary, reproducible timestamps.
 const brace=stanceTime*planted;
 const withdrawal=prep*planted;
 const drive=release*reach;
 // Recovery follows real contact; it may also follow a missed *release*
 // but must NEVER be represented as a hit.
 const residual=release*recovery*.28+hit*recovery*.35;
 return {
  rootX:direction*(drive*5-withdrawal*4-dodge*8*foot-hit*3),
  bob:brace*.75+drive*1.1-hit*3+dodge*1.8,
  lean:direction*(brace*.012-withdrawal*.09+drive*.14-
    hit*.105+block*.048-dodge*.095),
  handX:direction*(brace*6-withdrawal*11+drive*36-dodge*6),
  handLift:brace*8+withdrawal*16+drive*39+block*29*guard+
    hit*10+residual*5,
  headX:direction*(withdrawal*2-drive*3+hit*9-dodge*4),
  hair:(drive*.92+hit*.70+residual*.7)*follow,
  cloth:(drive*.9+block*.35+residual*.95+Math.abs(slow)*.13)*follow,
  strike:drive*.34,
  guard:brace*guard*.2+block*guard*.65,
  step:(drive*.18+withdrawal*.1+dodge*.3)*foot
 };
}
v24Dynamics=function(s,t,role){
 const base=v44PrevDynamics(s,t,role),p=v44Pose(s,t,role);
 return {...base,rootX:base.rootX+p.rootX,bob:base.bob+p.bob,
  lean:base.lean+p.lean,handX:base.handX+p.handX,
  handLift:base.handLift+p.handLift,headX:base.headX+p.headX,
  hair:base.hair+p.hair,cloth:base.cloth+p.cloth,
  strike:base.strike+p.strike,guard:base.guard+p.guard,
  step:base.step+p.step};
};
v24FootPose=function(s,t,role,side,baseX,baseY){
 const [x,y]=v44PrevFoot(s,t,role,side,baseX,baseY);
 const opt=v44Of(s);if(!opt.enabled||s.kind!=='fight')return [x,y];
 const beat=v25Contact(s,t),attack=beat.active&&beat.actor===role;
 const defend=beat.active&&beat.actor!==role;
 const release=attack?clamp(beat.release,0,1):0;
 const anticipate=attack?clamp(beat.anticipation,0,1):0;
 const evade=defend&&beat.outcome==='dodge'?clamp(beat.defense,0,1):0;
 const hit=defend&&beat.outcome==='hit'?clamp(beat.contact,0,1):0;
 const power=opt.steps/100,stance=opt.stance/100,sign=side==='left'?-1:1;
 const phase=t*2.65+(role==='partner'?1.95:0);
 // Opposite grounded weight shift for each planted foot.
 const weight=Math.sin(phase)*stance;
 const shift=sign*(3.5*weight+14*release*power-
  8*anticipate*power-12*evade*power-4*hit*power);
 const lift=Math.max(0,Math.sin(phase+sign*Math.PI*.25))*
  (2.8+5*power)*power+evade*7*power;
 return [x+shift,y-lift];
};
function v44Episode(){
 if(!P)return null;
 return P.episodes[Number($('v44-episode').value)||0]||P.episodes[0]||null;
}
function v44Scene(){
 const ep=v44Episode();
 return ep?.scenes?.[Number($('v44-scene').value)||0]||null;
}
function v44Show(){
 if(!P)return;v44Pause();
 const sel=$('v44-episode'),old=sel.value;
 sel.innerHTML=P.episodes.map((ep,i)=>
  '<option value="'+i+'">Серия '+ep.number+' — '+escapeHTML(ep.title)+'</option>').join('');
 sel.value=[...sel.options].some(o=>o.value===old)?old:String(epIndex);
 if(!sel.value&&P.episodes.length)sel.value='0';
 v44Scenes();
}
function v44Scenes(){
 v44Pause();
 const ep=v44Episode(),el=$('v44-scene'),old=el.value;
 el.innerHTML=(ep?.scenes||[]).map((s,i)=>
  '<option value="'+i+'">'+(i+1)+'. '+escapeHTML(s.title)+
  (s.kind==='fight'?' · Бой':'')+'</option>').join('');
 const first=(ep?.scenes||[]).findIndex(s=>s.kind==='fight');
 el.value=[...el.options].some(o=>o.value===old)?old:String(first>=0?first:0);
 v44Controls();v44SeekScene();v44Render();
}
function v44Controls(){
 const s=v44Scene();if(!s)return;
 const o=v44Of(s);
 $('v44-enabled').checked=o.enabled;
 $('v44-profile').value=o.profile;
 for(const name of ['stance','reach','guard','recovery','steps','secondary']){
  $('v44-'+name).value=o[name];$('v44-label-'+name).textContent=String(o[name]);
 }
}
function v44SeekScene(){
 const ep=v44Episode(),plan=v35Plan(ep);
 if(!plan?.rows?.length)return;
 const row=plan.rows.find(r=>r.index===Number($('v44-scene').value));
 v44Time=row?row.start+row.duration*.32:0;
}
function v44Save(){
 const s=v44Scene();if(!s)return;
 const o=v44Of(s);
 o.enabled=$('v44-enabled').checked;o.profile=$('v44-profile').value;
 for(const k of ['stance','reach','guard','recovery','steps','secondary'])
  o[k]=Number($('v44-'+k).value);
 save();v44Render();
 notify('V44: настоящие позы и постановка шагов сохранены, канон не изменён.');
}
function v44Preset(){
 const s=v44Scene();if(!s)return;
 const o=v44Of(s),profile=$('v44-profile').value;
 Object.assign(o,v44Profiles[profile],{profile,enabled:true});
 save();v44Controls();v44Render();
}
function v44Render(){
 const ep=v44Episode(),plan=v35Plan(ep);if(!ep||!plan.rows.length)return;
 v44Time=clamp(v44Time,0,plan.duration);
 const state=v38Frame($('v44-preview'),ep,v44Time),row=state?.row;
 const local=row?Math.max(0,v44Time-row.start):0,beat=row?v25Contact(row.scene,local):null;
 $('v44-time').textContent=v44Time.toFixed(2)+' / '+plan.duration.toFixed(2)+
  ' сек · '+(row?.scene?.title||'')+' · '+(beat?.outcome||'idle');
 $('v44-seek').value=plan.duration?Math.round(1000*v44Time/plan.duration):0;
}
function v44Pause(){
 v44Playing=false;v44Stamp=0;
 if(v44RAF){cancelAnimationFrame(v44RAF);v44RAF=0;}
 if($('v44-play'))$('v44-play').textContent='Воспроизвести';
}
function v44Tick(ts){
 if(!v44Playing)return;
 const dt=v44Stamp?Math.min(.15,(ts-v44Stamp)/1000):0;
 v44Stamp=ts;v44Time=Math.min(v35Plan(v44Episode()).duration,v44Time+dt);
 v44Render();
 if(v44Time>=v35Plan(v44Episode()).duration){v44Pause();return;}
 v44RAF=requestAnimationFrame(v44Tick);
}
function v44Toggle(){
 if(v44Playing){v44Pause();return;}
 const plan=v35Plan(v44Episode());if(!plan.rows.length)return;
 if(v44Time>=plan.duration)v44Time=0;
 v44Playing=true;v44Stamp=0;$('v44-play').textContent='Пауза';
 v44RAF=requestAnimationFrame(v44Tick);
}
function v44Manifest(){
 if(!P)return {};
 return {format:'AIAnimeFactoryActorKeyposes/44',version:44,
  episodes:P.episodes.map(ep=>({number:ep.number,title:ep.title,
   scenes:ep.scenes.map((s,i)=>({index:i,title:s.title,kind:s.kind,
    keyposes:{...v44Of(s)}}))})),
  note:'Only existing V25 hit/block/dodge/miss allowed. V19–V43 old data remains authoritative.'};
}
function v44Audit(){
 const errors=[];if(!P)return errors;
 for(const ep of P.episodes)for(const s of ep.scenes){
  const o=v44Of(s);if(!o.enabled||s.kind!=='fight')continue;
  const id='Серия '+ep.number+', '+s.title+': ';
  if(o.reach>95&&o.stance>93)errors.push(id+'сильно вытянутая рука и широкая стойка могут выглядеть неестественно.');
  if(o.steps>95&&o.stance<20)errors.push(id+'большие шаги без опоры.');
  if(o.guard<12)errors.push(id+'слабая защитная стойка.');
 }
 return errors;
}
async function v44Sheet(){
 await preloadArtwork();
 const ep=v44Episode(),plan=v35Plan(ep);
 if(!ep||!plan.rows.length)return;
 const frame=document.createElement('canvas'),grid=document.createElement('canvas');
 frame.width=640;frame.height=360;grid.width=1280;grid.height=720;
 const ctx=grid.getContext('2d'),s=v44Scene(),o=v44Of(s),prev=o.enabled;
 try{
  const row=plan.rows.find(r=>r.index===Number($('v44-scene').value));
  for(let i=0;i<4;i++){
   o.enabled=i%2===1;
   const t=row?row.start+row.duration*(i<2?.3:.68):plan.duration*(i+.5)/4;
   v38Frame(frame,ep,t);
   ctx.drawImage(frame,(i%2)*640,Math.floor(i/2)*360);
  }
 }finally{o.enabled=prev;}
 download('V44_TRUE_RIG_BEFORE_AFTER.png',await blobPNG(grid));
}
$('v44-episode').onchange=v44Scenes;
$('v44-scene').onchange=()=>{v44Controls();v44SeekScene();v44Render();};
$('v44-profile').onchange=v44Preset;
$('v44-enabled').onchange=v44Save;
for(const key of ['stance','reach','guard','recovery','steps','secondary']){
 $('v44-'+key).oninput=()=>{
  $('v44-label-'+key).textContent=$('v44-'+key).value;v44Render();
 };
}
$('v44-save').onclick=v44Save;
$('v44-play').onclick=v44Toggle;
$('v44-first').onclick=()=>{v44Pause();v44Time=0;v44Render();};
$('v44-seek').oninput=e=>{
 v44Pause();v44Time=v35Plan(v44Episode()).duration*Number(e.target.value)/1000;
 v44Render();
};
$('v44-sheet').onclick=async()=>{try{await v44Sheet();}catch(e){notify('V44 PNG: '+e.message);}};
$('v44-json').onclick=()=>download('V44_ACTOR_KEYPOSES.json',
 new Blob([JSON.stringify(v44Manifest(),null,2)],{type:'application/json;charset=utf-8'}));
$('v44-audit').onclick=()=>{$('v44-report').textContent=v44Audit().join('\n')||
 'Технических предупреждений о позах V44 нет. Оцените настоящие кадры.';};
