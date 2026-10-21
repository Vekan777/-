/* AI Anime Factory V38 — real image finishing for 2D Canvas episodes.
   All new settings are stored ONLY in scene.cameraV38.
   Base drawScene/V35 overlaps, V36 audio and V37 subtitle story remain authoritative.
*/
const v38Looks={
 neutral:{brightness:1,contrast:1,saturation:1,warmth:0,vignette:0},
 cinematic:{brightness:1.03,contrast:1.18,saturation:1.14,warmth:8,vignette:.25},
 sunset:{brightness:1.06,contrast:1.1,saturation:1.24,warmth:28,vignette:.17},
 moonlight:{brightness:.84,contrast:1.19,saturation:.82,warmth:-32,vignette:.32},
 vivid:{brightness:1.08,contrast:1.13,saturation:1.4,warmth:4,vignette:.15}
};
const v38Defaults={zoomStart:1,zoomEnd:1.12,panStart:0,panEnd:0,
 brightness:1.03,contrast:1.18,saturation:1.14,warmth:8,vignette:.25,letterbox:false};
let v38Scratch=null,v38At=0,v38Playing=false,v38Stamp=0,v38RAF=0;
function v38Num(v,d,lo,hi){
 const n=Number(v);return Number.isFinite(n)?clamp(n,lo,hi):d;
}
function v38Of(scene){
 if(!scene.cameraV38||typeof scene.cameraV38!=='object'||Array.isArray(scene.cameraV38))
  scene.cameraV38={};
 const config=scene.cameraV38;
 const specs={zoomStart:[1,1,1.3],zoomEnd:[1.12,1,1.3],
 panStart:[0,-1,1],panEnd:[0,-1,1],brightness:[1.03,.6,1.5],
 contrast:[1.18,.6,1.5],saturation:[1.14,0,2],
 warmth:[8,-50,50],vignette:[.25,0,.65]};
 for(const [key,[defaultValue,min,max]] of Object.entries(specs))
  config[key]=v38Num(config[key],defaultValue,min,max);
 config.letterbox=config.letterbox===true;
 return config;
}
function v38Settings(scene){
 const c=v38Of(scene);return {...c};
}
function v38Ease(t){const v=clamp(t,0,1);return v*v*(3-2*v);}
function v38Mix(a,b,t){return a+(b-a)*t;}
function v38LookAt(state){
 const row=state.row;
 if(!row)return {...v38Defaults,zoom:1,pan:0};
 const data=v38Of(row.scene),p=v38Ease((state.t-row.start)/row.duration);
 const out={...data,zoom:v38Mix(data.zoomStart,data.zoomEnd,p),
  pan:v38Mix(data.panStart,data.panEnd,p)};
 const prev=state.previous;
 if(prev&&prev.outgoing>.0001&&state.t<row.start+prev.outgoing){
  const before=v38Of(prev.scene),weight=v38Ease((state.t-row.start)/prev.outgoing);
  const old={...before,zoom:before.zoomEnd,pan:before.panEnd};
  for(const key of ['brightness','contrast','saturation','warmth','vignette','zoom','pan'])
   out[key]=v38Mix(old[key],out[key],weight);
  out.letterbox=weight<.5?before.letterbox:data.letterbox;
 }
 return out;
}
function v38Canvas(w,h){
 if(!v38Scratch)v38Scratch=document.createElement('canvas');
 if(v38Scratch.width!==w)v38Scratch.width=w;
 if(v38Scratch.height!==h)v38Scratch.height=h;
 return v38Scratch;
}
function v38Frame(canvas,episode,sec){
 const w=canvas.width,h=canvas.height,raw=v38Canvas(w,h);
 const state=v35Frame(raw,episode,sec),ctx=canvas.getContext('2d');
 const look=v38LookAt(state);
 ctx.save();
 ctx.clearRect(0,0,w,h);
 ctx.fillStyle='#05070b';ctx.fillRect(0,0,w,h);
 const extraX=Math.max(0,(look.zoom-1)*w/2);
 const dx=look.pan*extraX*.9;
 ctx.translate(w/2+dx,h/2);
 ctx.scale(look.zoom,look.zoom);
 ctx.filter='brightness('+look.brightness.toFixed(3)+') contrast('+
  look.contrast.toFixed(3)+') saturate('+look.saturation.toFixed(3)+')';
 ctx.drawImage(raw,-w/2,-h/2,w,h);
 ctx.filter='none';ctx.restore();
 if(look.warmth){
  ctx.save();ctx.globalAlpha=Math.abs(look.warmth)/650;
  ctx.fillStyle=look.warmth>0?'#ff9b40':'#4088ff';
  ctx.fillRect(0,0,w,h);ctx.restore();
 }
 if(look.vignette>.001){
  const g=ctx.createRadialGradient(w/2,h/2,Math.min(w,h)*.16,
                                   w/2,h/2,Math.max(w,h)*.75);
  g.addColorStop(0,'rgba(0,0,0,0)');
  g.addColorStop(1,'rgba(0,0,0,'+look.vignette.toFixed(3)+')');
  ctx.fillStyle=g;ctx.fillRect(0,0,w,h);
 }
 if(look.letterbox){
  const bar=Math.round(h*.09);ctx.fillStyle='#000';
  ctx.fillRect(0,0,w,bar);ctx.fillRect(0,h-bar,w,bar);
 }
 // Subtitle text is drawn LAST so cinematography never reduces readability.
 v37Paint(canvas,episode,sec);
 return state;
}
function v38Episode(){
 if(!P)return null;
 const i=Number($('v38-episode').value)||0;
 return P.episodes[i]||P.episodes[0]||null;
}
function v38Scene(){
 const e=v38Episode();return e?.scenes?.[Number($('v38-scene').value)||0]||null;
}
function v38Show(){
 if(!P)return;
 v38Pause();
 const sel=$('v38-episode'),old=sel.value;
 sel.innerHTML=P.episodes.map((e,i)=>
  '<option value="'+i+'">Серия '+e.number+' — '+escapeHTML(e.title)+'</option>').join('');
 sel.value=[...sel.options].some(o=>o.value===old)?old:String(epIndex);
 if(!sel.value&&P.episodes.length)sel.value='0';
 v38Scenes();
}
function v38Scenes(){
 v38Pause();const episode=v38Episode(),sel=$('v38-scene'),old=sel.value;
 sel.innerHTML=(episode?.scenes||[]).map((s,i)=>
  '<option value="'+i+'">'+(i+1)+'. '+escapeHTML(s.title)+'</option>').join('');
 sel.value=[...sel.options].some(o=>o.value===old)?old:'0';
 v38Controls();v38At=0;v38Render();
}
function v38Controls(){
 const s=v38Scene();if(!s)return;
 const cfg=v38Of(s);
 for(const key of ['zoomStart','zoomEnd','panStart','panEnd',
   'brightness','contrast','saturation','warmth','vignette']){
  const el=$('v38-'+key);if(el)el.value=cfg[key];
 }
 $('v38-letterbox').checked=cfg.letterbox;
 v38Labels();
}
function v38Labels(){
 for(const key of ['zoomStart','zoomEnd','panStart','panEnd',
   'brightness','contrast','saturation','warmth','vignette']){
  const el=$('v38-'+key),label=$('v38-n-'+key);
  if(el&&label)label.textContent=Number(el.value).toFixed(2);
 }
}
function v38Save(){
 const s=v38Scene();if(!s)return;
 const cfg=v38Of(s);
 for(const key of ['zoomStart','zoomEnd','panStart','panEnd',
  'brightness','contrast','saturation','warmth','vignette'])
  cfg[key]=Number($('v38-'+key).value);
 cfg.letterbox=$('v38-letterbox').checked;
 v38Of(s);save();v38Render();v38Labels();
 notify('V38: камера и цвет сцены сохранены, исходный сюжет не изменён.');
}
function v38Preset(){
 const s=v38Scene();if(!s)return;
 const key=$('v38-preset').value;
 const preset=v38Looks[key];if(!preset)return;
 const cfg=v38Of(s);Object.assign(cfg,preset);
 save();v38Controls();v38Render();
}
function v38Render(){
 const e=v38Episode(),p=v35Plan(e);if(!e||!p.rows.length)return;
 v38At=clamp(v38At,0,p.duration);
 const state=v38Frame($('v38-preview'),e,v38At);
 $('v38-time').textContent=v38At.toFixed(2)+' / '+p.duration.toFixed(2)+
  ' сек · сцена '+((state.row?.index??0)+1)+'/'+p.rows.length;
 $('v38-seek').value=p.duration?Math.round(v38At/p.duration*1000):0;
}
function v38Pause(){
 v38Playing=false;v38Stamp=0;
 if(v38RAF){cancelAnimationFrame(v38RAF);v38RAF=0;}
 if($('v38-play'))$('v38-play').textContent='Воспроизвести';
}
function v38Tick(ts){
 if(!v38Playing)return;
 const dt=v38Stamp?Math.min(.15,(ts-v38Stamp)/1000):0;v38Stamp=ts;
 v38At=Math.min(v35Plan(v38Episode()).duration,v38At+dt);
 v38Render();
 if(v38At>=v35Plan(v38Episode()).duration){v38Pause();return;}
 v38RAF=requestAnimationFrame(v38Tick);
}
function v38Toggle(){
 if(v38Playing){v38Pause();return;}
 const p=v35Plan(v38Episode());if(!p.rows.length)return;
 if(v38At>=p.duration)v38At=0;
 v38Playing=true;v38Stamp=0;$('v38-play').textContent='Пауза';
 v38RAF=requestAnimationFrame(v38Tick);
}
function v38Audit(){
 const issues=[];
 if(!P)return ['Проект не открыт.'];
 for(const ep of P.episodes){
  const p=v35Plan(ep);
  for(const row of p.rows){
   const c=v38Of(row.scene),tag='Серия '+ep.number+', сцена '+(row.index+1)+': ';
   const dz=Math.abs(c.zoomEnd-c.zoomStart);
   if(dz>.22&&row.duration<2)issues.push(tag+'слишком быстрый наезд камеры.');
   if(Math.max(c.zoomStart,c.zoomEnd)<1.025&&Math.max(Math.abs(c.panStart),Math.abs(c.panEnd))>.2)
    issues.push(tag+'панорамирование почти не видно без увеличения.');
   if(c.brightness<.75)issues.push(tag+'слишком темный кадр может скрыть детали боя.');
   if(c.saturation<.55)issues.push(tag+'очень низкая насыщенность.');
   if(c.letterbox&&row.duration<.5)issues.push(tag+'короткий кадр с киношными полосами.');
  }
 }
 return issues;
}
function v38Manifest(){
 if(!P)return {};
 return {format:'AIAnimeFactoryCinematicFinishing/38',version:38,
   episodes:P.episodes.map(ep=>({number:ep.number,title:ep.title,
    totalSeconds:v35Plan(ep).duration,scenes:v35Plan(ep).rows.map(r=>({
      sceneIndex:r.index,title:r.title,startSeconds:r.start,endSeconds:r.end,
      shot:v38Settings(r.scene)}))})),warnings:v38Audit(),
   note:'All V19–V37 scene/story/audio/subtitles fields remain authoritative.'};
}
async function v38Evidence(){
 await preloadArtwork();
 const e=v38Episode(),p=v35Plan(e);if(!p.rows.length)return;
 const c=document.createElement('canvas');c.width=640;c.height=360;
 const b=document.createElement('canvas');b.width=1280;b.height=720;
 const g=b.getContext('2d');
 for(let i=0;i<4;i++){
  const sec=p.duration*(i+.5)/4;
  v38Frame(c,e,sec);g.drawImage(c,(i%2)*640,Math.floor(i/2)*360);
 }
 download('V38_FOUR_REAL_CINEMATIC_FRAMES_'+slug(e.title)+'.png',await blobPNG(b));
}
$('v38-episode').onchange=v38Scenes;
$('v38-scene').onchange=v38Controls;
$('v38-preset').onchange=v38Preset;
for(const name of ['zoomStart','zoomEnd','panStart','panEnd',
 'brightness','contrast','saturation','warmth','vignette']){
 $('v38-'+name).oninput=v38Labels;
}
$('v38-save').onclick=v38Save;
$('v38-play').onclick=v38Toggle;
$('v38-first').onclick=()=>{v38Pause();v38At=0;v38Render();};
$('v38-seek').oninput=e=>{v38Pause();v38At=v35Plan(v38Episode()).duration*Number(e.target.value)/1000;v38Render();};
$('v38-audit').onclick=()=>{$('v38-report').textContent=v38Audit().join('\n')||
 'V38: эвристических предупреждений по камере и цвету нет.';};
$('v38-json').onclick=()=>download('V38_CINEMATIC_FINISHING.json',
 new Blob([JSON.stringify(v38Manifest(),null,2)],{type:'application/json;charset=utf-8'}));
$('v38-sheet').onclick=async()=>{try{await v38Evidence();}catch(e){notify('V38 PNG: '+e.message);}};
