/* AI Anime Factory V21: visual quality and cinematic effects.
   Runs inside the original V19/V20 renderer closure. No external libraries.
   Scene-specific settings and deterministic frames: no random flicker.
*/
const V21_LOOKS = {
  azure:{back:'#18384f',shine:'#96ddff',shadow:'#061727',air:'#a4d9fa'},
  sunset:{back:'#75443d',shine:'#ffe5af',shadow:'#291421',air:'#ffad7c'},
  moon:{back:'#35375c',shine:'#c4ceff',shadow:'#0a0e26',air:'#b3c8fa'},
  emerald:{back:'#1c5447',shine:'#a4f5ce',shadow:'#071f27',air:'#8be1be'},
  crimson:{back:'#70364d',shine:'#ffb6c6',shadow:'#230c21',air:'#ee8ca8'}
};
function v21Look(s){
  if(!s.visualV21||typeof s.visualV21!=='object')s.visualV21={};
  const v=s.visualV21,valid=['azure','sunset','moon','emerald','crimson'];
  if(!valid.includes(v.look))v.look=s.kind==='romance'?'sunset':s.kind==='fight'?'crimson':s.background==='forest'?'emerald':'azure';
  if(!['clear','mist','rain','snow','embers'].includes(v.weather))v.weather=s.kind==='fight'?'embers':s.kind==='romance'?'mist':'clear';
  for(const [key,defaultValue] of [['intensity',72],['depth',67],['rays',50],['rim',60],['sparks',65],['grain',10]]){
    const n=Number(v[key]);v[key]=Number.isFinite(n)?clamp(n,0,100):defaultValue;
  }
  if(v.enabled!==false)v.enabled=true;
  return v;
}
function v21Palette(s){return V21_LOOKS[v21Look(s).look]||V21_LOOKS.azure;}
function v21Rand(n){let x=(n*1664525+1013904223)>>>0;x^=x>>>16;x=Math.imul(x,2246822519);x^=x>>>13;return (x>>>0)/4294967296;}
function v21AtmosphereBack(g,w,h,s,t){
  const o=v21Look(s);if(!o.enabled)return;
  const c=v21Palette(s),v=o.intensity/100,d=o.depth/100;
  g.save();
  const haze=g.createLinearGradient(0,h*.21,0,h);
  haze.addColorStop(0,'rgba(0,0,0,0)');haze.addColorStop(.63,c.back+'13');haze.addColorStop(1,c.air+'30');
  g.globalAlpha=.36*v;g.fillStyle=haze;g.fillRect(0,0,w,h);
  const x=w*(.72+Math.sin(t*.15)*.004),y=h*.15;
  if(o.rays>0){
    g.globalCompositeOperation='screen';
    for(let i=0;i<5;i++){
      g.beginPath();g.moveTo(x,y);
      const a=.4+i*.38;
      g.lineTo(x-w*(.5+i*.15),h*.81);
      g.lineTo(x-w*(.46+i*.15)+w*.08*d,h*.81);
      g.closePath();
      g.globalAlpha=(.023+.023*(i%3))*v*o.rays/100;g.fillStyle=c.shine;g.fill();
    }
  }
  g.globalCompositeOperation='source-over';g.globalAlpha=.2*d;
  g.strokeStyle=c.air;g.lineWidth=Math.max(1,w*.002);
  // Distinctive environment silhouettes: temple arcs / tree trunks / ruins.
  if(s.background==='temple'){
    for(let i=0;i<5;i++){
      const cx=w*(i*.29-.12),roof=h*(.38+(i%2)*.08);
      g.beginPath();g.moveTo(cx,roof+h*.34);g.lineTo(cx,roof+h*.045);
      g.quadraticCurveTo(cx+w*.085,roof-h*.045,cx+w*.17,roof+h*.045);
      g.lineTo(cx+w*.17,roof+h*.34);g.stroke();
    }
  }else if(s.background==='forest'){
    for(let i=0;i<7;i++){
      const x=w*v21Rand(i+22),ht=h*(.35+v21Rand(i+34)*.2);
      g.beginPath();g.moveTo(x,h*.77);g.lineTo(x-w*.017,h*.77-ht);g.stroke();
      g.beginPath();g.arc(x,h*.77-ht,w*(.07+v21Rand(i+61)*.05),0,Math.PI*2);g.stroke();
    }
  }else{
    for(let i=0;i<7;i++){
      const x=w*(i/6),ht=h*(.14+.1*v21Rand(i+72));
      g.beginPath();g.moveTo(x,h*.77);g.lineTo(x+w*.018,h*.77-ht);
      g.lineTo(x+w*.09,h*.77-ht-h*.02);g.stroke();
    }
  }
  g.restore();
}
function v21CharacterBack(g,w,h,s,t,poses){
  const o=v21Look(s);if(!o.enabled||o.rim<=0)return;
  const c=v21Palette(s);
  g.save();g.globalCompositeOperation='screen';
  for(const p of [poses.hero,poses.partner]){
    const x=p.x*w,y=p.y*h-w*.15;
    const radius=w*.23*p.scale;
    const glow=g.createRadialGradient(x-w*.015,y-w*.05,1,x,y,radius);
    glow.addColorStop(0,c.shine+'55');glow.addColorStop(.45,c.air+'19');glow.addColorStop(1,c.air+'00');
    g.globalAlpha=.26*o.rim/100;g.fillStyle=glow;g.fillRect(x-radius,y-radius,radius*2,radius*2);
  }
  g.restore();
}
function v21CharacterDetail(g,w,h,s,t,poses,hero,second){
  const o=v21Look(s);if(!o.enabled||o.rim<=0)return;
  const c=v21Palette(s),strength=o.rim/100;
  const chars=[[poses.hero,hero],[poses.partner,second]];
  g.save();
  for(let i=0;i<2;i++){
    const [p,actor]=chars[i],x=p.x*w,y=p.y*h,z=p.scale*w/960;
    const glow=actor.accent||c.shine;
    g.globalAlpha=.40*strength;g.strokeStyle=c.shine;
    g.lineWidth=Math.max(.7,2.2*z);g.lineCap='round';g.shadowBlur=Math.min(12,w*.012);g.shadowColor=c.shine;
    g.beginPath();g.moveTo(x-z*27,y-z*150);g.quadraticCurveTo(x-z*53,y-z*191,x-z*17,y-z*223);g.stroke();
    g.beginPath();g.moveTo(x+z*32,y-z*143);g.quadraticCurveTo(x+z*41,y-z*109,x+z*38,y-z*90);g.stroke();
    // Center emblem glint and luminous costume micro-detail.
    g.globalAlpha=(.26+.22*Math.sin(t*1.4+i)**2)*strength;g.fillStyle=glow;
    g.beginPath();g.arc(x,y-z*139,Math.max(1,z*4),0,Math.PI*2);g.fill();
    g.shadowBlur=0;
  }
  g.restore();
}
function v21ImpactDetails(g,w,h,s,t,st,poses){
  const o=v21Look(s);if(!o.enabled||s.kind!=='fight'||!st)return;
  if(!['hit','block'].includes(st.event.outcome))return;
  const c=v21Palette(s),strength=clamp(st.nearHit,0,1),sparks=o.sparks/100;
  if(strength<.02||sparks<=0)return;
  const attacker=poses[st.event.actor],opponent=poses[st.event.actor==='hero'?'partner':'hero'];
  const px=(attacker.x+opponent.x)*w/2,py=(attacker.y+opponent.y)*h/2-w*.09;
  const seed=Math.round(st.event.sec*173);
  g.save();g.globalCompositeOperation='screen';
  g.strokeStyle=st.event.outcome==='block'?'#9adffd':c.shine;
  g.lineWidth=Math.max(1,w*.002);g.globalAlpha=.5*strength*sparks;
  const ring=w*(.027+.076*(1-strength));
  g.beginPath();g.ellipse(px,py,ring,ring*.65,t*.3,0,Math.PI*2);g.stroke();
  for(let i=0;i<18;i++){
    const a=v21Rand(seed+i*11)*6.283,dist=w*(.025+.08*v21Rand(seed+i*17));
    const inner=dist*(.3+.35*(1-strength)),outer=inner+dist*(.2+.6*v21Rand(seed+i*31));
    g.globalAlpha=strength*sparks*(.15+.6*v21Rand(seed+i*23));
    g.lineWidth=Math.max(.8,w*(.0007+.002*v21Rand(seed+i*5)));
    g.beginPath();g.moveTo(px+Math.cos(a)*inner,py+Math.sin(a)*inner*.7);
    g.lineTo(px+Math.cos(a)*outer,py+Math.sin(a)*outer*.7);g.stroke();
  }
  g.restore();
}
function v21AtmosphereFront(g,w,h,s,t){
  const o=v21Look(s);if(!o.enabled)return;
  const c=v21Palette(s),strength=o.intensity/100;
  g.save();
  if(o.weather==='mist'){
    const fog=g.createLinearGradient(0,h*.48,0,h);
    fog.addColorStop(0,c.air+'00');fog.addColorStop(.75,c.air+'14');fog.addColorStop(1,c.air+'32');
    g.globalAlpha=.35*strength;g.fillStyle=fog;g.fillRect(0,0,w,h);
  }else if(o.weather==='rain'||o.weather==='snow'||o.weather==='embers'){
    const count=o.weather==='rain'?85:35;
    for(let i=0;i<count;i++){
      const rx=v21Rand(i+61),ry=v21Rand(i+123),speed=o.weather==='rain'?.35:o.weather==='snow'?.045:.07;
      const x=((rx+(o.weather==='embers'?.025:-.07)*t+i*.00015)%1+1)%1*w;
      const y=((ry+(o.weather==='embers'?-speed:speed)*t)%1+1)%1*h;
      if(o.weather==='rain'){
        g.strokeStyle=c.air;g.lineWidth=Math.max(.6,w*.001);
        g.globalAlpha=(.04+.15*v21Rand(i+323))*strength;
        g.beginPath();g.moveTo(x,y);g.lineTo(x-w*.009,y+h*.044);g.stroke();
      }else{
        const radius=w*(.001+v21Rand(i+312)*.0024);
        g.globalAlpha=(.12+.3*v21Rand(i+424))*strength;
        g.fillStyle=o.weather==='embers'?'#ffcf93':c.air;
        g.beginPath();g.arc(x+Math.sin(t+i)*w*.006,y,radius,0,Math.PI*2);g.fill();
      }
    }
  }
  g.restore();
}
function v21Grade(g,w,h,s,t){
  const o=v21Look(s);if(!o.enabled)return;
  const c=v21Palette(s);
  g.save();g.globalAlpha=.055*o.intensity/100;g.fillStyle=c.back;g.fillRect(0,0,w,h);
  if(o.grain>0){
    g.globalAlpha=.045*o.grain/100;g.fillStyle='#f5f1de';
    const step=Math.max(1,Math.round(w/400));
    for(let i=0;i<85;i++){
      const x=v21Rand(i*7+17+Math.floor(t*6)*13)*w;
      const y=v21Rand(i*9+18+Math.floor(t*6)*13)*h;
      g.fillRect(x,y,step,step);
    }
  }
  g.restore();
}
function v21VisualQA(){
  const warnings=[];
  for(const e of P.episodes)for(const s of e.scenes){
    const o=v21Look(s);
    if(o.weather==='embers'&&s.kind==='romance')warnings.push(e.number+'/'+s.title+': искры в романтической сцене могут мешать тону.');
    if(o.grain>75)warnings.push(e.number+'/'+s.title+': сильное зерно снижает читаемость на 640x360.');
    if(o.sparks>90&&o.intensity>90)warnings.push(e.number+'/'+s.title+': пересвет — снизьте интенсивность.');
    if(o.rim>93)warnings.push(e.number+'/'+s.title+': контурный свет чрезмерный.');
  }
  return warnings;
}
function v21VisualPlan(){
  let result=['V21 VISUAL QUALITY — ПОКАДРОВЫЙ ПЛАН',P.title,'Рендер: 2D canvas (детерминированный)',''];
  for(const e of P.episodes)for(const s of e.scenes){
    const o=v21Look(s),pal=v21Palette(s);
    result.push('Серия '+e.number+' / '+s.title,
      'LOOK='+o.look+'; WEATHER='+o.weather+'; LIGHT='+o.intensity+'; DEPTH='+o.depth+
      '; RAYS='+o.rays+'; RIM='+o.rim+'; SPARKS='+o.sparks+'; GRAIN='+o.grain,
      'Ключевой свет: '+pal.shine+' / Тень: '+pal.shadow,'');
  }
  result.push('ЗАМЕЧАНИЯ:',...v21VisualQA());
  return result.join('\n');
}
function v21RenderPanel(){
  if(!P)return;
  const select=$('v21-scene');if(!select)return;
  const selected=String(epIndex)+':'+String(scIndex);
  select.innerHTML=qualitySceneList();select.value=selected;
  const o=v21Look(scene());
  $('v21-enabled').checked=o.enabled!==false;
  $('v21-look').value=o.look;$('v21-weather').value=o.weather;
  for(const k of ['intensity','depth','rays','rim','sparks','grain']){
    $('v21-'+k).value=o[k];$('v21-'+k+'-value').textContent=String(o[k]);
  }
  $('v21-qa').textContent=v21VisualQA().slice(0,30).join('\n')||'Автоматическая проверка освещения: серьёзных замечаний нет.';
  v21Preview();
}
function v21Preview(){
  if(!P)return;
  const s=scene();const t=s.duration*(Number($('v21-position').value)||50)/100;
  drawScene($('v21-preview'),s,t);
  $('v21-caption').textContent='V21: '+s.title+' · '+t.toFixed(2)+' сек · '+v21Look(s).look;
}
function v21SaveLook(){
  const o=v21Look(scene());o.enabled=$('v21-enabled').checked;
  o.look=$('v21-look').value;o.weather=$('v21-weather').value;
  for(const k of ['intensity','depth','rays','rim','sparks','grain'])o[k]=clamp(Number($('v21-'+k).value)||0,0,100);
  save();v21RenderPanel();notify('V21: визуальный стиль сцены сохранён в JSON и рендере.');
}
function v21Preset(){
  const s=scene(),o=v21Look(s);
  const preset=s.kind==='fight'?{look:'crimson',weather:'embers',intensity:76,depth:70,rays:42,rim:78,sparks:75,grain:8}:
    s.kind==='romance'?{look:'sunset',weather:'mist',intensity:55,depth:65,rays:68,rim:55,sparks:12,grain:7}:
    s.kind==='betrayal'?{look:'moon',weather:'rain',intensity:66,depth:78,rays:45,rim:74,sparks:10,grain:11}:
    {look:'azure',weather:'clear',intensity:66,depth:70,rays:50,rim:62,sparks:25,grain:8};
  Object.assign(o,preset,{enabled:true});
  save();v21RenderPanel();notify('V21: режиссёрский визуальный пресет применён.');
}
async function v21ShotSheet(){
  await preloadArtwork();
  const out=document.createElement('canvas');out.width=1280;out.height=720;
  const frame=document.createElement('canvas');frame.width=640;frame.height=360;
  const g=out.getContext('2d'),s=scene(),times=[.12,.36,.61,.89];
  for(let i=0;i<4;i++){
    drawScene(frame,s,s.duration*times[i],false);
    const x=(i%2)*640,y=Math.floor(i/2)*360;
    g.drawImage(frame,x,y);
    g.fillStyle='rgba(8,12,28,.78)';g.fillRect(x+6,y+5,125,23);
    g.fillStyle='#fef7ed';g.font='bold 14px sans-serif';g.fillText('V21 кадр '+(i+1),x+15,y+22);
  }
  download('V21_'+slug(s.title)+'_SHOT_SHEET.png',await blobPNG(out));
  notify('V21: лист четырёх кадров PNG готов.');
}
$('v21-scene').onchange=event=>{
  const [i,j]=event.target.value.split(':').map(Number);
  selectScene(i,j);show('visual-v21');
};
$('v21-position').oninput=v21Preview;
for(const key of ['intensity','depth','rays','rim','sparks','grain'])
  $('v21-'+key).oninput=()=>{$('v21-'+key+'-value').textContent=$('v21-'+key).value;};
$('v21-save').onclick=v21SaveLook;
$('v21-preset').onclick=v21Preset;
$('v21-sheet').onclick=async()=>{try{await v21ShotSheet();}catch(e){notify('V21 PNG: '+e.message);}};
$('v21-report').onclick=()=>download('V21_VISUAL_LOOKDEV_RU.txt',
  new Blob([v21VisualPlan()],{type:'text/plain;charset=utf-8'}));
