/* AI Anime Factory V29 — ANIMATION & COMBAT POLISH.
   Synchronize V24 stance and V25 limbs to one authoritative fight beat.
   No fake hits, no edits to imported artwork, deterministic scene time.
*/
function v29Options(s){
 if(!s.polishV29||typeof s.polishV29!=='object'||Array.isArray(s.polishV29))s.polishV29={};
 const o=s.polishV29;
 for(const [k,d] of [['timing',78],['stance',75],['follow',64],['impact',68],['smoothness',80]]){
  o[k]=Number.isFinite(Number(o[k]))?clamp(Number(o[k]),0,100):d;
 }
 if(!['natural','action','subtle'].includes(o.style))o.style='natural';
 o.enabled=o.enabled!==false;
 return o;
}
function v29Ease(x){const t=clamp(x,0,1);return t*t*(3-2*t);}
function v29Beat(s,t){
 const none={active:false,actor:null,outcome:'idle',anticipation:0,release:0,
  contact:0,guard:0,dodge:0,recovery:0,commit:0};
 if(s.kind!=='fight')return none;
 const c=v25Contact(s,t);
 if(!c.active)return none;
 const anticipation=clamp(c.anticipation,0,1);
 const release=clamp(c.release,0,1);
 // Hit pulses remain strictly tied to V19/V17 event classification.
 const contact=['hit','block'].includes(c.outcome)?clamp(c.contact,0,1):0;
 const guard=c.outcome==='block'?clamp(c.defense,0,1):0;
 const dodge=c.outcome==='dodge'?clamp(c.defense,0,1):0;
 const recovery=clamp((1-release)*(contact+guard)*.43,0,1);
 return {active:true,actor:c.actor,outcome:c.outcome,anticipation,release,
  contact,guard,dodge,recovery,commit:Math.max(release,contact,guard,dodge)};
}
function v29Actor(s,t,role){
 const o=v29Options(s);
 const zero={lean:0,rootX:0,rootY:0,handX:0,handY:0,
  guardY:0,headX:0,footLock:0,follow:0};
 if(!o.enabled||s.kind!=='fight')return zero;
 const b=v29Beat(s,t);
 if(!b.active)return zero;
 const active=b.actor===role;
 const reactive=b.actor&&b.actor!==role;
 const intensity=(o.style==='action'?1.25:o.style==='subtle'?.48:1);
 const timing=o.timing/100,stance=o.stance/100,
       follow=o.follow/100,impact=o.impact/100;
 const anticipation=active?b.anticipation*timing:0;
 const release=active?b.release*timing:0;
 const guard=reactive?b.guard*stance:0;
 const dodge=reactive?b.dodge*stance:0;
 const recoil=reactive&&b.outcome==='hit'?b.contact*impact:0;
 const settle=b.recovery*follow;
 const footLock=clamp(Math.max(anticipation*.82,release*.9,
                              guard*.8,dodge*.6,recoil*.94),0,1)*stance;
 // A grounded wind-up, forward strike, aftershock and recover are driven by
 // the exact SAME scene beat, not independently timed sine pulses.
 return {
  lean:clamp((-anticipation*.11+release*.16-recoil*.17+
               guard*.095-dodge*.15+settle*.03)*intensity,-.22,.22),
  rootX:(release*3.4-anticipation*1.5-recoil*2.5-dodge*3.2)*intensity,
  rootY:(-release*1.6+recoil*2.3+settle*.6)*intensity,
  handX:(release*15-anticipation*4-guard*4)*intensity,
  handY:(release*13+anticipation*7+guard*18)*intensity,
  guardY:guard*23*intensity,
  headX:(recoil*2.7-anticipation*1.5-dodge*3.3)*intensity,
  footLock,follow:clamp(settle*.75+recoil*.4,0,1)*intensity
 };
}
function v29FootPose(s,t,role,side,point){
 const o=v29Options(s),m=v29Actor(s,t,role);
 if(!o.enabled||s.kind!=='fight')return point;
 const lock=v29Ease(m.footLock)*(o.smoothness/100);
 // Lock the vertical displacement during impact to eliminate "floating".
 // Preserve some horizontal stance width so weight looks planted.
 return [point[0]*(1-lock*.18),point[1]+
   Math.max(0,4-point[1])*lock*.75];
}
function v29GroundPulse(s,t,role){
 const old=v28Footfall(s,t,role);
 const o=v29Options(s);
 if(!o.enabled||s.kind!=='fight')return old;
 const b=v29Beat(s,t);
 if(!b.active)return old;
 const a=v29Actor(s,t,role);
 // Reduce random-looking dust when both feet are planted for a strike/guard.
 // A little contact kick is permitted only for existing hit/block outcomes.
 const planted=old*(1-v29Ease(a.footLock)*.88);
 const impact=b.actor!==role&&['hit','block'].includes(b.outcome)?
   b.contact*.35*(o.impact/100):0;
 return clamp(planted+impact,0,1);
}
function v29Timeline(s,t){
 const b=v29Beat(s,t);
 if(!b.active)return 'Пауза / движение';
 const role=b.actor==='hero'?'Герой':'Соперник';
 const phase=b.contact>.25?(b.outcome==='block'?'Блок':'Контакт'):
             b.dodge>.25?'Уклонение':
             b.release>.2?'Удар':b.anticipation>.2?'Подготовка':'Восстановление';
 return role+' · '+phase+' · результат '+b.outcome;
}
function v29QA(){
 if(!P)return [];
 const errors=[];
 for(const ep of P.episodes)for(const s of ep.scenes){
  if(s.kind!=='fight')continue;
  const o=v29Options(s);if(!o.enabled)continue;
  if(o.stance<15&&o.impact>90)
   errors.push('Серия '+ep.number+', '+s.title+': слабая опора ног при очень резкой реакции.');
  if(o.timing<15&&o.follow>90)
   errors.push('Серия '+ep.number+', '+s.title+': затухание сильнее основного движения.');
 }
 return errors;
}
function v29Plan(){
 if(!P)return '';
 const text=['AI ANIME FACTORY V29 — ТАЙМИНГ АНИМАЦИИ И БОЯ',P.title,''];
 for(const ep of P.episodes)for(const s of ep.scenes){
  if(s.kind!=='fight')continue;
  const o=v29Options(s);
  text.push('Серия '+ep.number+' — '+s.title,'Профиль '+o.style+
   '; тайминг '+o.timing+'; опора '+o.stance+
   '; затухание '+o.follow+'; контакт '+o.impact+
   '; плавность '+o.smoothness+'; включено '+o.enabled);
  for(const p of [.2,.35,.5,.65,.8])
   text.push(Math.round(p*100)+'% — '+v29Timeline(s,s.duration*p));
  text.push('');
 }
 text.push('Отсутствующие попадания не создаются. Правила боя V19/V17 остаются неизменными.');
 return text.join('\n');
}
function v29FightScenes(){
 const all=[];
 P.episodes.forEach((ep,i)=>ep.scenes.forEach((s,j)=>{
  if(s.kind==='fight')all.push({i,j,title:s.title,number:ep.number});
 }));
 return all;
}
function v29Scene(){
 const choice=$('v29-scene').value;
 if(!choice)return null;
 const [i,j]=choice.split(':').map(Number);
 return P?.episodes[i]?.scenes[j]||null;
}
function v29Show(){
 if(!P)return;
 const all=v29FightScenes(),sel=$('v29-scene'),old=sel.value;
 sel.innerHTML=all.map(r=>'<option value="'+r.i+':'+r.j+'">Серия '+
  r.number+' — '+escapeHTML(r.title)+'</option>').join('');
 if(!all.length){
  $('v29-caption').textContent='В проекте пока нет боевой сцены.';
  $('v29-qa').textContent='Нечего проверять.';
  for(const id of ['v29-before','v29-after'])
   $(id).getContext('2d').clearRect(0,0,640,360);
  return;
 }
 const active=epIndex+':'+scIndex;
 sel.value=all.some(v=>v.i+':'+v.j===active)?active:
   all.some(v=>v.i+':'+v.j===old)?old:all[0].i+':'+all[0].j;
 const s=v29Scene(),o=v29Options(s);
 $('v29-enabled').checked=o.enabled;$('v29-style').value=o.style;
 for(const key of ['timing','stance','follow','impact','smoothness']){
  $('v29-'+key).value=o[key];$('v29-'+key+'-n').textContent=String(o[key]);
 }
 $('v29-qa').textContent=v29QA().slice(0,35).join('\n')||
   'Основные параметры постановки боя согласованы.';
 v29Preview();
}
function v29Preview(){
 const s=v29Scene();if(!s)return;
 const t=s.duration*(Number($('v29-position').value)||0)/100;
 const o=v29Options(s),enabled=o.enabled;
 try{
  o.enabled=false;drawScene($('v29-before'),s,t,false);
  o.enabled=enabled;drawScene($('v29-after'),s,t,false);
 }finally{o.enabled=enabled;}
 $('v29-caption').textContent=s.title+' · '+t.toFixed(2)+' с · '+v29Timeline(s,t);
}
function v29Save(){
 const s=v29Scene();if(!s)return;
 const o=v29Options(s);
 o.enabled=$('v29-enabled').checked;o.style=$('v29-style').value;
 for(const key of ['timing','stance','follow','impact','smoothness'])
  o[key]=clamp(Number($('v29-'+key).value)||0,0,100);
 save();v29Show();notify('V29: движение и бой синхронизированы для сцены.');
}
function v29Preset(){
 const s=v29Scene();if(!s)return;
 Object.assign(v29Options(s),{enabled:true,style:'action',
  timing:83,stance:88,follow:69,impact:78,smoothness:85});
 save();v29Show();notify('V29: профиль чёткого боевого ритма установлен.');
}
async function v29Sheet(){
 await preloadArtwork();
 const s=v29Scene();if(!s)return;
 const out=document.createElement('canvas'),one=document.createElement('canvas');
 out.width=1280;out.height=720;one.width=640;one.height=360;
 const g=out.getContext('2d');
 for(const [i,pct] of [.18,.36,.60,.82].entries()){
  drawScene(one,s,s.duration*pct,false);
  const x=(i%2)*640,y=Math.floor(i/2)*360;g.drawImage(one,x,y);
  g.fillStyle='rgba(4,11,25,.85)';g.fillRect(x+9,y+9,320,28);
  g.font='bold 13px Arial';g.fillStyle='#f1dfc9';
  g.fillText('V29 '+Math.round(pct*100)+'% '+v29Timeline(s,s.duration*pct),x+16,y+28,300);
 }
 download('V29_MOTION_BEATS_'+slug(s.title)+'.png',await blobPNG(out));
 notify('V29: 4 кадра боевого тайминга сохранены.');
}
$('v29-scene').onchange=e=>{
 const [i,j]=e.target.value.split(':').map(Number);
 selectScene(i,j);show('polish-v29');
};
$('v29-position').oninput=v29Preview;
$('v29-save').onclick=v29Save;$('v29-preset').onclick=v29Preset;
$('v29-sheet').onclick=async()=>{try{await v29Sheet();}catch(e){notify('V29 PNG: '+e.message);}};
$('v29-plan').onclick=()=>download('V29_COMBAT_TIMING_RU.txt',
 new Blob([v29Plan()],{type:'text/plain;charset=utf-8'}));
for(const key of ['timing','stance','follow','impact','smoothness'])
 $('v29-'+key).oninput=e=>{$('v29-'+key+'-n').textContent=e.target.value;};
