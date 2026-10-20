/* AI Anime Factory V28 — Character / Environment interactions.
   Deterministic 2D Canvas staging; no texture/asset mutation, no random source,
   and only existing combat events authorize an impact environment effect.
*/
function v28Options(s){
 if(!s.interactionV28||typeof s.interactionV28!=='object'||Array.isArray(s.interactionV28))s.interactionV28={};
 const o=s.interactionV28;
 for(const [key,defaultValue] of [['footsteps',72],['dust',68],['bounce',73],['scars',61],['impactFX',68]]){
  o[key]=Number.isFinite(Number(o[key]))?clamp(Number(o[key]),0,100):defaultValue;
 }
 if(!['auto','subtle','dramatic'].includes(o.style))o.style='auto';
 o.enabled=o.enabled!==false;
 return o;
}
function v28Phase(s,t,role){
 const base=t*(s.kind==='fight'?2.65:1.65)+(role==='partner'?Math.PI*.62:0);
 return base;
}
function v28Footfall(s,t,role){
 const phi=v28Phase(s,t,role),freq=s.kind==='fight'?2.65:1.65;
 const pulse=Math.max(0,Math.cos(phi*2));
 return Math.pow(pulse,14);
}
function v28Boost(s){
 const o=v28Options(s);return o.style==='dramatic'?1.35:o.style==='subtle'?.55:1;
}
function v28Background(g,w,h,s,t){
 const o=v28Options(s);if(!o.enabled)return;
 // Soft world-space bounce illumination is emitted behind the characters.
 const pal=v27Palette(s),boost=v28Boost(s),strength=o.bounce/100*boost;
 if(strength<=0)return;
 g.save();g.globalAlpha=Math.min(.22,strength*.18);
 g.fillStyle=pal.accent;
 for(const side of [-1,1]){
  const centerX=(side<0?.29:.71)*w+Math.sin(t*.42+side)*w*.014;
  const y=h*.72;
  const grad=g.createRadialGradient(centerX,y,0,centerX,y,w*.24);
  grad.addColorStop(0,pal.rim);grad.addColorStop(1,'rgba(0,0,0,0)');
  g.fillStyle=grad;g.fillRect(centerX-w*.24,y-w*.24,w*.48,w*.48);
 }
 g.restore();
}
function v28Ground(g,w,h,s,t,poses){
 const o=v28Options(s);
 if(!o.enabled||!poses)return;
 const pal=v27Palette(s),boost=v28Boost(s),amount=o.footsteps/100*boost;
 const dust=o.dust/100*boost;
 g.save();
 for(const role of ['hero','partner']){
  const p=poses[role];if(!p)continue;
  const scale=clamp(Number(p.scale)||1,.35,2);
  const x=p.x*w,y=p.y*h+3;
  const foot=v28Footfall(s,t,role);
  const motion=v24Dynamics(s,t,role);
  const footOffset=motion.step*w*.009;
  // Foot-contact effects are grounded at the actor's current scene-space pose.
  g.globalAlpha=clamp(amount*(.18+foot*.26),0,.56);
  g.fillStyle=pal.earth;
  const side=Math.sin(v28Phase(s,t,role))>=0?1:-1;
  const stepX=x+side*w*.021*scale+footOffset;
  g.beginPath();g.ellipse(stepX,y,w*.019*scale,h*.007*scale,0,0,Math.PI*2);g.fill();
  // Fine particulate clouds rise on the actual footfall pulse and fade.
  const radius=w*(.011+foot*.025)*scale;
  g.globalAlpha=clamp(dust*foot*.27,0,.38);
  const gradient=g.createRadialGradient(stepX,y-radius*.5,0,stepX,y-radius*.5,radius*2.5);
  gradient.addColorStop(0,pal.accent);gradient.addColorStop(1,'rgba(0,0,0,0)');
  g.fillStyle=gradient;g.fillRect(stepX-radius*2.5,y-radius*3,radius*5,radius*5);
  g.globalAlpha=clamp(dust*foot*.38,0,.45);
  g.strokeStyle=pal.distant;g.lineWidth=Math.max(1,w*.0016);
  for(let i=0;i<4;i++){
   const angle=(i*1.9+t*.21);
   const dx=Math.sin(angle)*radius*(.5+foot*.7);
   const dy=Math.abs(Math.cos(angle))*radius*.9;
   g.beginPath();g.moveTo(stepX+dx*.5,y-dy*.15);
   g.lineTo(stepX+dx,y-dy);g.stroke();
  }
 }
 g.restore();
}
function v28ImpactAt(s,t){
 if(s.kind!=='fight')return null;
 const v=v25Contact(s,t);
 if(!v.active||!['hit','block'].includes(v.outcome))return null;
 const strength=clamp(v.contact,0,1);
 if(strength<=.001)return null;
 return {kind:v.outcome,strength,actor:v.actor};
}
function v28CombatGround(g,w,h,s,t,poses){
 const o=v28Options(s);if(!o.enabled)return;
 const effect=v28ImpactAt(s,t),palette=v27Palette(s);
 if(!effect||!poses?.hero||!poses?.partner)return;
 const focus=effect.actor==='hero'?poses.partner:poses.hero;
 const x=focus.x*w,y=focus.y*h+2;
 const strength=effect.strength*(o.scars/100)*v28Boost(s);
 // A temporary scuff/ripple appears only for a confirmed hit or block.
 // Never fake a hit for misses or dodges. Scene remains non-destructive.
 g.save();g.globalAlpha=clamp(strength*.57,0,.7);
 g.strokeStyle=effect.kind==='block'?palette.rim:palette.accent;
 g.lineWidth=Math.max(1,w*.002);
 for(let ring=0;ring<3;ring++){
  const radius=w*(.025+ring*.029+effect.strength*.02);
  g.beginPath();g.ellipse(x,y,radius,h*(.008+ring*.003),0,0,Math.PI*2);g.stroke();
 }
 if(effect.kind==='hit'){
  g.strokeStyle=palette.distant;g.globalAlpha=clamp(strength*.35,0,.45);
  for(let i=0;i<5;i++){
   const angle=i*Math.PI*2/5+t*.12;
   g.beginPath();g.moveTo(x+Math.cos(angle)*w*.016,y);
   g.lineTo(x+Math.cos(angle)*w*.06,y+Math.sin(angle)*h*.017);g.stroke();
  }
 }
 g.restore();
}
function v28ActorLight(g,w,h,s,t,poses){
 const o=v28Options(s);if(!o.enabled||!poses)return;
 const pal=v27Palette(s),boost=v28Boost(s),level=o.bounce/100*boost;
 g.save();
 for(const role of ['hero','partner']){
  const p=poses[role];if(!p)continue;
  const size=w*.17*clamp(Number(p.scale)||1,.5,1.7);
  const cx=p.x*w,cy=p.y*h-w*.15;
  g.globalAlpha=clamp(level*.08,0,.12);
  const light=g.createRadialGradient(cx,cy,0,cx,cy,size);
  light.addColorStop(0,pal.accent);light.addColorStop(1,'rgba(0,0,0,0)');
  g.fillStyle=light;g.fillRect(cx-size,cy-size,size*2,size*2);
 }
 const hit=v28ImpactAt(s,t);
 if(hit&&o.impactFX>0){
  const defender=hit.actor==='hero'?poses.partner:poses.hero;
  if(defender){
   const power=clamp(hit.strength*o.impactFX/100*boost,0,1);
   const x=defender.x*w,y=defender.y*h-w*.15;
   g.globalAlpha=power*.18;
   const flash=g.createRadialGradient(x,y,0,x,y,w*.12);
   flash.addColorStop(0,hit.kind==='block'?pal.rim:pal.accent);
   flash.addColorStop(1,'rgba(0,0,0,0)');
   g.fillStyle=flash;g.fillRect(x-w*.12,y-w*.12,w*.24,w*.24);
  }
 }
 g.restore();
}
function v28QA(){
 if(!P)return [];
 const issues=[];
 for(const ep of P.episodes)for(const s of ep.scenes){
  const o=v28Options(s);if(!o.enabled)continue;
  if(o.dust>92&&o.bounce>92)issues.push('Серия '+ep.number+', '+s.title+': сильная пыль и свет могут ухудшить видимость персонажей.');
  if(o.impactFX>90&&s.kind!=='fight')issues.push('Серия '+ep.number+', '+s.title+': настройка боевого эффекта неактивна вне боя.');
 }
 return issues;
}
function v28Plan(){
 if(!P)return '';
 const lines=['AI ANIME FACTORY V28 — ВЗАИМОДЕЙСТВИЕ С МИРОМ',P.title,''];
 for(const ep of P.episodes)for(const s of ep.scenes){
  const o=v28Options(s);
  lines.push('Серия '+ep.number+' · '+s.title+' ('+s.kind+')',
    'Стиль '+o.style+'; следы '+o.footsteps+'; пыль '+o.dust+
    '; свет '+o.bounce+'; земля после удара '+o.scars+
    '; боевая вспышка '+o.impactFX+'; включено '+o.enabled);
 }
 lines.push('Попадание/блок определяется только из существующих событий V19/V17.');
 return lines.join('\n');
}
function v28Show(){
 if(!P)return;
 const s=scene(),sel=$('v28-scene');
 sel.innerHTML=qualitySceneList();sel.value=epIndex+':'+scIndex;
 const o=v28Options(s);
 $('v28-enabled').checked=o.enabled;$('v28-style').value=o.style;
 for(const k of ['footsteps','dust','bounce','scars','impactFX']){
  $('v28-'+k).value=o[k];$('v28-'+k+'-n').textContent=String(o[k]);
 }
 $('v28-qa').textContent=v28QA().slice(0,30).join('\n')||
  'Контроль взаимодействия: критических конфликтов параметров нет.';
 v28Preview();
}
function v28Preview(){
 if(!P)return;
 const s=scene(),o=v28Options(s);
 const t=s.duration*(Number($('v28-position').value)||0)/100;
 const was=o.enabled;
 try{
  o.enabled=false;drawScene($('v28-before'),s,t,false);
  o.enabled=was;drawScene($('v28-after'),s,t,false);
 }finally{o.enabled=was;}
 const impact=v28ImpactAt(s,t);
 $('v28-caption').textContent=s.title+' · '+t.toFixed(2)+' с · '+(impact?
    (impact.kind==='hit'?'Попадание': 'Блок'):'Свет и контакт с землёй');
}
function v28Save(){
 const o=v28Options(scene());
 o.enabled=$('v28-enabled').checked;o.style=$('v28-style').value;
 for(const k of ['footsteps','dust','bounce','scars','impactFX'])
  o[k]=clamp(Number($('v28-'+k).value)||0,0,100);
 save();v28Show();notify('V28: взаимодействие персонажей с миром сохранено.');
}
function v28Preset(){
 const o=v28Options(scene());
 Object.assign(o,{enabled:true,style:'dramatic',footsteps:87,dust:81,
  bounce:82,scars:79,impactFX:84});
 save();v28Show();notify('V28: усиленная контактная постановка применена.');
}
async function v28Sheet(){
 await preloadArtwork();
 const s=scene(),board=document.createElement('canvas'),frame=document.createElement('canvas');
 board.width=1280;board.height=720;frame.width=640;frame.height=360;
 const g=board.getContext('2d');
 for(const [i,percent] of [.17,.37,.62,.86].entries()){
  drawScene(frame,s,s.duration*percent,false);
  const x=i%2*640,y=Math.floor(i/2)*360;g.drawImage(frame,x,y);
  g.fillStyle='rgba(4,10,22,.83)';g.fillRect(x+9,y+9,229,29);
  g.fillStyle='#f2dfca';g.font='bold 14px Arial';
  g.fillText('V28 МИР '+Math.round(percent*100)+'%',x+16,y+28);
 }
 download('V28_INTERACTION_'+slug(s.title)+'.png',await blobPNG(board));
 notify('V28: кадры взаимодействия PNG сохранены.');
}
$('v28-scene').onchange=e=>{
 const [i,j]=e.target.value.split(':').map(Number);
 selectScene(i,j);show('interaction-v28');
};
$('v28-position').oninput=v28Preview;
$('v28-save').onclick=v28Save;$('v28-preset').onclick=v28Preset;
$('v28-sheet').onclick=async()=>{try{await v28Sheet();}catch(e){notify('V28 PNG: '+e.message);}};
$('v28-plan').onclick=()=>download('V28_INTERACTION_PLAN_RU.txt',
 new Blob([v28Plan()],{type:'text/plain;charset=utf-8'}));
for(const k of ['footsteps','dust','bounce','scars','impactFX'])
 $('v28-'+k).oninput=e=>{$('v28-'+k+'-n').textContent=e.target.value;};
