/* AI Anime Factory V42 — procedural 2D scene depth and directed lighting.
 * Additive finishing layer on the genuine V19–V41 renderer; no new combat events,
 * no story rewrite, no external artwork rewriting or false 3D claims.
 */
const v42Presets={
 dawn:{hue:'gold',depth:48,light:65,atmosphere:24,particles:16,wind:22},
 storm:{hue:'blue',depth:68,light:52,atmosphere:66,particles:68,wind:72},
 ember:{hue:'orange',depth:58,light:82,atmosphere:49,particles:62,wind:42},
 moon:{hue:'violet',depth:72,light:74,atmosphere:55,particles:24,wind:21}
};
const v42Palette={
 gold:[255,204,126],blue:[122,195,245],orange:[255,126,68],violet:[169,158,250]
};
let v42Time=0,v42Playing=false,v42Timestamp=0,v42RAF=0;
const v42Before=v38Frame;
function v42Of(s){
 if(!s.stageV42||typeof s.stageV42!=='object'||Array.isArray(s.stageV42))
  s.stageV42={};
 const p=s.stageV42;
 if(!Object.prototype.hasOwnProperty.call(v42Presets,p.preset))p.preset='dawn';
 const defaults=v42Presets[p.preset];
 for(const key of ['depth','light','atmosphere','particles','wind']){
  const val=Number(p[key]);
  p[key]=Number.isFinite(val)?clamp(val,0,100):defaults[key];
 }
 p.enabled=p.enabled!==false;
 return p;
}
function v42RGB(color,a){
 return 'rgba('+color[0]+','+color[1]+','+color[2]+','+clamp(a,0,1).toFixed(4)+')';
}
function v42Noise(index,salt){
 const x=Math.sin((index+1)*73.521+salt*19.377)*14875.343;
 return x-Math.floor(x);
}
function v42Layers(canvas,state){
 const row=state?.row;if(!row)return;
 const scene=row.scene,c=v42Of(scene);
 if(!c.enabled)return;
 const w=canvas.width,h=canvas.height,ctx=canvas.getContext('2d');
 const scale=w/640,time=Math.max(0,state.t-row.start),depth=c.depth/100;
 const light=c.light/100,atmos=c.atmosphere/100,particle=c.particles/100;
 const wind=c.wind/100,palette=v42Palette[v42Presets[c.preset].hue];
 ctx.save();
 // Receding silhouettes: distant horizon responds slowly, near edges faster.
 // Translucency preserves real V23/V41 characters and existing authored world.
 if(depth>.01){
  for(let plane=0;plane<3;plane++){
   const velocity=(plane+1)*wind*1.9;
   const offset=(time*velocity)%Math.max(1,w*.22);
   ctx.fillStyle=v42RGB(palette,depth*(.036+plane*.028));
   const floor=h*(.67+plane*.074);
   ctx.beginPath();ctx.moveTo(-5,floor);
   for(let i=-1;i<=9;i++){
    const x=(i*w/8)-offset;
    const ridge=v42Noise(i+40,plane+3)*h*(.055+plane*.025);
    ctx.lineTo(x,floor-ridge);
   }
   ctx.lineTo(w+5,h);ctx.lineTo(-5,h);ctx.closePath();ctx.fill();
  }
 }
 // A shaped key light gives stage direction rather than indiscriminate exposure.
 if(light>.005){
  const drift=Math.sin(time*.42)*.05*w;
  const cx=w*.69+drift,cy=h*.21;
  const radius=w*(.43+depth*.13);
  const g=ctx.createRadialGradient(cx,cy,radius*.02,cx,cy,radius);
  g.addColorStop(0,v42RGB(palette,light*.25));
  g.addColorStop(.40,v42RGB(palette,light*.10));
  g.addColorStop(1,v42RGB(palette,0));
  ctx.fillStyle=g;ctx.fillRect(0,0,w,h);
  ctx.save();ctx.globalCompositeOperation='screen';
  const cone=ctx.createLinearGradient(cx,cy,cx-w*.40,h);
  cone.addColorStop(0,v42RGB(palette,light*.14));
  cone.addColorStop(1,v42RGB(palette,0));
  ctx.fillStyle=cone;ctx.beginPath();ctx.moveTo(cx,0);
  ctx.lineTo(cx+w*.26,h);ctx.lineTo(cx-w*.45,h);ctx.closePath();ctx.fill();
  ctx.restore();
 }
 if(atmos>.01){
  const mist=ctx.createLinearGradient(0,h*.55,0,h);
  mist.addColorStop(0,v42RGB(palette,0));
  mist.addColorStop(.76,v42RGB(palette,atmos*.09));
  mist.addColorStop(1,v42RGB(palette,atmos*.16));
  ctx.fillStyle=mist;ctx.fillRect(0,h*.5,w,h*.5);
 }
 // Deterministic particles: no random calls and no accumulated simulation.
 if(particle>.01){
  const total=Math.round(7+particle*40);
  for(let i=0;i<total;i++){
   const sx=v42Noise(i,11),sy=v42Noise(i,18),speed=.006+.013*v42Noise(i,29);
   const x=((sx+time*speed*wind+time*.004)%1)*w;
   const y=((sy+time*(.014+.01*v42Noise(i,31)))%1)*h;
   const r=(1+2.2*v42Noise(i,35))*scale*(c.preset==='storm'?.65:1);
   const alpha=particle*(.10+.19*v42Noise(i,44));
   ctx.fillStyle=v42RGB(palette,alpha);
   if(c.preset==='storm'){
    ctx.save();ctx.strokeStyle=v42RGB(palette,Math.min(.46,alpha*1.6));
    ctx.lineWidth=Math.max(.8,scale*.8);ctx.beginPath();
    ctx.moveTo(x,y);ctx.lineTo(x-wind*9*scale,y+13*scale);ctx.stroke();ctx.restore();
   }else{
    ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill();
   }
  }
 }
 // Impacts may illuminate the frame ONLY if the established V25 outcome
 // already represents an actual contact; V42 never creates or changes a hit.
 if(scene.kind==='fight'){
  const beat=v25Contact(scene,time);
  const impact=beat?.active&&(beat.outcome==='hit'||beat.outcome==='block')?
    clamp(Number(beat.contact)||0,0,1):0;
  if(impact>.01){
   ctx.fillStyle=v42RGB(palette,Math.min(.16,light*impact*.15));
   ctx.fillRect(0,0,w,h);
  }
 }
 ctx.restore();
}
v38Frame=function(canvas,episode,sec){
 const result=v42Before(canvas,episode,sec);
 v42Layers(canvas,result);
 // V37 captions are repainted last, so fog, light and rain don't obscure text.
 v37Paint(canvas,episode,sec);
 return result;
};
function v42Episode(){
 if(!P)return null;
 return P.episodes[Number($('v42-episode').value)||0]||P.episodes[0]||null;
}
function v42Scene(){
 const e=v42Episode();return e?.scenes?.[Number($('v42-scene').value)||0]||null;
}
function v42Show(){
 if(!P)return;v42Pause();
 const select=$('v42-episode'),old=select.value;
 select.innerHTML=P.episodes.map((ep,i)=>
  '<option value="'+i+'">Серия '+ep.number+' — '+escapeHTML(ep.title)+'</option>').join('');
 select.value=[...select.options].some(o=>o.value===old)?old:String(epIndex);
 if(!select.value&&P.episodes.length)select.value='0';
 v42Scenes();
}
function v42Scenes(){
 v42Pause();const ep=v42Episode(),select=$('v42-scene'),old=select.value;
 select.innerHTML=(ep?.scenes||[]).map((s,i)=>
  '<option value="'+i+'">'+(i+1)+'. '+escapeHTML(s.title)+'</option>').join('');
 select.value=[...select.options].some(o=>o.value===old)?old:'0';
 v42Time=0;v42Controls();v42Render();
}
function v42Controls(){
 const s=v42Scene();if(!s)return;
 const p=v42Of(s);$('v42-enabled').checked=p.enabled;
 $('v42-preset').value=p.preset;
 for(const key of ['depth','light','atmosphere','particles','wind']){
  $('v42-'+key).value=p[key];$('v42-label-'+key).textContent=String(p[key]);
 }
}
function v42Save(){
 const s=v42Scene();if(!s)return;
 const p=v42Of(s);p.enabled=$('v42-enabled').checked;
 p.preset=$('v42-preset').value;
 for(const key of ['depth','light','atmosphere','particles','wind'])
  p[key]=Number($('v42-'+key).value);
 save();v42Render();
 notify('V42: постановка сцены сохранена без изменения сюжета.');
}
function v42Preset(){
 const s=v42Scene();if(!s)return;
 const p=v42Of(s),name=$('v42-preset').value;
 if(!v42Presets[name])return;
 Object.assign(p,v42Presets[name],{preset:name,enabled:true});
 save();v42Controls();v42Render();
}
function v42Render(){
 const e=v42Episode(),p=v35Plan(e);if(!e||!p.rows.length)return;
 v42Time=clamp(v42Time,0,p.duration);
 const row=v38Frame($('v42-preview'),e,v42Time);
 $('v42-seek').value=p.duration?Math.round(1000*v42Time/p.duration):0;
 $('v42-time').textContent=v42Time.toFixed(2)+' / '+p.duration.toFixed(2)+
 ' с · сцена '+((row.row?.index??0)+1)+'/'+p.rows.length;
}
function v42Pause(){
 v42Playing=false;v42Timestamp=0;
 if(v42RAF){cancelAnimationFrame(v42RAF);v42RAF=0;}
 if($('v42-play'))$('v42-play').textContent='Воспроизвести';
}
function v42Tick(stamp){
 if(!v42Playing)return;
 const dt=v42Timestamp?Math.min(.15,(stamp-v42Timestamp)/1000):0;
 v42Timestamp=stamp;v42Time=Math.min(v35Plan(v42Episode()).duration,v42Time+dt);
 v42Render();
 if(v42Time>=v35Plan(v42Episode()).duration){v42Pause();return;}
 v42RAF=requestAnimationFrame(v42Tick);
}
function v42Toggle(){
 if(v42Playing){v42Pause();return;}
 const p=v35Plan(v42Episode());if(!p.rows.length)return;
 if(v42Time>=p.duration)v42Time=0;
 v42Playing=true;v42Timestamp=0;$('v42-play').textContent='Пауза';
 v42RAF=requestAnimationFrame(v42Tick);
}
function v42Manifest(){
 if(!P)return {};
 return {format:'AIAnimeFactoryStageDepth/42',version:42,
  episodes:P.episodes.map(ep=>({number:ep.number,title:ep.title,
   scenes:ep.scenes.map((s,i)=>({index:i,title:s.title,stage:{...v42Of(s)}}))})),
  note:'V19–V41 script, actor, fight outcomes, audio, subtitles and camera unmodified.'};
}
function v42Audit(){
 const warnings=[];if(!P)return warnings;
 for(const ep of P.episodes)for(const s of ep.scenes){
  const o=v42Of(s),label='Серия '+ep.number+', '+s.title+': ';
  if(!o.enabled)continue;
  if(o.atmosphere>92&&o.particles>90)warnings.push(label+'туман и частицы могут ухудшить читаемость боя.');
  if(o.light>95&&o.depth>90)warnings.push(label+'очень высокая яркость и плотность слоёв.');
  if(s.kind==='fight'&&o.particles>90)warnings.push(label+'частицы способны заслонять контур удара.');
 }
 return warnings;
}
async function v42Evidence(){
 await preloadArtwork();
 const ep=v42Episode(),p=v35Plan(ep);if(!p.rows.length)return;
 const c=document.createElement('canvas'),sheet=document.createElement('canvas');
 c.width=640;c.height=360;sheet.width=1280;sheet.height=720;
 const ctx=sheet.getContext('2d');
 for(let i=0;i<4;i++){
  v38Frame(c,ep,p.duration*(i+.5)/4);
  ctx.drawImage(c,(i%2)*640,Math.floor(i/2)*360);
 }
 download('V42_FOUR_REAL_STAGE_FRAMES_'+slug(ep.title)+'.png',await blobPNG(sheet));
}
$('v42-episode').onchange=v42Scenes;
$('v42-scene').onchange=()=>{v42Controls();v42Render();};
$('v42-enabled').onchange=v42Save;
$('v42-preset').onchange=v42Preset;
for(const key of ['depth','light','atmosphere','particles','wind']){
 $('v42-'+key).oninput=()=>{
  $('v42-label-'+key).textContent=$('v42-'+key).value;
  v42Render();
 };
}
$('v42-save').onclick=v42Save;
$('v42-play').onclick=v42Toggle;
$('v42-first').onclick=()=>{v42Pause();v42Time=0;v42Render();};
$('v42-seek').oninput=e=>{
 v42Pause();v42Time=v35Plan(v42Episode()).duration*Number(e.target.value)/1000;v42Render();
};
$('v42-json').onclick=()=>download('V42_STAGE_DEPTH.json',
 new Blob([JSON.stringify(v42Manifest(),null,2)],{type:'application/json;charset=utf-8'}));
$('v42-audit').onclick=()=>{$('v42-report').textContent=v42Audit().join('\n')||
 'Технических предупреждений по атмосфере V42 не обнаружено.';};
$('v42-sheet').onclick=async()=>{try{await v42Evidence();}catch(e){notify('V42 PNG: '+e.message);}};
