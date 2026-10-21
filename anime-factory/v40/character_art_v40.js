/* V40 — character drawing refinement integrated into the existing vector rig.
   Additive wrappers, do not modify user-supplied PNG/PSD artwork or canonical story.
   All coordinates below use the original V23 head/torso local coordinate system.
*/
const v40Profiles={
  dramatic:{line:72,eyes:88,hair:82,costume:78,shine:65},
  clean:{line:42,eyes:72,hair:54,costume:42,shine:36},
  ornate:{line:88,eyes:78,hair:94,costume:96,shine:88}
};
let v40Selected=0;
const v40FaceBase=v23FaceForm,v40HairBase=v23HairForm,
 v40CostumeBase=v23CostumeForm;
function v40Of(c){
 if(!c.visualV40||typeof c.visualV40!=='object'||Array.isArray(c.visualV40))
  c.visualV40={};
 const a=c.visualV40;
 if(!Object.hasOwn(v40Profiles,a.profile))a.profile='dramatic';
 for(const [key,def] of Object.entries(v40Profiles[a.profile]))
  a[key]=Number.isFinite(Number(a[key]))?clamp(Number(a[key]),0,100):def;
 a.enabled=a.enabled!==false;
 return a;
}
function v40FaceInk(g,c,s,role,t){
 const a=v40Of(c);if(!a.enabled)return;
 const k=a.eyes/100,detail=a.line/100,shimmer=a.shine/100;
 const emotion=v13Face(s,role,t);
 g.save();g.lineCap='round';g.lineJoin='round';
 // Eyes remain bound to the old blink and gaze logic, not independent effects.
 const aperture=clamp(1-emotion.closed,0,1);
 const gaze=clamp(emotion.gaze,-1,1)*3.2;
 for(const side of [-1,1]){
  const cx=side*17+gaze;
  const irisY=-219;
  g.globalAlpha=(.35+.55*k)*aperture;
  g.fillStyle=c.accent||'#87d5f0';
  g.beginPath();g.ellipse(cx,irisY,4.9,6.6*aperture+.35,0,0,Math.PI*2);g.fill();
  g.fillStyle='#102439';g.globalAlpha=.78*aperture;
  g.beginPath();g.ellipse(cx+.9,irisY,2.35,4.3*aperture+.15,0,0,Math.PI*2);g.fill();
  g.fillStyle='#fff';g.globalAlpha=shimmer*aperture;
  g.beginPath();g.ellipse(cx-1.4,irisY-2,1.7,1.8,0,0,Math.PI*2);g.fill();
  g.strokeStyle=c.hair||'#203551';g.lineWidth=1.4+detail*1.2;
  g.globalAlpha=detail*.76;
  g.beginPath();g.moveTo(side*7,-226);
  g.quadraticCurveTo(side*17,-229.5-side*emotion.brow*1.5,side*29,-225);
  g.stroke();
  g.globalAlpha=shimmer*.19;
  g.fillStyle='#fbb6ae';
  g.beginPath();g.ellipse(side*28,-206,6,2.7,0,0,Math.PI*2);g.fill();
 }
 g.restore();
}
function v40HairInk(g,c,s,role,t,wind){
 const a=v40Of(c);if(!a.enabled)return;
 const k=a.hair/100,shine=a.shine/100;
 const drift=clamp(wind,-5,5);
 g.save();g.lineCap='round';g.lineJoin='round';
 // Physically attached to existing head space and V24/V39 movement.
 g.strokeStyle=c.hair||'#29446d';g.lineWidth=3.4;
 g.globalAlpha=k*.86;
 for(let i=-3;i<=3;i++){
  const root=i*10,tipX=root+drift*3+i*.65;
  g.beginPath();g.moveTo(root,-257+Math.abs(i)*1.8);
  g.quadraticCurveTo(root+drift*1.8+6,-243,
   tipX+(i<0?-5:5),-224+Math.abs(i)*2.8);g.stroke();
 }
 g.strokeStyle='#e1f3ff';g.globalAlpha=k*shine*.42;g.lineWidth=1.55;
 for(let i=-2;i<=2;i++){
  const root=i*11+3;
  g.beginPath();g.moveTo(root,-255+Math.abs(i));
  g.quadraticCurveTo(root+drift*2,-240,root+drift*3+4,-231+Math.abs(i)*3);
  g.stroke();
 }
 g.restore();
}
function v40CostumeInk(g,c,s,role,t,cloth){
 const a=v40Of(c);if(!a.enabled)return;
 const k=a.costume/100,line=a.line/100,gloss=a.shine/100;
 g.save();g.lineCap='round';g.lineJoin='round';
 // Shoulder guards, seam contours, brooch and fold highlights; true rig space.
 const accent=c.accent||'#88d8ee';
 g.strokeStyle=accent;g.globalAlpha=.75*k;g.lineWidth=1.5+line*1.5;
 for(const side of [-1,1]){
  g.beginPath();g.moveTo(side*17,-167);
  g.quadraticCurveTo(side*40,-172,side*47,-148);
  g.quadraticCurveTo(side*35,-145,side*26,-133);g.stroke();
  g.beginPath();g.moveTo(side*26,-124);
  g.quadraticCurveTo(side*(22+cloth*2),-112,side*28,-88);g.stroke();
 }
 g.globalAlpha=.45*k;
 g.fillStyle='#e8f9ff';
 g.beginPath();g.moveTo(0,-141);g.lineTo(8,-132);g.lineTo(0,-123);
 g.lineTo(-8,-132);g.closePath();g.fill();
 g.fillStyle=accent;g.globalAlpha=.9*k;
 g.beginPath();g.ellipse(0,-132,3.7,5.1,0,0,Math.PI*2);g.fill();
 g.globalAlpha=.23*gloss*k;g.fillStyle='#fff';
 g.beginPath();g.moveTo(-15,-116);g.lineTo(-8,-106);g.lineTo(-13,-91);g.closePath();g.fill();
 g.restore();
}
v23FaceForm=function(g,c,s,role,t){
 v40FaceBase(g,c,s,role,t);
 v40FaceInk(g,c,s,role,t);
};
v23HairForm=function(g,c,s,role,t,wind){
 v40HairBase(g,c,s,role,t,wind);
 v40HairInk(g,c,s,role,t,wind);
};
v23CostumeForm=function(g,c,s,role,t,cloth){
 v40CostumeBase(g,c,s,role,t,cloth);
 v40CostumeInk(g,c,s,role,t,cloth);
};
function v40Show(){
 if(!P)return;
 const sel=$('v40-character'),old=Number(sel.value);
 sel.innerHTML=P.characters.map((c,i)=>'<option value="'+i+'">'+escapeHTML(c.name)+'</option>').join('');
 v40Selected=Number.isInteger(old)&&old>=0&&old<P.characters.length?old:0;
 sel.value=String(v40Selected);
 v40Controls();
}
function v40Controls(){
 if(!P)return;
 v40Selected=Number($('v40-character').value)||0;
 const c=P.characters[v40Selected],a=v40Of(c);
 $('v40-enabled').checked=a.enabled;
 $('v40-profile').value=a.profile;
 for(const key of ['eyes','hair','costume','line','shine']){
  $('v40-'+key).value=a[key];$('v40-label-'+key).textContent=String(a[key]);
 }
 v40Preview();
}
function v40Save(){
 const c=P?.characters[v40Selected];if(!c)return;
 const a=v40Of(c);a.enabled=$('v40-enabled').checked;
 a.profile=$('v40-profile').value;
 for(const key of ['eyes','hair','costume','line','shine'])
  a[key]=Number($('v40-'+key).value);
 save();v40Preview();
 notify('V40: художественные детали персонажа сохранены, сюжет не изменён.');
}
function v40Preset(){
 const c=P?.characters[v40Selected];if(!c)return;
 const a=v40Of(c);a.profile=$('v40-profile').value;
 Object.assign(a,v40Profiles[a.profile]);a.enabled=true;
 save();v40Controls();
}
function v40Preview(){
 const s=scene();if(!s)return;
 const t=s.duration*(Number($('v40-time').value)||0)/100;
 const before=$('v40-before'),after=$('v40-after');
 const c=P.characters[v40Selected],a=v40Of(c);
 const prev=a.enabled;
 try{
  a.enabled=false;drawScene(before,s,t);
  a.enabled=prev;drawScene(after,s,t);
 }finally{a.enabled=prev;}
 $('v40-caption').textContent='Кадр '+t.toFixed(2)+' сек · '+c.name+
  ' · до / после одной настройки V40';
}
async function v40Sheet(){
 await preloadArtwork();
 const s=scene(),t=s.duration*(Number($('v40-time').value)||0)/100;
 const image=document.createElement('canvas'),small=document.createElement('canvas');
 image.width=1280;image.height=720;small.width=640;small.height=360;
 const ctx=image.getContext('2d'),c=P.characters[v40Selected],a=v40Of(c),prev=a.enabled;
 try{
  const samples=[Math.max(0,t-.18),t,Math.min(s.duration,t+.18),Math.min(s.duration,t+.36)];
  samples.forEach((sec,i)=>{
   a.enabled=i%2===1;drawScene(small,s,sec);
   ctx.drawImage(small,(i%2)*640,Math.floor(i/2)*360);
  });
 }finally{a.enabled=prev;}
 download('V40_FOUR_CHARACTER_DRAWINGS.png',await blobPNG(image));
}
function v40Manifest(){
 if(!P)return {};
 return {format:'AIAnimeFactoryCharacterArt/40',version:40,characters:
  P.characters.map(c=>({name:c.name,role:c.role,quality:{...v40Of(c)}})),
  preserved:'V19–V39 original script, scene/camera/audio/subtitle and fight events unchanged.'};
}
function v40Audit(){
 if(!P)return [];
 const messages=[];
 for(const c of P.characters){
  const a=v40Of(c);if(!a.enabled)continue;
  if(a.eyes>90&&a.hair<20)messages.push(c.name+': высокий контраст лица без проработки волос.');
  if(a.costume>90&&a.line<20)messages.push(c.name+': сложный костюм при слабых контурах.');
  if(!v23Style(c).enabled)messages.push(c.name+': часть V23 элементов отключена.');
 }
 return messages;
}
$('v40-character').onchange=v40Controls;
$('v40-profile').onchange=v40Preset;
$('v40-time').oninput=v40Preview;
$('v40-enabled').onchange=v40Save;
for(const key of ['eyes','hair','costume','line','shine']){
 $('v40-'+key).oninput=()=>{
  $('v40-label-'+key).textContent=$('v40-'+key).value;
  v40Preview();
 };
}
$('v40-save').onclick=v40Save;
$('v40-sheet').onclick=async()=>{try{await v40Sheet();}catch(e){notify('V40 PNG: '+e.message);}};
$('v40-json').onclick=()=>download('V40_CHARACTER_ART.json',
 new Blob([JSON.stringify(v40Manifest(),null,2)],{type:'application/json;charset=utf-8'}));
$('v40-audit').onclick=()=>{$('v40-report').textContent=v40Audit().join('\n')||
 'Нет эвристических замечаний; оцените реальные PNG-кадры.';};
