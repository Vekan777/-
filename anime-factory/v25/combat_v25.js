/* AI Anime Factory V25 Combat Choreography.
   Coordinate both actors in the same 2D fight without rewriting V19–V24.
   Contact status only comes from existing V19/V17 fight events; never synthesize hits.
*/
function v25Options(s){
 if(!s.choreographyV25||typeof s.choreographyV25!=='object'||Array.isArray(s.choreographyV25))s.choreographyV25={};
 const o=s.choreographyV25;
 for(const [key,def] of [['distance',65],['footwork',75],['guard',72],['response',70],['rhythm',62]]){
  o[key]=Number.isFinite(Number(o[key]))?clamp(Number(o[key]),0,100):def;
 }
 if(!['balanced','duel','defensive'].includes(o.style))o.style='balanced';
 o.enabled=o.enabled!==false;
 return o;
}
function v25Contact(s,t,existingCombat=null,existingImpact=null){
 const empty={active:false,actor:null,outcome:'idle',anticipation:0,release:0,contact:0,defense:0};
 if(s.kind!=='fight')return empty;
 const impact=existingImpact||impact19State(s,t);
 if(impact&&impact.event){
  const outcome=String(impact.event.outcome||'miss');
  const release=clamp(Number(impact.release)||0,0,1);
  const anticipation=clamp(Number(impact.anticipation)||0,0,1);
  const contact=(outcome==='hit'||outcome==='block')?
    clamp(Number(impact.nearHit)||0,0,1):0;
  const defense=(outcome==='dodge'||outcome==='block')?
    clamp(Number(impact.nearHit)||0,0,1):0;
  return {active:true,actor:impact.event.actor==='partner'?'partner':'hero',
    outcome,anticipation,release,contact,defense};
 }
 const combat=existingCombat||combat17State(s,t);
 if(!combat||!combat.attack)return empty;
 const outcome=['hit','block','miss','dodge'].includes(combat.result)?combat.result:'miss';
 const intensity=clamp(Number(combat.strength)||0,0,1);
 return {active:true,actor:combat.attack.actor==='partner'?'partner':'hero',
   outcome,anticipation:0,release:intensity,contact:
     (outcome==='hit'||outcome==='block')?intensity:0,
   defense:(outcome==='dodge'||outcome==='block')?intensity:0};
}
function v25Actor(s,t,role){
 const zero={lean:0,attack:0,guard:0,step:0,recoil:0};
 const o=v25Options(s);
 if(!o.enabled||s.kind!=='fight')return zero;
 const e=v25Contact(s,t),defender=e.actor&&e.actor!==role;
 const attacker=e.actor===role;
 const rhythm=o.rhythm/100,weight=o.footwork/100,defense=o.guard/100;
 const resistance=o.response/100,style=o.style==='defensive'?1.25:o.style==='duel'?1.12:1;
 const attack=attacker?e.release*.65+e.anticipation*.15:0;
 const guard=defender?e.defense*defense*style:0;
 // Recoil only on confirmed hit to defender; no visually fake hit on a miss.
 const recoil=defender&&e.outcome==='hit'?e.contact*resistance:0;
 const evade=defender&&e.outcome==='dodge'?e.defense*resistance:0;
 const rolePhase=role==='hero'?0:1.25;
 const step=Math.sin(t*3.0+rolePhase)*rhythm*weight*2.0;
 return {attack,guard,recoil,step:step-evade*4.5-recoil*1.8,
  lean:attack*.07-guard*.07-recoil*.14-evade*.09+
       Math.sin(t*2.2+rolePhase)*rhythm*.01};
}
function v25PairPose(s,t,poses,combat=null,impact=null){
 const o=v25Options(s);
 if(!o.enabled||s.kind!=='fight')return;
 const h=poses.hero,p=poses.partner;
 if(!h||!p)return;
 const e=v25Contact(s,t,combat,impact);
 const forward=Math.sign(p.x-h.x)||1;
 const center=(h.x+p.x)*.5;
 const existing=Math.abs(p.x-h.x);
 // World-space separation is never lowered below the stated cinematic
 // threshold, and historical combat outcomes remain authoritative.
 const desired=clamp(.30-o.distance/100*.115,.17,.30);
 const force=o.footwork/100*(o.style==='defensive'?.45:.76);
 const release=e.active?e.release:0;
 const pre=e.active?e.anticipation:0;
 const lunge=e.actor?release*o.rhythm/100*.028:0;
 const target=clamp(desired-lunge+pre*.012,.145,.40);
 const spacing=existing*(1-force*.65)+target*(force*.65);
 const hN=clamp(center-forward*spacing*.5,.065,.935);
 const pN=clamp(center+forward*spacing*.5,.065,.935);
 h.x=hN;p.x=pN;
 // Defensive movement uses an existing classified event, not a new
 // unverified hit/block label.
 if(e.actor){
  const attacker=poses[e.actor];
  const defender=poses[e.actor==='hero'?'partner':'hero'];
  const dir=(defender.x>=attacker.x?1:-1);
  const surge=release*.012*force;
  attacker.x=clamp(attacker.x+dir*surge,.055,.945);
  if(e.outcome==='dodge'){
   defender.x=clamp(defender.x+dir*e.defense*.026*o.response/100,.055,.945);
  }else if(e.outcome==='hit'&&e.contact>0){
   defender.x=clamp(defender.x+dir*e.contact*.014*o.response/100,.055,.945);
   defender.y-=e.contact*.004*o.response/100;
  }
 }
}
function v25ContactText(s,t){
 const c=v25Contact(s,t);
 const ru={idle:'Пауза',hit:'Попадание',block:'Блок',dodge:'Уклонение',miss:'Промах'};
 const who={hero:'герой',partner:'соперник'};
 return (c.active?'Атакует '+(who[c.actor]||'боец')+': ':'')+
   (ru[c.outcome]||c.outcome)+' · сила '+Math.round(c.release*100)+'%';
}
function v25QA(){
 if(!P)return [];
 const errors=[];
 for(const episode of P.episodes)for(const s of episode.scenes){
  if(s.kind!=='fight')continue;
  const o=v25Options(s);
  if(!o.enabled)continue;
  if(o.distance<15&&o.footwork>95)
   errors.push('Серия '+episode.number+': '+s.title+' — высокая подвижность при широкой дистанции.');
  if(o.guard<10)
   errors.push('Серия '+episode.number+': '+s.title+' — защитная стойка почти не видна.');
  if(o.response<10)
   errors.push('Серия '+episode.number+': '+s.title+' — слабая отдача после попадания.');
 }
 return errors;
}
function v25Plan(){
 if(!P)return '';
 const lines=['AI ANIME FACTORY V25 — ПОСТАНОВКА БОЯ',P.title,''];
 for(const ep of P.episodes){
  for(const s of ep.scenes){
   if(s.kind!=='fight')continue;
   const o=v25Options(s);
   lines.push('Серия '+ep.number+' — '+s.title,'Стиль '+o.style+
    '; дистанция '+o.distance+'; шаг '+o.footwork+
    '; защита '+o.guard+'; реакция '+o.response+
    '; ритм '+o.rhythm+'; включено '+o.enabled);
   for(const point of [.15,.30,.48,.65,.82]){
    lines.push(Math.round(point*100)+'% '+v25ContactText(s,s.duration*point));
   }
   lines.push('');
  }
 }
 lines.push('Только существующие события решают: hit/block/dodge/miss.');
 return lines.join('\n');
}
function v25Show(){
 if(!P)return;
 const sel=$('v25-scene'),all=[];
 P.episodes.forEach((ep,i)=>ep.scenes.forEach((s,j)=>{
  if(s.kind==='fight')all.push([i,j,s.title,ep.number]);
 }));
 sel.innerHTML=all.map(v=>'<option value="'+v[0]+':'+v[1]+'">'+
  'Серия '+v[3]+' — '+escapeHTML(v[2])+'</option>').join('');
 if(!all.length){
  $('v25-status').textContent='В проекте нет боевых сцен. Добавьте сцену боя во вкладке сценария.';
  $('v25-before').getContext('2d').clearRect(0,0,640,360);
  $('v25-after').getContext('2d').clearRect(0,0,640,360);
  $('v25-qa').textContent='Нет боевых сцен.';
  return;
 }
 const key=epIndex+':'+scIndex;
 if(all.some(([i,j])=>i+':'+j===key))sel.value=key;
 else sel.value=all[0][0]+':'+all[0][1];
 const [i,j]=sel.value.split(':').map(Number),s=P.episodes[i].scenes[j],o=v25Options(s);
 $('v25-enabled').checked=o.enabled;$('v25-style').value=o.style;
 for(const name of ['distance','footwork','guard','response','rhythm']){
  $('v25-'+name).value=o[name];
  $('v25-'+name+'-n').textContent=String(o[name]);
 }
 $('v25-qa').textContent=v25QA().slice(0,30).join('\n')||
  'Параметры боевой хореографии: замечаний нет.';
 v25Preview();
}
function v25Scene(){
 const [i,j]=$('v25-scene').value.split(':').map(Number);
 return P?.episodes[i]?.scenes[j]||scene();
}
function v25Preview(){
 if(!P||!$('v25-scene').value)return;
 const s=v25Scene(),opts=v25Options(s);
 const t=s.duration*(Number($('v25-position').value)||0)/100;
 const was=opts.enabled;
 try{
  opts.enabled=false;drawScene($('v25-before'),s,t,false);
  opts.enabled=was;drawScene($('v25-after'),s,t,false);
 }finally{opts.enabled=was;}
 $('v25-status').textContent=s.title+' | '+t.toFixed(2)+' с | '+v25ContactText(s,t);
}
function v25Save(){
 const o=v25Options(v25Scene());
 o.enabled=$('v25-enabled').checked;o.style=$('v25-style').value;
 for(const key of ['distance','footwork','guard','response','rhythm'])
  o[key]=clamp(Number($('v25-'+key).value)||0,0,100);
 save();v25Show();notify('V25: боевая хореография сохранена для сцены.');
}
function v25Preset(){
 const o=v25Options(v25Scene());
 Object.assign(o,{enabled:true,style:'duel',distance:76,footwork:82,
  guard:79,response:74,rhythm:72});
 save();v25Show();notify('V25: дуэльный профиль применён.');
}
async function v25Sheet(){
 await preloadArtwork();
 const s=v25Scene(),out=document.createElement('canvas'),frame=document.createElement('canvas');
 out.width=1280;out.height=720;frame.width=640;frame.height=360;
 const g=out.getContext('2d');
 for(const [i,pct] of [.15,.36,.62,.84].entries()){
  drawScene(frame,s,s.duration*pct,false);
  const x=(i%2)*640,y=Math.floor(i/2)*360;g.drawImage(frame,x,y);
  g.fillStyle='rgba(4,10,24,.76)';g.fillRect(x+10,y+9,205,27);
  g.fillStyle='#f1e4cf';g.font='bold 14px Arial';
  g.fillText('V25 '+Math.round(pct*100)+'% '+v25Contact(s,s.duration*pct).outcome,x+17,y+27);
 }
 download('V25_FIGHT_'+slug(s.title)+'.png',await blobPNG(out));
 notify('V25: 4 проверочных кадра боя сохранены.');
}
$('v25-scene').onchange=e=>{const [i,j]=e.target.value.split(':').map(Number);selectScene(i,j);show('combat-v25');};
$('v25-position').oninput=v25Preview;
$('v25-style').onchange=()=>{$('v25-status').textContent='Нажмите «Сохранить» для применения профиля.';};
$('v25-enabled').onchange=()=>{$('v25-status').textContent='Нажмите «Сохранить» для применения изменений.';};
$('v25-save').onclick=v25Save;
$('v25-preset').onclick=v25Preset;
$('v25-sheet').onclick=async()=>{try{await v25Sheet();}catch(e){notify('V25 PNG: '+e.message);}};
$('v25-plan').onclick=()=>download('V25_COMBAT_PLAN_RU.txt',new Blob([v25Plan()],{type:'text/plain;charset=utf-8'}));
for(const key of ['distance','footwork','guard','response','rhythm']){
 $('v25-'+key).oninput=e=>{$('v25-'+key+'-n').textContent=e.target.value;};
}
