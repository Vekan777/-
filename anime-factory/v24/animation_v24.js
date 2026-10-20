/* AI Anime Factory V24: deterministic character performance and weight transfer.
   Procedural rig only. Native user-provided PNG/cutout layers remain unchanged.
   All animation is sampled from scene time (no accumulated integration state).
*/
function v24Options(s){
 if(!s.motionV24||typeof s.motionV24!=='object'||Array.isArray(s.motionV24))s.motionV24={};
 const o=s.motionV24;
 for(const [key,def] of [['stride',68],['weight',70],['anticipation',78],['recoil',66],['followThrough',64]]){
  o[key]=Number.isFinite(Number(o[key]))?clamp(Number(o[key]),0,100):def;
 }
 if(!['auto','cinematic','subtle'].includes(o.style))o.style='auto';
 o.enabled=o.enabled!==false;
 return o;
}
function v24Pulse(x,center,width){const d=(x-center)/width;return Math.exp(-d*d*2.5);}
function v24Smooth(x){const u=clamp(x,0,1);return u*u*(3-2*u);}
function v24Dynamics(s,t,role){
 const o=v24Options(s),zero={step:0,rootX:0,bob:0,lean:0,strike:0,guard:0,handX:0,handLift:0,hair:0,cloth:0,headX:0};
 if(!o.enabled)return zero;
 const v=clamp(t/Math.max(.1,s.duration),0,1);
 const battle=s.kind==='fight',style=o.style==='auto'?(battle?'cinematic':'subtle'):o.style;
 const moodScale=style==='cinematic'?1:.52;
 const stepPower=(o.stride/100)*moodScale;
 const weight=o.weight/100;
 const pace=battle?2.65:1.65;
 // Stance shifts smoothly between planted legs; phases differ for each actor.
 const phase=t*pace+(role==='partner'?Math.PI*.62:0);
 const step=Math.sin(phase)*stepPower;
 const swing=Math.cos(phase);
 const leftPlant=v24Smooth((Math.sin(phase)+1)*.5);
 const bob=(1-Math.abs(swing))*1.5*weight*stepPower;
 const rootX=Math.sin(phase*.5)*2.4*stepPower;
 let windup=0,strike=0,hit=0,block=0;
 if(battle){
  // Prefer the original V19 attack timeline when it exists; fall back to
  // existing procedural combat pulses for user projects without attack beats.
  const impact=impact19State(s,t);
  if(impact&&impact.event){
   const attacker=impact.event.actor===role;
   const approved=impact.event.outcome==='hit'||impact.event.outcome==='block';
   if(attacker){
    windup=impact.anticipation;
    strike=impact.release;
   }else{
    hit=approved&&impact.event.outcome==='hit'?impact.nearHit:0;
    block=impact.event.outcome==='block'?impact.nearHit:0;
   }
  }else{
   const attackAt=role==='hero'?.31:.61;
   windup=v24Pulse(v,attackAt-.055,.062);
   strike=v24Pulse(v,attackAt+.035,.065);
  }
 }
 const a=o.anticipation/100,m=o.recoil/100,f=o.followThrough/100;
 const lead=strike*a,brace=windup*a;
 const inertia=(v24Pulse(v,role==='hero'?.39:.69,.11)*f)*moodScale;
 const recoil=hit*m;
 const lean=(-brace*.095+lead*.13-recoil*.14+block*.045+
             Math.sin(phase)*.018*weight)*moodScale;
 return {
  step:step,
  rootX:rootX+(lead*.8-recoil*2.8)*weight,
  bob:bob-recoil*2.0*weight,
  lean,
  strike:lead,
  guard:block*m+brace*.27,
  handX:lead*24-recoil*6,
  handLift:lead*31+brace*9+block*13,
  headX:recoil*4.5-lead*1.3,
  hair:(inertia*.55+recoil*.5-brace*.25)*f,
  cloth:(inertia*.7+lead*.5-recoil*.65)*f
 };
}
function v24FootPose(s,t,role,side,baseX,baseY){
 const o=v24Options(s);if(!o.enabled)return [baseX,baseY];
 const mode=o.style==='auto'?(s.kind==='fight'?'cinematic':'subtle'):o.style;
 const k=o.stride/100*(mode==='cinematic'?1:.5);
 const phase=t*(s.kind==='fight'?2.65:1.65)+(role==='partner'?Math.PI*.62:0);
 const u=Math.sin(phase+(side==='right'?Math.PI:0));
 // A stance foot remains near the ground; a swing foot traces an upward arc.
 const swing=v24Smooth(Math.max(0,u));
 const lift=7*k*swing;
 const xshift=Math.cos(phase+(side==='right'?Math.PI:0))*10*k;
 return [baseX+xshift,baseY-lift];
}
function v24Plan(){
 if(!P)return '';
 const txt=['AI ANIME FACTORY V24 — ДВИЖЕНИЕ, ВЕС, БОЙ',P.title,''];
 for(const ep of P.episodes){
  txt.push('СЕРИЯ '+ep.number+': '+ep.title);
  for(const s of ep.scenes){
   const o=v24Options(s);
   txt.push('Сцена '+s.title+': '+s.kind,'Шаг '+o.stride+'; вес '+o.weight+
     '; подготовка '+o.anticipation+'; отдача '+o.recoil+
     '; инерция '+o.followThrough+'; стиль '+o.style+
     '; включено '+o.enabled);
  }
 }
 return txt.join('\n');
}
function v24MotionQA(){
 if(!P)return [];
 const issues=[];
 for(const ep of P.episodes)for(const s of ep.scenes){
  const o=v24Options(s);if(!o.enabled)continue;
  if(s.kind==='fight'&&o.anticipation<12)
   issues.push('Серия '+ep.number+', '+s.title+': почти отсутствует подготовка к атаке.');
  if(s.kind==='fight'&&o.recoil<12)
   issues.push('Серия '+ep.number+', '+s.title+': слабая реакция на попадания.');
  if(o.stride>94&&o.weight<15)
   issues.push('Серия '+ep.number+', '+s.title+': большой шаг при очень малом переносе веса.');
 }
 return issues;
}
function v24Show(){
 if(!P)return;
 const s=scene(),sel=$('v24-scene');
 sel.innerHTML=qualitySceneList();sel.value=epIndex+':'+scIndex;
 const o=v24Options(s);
 $('v24-enabled').checked=o.enabled;
 $('v24-style').value=o.style;
 for(const name of ['stride','weight','anticipation','recoil','followThrough']){
  $('v24-'+name).value=o[name];$('v24-'+name+'-n').textContent=String(o[name]);
 }
 $('v24-qa').textContent=v24MotionQA().slice(0,35).join('\n')||
  'Контроль движений: явных проблем с параметрами не найдено.';
 v24Preview();
}
function v24Preview(){
 if(!P)return;
 const s=scene(),o=v24Options(s),t=s.duration*(Number($('v24-playhead').value)||0)/100;
 const enabled=o.enabled;
 try{
  o.enabled=false;
  drawScene($('v24-before'),s,t);
  o.enabled=enabled;
  drawScene($('v24-after'),s,t);
 }finally{
  o.enabled=enabled;
 }
 $('v24-caption').textContent='Серия '+(epIndex+1)+' / '+s.title+' / '+t.toFixed(2)+' с.';
}
function v24Save(){
 const o=v24Options(scene());
 o.enabled=$('v24-enabled').checked;
 o.style=$('v24-style').value;
 for(const name of ['stride','weight','anticipation','recoil','followThrough'])
  o[name]=clamp(Number($('v24-'+name).value)||0,0,100);
 save();v24Show();notify('V24: движение и вес сохранены для сцены.');
}
function v24Preset(){
 const s=scene(),o=v24Options(s);
 Object.assign(o,(s.kind==='fight'?{
  style:'cinematic',stride:78,weight:79,anticipation:84,recoil:78,followThrough:70
 }:{
  style:'subtle',stride:42,weight:61,anticipation:48,recoil:35,followThrough:55
 }),{enabled:true});
 save();v24Show();notify('V24: постановочный профиль установлен.');
}
async function v24Sheet(){
 await preloadArtwork();
 const s=scene(),o=v24Options(s),out=document.createElement('canvas'),
       scratch=document.createElement('canvas'),g=out.getContext('2d');
 out.width=1280;out.height=720;scratch.width=640;scratch.height=360;
 const was=o.enabled;
 try{
  for(let i=0;i<4;i++){
   const pct=[.18,.39,.61,.82][i],x=i%2*640,y=Math.floor(i/2)*360;
   o.enabled=was;
   drawScene(scratch,s,s.duration*pct,false);
   g.drawImage(scratch,x,y);
   g.fillStyle='rgba(5,15,31,.76)';g.fillRect(x+8,y+8,210,25);
   g.font='bold 15px Arial';g.fillStyle='#f0e3c6';
   g.fillText('V24 ДВИЖЕНИЕ '+Math.round(pct*100)+'%',x+15,y+26);
  }
 }finally{o.enabled=was;}
 download('V24_MOTION_'+slug(s.title)+'.png',await blobPNG(out));
 notify('V24: кадры движения PNG сохранены.');
}
$('v24-scene').onchange=e=>{
 const parts=e.target.value.split(':').map(Number);
 selectScene(parts[0],parts[1]);show('animation-v24');
};
$('v24-playhead').oninput=v24Preview;
$('v24-style').onchange=()=>{$('v24-caption').textContent='Нажмите «Сохранить» для применения нового стиля.';};
$('v24-enabled').onchange=()=>{$('v24-caption').textContent='Нажмите «Сохранить» для применения переключателя.';};
$('v24-save').onclick=v24Save;
$('v24-preset').onclick=v24Preset;
$('v24-sheet').onclick=async()=>{try{await v24Sheet();}catch(e){notify('V24 PNG: '+e.message);}};
$('v24-plan').onclick=()=>download('V24_MOTION_PLAN_RU.txt',
 new Blob([v24Plan()],{type:'text/plain;charset=utf-8'}));
for(const name of ['stride','weight','anticipation','recoil','followThrough']){
 $('v24-'+name).oninput=e=>{$('v24-'+name+'-n').textContent=e.target.value;};
}
