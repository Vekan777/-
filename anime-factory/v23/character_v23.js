/* AI Anime Factory V23 Character Quality.
   Improvements apply only to the procedural vector rig or its missing cutout parts.
   Existing author-owned PNG cutout layers and character illustrations remain intact.
   Stable character-specific properties; deterministic animation; no network calls.
*/
const V23_PROFILES=['balanced','heroic','slim'];
function v23Style(c){
 if(!c.qualityV23||typeof c.qualityV23!=='object'||Array.isArray(c.qualityV23))c.qualityV23={};
 const a=c.qualityV23;
 if(!V23_PROFILES.includes(a.profile))a.profile='balanced';
 for(const [key,def] of [['anatomy',72],['hairDetail',76],['costumeDetail',70],['secondaryMotion',65]]){
  a[key]=Number.isFinite(Number(a[key]))?clamp(Number(a[key]),0,100):def;
 }
 a.enabled=a.enabled!==false;
 return a;
}
function v23HeadScale(c){
 const a=v23Style(c);
 if(!a.enabled)return 1;
 return 1+(a.profile==='slim'?.055:a.profile==='heroic'?-.045:0)*a.anatomy/100;
}
function v23Secondary(s,c,t,role){
 const a=v23Style(c);
 if(!a.enabled||!a.secondaryMotion)return {body:0,hair:0,cloth:0};
 const strength=a.secondaryMotion/100;
 const phase=(role==='hero'?0:1.3);
 // Phase-delayed secondary motion. Pure function of t, so film exports are repeatable.
 const foot=Math.sin(t*4.8+phase)*.35;
 return {body:Math.sin(t*2.8+phase)*.8*strength,
  hair:(Math.sin(t*3.2+phase-.6)+.25*foot)*.85*strength,
  cloth:Math.sin(t*2.25+phase-1.1)*.88*strength};
}
function v23LegForm(g,c,s,role,t,steps){
 const a=v23Style(c);if(!a.enabled||a.anatomy<=0)return;
 const k=a.anatomy/100,heroic=a.profile==='heroic',slim=a.profile==='slim';
 const shin=heroic?12:slim?7:10;
 g.save();g.lineJoin='round';g.lineCap='round';
 for(const side of [-1,1]){
  const kneeX=side*(side<0?30:28)+side*steps*13;
  const footX=side*36+side*steps*29;
  const lift=side<0?Math.max(0,steps):Math.max(0,-steps);
  const kneeY=-44+lift*13,footY=4-lift*10;
  g.globalAlpha=.72*k;g.strokeStyle='#60748f';g.lineWidth=shin;
  g.beginPath();g.moveTo(kneeX,kneeY+2);g.quadraticCurveTo((kneeX+footX)/2+side*2,-17,footX,footY-6);g.stroke();
  g.globalAlpha=.88*k;g.fillStyle=c.accent||'#91d7ee';
  g.beginPath();g.ellipse(kneeX,kneeY,shin*.62,7,side*.14,0,Math.PI*2);g.fill();
  g.globalAlpha=.55*k;g.strokeStyle='#d0e2f2';g.lineWidth=1.5;
  g.beginPath();g.moveTo(kneeX+side*3,kneeY+10);g.lineTo(footX+side*3,footY-8);g.stroke();
 }
 g.restore();
}
function v23TorsoForm(g,c,s,role,t,cloth){
 const a=v23Style(c);if(!a.enabled||a.anatomy<=0)return;
 const k=a.anatomy/100;
 const shoulder=a.profile==='heroic'?49:a.profile==='slim'?35:42;
 const waist=a.profile==='heroic'?31:a.profile==='slim'?24:29;
 const gradient=g.createLinearGradient(-shoulder,-150,waist,-88);
 gradient.addColorStop(0,c.coat||'#3e587b');
 gradient.addColorStop(.52,'#34485f');
 gradient.addColorStop(1,c.coat||'#3e587b');
 g.save();g.globalAlpha=.82*k;g.fillStyle=gradient;
 g.beginPath();g.moveTo(-shoulder,-153);g.quadraticCurveTo(-shoulder*.4,-177,0,-177);
 g.quadraticCurveTo(shoulder*.55,-176,shoulder,-153);
 g.quadraticCurveTo(waist+4,-130,waist+cloth*5,-84);
 g.quadraticCurveTo(0,-75,-waist-cloth*5,-84);
 g.quadraticCurveTo(-waist-5,-128,-shoulder,-153);g.closePath();g.fill();
 // Neck-to-shoulder anatomy and shaped waist, not arbitrary frame-to-frame warping.
 g.globalAlpha=.58*k;g.strokeStyle='#b2cee1';g.lineWidth=2;
 g.beginPath();g.moveTo(-shoulder+4,-150);g.quadraticCurveTo(-25,-164,-11,-164);
 g.moveTo(shoulder-4,-150);g.quadraticCurveTo(25,-164,11,-164);g.stroke();
 g.restore();
}
function v23CostumeForm(g,c,s,role,t,cloth){
 const a=v23Style(c);if(!a.enabled||a.costumeDetail<=0)return;
 const k=a.costumeDetail/100;
 g.save();g.lineCap='round';g.lineJoin='round';
 g.globalAlpha=.7*k;g.strokeStyle=c.accent||'#8bc8df';g.lineWidth=2.4;
 for(const side of [-1,1]){
  g.beginPath();g.moveTo(side*24,-148);g.quadraticCurveTo(side*29,-128,side*(27+cloth*4),-100);g.stroke();
  g.beginPath();g.moveTo(side*12,-111);g.lineTo(side*18,-106);g.stroke();
 }
 g.globalAlpha=.45*k;g.fillStyle='#d8eafa';
 for(const x of [-12,12]){
  g.beginPath();g.ellipse(x,-95,2.6,1.9,0,0,Math.PI*2);g.fill();
 }
 g.restore();
}
function v23ArmForm(g,c,s,role,t,leftElbow,leftHand,rightElbow,rightHand){
 const a=v23Style(c);if(!a.enabled||a.anatomy<=0)return;
 const k=a.anatomy/100;
 g.save();g.lineJoin='round';g.lineCap='round';
 for(const [elbow,hand,side] of [[leftElbow,leftHand,-1],[rightElbow,rightHand,1]]){
  g.globalAlpha=.7*k;g.strokeStyle='#667d94';g.lineWidth=a.profile==='heroic'?11:8;
  g.beginPath();g.moveTo(elbow[0],elbow[1]);g.quadraticCurveTo((elbow[0]+hand[0])/2,(elbow[1]+hand[1])/2,hand[0],hand[1]);g.stroke();
  g.globalAlpha=.85*k;g.fillStyle=c.accent||'#91d7ee';
  g.beginPath();g.ellipse(elbow[0],elbow[1],8,9,side*.16,0,Math.PI*2);g.fill();
  g.globalAlpha=.72*k;g.fillStyle='#f1cfc4';
  g.beginPath();g.ellipse(hand[0],hand[1],6,5.2,side*.12,0,Math.PI*2);g.fill();
 }
 g.restore();
}
function v23FaceForm(g,c,s,role,t){
 const a=v23Style(c);if(!a.enabled||!a.anatomy)return;
 const k=a.anatomy/100;
 g.save();
 g.strokeStyle='#b07b7b';g.globalAlpha=.3*k;g.lineWidth=1.7;
 g.beginPath();g.moveTo(-31,-209);g.quadraticCurveTo(-23,-184,-4,-180);
 g.moveTo(31,-209);g.quadraticCurveTo(23,-184,4,-180);g.stroke();
 g.globalAlpha=.17*k;g.fillStyle='#fff1df';
 for(const sign of [-1,1]){g.beginPath();g.ellipse(sign*27,-204,7,4,0,0,Math.PI*2);g.fill();}
 g.restore();
}
function v23HairForm(g,c,s,role,t,wind){
 const a=v23Style(c);if(!a.enabled||!a.hairDetail)return;
 const k=a.hairDetail/100,detail=wind+v23Secondary(s,c,t,role).hair;
 g.save();g.lineJoin='round';g.lineCap='round';g.strokeStyle='#c3e0f5';
 g.globalAlpha=.47*k;g.lineWidth=2.25;
 for(const i of [-2,-1,0,1,2]){
  const root=i*13;
  g.beginPath();g.moveTo(root,-263-Math.abs(i%2)*4);
  g.quadraticCurveTo(root+detail*3+6,-251,root+detail*9+4,-229+Math.abs(i)*3);g.stroke();
 }
 g.globalAlpha=.7*k;g.fillStyle=c.hair||'#34517e';
 for(const sign of [-1,1]){
  g.beginPath();g.moveTo(sign*28,-245);
  g.quadraticCurveTo(sign*(43+detail*2),-226,sign*(37+detail*7),-193);
  g.lineTo(sign*(27+detail*3),-213);g.closePath();g.fill();
 }
 g.restore();
}
function v23Report(){
 if(!P)return '';
 const lines=['AI ANIME FACTORY V23 — CHARACTER QUALITY',P.title,''];
 for(const c of P.characters){
  const a=v23Style(c);
  lines.push(c.name+' ('+c.role+')', 'Профиль: '+a.profile+
   '; анатомия '+a.anatomy+'%; волосы '+a.hairDetail+
   '%; костюм '+a.costumeDetail+'%; динамика '+a.secondaryMotion+
   '%; включено '+a.enabled,'');
 }
 return lines.join('\n');
}
function v23CharacterQA(){
 if(!P)return [];
 const issues=[];
 for(const c of P.characters){
  const a=v23Style(c);
  if(!a.enabled)continue;
  if(a.anatomy>85&&a.profile==='heroic'&&a.hairDetail<15)
   issues.push(c.name+': силуэт выразительнее волос; проверьте читаемость головы.');
  if(a.secondaryMotion>90)
   issues.push(c.name+': сильная вторичная динамика, проверьте постановку кадров.');
 }
 return issues;
}
function v23Show(){
 if(!P)return;
 const select=$('v23-character'),selected=select.value,old=selected===''?0:Number(selected);
 select.innerHTML=P.characters.map((c,i)=>'<option value="'+i+'">'+escapeHTML(c.name)+'</option>').join('');
 const i=clamp(Number.isFinite(old)?old:0,0,P.characters.length-1);
 select.value=String(i);
 const a=v23Style(P.characters[i]);
 $('v23-enabled').checked=a.enabled;$('v23-profile').value=a.profile;
 for(const key of ['anatomy','hairDetail','costumeDetail','secondaryMotion']){
  $('v23-'+key).value=a[key];$('v23-'+key+'-n').textContent=String(a[key]);
 }
 $('v23-report').textContent=v23CharacterQA().slice(0,30).join('\n')||
  'Проверка параметров: критичных замечаний нет.';
 v23Preview();
}
function v23Preview(){
 if(!P)return;
 const s=scene(),t=s.duration*(Number($('v23-playhead').value)||0)/100;
 drawScene($('v23-preview'),s,t);
 $('v23-caption').textContent=s.title+' · '+t.toFixed(2)+' с · '+P.characters[Number($('v23-character').value)||0].name;
}
function v23Save(){
 const c=P.characters[Number($('v23-character').value)||0],a=v23Style(c);
 a.enabled=$('v23-enabled').checked;a.profile=$('v23-profile').value;
 for(const key of ['anatomy','hairDetail','costumeDetail','secondaryMotion'])
  a[key]=clamp(Number($('v23-'+key).value)||0,0,100);
 save();v23Show();notify('V23: параметры героя сохранены в JSON проекта.');
}
function v23Preset(){
 const c=P.characters[Number($('v23-character').value)||0],a=v23Style(c);
 a.enabled=true;a.profile='balanced';a.anatomy=76;a.hairDetail=84;
 a.costumeDetail=80;a.secondaryMotion=62;
 save();v23Show();notify('V23: профиль аниме-персонажа применён.');
}
async function v23Sheet(){
 await preloadArtwork();
 const s=scene(),out=document.createElement('canvas'),small=document.createElement('canvas');
 out.width=1280;out.height=720;small.width=640;small.height=360;
 const g=out.getContext('2d');
 for(const [i,pct] of [.12,.36,.63,.88].entries()){
  drawScene(small,s,s.duration*pct,false);
  const x=i%2*640,y=Math.floor(i/2)*360;
  g.drawImage(small,x,y);g.fillStyle='rgba(3,9,24,.78)';
  g.fillRect(x+6,y+5,170,26);g.fillStyle='#f8e9d6';g.font='bold 14px Arial';
  g.fillText('V23 • '+Math.round(pct*100)+'%',x+16,y+24);
 }
 download('V23_CHARACTERS_'+slug(s.title)+'.png',await blobPNG(out));
 notify('V23: лист четырёх кадров PNG сохранён.');
}
$('v23-character').onchange=v23Show;
$('v23-playhead').oninput=v23Preview;
$('v23-save').onclick=v23Save;
$('v23-preset').onclick=v23Preset;
$('v23-sheet').onclick=async()=>{try{await v23Sheet();}catch(e){notify('V23 PNG: '+e.message);}};
$('v23-txt').onclick=()=>download('V23_CHARACTER_LOOKDEV_RU.txt',
 new Blob([v23Report()],{type:'text/plain;charset=utf-8'}));
for(const key of ['anatomy','hairDetail','costumeDetail','secondaryMotion'])
 $('v23-'+key).oninput=e=>{$('v23-'+key+'-n').textContent=e.target.value;v23Preview();};
