/* AI Anime Factory V22 - Acting and Combat Direction.
   All effects are deterministic, per-scene and included in PNG/ZIP renders.
   Custom image layers are NOT overwritten or obscured by generated facial art.
*/
const V22_EMOTIONS=['neutral','gentle','determined','angry','sad','shocked'];
function v22Settings(s){
 if(!s.actingV22||typeof s.actingV22!=='object')s.actingV22={};
 const a=s.actingV22;
 if(!Array.isArray(a.beats))a.beats=[];
 a.beats=a.beats.filter(b=>b&&typeof b==='object').slice(0,24);
 for(const b of a.beats){
  b.t=clamp(Number(b.t)||0,0,1);
  b.hero=V22_EMOTIONS.includes(b.hero)?b.hero:'neutral';
  b.partner=V22_EMOTIONS.includes(b.partner)?b.partner:'neutral';
 }
 a.beats.sort((x,y)=>x.t-y.t);
 if(!Number.isFinite(Number(a.faceStrength)))a.faceStrength=70;
 if(!Number.isFinite(Number(a.combatFocus)))a.combatFocus=72;
 if(!Number.isFinite(Number(a.breathing)))a.breathing=56;
 for(const name of ['faceStrength','combatFocus','breathing'])
  a[name]=clamp(Number(a[name]),0,100);
 if(a.enabled!==false)a.enabled=true;
 return a;
}
function v22Mood(s,role,t,fallback){
 const a=v22Settings(s);
 if(!a.enabled||!a.beats.length)return fallback;
 const f=clamp(t/Math.max(.1,s.duration),0,1);
 let chosen=null;
 for(const b of a.beats)if(b.t<=f+.0001)chosen=b;else break;
 if(!chosen)return fallback;
 return chosen[role==='partner'?'partner':'hero']||fallback;
}
function v22BodyBreath(s,role,t){
 const a=v22Settings(s);if(!a.enabled)return 0;
 const phase=(role==='hero'?0:1.2)+t*1.7;
 return Math.sin(phase)*a.breathing/100*1.4;
}
function v22FaceDetails(g,c,s,role,t,design,f){
 const settings=v22Settings(s);if(!settings.enabled||settings.faceStrength<=0)return;
 const m=v22Mood(s,role,t,qualityMood(s,role)),intensity=settings.faceStrength/100;
 g.save();
 // Natural face planes and softly glowing eye highlights, keeping original bone structure.
 let sheen=g.createLinearGradient(-34,-249,30,-187);
 sheen.addColorStop(0,'rgba(255,247,230,.38)');
 sheen.addColorStop(.6,'rgba(255,234,217,.05)');
 sheen.addColorStop(1,'rgba(75,22,47,.13)');
 g.globalAlpha=intensity*.55;g.fillStyle=sheen;
 g.beginPath();g.moveTo(-33,-233);g.quadraticCurveTo(-11,-248,17,-230);
 g.quadraticCurveTo(25,-198,0,-182);g.quadraticCurveTo(-31,-196,-33,-233);g.fill();
 g.globalAlpha=intensity*.5;g.strokeStyle=c.hair||'#3b4a6d';
 g.lineWidth=1.35;
 for(const sign of [-1,1]){
  // Line-weight variation on lashes for readable close-up expressions.
  g.beginPath();g.moveTo(sign*8,-223);g.quadraticCurveTo(sign*18,-228,sign*28,-224);g.stroke();
  if(m==='shocked'){
   g.strokeStyle='#936b7e';g.beginPath();g.moveTo(sign*12,-241);
   g.lineTo(sign*23,-243);g.stroke();
  }
  if(m==='sad'){
   g.fillStyle='#9cd8ef';g.globalAlpha=intensity*.58;
   g.beginPath();g.ellipse(sign*24,-204,1.5,4.3,0,0,Math.PI*2);g.fill();
  }else if(m==='gentle'){
   g.fillStyle='#f1a2ab';g.globalAlpha=intensity*.17;
   g.beginPath();g.ellipse(sign*23,-202,9,4,0,0,Math.PI*2);g.fill();
  }else if(m==='angry'){
   g.strokeStyle='#8f6366';g.lineWidth=1.8;g.globalAlpha=intensity*.58;
   g.beginPath();g.moveTo(sign*8,-237);g.lineTo(sign*23,-231);g.stroke();
  }
 }
 g.restore();
}
function v22CombatClarity(g,w,h,s,t,st,poses){
 const a=v22Settings(s);if(!a.enabled||!st||s.kind!=='fight'||a.combatFocus<=0)return;
 if(!['hit','block'].includes(st.result)||!st.attack)return;
 const strength=clamp(st.strength,0,1)*a.combatFocus/100;
 if(strength<.04)return;
 const attack=poses[st.attack.actor],target=poses[st.attack.actor==='hero'?'partner':'hero'];
 if(!attack||!target)return;
 const cx=(attack.x+target.x)*w/2;
 const cy=(attack.y+target.y)*h/2-w*.13;
 g.save();g.globalCompositeOperation='screen';
 const color=st.result==='block'?'#85ddff':'#ffdfb3';
 // Distinctive clash shape: impact ring, rim glint and diminishing direction rays.
 g.strokeStyle=color;g.lineCap='round';g.lineWidth=Math.max(1,w*.0045);
 g.globalAlpha=strength*.68;
 g.beginPath();g.ellipse(cx,cy,w*.02,w*.013,0,0,Math.PI*2);g.stroke();
 for(let i=0;i<12;i++){
  const angle=i*Math.PI/6+(.07*Math.sin(t*3));
  const d=w*(.028+.015*Math.sin(i*2.1)**2);
  const length=d+w*(.055+.027*(i%3))*strength;
  g.globalAlpha=strength*(.18+.3*(i%4)/3);
  g.lineWidth=Math.max(.8,w*(.0015+.0006*(i%2)));
  g.beginPath();g.moveTo(cx+Math.cos(angle)*d,cy+Math.sin(angle)*d*.75);
  g.lineTo(cx+Math.cos(angle)*length,cy+Math.sin(angle)*length*.75);g.stroke();
 }
 g.restore();
}
function v22Plan(){
 if(!P)return '';
 let txt=['AI ANIME FACTORY V22 — АКТЁРСКАЯ И БОЕВАЯ ПОСТАНОВКА',P.title,''];
 for(const ep of P.episodes){
  txt.push('СЕРИЯ '+ep.number+' — '+ep.title);
  for(const s of ep.scenes){
   const a=v22Settings(s);txt.push('СЦЕНА '+s.title+' | '+s.kind,
    'Лицо '+a.faceStrength+' | бой '+a.combatFocus+' | дыхание '+a.breathing);
   for(const b of a.beats)txt.push(Math.round(b.t*100)+'%: герой '+b.hero+', партнёр '+b.partner);
  }
 }
 return txt.join('\n');
}
function v22Preset(s){
 const a=v22Settings(s),first={
 fight:['determined','angry'],romance:['gentle','gentle'],
 betrayal:['shocked','angry'],friendship:['gentle','gentle'],
 opening:['neutral','neutral'],ending:['determined','gentle']
 }[s.kind]||['neutral','neutral'];
 const second=s.kind==='fight'?['angry','shocked']:
   s.kind==='betrayal'?['sad','determined']:
   s.kind==='romance'?['gentle','gentle']:first;
 a.beats=[
  {t:0,hero:first[0],partner:first[1]},
  {t:.5,hero:second[0],partner:second[1]},
  {t:.85,hero:first[0],partner:first[1]}
 ];
 a.faceStrength=75;a.combatFocus=s.kind==='fight'?78:25;
 a.breathing=58;a.enabled=true;
 return a;
}
function v22ActingQA(){
 const issues=[];
 for(const ep of P.episodes)for(const s of ep.scenes){
  const a=v22Settings(s);
  for(let i=1;i<a.beats.length;i++)
   if(a.beats[i].t<=a.beats[i-1].t)
    issues.push('Серия '+ep.number+', '+s.title+': одинаковый момент эмоций '+i);
  if(s.kind==='betrayal'&&!a.beats.some(b=>b.hero==='shocked'||b.hero==='sad'))
    issues.push('Серия '+ep.number+', '+s.title+': реакция героя на предательство не показана.');
  if(s.kind==='fight'&&a.beats.length<2)
    issues.push('Серия '+ep.number+', '+s.title+': нет смены эмоций в бою.');
 }
 return issues;
}
function v22Show(){
 if(!P)return;
 const sel=$('v22-scene'),val=epIndex+':'+scIndex;
 sel.innerHTML=qualitySceneList();sel.value=val;
 const a=v22Settings(scene());
 $('v22-enabled').checked=a.enabled;
 for(const name of ['faceStrength','combatFocus','breathing']){
  $('v22-'+name).value=a[name];$('v22-'+name+'-n').textContent=a[name];
 }
 const chosen=Number($('v22-beat-list').value)||0;
 $('v22-beat-list').innerHTML=a.beats.map((b,i)=>
  '<option value="'+i+'">'+Math.round(b.t*100)+'% — '+b.hero+' / '+b.partner+'</option>').join('');
 const idx=Math.max(0,Math.min(chosen,a.beats.length-1)),b=a.beats[idx];
 if(b){
  $('v22-beat-list').value=String(idx);$('v22-t').value=Math.round(b.t*100);
  $('v22-hero').value=b.hero;$('v22-partner').value=b.partner;
 }else $('v22-beat-list').value='';
 $('v22-qa').textContent=v22ActingQA().slice(0,50).join('\n')||'Актёрский QA: существенных замечаний нет.';
 v22Preview();
}
function v22Preview(){
 if(!P)return;
 const s=scene(),pct=Number($('v22-playhead').value)||0,t=s.duration*pct/100;
 drawScene($('v22-preview'),s,t);
 $('v22-time').textContent=pct+'% | '+t.toFixed(2)+' с | '+v22Mood(s,'hero',t,qualityMood(s,'hero'));
}
function v22SaveOptions(){
 const a=v22Settings(scene());
 a.enabled=$('v22-enabled').checked;
 for(const name of ['faceStrength','combatFocus','breathing'])
  a[name]=clamp(Number($('v22-'+name).value)||0,0,100);
 save();v22Show();notify('V22: настройки персонажа и боя сохранены.');
}
function v22SaveBeat(){
 const a=v22Settings(scene()),index=Number($('v22-beat-list').value);
 const beat={
  t:clamp(Number($('v22-t').value)/100,0,1),
  hero:$('v22-hero').value,partner:$('v22-partner').value
 };
 if(Number.isInteger(index)&&index>=0&&index<a.beats.length)a.beats[index]=beat;
 else a.beats.push(beat);
 a.beats.sort((x,y)=>x.t-y.t);save();v22Show();
 notify('V22: актёрский ключ сохранён.');
}
function v22NewBeat(){
 const a=v22Settings(scene()),t=clamp(Number($('v22-playhead').value)/100,0,1);
 a.beats.push({t,hero:'determined',partner:'shocked'});
 a.beats.sort((x,y)=>x.t-y.t);
 save();v22Show();notify('V22: новая эмоция добавлена в текущий момент.');
}
function v22DeleteBeat(){
 const a=v22Settings(scene()),idx=Number($('v22-beat-list').value);
 if(idx<0||idx>=a.beats.length)return;
 a.beats.splice(idx,1);save();v22Show();
}
async function v22ActorSheet(){
 await preloadArtwork();
 const s=scene(),out=document.createElement('canvas'),scratch=document.createElement('canvas');
 out.width=1280;out.height=720;scratch.width=640;scratch.height=360;
 const g=out.getContext('2d');
 for(const [i,pct] of [.12,.38,.64,.9].entries()){
  drawScene(scratch,s,s.duration*pct,false);
  const x=i%2*640,y=Math.floor(i/2)*360;g.drawImage(scratch,x,y);
  g.fillStyle='rgba(2,12,25,.76)';g.fillRect(x+9,y+8,195,25);
  g.fillStyle='#ffecc8';g.font='bold 15px Arial';
  g.fillText('АКТ '+(i+1)+' • '+Math.round(pct*100)+'%',x+18,y+26);
 }
 download('V22_ACTING_'+slug(s.title)+'.png',await blobPNG(out));
 notify('V22: контактный лист с эмоциями сохранён.');
}
$('v22-scene').onchange=e=>{const [i,j]=e.target.value.split(':').map(Number);selectScene(i,j);show('acting-v22');};
$('v22-playhead').oninput=v22Preview;
$('v22-beat-list').onchange=v22Show;
$('v22-preset').onclick=()=>{v22Preset(scene());save();v22Show();};
$('v22-new').onclick=v22NewBeat;
$('v22-save-beat').onclick=v22SaveBeat;
$('v22-delete').onclick=v22DeleteBeat;
$('v22-save').onclick=v22SaveOptions;
$('v22-report').onclick=()=>download('V22_ACTING_PLAN_RU.txt',new Blob([v22Plan()],{type:'text/plain;charset=utf-8'}));
$('v22-contact').onclick=async()=>{try{await v22ActorSheet();}catch(err){notify('V22 PNG: '+err.message);}};
for(const name of ['faceStrength','combatFocus','breathing'])
 $('v22-'+name).oninput=e=>{$('v22-'+name+'-n').textContent=e.target.value;};
