/* AI Anime Factory V27 — procedural environment staging for 2D Canvas.
   Additive to V19–V26. No imported character art or authored PNG is rewritten.
   Motion depends solely on scene time, and every loop has an explicit bound. */
function v27World(s){
 if(!s.worldV27||typeof s.worldV27!=='object'||Array.isArray(s.worldV27))s.worldV27={};
 const a=s.worldV27;
 if(!['auto','city','forest','temple','battlefield'].includes(a.biome))a.biome='auto';
 for(const [k,def] of [['depth',76],['lighting',68],['grounding',74],['atmosphere',61],['foreground',52]]){
  a[k]=Number.isFinite(Number(a[k]))?clamp(Number(a[k]),0,100):def;
 }
 a.enabled=a.enabled!==false;
 return a;
}
function v27Biome(s){
 const a=v27World(s);
 return a.biome==='auto'?(['city','forest','temple','battlefield'].includes(s.background)?s.background:'city'):a.biome;
}
function v27Palette(s){
 const kind=v27Biome(s);
 return ({
  city:{distant:'#748fae',rim:'#9dd3fb',earth:'#294461',accent:'#fbc991'},
  forest:{distant:'#61918e',rim:'#b0edd0',earth:'#1c494a',accent:'#e0efba'},
  temple:{distant:'#a18baa',rim:'#e0cbec',earth:'#504963',accent:'#f1d1ad'},
  battlefield:{distant:'#b87674',rim:'#ffc4ab',earth:'#563d4d',accent:'#ffdfac'}
 })[kind];
}
function v27Back(g,w,h,s,t){
 const a=v27World(s);if(!a.enabled)return;
 const depth=a.depth/100,atm=a.atmosphere/100,light=a.lighting/100;
 const kind=v27Biome(s),palette=v27Palette(s);
 // Layers have different velocities for a mild parallax read, with no
 // dependence on wall time, random(), frames already drawn or network.
 g.save();
 const slow=Math.sin(t*.16)*w*.005,fast=Math.sin(t*.27+.6)*w*.009;
 const horizon=h*.765;
 for(let plane=0;plane<3;plane++){
  const k=plane/2,velocity=slow*(1-k)+fast*k;
  const y=h*(.52+plane*.075);
  g.globalAlpha=(.10+depth*.20)*(1-plane*.17);
  g.strokeStyle=palette.distant;
  g.lineWidth=Math.max(1,w*.0018*(1+plane*.6));
  for(let i=0;i<13;i++){
   const x=(i*w/10-w*.12)+velocity;
   const bh=h*(.07+((i*17+plane*13)%11)*.012);
   if(kind==='forest'){
    g.beginPath();g.moveTo(x,y);g.lineTo(x,y-bh);
    g.moveTo(x,y-bh*.8);g.lineTo(x-w*.023,y-bh*.38);
    g.moveTo(x,y-bh*.78);g.lineTo(x+w*.025,y-bh*.34);g.stroke();
   }else if(kind==='temple'){
    g.strokeRect(x,y-bh,w*.035,bh);
    g.beginPath();g.moveTo(x-w*.01,y-bh);g.lineTo(x+w*.045,y-bh);g.stroke();
   }else if(kind==='battlefield'){
    g.beginPath();g.moveTo(x,y);g.lineTo(x+w*.012,y-bh*.78);g.stroke();
   }else{
    g.strokeRect(x,y-bh,w*.031,bh);
    g.beginPath();g.moveTo(x+w*.01,y-bh*.7);g.lineTo(x+w*.01,y-bh*.3);g.stroke();
   }
  }
 }
 // Ground-plane converges toward one vanishing point. As a distinct pass it
 // uses the same pixel coordinates as actors and their contact shadows.
 g.globalAlpha=depth*.3;
 g.strokeStyle=palette.distant;
 g.lineWidth=Math.max(1,w*.0013);
 for(let row=0;row<7;row++){
  const p=(row+1)/8;
  const y=horizon+(h-horizon)*p*p;
  g.beginPath();g.moveTo(0,y);g.lineTo(w,y);g.stroke();
 }
 for(let i=-6;i<=6;i++){
  g.beginPath();g.moveTo(w*.5,horizon);g.lineTo(w*(.5+i*.12),h);g.stroke();
 }
 // Distant haze; intentionally translucent, avoiding flat opaque painting.
 g.globalAlpha=atm*.14;
 const haze=g.createLinearGradient(0,h*.42,0,horizon);
 haze.addColorStop(0,'rgba(230,236,247,0)');
 haze.addColorStop(1,palette.rim);
 g.fillStyle=haze;g.fillRect(0,h*.42,w,h*.36);
 // Environment bounce-light hints independent from the cinematic camera.
 const sx=w*.78+Math.sin(t*.18)*w*.01,sy=h*.26;
 g.globalAlpha=light*.24;
 const glow=g.createRadialGradient(sx,sy,w*.01,sx,sy,w*.40);
 glow.addColorStop(0,palette.accent);
 glow.addColorStop(1,'rgba(0,0,0,0)');
 g.fillStyle=glow;g.fillRect(sx-w*.4,sy-w*.4,w*.8,w*.8);
 g.restore();
}
function v27Feet(g,w,h,s,t,poses){
 const a=v27World(s);if(!a.enabled||!poses)return;
 const palette=v27Palette(s),amount=a.grounding/100;
 g.save();
 for(const role of ['hero','partner']){
  const p=poses[role];if(!p)continue;
  const r=Math.max(.4,Number(p.scale)||1);
  const x=p.x*w,y=p.y*h;
  const stride=v24Dynamics(s,t,role).step;
  // Contact shadows are based on actual actor position, never fixed scene
  // center; keep alpha bounded when a fighter moves.
  const gradient=g.createRadialGradient(x,y+2,0,x,y+2,w*.09*r);
  gradient.addColorStop(0,'rgba(1,5,12,'+(amount*.37).toFixed(3)+')');
  gradient.addColorStop(1,'rgba(1,5,12,0)');
  g.fillStyle=gradient;
  g.save();g.translate(x,y+3);g.scale(1,.31);g.beginPath();
  g.arc(0,0,w*.10*r,0,Math.PI*2);g.fill();g.restore();
  g.strokeStyle=palette.rim;g.globalAlpha=amount*.25;
  g.lineWidth=Math.max(1,w*.0018);
  g.beginPath();g.ellipse(x,y+1,w*.055*r,h*.011*r,0,0,Math.PI);g.stroke();
  const offset=stride*w*.009;
  g.globalAlpha=amount*.21;
  g.fillStyle=palette.accent;
  for(const dir of [-1,1]){
   g.beginPath();g.ellipse(x+dir*w*.02+offset,y+2,w*.014,h*.005,0,0,Math.PI*2);g.fill();
  }
 }
 g.restore();
}
function v27Front(g,w,h,s,t){
 const a=v27World(s);if(!a.enabled||!a.foreground)return;
 const kind=v27Biome(s),palette=v27Palette(s),power=a.foreground/100;
 // Carefully limited edge silhouettes; face/body area stays unobscured.
 g.save();g.globalAlpha=power*.27;
 g.fillStyle=palette.earth;
 const sway=Math.sin(t*.4)*w*.005;
 for(const side of [-1,1]){
  const anchor=side<0?0:w;
  for(let i=0;i<3;i++){
   const dx=side*(w*(.025+i*.021))+sway,top=h*(.69+i*.055);
   if(kind==='forest'){
    g.beginPath();g.moveTo(anchor,top);g.lineTo(anchor+dx,top-h*.11);
    g.lineTo(anchor+dx*1.7,h);g.lineTo(anchor,h);g.closePath();g.fill();
   }else if(kind==='temple'){
    g.fillRect(anchor+dx,top,w*.018,h-top);
   }else{
    g.beginPath();g.moveTo(anchor,top);
    g.lineTo(anchor+dx,top-h*.045);g.lineTo(anchor+dx*1.5,h);
    g.lineTo(anchor,h);g.closePath();g.fill();
   }
  }
 }
 g.restore();
}
function v27QA(){
 if(!P)return [];
 const result=[];
 for(const ep of P.episodes)for(const s of ep.scenes){
  const o=v27World(s);if(!o.enabled)continue;
  if(o.foreground>90&&o.depth<15)result.push(
   'Серия '+ep.number+', '+s.title+': объём переднего плана сильнее фоновой глубины.');
  if(o.lighting>94&&o.atmosphere>94)result.push(
   'Серия '+ep.number+', '+s.title+': слишком сильное свечение и туман, проверьте лица.');
 }
 return result;
}
function v27Plan(){
 if(!P)return '';
 const lines=['AI ANIME FACTORY V27 — ПАСПОРТ ОКРУЖЕНИЯ',P.title,''];
 for(const ep of P.episodes){
  lines.push('Серия '+ep.number+': '+ep.title);
  for(const s of ep.scenes){
   const o=v27World(s);lines.push(s.title+' ('+s.kind+') · '+v27Biome(s)+
    ' · глубина '+o.depth+' · свет '+o.lighting+
    ' · земля '+o.grounding+' · атмосфера '+o.atmosphere+
    ' · передний план '+o.foreground+' · включено '+o.enabled);
  }
 }
 return lines.join('\n');
}
function v27Show(){
 if(!P)return;
 const sel=$('v27-scene');
 sel.innerHTML=qualitySceneList();
 sel.value=epIndex+':'+scIndex;
 const o=v27World(scene());
 $('v27-enabled').checked=o.enabled;$('v27-biome').value=o.biome;
 for(const key of ['depth','lighting','grounding','atmosphere','foreground']){
  $('v27-'+key).value=o[key];$('v27-'+key+'-n').textContent=String(o[key]);
 }
 $('v27-qa').textContent=v27QA().slice(0,30).join('\n')||
  'Глубина, свет и земля: критических конфликтов не найдено.';
 v27Preview();
}
function v27Preview(){
 if(!P)return;
 const s=scene(),o=v27World(s),t=s.duration*(Number($('v27-position').value)||0)/100;
 const enabled=o.enabled;
 try{
  o.enabled=false;drawScene($('v27-before'),s,t,false);
  o.enabled=enabled;drawScene($('v27-after'),s,t,false);
 }finally{o.enabled=enabled;}
 $('v27-caption').textContent=s.title+' · '+v27Biome(s)+' · '+t.toFixed(2)+' с';
}
function v27Save(){
 const o=v27World(scene());
 o.enabled=$('v27-enabled').checked;o.biome=$('v27-biome').value;
 for(const key of ['depth','lighting','grounding','atmosphere','foreground'])
  o[key]=clamp(Number($('v27-'+key).value)||0,0,100);
 save();v27Show();notify('V27: настройки окружения сцены сохранены.');
}
function v27Preset(){
 const s=scene(),o=v27World(s);
 Object.assign(o,{enabled:true,biome:'auto',depth:86,lighting:75,
  grounding:82,atmosphere:62,foreground:60});
 save();v27Show();notify('V27: кинематографичный мир настроен.');
}
async function v27Sheet(){
 await preloadArtwork();
 const s=scene(),board=document.createElement('canvas'),scratch=document.createElement('canvas');
 board.width=1280;board.height=720;scratch.width=640;scratch.height=360;
 const g=board.getContext('2d');
 for(const [i,percent] of [.14,.38,.64,.88].entries()){
  drawScene(scratch,s,s.duration*percent,false);
  const x=i%2*640,y=Math.floor(i/2)*360;g.drawImage(scratch,x,y);
  g.fillStyle='rgba(4,11,23,.81)';g.fillRect(x+8,y+8,216,28);
  g.fillStyle='#eddfc8';g.font='bold 14px Arial';
  g.fillText('V27 ОКРУЖЕНИЕ '+Math.round(percent*100)+'%',x+16,y+28);
 }
 download('V27_WORLD_'+slug(s.title)+'.png',await blobPNG(board));
 notify('V27: 4 кадра окружения PNG сохранены.');
}
$('v27-scene').onchange=e=>{const [i,j]=e.target.value.split(':').map(Number);
 selectScene(i,j);show('world-v27');};
$('v27-position').oninput=v27Preview;
$('v27-save').onclick=v27Save;$('v27-preset').onclick=v27Preset;
$('v27-sheet').onclick=async()=>{try{await v27Sheet();}catch(e){notify('V27 PNG: '+e.message);}};
$('v27-plan').onclick=()=>download('V27_WORLD_PLAN_RU.txt',
 new Blob([v27Plan()],{type:'text/plain;charset=utf-8'}));
for(const k of ['depth','lighting','grounding','atmosphere','foreground'])
 $('v27-'+k).oninput=e=>{$('v27-'+k+'-n').textContent=e.target.value;};
