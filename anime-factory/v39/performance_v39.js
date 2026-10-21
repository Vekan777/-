/* AI Anime Factory V39: real procedural-rig performance and outcome-faithful combat.
   No new hit/event can be created. No rewrite of scene story or original animation.
   V39 enhances v24Dynamics and v13Face at their ORIGINAL draw-time call sites.
*/
const v39Defaults={enabled:true,energy:65,facial:62,anticipation:72,
 followThrough:68,impact:70,streaks:48};
const v39PrevMotion=v24Dynamics, v39PrevFace=v13Face;
let v39At=0,v39Playing=false,v39Stamp=0,v39RAF=0;
function v39Of(s){
 if(!s.performanceV39||typeof s.performanceV39!=='object'||Array.isArray(s.performanceV39))
  s.performanceV39={};
 const o=s.performanceV39;
 for(const [key,val] of Object.entries(v39Defaults)){
  if(key==='enabled')o.enabled=o.enabled!==false;
  else o[key]=Number.isFinite(Number(o[key]))?clamp(Number(o[key]),0,100):val;
 }
 return o;
}
function v39Pulse(time,center,width){
 const d=(time-center)/Math.max(.02,width);return Math.exp(-d*d*3);
}
function v39Move(s,t,role){
 const o=v39Of(s);
 const z={rootX:0,bob:0,lean:0,handX:0,handLift:0,
  headX:0,hair:0,cloth:0,strike:0,guard:0};
 if(!o.enabled)return z;
 const focus=clamp(t/Math.max(.1,s.duration),0,1);
 const mood=s.kind==='fight'?1:.35,energy=o.energy/100;
 const phase=t*(s.kind==='fight'?4.5:2.35)+(role==='hero'?0:1.73);
 const breathing=Math.sin(phase)*energy*mood;
 const contacts=s.kind==='fight'?v25Contact(s,t):null;
 const attacker=contacts?.active&&contacts.actor===role;
 const defender=contacts?.active&&contacts.actor!==role;
 const release=attacker?contacts.release:0;
 const brace=attacker?contacts.anticipation:0;
 const realHit=defender&&contacts.outcome==='hit'?contacts.contact:0;
 const realBlock=defender&&contacts.outcome==='block'?contacts.defense:0;
 const dodge=defender&&contacts.outcome==='dodge'?contacts.defense:0;
 const follow=energy*o.followThrough/100,prep=o.anticipation/100;
 const residual=v39Pulse(focus,role==='hero'?.42:.69,.12)*follow*.26;
 return {
  rootX:breathing*1.3+release*3.5*energy-realHit*5*energy-dodge*3*energy,
  bob:Math.abs(breathing)*1.05-realHit*2.5*energy,
  lean:release*.055*energy-brace*.052*prep-realHit*.09*energy+
   dodge*.075*energy+breathing*.007,
  handX:release*20*energy-brace*7*prep,
  handLift:release*19*energy+brace*9*prep+realBlock*10*energy,
  headX:realHit*6*energy-release*2*energy,
  hair:(release*.65+realHit*.8+residual)*follow,
  cloth:(release*.7+realHit*.65+residual)*follow,
  strike:release*.17*energy,
  guard:realBlock*.26*energy
 };
}
v24Dynamics=function(s,t,role){
 const origin=v39PrevMotion(s,t,role),add=v39Move(s,t,role);
 return {...origin,rootX:origin.rootX+add.rootX,bob:origin.bob+add.bob,
  lean:origin.lean+add.lean,strike:origin.strike+add.strike,
  guard:origin.guard+add.guard,handX:origin.handX+add.handX,
  handLift:origin.handLift+add.handLift,
  headX:origin.headX+add.headX,hair:origin.hair+add.hair,cloth:origin.cloth+add.cloth};
};
v13Face=function(s,role,t,override=null){
 const base=v39PrevFace(s,role,t,override),o=v39Of(s);
 if(!o.enabled)return base;
 const weight=(o.facial/100);
 const contact=s.kind==='fight'?v25Contact(s,t):null;
 const beingHit=contact?.active&&contact.actor!==role&&contact.outcome==='hit';
 const defended=contact?.active&&contact.actor!==role&&contact.outcome==='block';
 const releasing=contact?.active&&contact.actor===role;
 const intensity=(beingHit?contact.contact:releasing?contact.release:defended?contact.defense:0)*weight;
 const shake=beingHit?intensity:0;
 const brows=(releasing?.25:beingHit?-.16:0)*intensity;
 return {...base,brow:clamp(base.brow+brows,-1,1),
  eye:clamp(base.eye-(releasing?.12:beingHit?.25:0)*intensity,.3,1.5),
  smile:clamp(base.smile-(releasing?.12:beingHit?.22:0)*intensity,-1,1),
  closed:clamp(base.closed+shake*.42,0,1)};
};
function v39Effects(ctx,state,width,height){
 const row=state?.row;if(!row)return;
 const s=row.scene,o=v39Of(s);
 if(!o.enabled||s.kind!=='fight')return;
 const local=clamp(state.t-row.start,0,row.duration),beat=v25Contact(s,local);
 if(!beat.active)return;
 const strength=o.impact/100,lines=o.streaks/100;
 const x=width*(beat.actor==='hero'?.53:.47),y=height*.53;
 // Only the canonical V17/V19 classified outcome may trigger contact visuals.
 const confirmed=(beat.outcome==='hit'||beat.outcome==='block')?beat.contact:0;
 const evasion=beat.outcome==='dodge'?beat.defense:0;
 const attack=beat.release||0;
 ctx.save();ctx.lineCap='round';
 if(lines>.01&&attack>.04){
  const alpha=Math.min(.36,lines*attack*.28);
  ctx.strokeStyle='rgba(210,238,255,'+alpha.toFixed(3)+')';
  for(let i=0;i<12;i++){
   const dx=(i-5.5)/11,edgeX=width*(.5+dx*.55);
   const edgeY=height*(.32+(i%4)*.115);
   ctx.beginPath();ctx.moveTo(edgeX,edgeY);
   ctx.lineTo(x+(edgeX-x)*.55,y+(edgeY-y)*.55);
   ctx.lineWidth=Math.max(1,width/640*(.9+(i%3)*.6));ctx.stroke();
  }
 }
 if(confirmed>.01&&strength>.01){
  const radius=width/640*(15+strength*confirmed*40);
  const a=Math.min(.8,strength*confirmed*.68);
  ctx.strokeStyle=beat.outcome==='block'?
   'rgba(108,204,255,'+a.toFixed(3)+')':
   'rgba(255,221,156,'+a.toFixed(3)+')';
  ctx.lineWidth=Math.max(1.5,width/640*2.8);
  ctx.beginPath();ctx.arc(x,y,radius,0,Math.PI*2);ctx.stroke();
  for(let i=0;i<8;i++){
   const theta=i*Math.PI/4,inner=radius*.6,outer=radius*1.45;
   ctx.beginPath();
   ctx.moveTo(x+Math.cos(theta)*inner,y+Math.sin(theta)*inner);
   ctx.lineTo(x+Math.cos(theta)*outer,y+Math.sin(theta)*outer);
   ctx.stroke();
  }
 }
 if(evasion>.04){
  const a=Math.min(.36,strength*evasion*.4);
  ctx.strokeStyle='rgba(160,225,250,'+a.toFixed(3)+')';
  ctx.lineWidth=width/640*2;
  for(let i=0;i<3;i++){
   ctx.beginPath();ctx.arc(x+width*.1,y,i*width*.022+width*.025,Math.PI*.78,Math.PI*1.2);ctx.stroke();
  }
 }
 ctx.restore();
}
function v39Episode(){
 if(!P)return null;
 return P.episodes[Number($('v39-episode').value)||0]||P.episodes[0]||null;
}
function v39Scene(){
 const e=v39Episode();
 return e?.scenes?.[Number($('v39-scene').value)||0]||null;
}
function v39Show(){
 if(!P)return;
 v39Pause();const select=$('v39-episode'),old=select.value;
 select.innerHTML=P.episodes.map((ep,i)=>
  '<option value="'+i+'">Серия '+ep.number+' — '+escapeHTML(ep.title)+'</option>').join('');
 select.value=[...select.options].some(o=>o.value===old)?old:String(epIndex);
 if(!select.value&&P.episodes.length)select.value='0';
 v39Scenes();
}
function v39Scenes(){
 v39Pause();const ep=v39Episode(),sel=$('v39-scene'),old=sel.value;
 sel.innerHTML=(ep?.scenes||[]).map((s,i)=>
  '<option value="'+i+'">'+(i+1)+'. '+escapeHTML(s.title)+'</option>').join('');
 sel.value=[...sel.options].some(o=>o.value===old)?old:'0';
 v39Controls();v39At=0;v39Render();
}
function v39Controls(){
 const s=v39Scene();if(!s)return;
 const o=v39Of(s);
 $('v39-enabled').checked=o.enabled;
 for(const key of ['energy','facial','anticipation','followThrough','impact','streaks']){
  $('v39-'+key).value=o[key];$('v39-label-'+key).textContent=String(o[key]);
 }
}
function v39Save(){
 const s=v39Scene();if(!s)return;
 const o=v39Of(s);o.enabled=$('v39-enabled').checked;
 for(const key of ['energy','facial','anticipation','followThrough','impact','streaks'])
  o[key]=Number($('v39-'+key).value);
 save();v39Render();
 notify('V39: движения рига и экспрессия сохранены, канонические атаки не изменены.');
}
function v39Preset(){
 const s=v39Scene();if(!s)return;
 const o=v39Of(s);
 if(s.kind==='fight')Object.assign(o,{energy:78,facial:70,anticipation:85,
  followThrough:80,impact:82,streaks:68});
 else Object.assign(o,{energy:32,facial:76,anticipation:45,
  followThrough:38,impact:0,streaks:0});
 save();v39Controls();v39Render();
}
function v39Frame(canvas,episode,sec){return v38Frame(canvas,episode,sec);}
function v39Render(){
 const e=v39Episode(),p=v35Plan(e);if(!e||!p.rows.length)return;
 v39At=clamp(v39At,0,p.duration);
 const s=v39Frame($('v39-preview'),e,v39At);
 $('v39-time').textContent=v39At.toFixed(2)+' / '+p.duration.toFixed(2)+
  ' сек · сцена '+((s.row?.index??0)+1)+'/'+p.rows.length;
 $('v39-seek').value=p.duration?Math.round(v39At/p.duration*1000):0;
}
function v39Pause(){
 v39Playing=false;v39Stamp=0;
 if(v39RAF){cancelAnimationFrame(v39RAF);v39RAF=0;}
 if($('v39-play'))$('v39-play').textContent='Воспроизвести';
}
function v39Tick(ts){
 if(!v39Playing)return;
 const dt=v39Stamp?Math.min(.15,(ts-v39Stamp)/1000):0;
 v39Stamp=ts;v39At=Math.min(v35Plan(v39Episode()).duration,v39At+dt);
 v39Render();if(v39At>=v35Plan(v39Episode()).duration){v39Pause();return;}
 v39RAF=requestAnimationFrame(v39Tick);
}
function v39Toggle(){
 if(v39Playing){v39Pause();return;}
 const p=v35Plan(v39Episode());if(!p.rows.length)return;
 if(v39At>=p.duration)v39At=0;
 v39Playing=true;v39Stamp=0;$('v39-play').textContent='Пауза';
 v39RAF=requestAnimationFrame(v39Tick);
}
function v39Audit(){
 if(!P)return ['Проект не открыт.'];
 const issues=[];
 for(const ep of P.episodes)for(const s of ep.scenes){
  const o=v39Of(s);if(!o.enabled)continue;
  const tag='Серия '+ep.number+', '+s.title+': ';
  if(s.kind==='fight'&&o.anticipation<15)
   issues.push(tag+'почти отсутствует подготовка к удару.');
  if(s.kind==='fight'&&o.followThrough<15)
   issues.push(tag+'недостаточная инерция после удара.');
  if(s.kind==='fight'&&o.streaks>90&&o.impact>90)
   issues.push(tag+'эффекты могут закрывать персонажей.');
  if(s.kind!=='fight'&&o.energy>90)
   issues.push(tag+'слишком высокая энергия для спокойной сцены.');
 }
 return issues;
}
function v39Manifest(){
 if(!P)return {};
 return {format:'AIAnimeFactoryCharacterPerformance/39',version:39,
  episodes:P.episodes.map(ep=>({number:ep.number,title:ep.title,
   scenes:ep.scenes.map((s,i)=>({index:i,title:s.title,kind:s.kind,
    performance:{...v39Of(s)}}))})),warnings:v39Audit(),
  note:'V17/V19 combat events are authoritative. No story or contact outcome is changed.'};
}
async function v39Evidence(){
 await preloadArtwork();
 const e=v39Episode(),p=v35Plan(e);if(!p.rows.length)return;
 const one=document.createElement('canvas'),grid=document.createElement('canvas');
 one.width=640;one.height=360;grid.width=1280;grid.height=720;
 const g=grid.getContext('2d');
 for(let i=0;i<4;i++){
  v39Frame(one,e,p.duration*(i+.5)/4);
  g.drawImage(one,(i%2)*640,Math.floor(i/2)*360);
 }
 download('V39_FOUR_REAL_CHARACTER_FRAMES_'+slug(e.title)+'.png',await blobPNG(grid));
}
$('v39-episode').onchange=v39Scenes;
$('v39-scene').onchange=()=>{v39Controls();v39Render();};
for(const key of ['energy','facial','anticipation','followThrough','impact','streaks']){
 $('v39-'+key).oninput=()=>{$('v39-label-'+key).textContent=$('v39-'+key).value;};
}
$('v39-save').onclick=v39Save;
$('v39-preset').onclick=v39Preset;
$('v39-play').onclick=v39Toggle;
$('v39-first').onclick=()=>{v39Pause();v39At=0;v39Render();};
$('v39-seek').oninput=e=>{
 v39Pause();v39At=v35Plan(v39Episode()).duration*Number(e.target.value)/1000;v39Render();
};
$('v39-audit').onclick=()=>{$('v39-report').textContent=v39Audit().join('\n')||
 'V39: эвристические предупреждения не обнаружены.';};
$('v39-json').onclick=()=>download('V39_CHARACTER_PERFORMANCE.json',
 new Blob([JSON.stringify(v39Manifest(),null,2)],{type:'application/json;charset=utf-8'}));
$('v39-sheet').onclick=async()=>{try{await v39Evidence();}catch(err){notify('V39 PNG: '+err.message);}};
