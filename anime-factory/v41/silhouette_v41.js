/* AI Anime Factory V41 — silhouette & costume art studio.
   This extends the actual procedural character rig at V23 draw sites.
   Story, fights, imported artwork, old layers and timing are untouched. */
const v41Presets={
 guardian:{cape:88,shoulders:86,collar:66,boots:72,hair:55,emblem:78,shape:'guardian',palette:'gold'},
 ranger:{cape:54,shoulders:38,collar:28,boots:84,hair:82,emblem:42,shape:'ranger',palette:'aqua'},
 arcanist:{cape:95,shoulders:30,collar:89,boots:36,hair:69,emblem:95,shape:'arcanist',palette:'violet'}
};
const v41Colors={gold:'#f4c76a',aqua:'#7bd4e2',violet:'#caa3fa',ember:'#f2a16e'};
const v41TorsoBase=v23TorsoForm,v41HairBase=v23HairForm,
 v41CostumeBase=v23CostumeForm,v41LegBase=v23LegForm;
let v41Selected=0;
function v41Of(c){
 if(!c.silhouetteV41||typeof c.silhouetteV41!=='object'||Array.isArray(c.silhouetteV41))
  c.silhouetteV41={};
 const o=c.silhouetteV41;
 if(!Object.prototype.hasOwnProperty.call(v41Presets,o.shape))o.shape='guardian';
 if(!Object.prototype.hasOwnProperty.call(v41Colors,o.palette))o.palette=v41Presets[o.shape].palette;
 for(const key of ['cape','shoulders','collar','boots','hair','emblem']){
  const num=Number(o[key]);
  o[key]=Number.isFinite(num)?clamp(num,0,100):v41Presets[o.shape][key];
 }
 o.enabled=o.enabled!==false;
 return o;
}
function v41C(c){const o=v41Of(c);return v41Colors[o.palette]||v41Colors.gold;}
function v41Cape(g,c,s,role,t,cloth){
 const o=v41Of(c);if(!o.enabled||o.cape<=0)return;
 const k=o.cape/100,flow=clamp(cloth,-5,5);
 const large=o.shape==='guardian',robe=o.shape==='arcanist';
 const spread=(large?58:robe?44:27)*(.55+.45*k);
 const hem=robe?39:large?22:12;
 g.save();g.lineJoin='round';g.lineCap='round';
 g.globalAlpha=Math.min(.92,.35+.6*k);
 g.fillStyle=c.coat||'#34475f';g.strokeStyle=v41C(c);
 g.lineWidth=2.1+o.shoulders/100*1.8;
 g.beginPath();g.moveTo(-25,-158);
 g.bezierCurveTo(-spread-12,-151,-spread+flow*4,-104,
                 -spread*.85+flow*9,-36-hem);
 g.quadraticCurveTo(flow*8,-59-hem,spread*.78+flow*7,-38-hem);
 g.bezierCurveTo(spread+flow*4,-100,spread+12,-152,25,-158);
 g.closePath();g.fill();g.stroke();
 // Contrast outline separates the figure from background during action scenes.
 g.strokeStyle='rgba(223,237,255,.6)';g.globalAlpha=.13+.33*k;g.lineWidth=1.5;
 g.beginPath();g.moveTo(-spread+flow*4,-103);
 g.quadraticCurveTo(-spread*.65+flow*7,-68-hem,flow*8,-59-hem);g.stroke();
 g.restore();
}
function v41Armor(g,c,s,role,t,cloth){
 const o=v41Of(c);if(!o.enabled)return;
 const accent=v41C(c),strength=o.shoulders/100,collar=o.collar/100;
 g.save();g.lineJoin='round';g.lineCap='round';
 for(const side of [-1,1]){
  const shoulder=37+strength*13;
  g.globalAlpha=.14+.74*strength;g.fillStyle=c.coat||'#385572';
  g.strokeStyle=accent;g.lineWidth=1.25+strength*1.9;
  g.beginPath();g.moveTo(side*16,-168);
  g.quadraticCurveTo(side*shoulder,-185,side*(shoulder+7),-151);
  g.lineTo(side*(31+strength*9),-135);
  g.quadraticCurveTo(side*24,-141,side*16,-168);
  g.closePath();g.fill();g.stroke();
  g.globalAlpha=.6*collar;g.strokeStyle=accent;g.lineWidth=2.25;
  g.beginPath();g.moveTo(side*9,-163);
  g.quadraticCurveTo(side*(14+collar*14),-155,side*20,-146);g.stroke();
 }
 if(o.emblem>0){
  const k=o.emblem/100;
  g.globalAlpha=.2+.75*k;g.fillStyle=accent;g.strokeStyle='#17263c';g.lineWidth=1.3;
  const size=7+4*k;
  g.beginPath();g.moveTo(0,-146-size);
  g.lineTo(size,-146);g.lineTo(0,-146+size);
  g.lineTo(-size,-146);g.closePath();g.fill();g.stroke();
  if(o.shape==='arcanist'){
   g.globalAlpha=.42*k;g.strokeStyle='#f4eeff';g.lineWidth=1.4;
   g.beginPath();g.arc(0,-146,size+5,0,Math.PI*2);g.stroke();
  }
 }
 g.restore();
}
function v41HairShape(g,c,s,role,t,wind){
 const o=v41Of(c);if(!o.enabled||o.hair<=0)return;
 const k=o.hair/100,accent=v41C(c),shift=clamp(wind,-5,5);
 g.save();g.lineCap='round';g.lineJoin='round';
 g.fillStyle=c.hair||'#28415d';g.strokeStyle=accent;g.globalAlpha=.25+.7*k;
 g.lineWidth=1.2+1.3*k;
 if(o.shape==='ranger'){
  // Dynamic long swept ponytail distinguishes ranger from armored silhouette.
  g.beginPath();g.moveTo(22,-249);
  g.bezierCurveTo(56+shift*2,-252,57+shift*5,-204,39+shift*8,-173);
  g.quadraticCurveTo(49+shift*4,-219,15,-233);
  g.closePath();g.fill();g.stroke();
 }else if(o.shape==='arcanist'){
  for(const sign of [-1,1]){
   g.beginPath();g.moveTo(sign*29,-251);
   g.quadraticCurveTo(sign*(50+shift*2),-238,sign*(38+shift*4),-183);
   g.lineTo(sign*(25+shift*2),-216);g.closePath();g.fill();g.stroke();
  }
 }else{
  for(const sign of [-1,1]){
   g.beginPath();g.moveTo(sign*12,-263);
   g.lineTo(sign*30,-285-4*k);
   g.quadraticCurveTo(sign*31,-261,sign*40,-244);
   g.closePath();g.fill();g.stroke();
  }
 }
 g.restore();
}
function v41Boots(g,c,s,role,t,steps){
 const o=v41Of(c);if(!o.enabled||o.boots<=0)return;
 const k=o.boots/100,accent=v41C(c);
 g.save();g.lineCap='round';g.strokeStyle=accent;g.lineWidth=1.2+1.6*k;
 g.globalAlpha=.2+.62*k;
 for(const sign of [-1,1]){
  const step=sign*steps;
  const kneeX=sign*(sign<0?30:28)+sign*steps*13;
  const footX=sign*36+sign*steps*29;
  const lift=sign<0?Math.max(0,steps):Math.max(0,-steps);
  const kneeY=-44+lift*13,footY=4-lift*10;
  g.beginPath();g.moveTo(kneeX-5,kneeY+7);
  g.lineTo(kneeX+6,kneeY+9);
  g.quadraticCurveTo((kneeX+footX)/2,-12,footX,footY-7);
  g.stroke();
  g.beginPath();g.moveTo(footX-12,footY-3);
  g.quadraticCurveTo(footX,footY-11,footX+13,footY-3);g.stroke();
 }
 g.restore();
}
// Wrappers draw in actual actor local space, not a screen-wide post effect.
v23TorsoForm=function(g,c,s,role,t,cloth){
 v41Cape(g,c,s,role,t,cloth);v41TorsoBase(g,c,s,role,t,cloth);
 v41Armor(g,c,s,role,t,cloth);
};
v23HairForm=function(g,c,s,role,t,wind){
 v41HairBase(g,c,s,role,t,wind);v41HairShape(g,c,s,role,t,wind);
};
v23LegForm=function(g,c,s,role,t,steps){
 v41LegBase(g,c,s,role,t,steps);v41Boots(g,c,s,role,t,steps);
};
v23CostumeForm=function(g,c,s,role,t,cloth){
 v41CostumeBase(g,c,s,role,t,cloth);
};
function v41Current(){return P?.characters?.[v41Selected]||null;}
function v41Show(){
 if(!P)return;
 const sel=$('v41-character'),old=Number(sel.value);
 sel.innerHTML=P.characters.map((c,i)=>
  '<option value="'+i+'">'+escapeHTML(c.name)+'</option>').join('');
 v41Selected=Number.isInteger(old)&&old>=0&&old<P.characters.length?old:0;
 sel.value=String(v41Selected);v41Controls();
}
function v41Controls(){
 v41Selected=Number($('v41-character').value)||0;
 const c=v41Current();if(!c)return;
 const o=v41Of(c);
 $('v41-enabled').checked=o.enabled;
 $('v41-shape').value=o.shape;$('v41-palette').value=o.palette;
 for(const key of ['cape','shoulders','collar','boots','hair','emblem']){
  $('v41-'+key).value=o[key];$('v41-label-'+key).textContent=String(o[key]);
 }
 v41Preview();
}
function v41Preset(){
 const c=v41Current();if(!c)return;
 const a=v41Of(c),shape=$('v41-shape').value;
 Object.assign(a,v41Presets[shape]);a.enabled=true;save();v41Controls();
}
function v41Save(){
 const c=v41Current();if(!c)return;
 const a=v41Of(c);
 a.enabled=$('v41-enabled').checked;
 a.shape=$('v41-shape').value;a.palette=$('v41-palette').value;
 for(const key of ['cape','shoulders','collar','boots','hair','emblem'])
  a[key]=clamp(Number($('v41-'+key).value),0,100);
 save();v41Controls();notify('V41: силуэт и костюм сохранены для выбранного персонажа.');
}
function v41Preview(){
 if(!P)return;
 const s=scene();if(!s)return;
 const t=s.duration*(Number($('v41-time').value)||0)/100;
 const c=v41Current();if(!c)return;
 const a=v41Of(c),prev=a.enabled;
 try{
  a.enabled=false;drawScene($('v41-before'),s,t);
  a.enabled=prev;drawScene($('v41-after'),s,t);
 }finally{a.enabled=prev;}
 $('v41-caption').textContent=c.name+' · '+t.toFixed(2)+' сек. — одна сцена и таймкод';
}
function v41Manifest(){
 if(!P)return {};
 return {format:'AIAnimeFactorySilhouetteStudio/41',version:41,
  characters:P.characters.map(c=>({name:c.name,role:c.role,
   silhouette:{...v41Of(c)}})),
  note:'Additive actor vector silhouette; story, old costume, fight and audio unchanged.'};
}
function v41Audit(){
 const out=[];if(!P)return out;
 for(const c of P.characters){
  const a=v41Of(c);if(!a.enabled)continue;
  if(a.cape>85&&a.shoulders>88)out.push(c.name+': плащ и плечи могут закрывать части костюма.');
  if(a.hair<15&&a.shape==='ranger')out.push(c.name+': прическа разведчика почти не видна.');
  if(a.emblem>85&&a.palette==='gold'&&a.shoulders>90)
   out.push(c.name+': проверьте читаемость эмблемы на доспехе.');
 }
 return out;
}
async function v41Sheet(){
 await preloadArtwork();
 const s=scene(),c=v41Current();if(!s||!c)return;
 const o=v41Of(c),old=o.enabled,frame=document.createElement('canvas'),
  sheet=document.createElement('canvas'),g=sheet.getContext('2d');
 frame.width=640;frame.height=360;sheet.width=1280;sheet.height=720;
 try{
  for(let i=0;i<4;i++){
   o.enabled=i%2===1;
   drawScene(frame,s,s.duration*(i<2?.35:.69));
   g.drawImage(frame,(i%2)*640,Math.floor(i/2)*360);
  }
 }finally{o.enabled=old;}
 download('V41_SILHOUETTE_BEFORE_AFTER.png',await blobPNG(sheet));
}
$('v41-character').onchange=v41Controls;
$('v41-shape').onchange=v41Preset;
$('v41-palette').onchange=v41Save;
$('v41-enabled').onchange=v41Save;
$('v41-time').oninput=v41Preview;
for(const key of ['cape','shoulders','collar','boots','hair','emblem']){
 $('v41-'+key).oninput=()=>{
  $('v41-label-'+key).textContent=$('v41-'+key).value;
  v41Preview();
 };
}
$('v41-save').onclick=v41Save;
$('v41-sheet').onclick=async()=>{try{await v41Sheet();}catch(err){notify('V41 PNG: '+err.message);}};
$('v41-json').onclick=()=>download('V41_SILHOUETTES.json',
 new Blob([JSON.stringify(v41Manifest(),null,2)],{type:'application/json;charset=utf-8'}));
$('v41-audit').onclick=()=>{$('v41-report').textContent=v41Audit().join('\n')||
 'Нет предупреждений по параметрам. Оцените реальные кадры.';};
