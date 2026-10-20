/* AI Anime Factory V26 - Cinematic Combat direction.
   Camera and scene overlays only. All story, combat and original art stay intact.
   Time-only sampling makes preview, render and PNG export reproducible.
*/
function v26Options(s){
 if(!s.cinemaV26||typeof s.cinemaV26!=='object'||Array.isArray(s.cinemaV26))s.cinemaV26={};
 const a=s.cinemaV26;
 for(const [k,d] of [['intensity',72],['tracking',74],['impactFocus',68],['letterbox',62],['transitions',48]]){
  a[k]=Number.isFinite(Number(a[k]))?clamp(Number(a[k]),0,100):d;
 }
 if(!['wide','dynamic','close','subtle'].includes(a.style))a.style='dynamic';
 a.enabled=a.enabled!==false;
 return a;
}
function v26Ease(v){const x=clamp(v,0,1);return x*x*(3-2*x);}
function v26Window(v,center,width){
 const a=Math.abs(v-center)/Math.max(.002,width);return v26Ease(1-a);
}
function v26Camera(s,t){
 const none={zoom:1,dx:0,dy:0,shot:'V25 · без V26'};
 const a=v26Options(s);
 if(!a.enabled||s.kind!=='fight')return none;
 const p=clamp(t/Math.max(s.duration,.01),0,1);
 const amp=a.intensity/100*(a.style==='subtle'?.5:1);
 const tracking=a.tracking/100,focus=a.impactFocus/100;
 const contact=v25Contact(s,t);
 const heroAttacks=contact.actor==='hero',partnerAttacks=contact.actor==='partner';
 const lead=heroAttacks?-.025:partnerAttacks?.025:0;
 // Three compact camera beats, softened around cut points to prevent flashes.
 const opening=1-v26Ease((p-.20)/.15);
 const middle=v26Ease((p-.22)/.16)*(1-v26Ease((p-.58)/.14));
 const ending=v26Ease((p-.59)/.15);
 const mode=a.style==='wide'?.56:a.style==='close'?1.40:1;
 const focusPulse=clamp(Math.max(contact.contact,contact.release*.6),0,1);
 const push=(.045*middle+.09*ending+.13*focusPulse*focus)*amp*mode;
 const zoom=clamp(1+push,1,1.28);
 const dx=clamp((Math.sin(p*Math.PI*1.7)*.017*tracking+
       lead*focusPulse*focus+.014*(middle-ending))*amp*mode,-.08,.08);
 const dy=clamp((-.011*middle-.022*ending-.012*focusPulse*focus)*amp*mode,-.045,.01);
 const shot=opening>.65?'Общий план':ending>.65?'Реакция / крупный план':'Средний план / сближение';
 return {zoom,dx,dy,shot};
}
function v26FinishFrame(g,w,h,s,t){
 const a=v26Options(s);
 if(!a.enabled||s.kind!=='fight')return;
 const p=clamp(t/Math.max(.01,s.duration),0,1);
 const intensity=a.intensity/100;
 g.save();
 // Letterbox is an overlay inside the final frame, not a destructive
 // crop of the user's source images or PNG/cutout.
 const bar=Math.round(h*.045*(a.letterbox/100)*intensity);
 if(bar>0){
  g.fillStyle='rgba(2,7,16,.94)';
  g.fillRect(0,0,w,bar);
  g.fillRect(0,h-bar,w,bar);
 }
 const trans=a.transitions/100;
 // Short fade on scene boundaries with an optional very brief soft
 // montage beat. Preserve visibility throughout the actual strike.
 const edge=Math.max(v26Window(p,0,.036),v26Window(p,1,.042));
 const middle=v26Window(p,.36,.012)*.28+v26Window(p,.72,.012)*.22;
 const fade=clamp((edge*.44+middle)*trans*intensity,0,.46);
 if(fade>.002){
  g.fillStyle='rgba(3,8,19,'+fade.toFixed(4)+')';
  g.fillRect(0,0,w,h);
 }
 g.restore();
}
function v26QA(){
 if(!P)return [];
 const errors=[];
 for(const ep of P.episodes)for(const s of ep.scenes){
  if(s.kind!=='fight')continue;
  const a=v26Options(s);if(!a.enabled)continue;
  if(a.impactFocus>90&&a.tracking>95)errors.push(
   'Серия '+ep.number+', '+s.title+': сильное слежение и крупность кадра — проверьте резкость монтажа.');
  if(a.transitions>90)errors.push(
   'Серия '+ep.number+', '+s.title+': длинные затемнения могут скрыть часть боя.');
 }
 return errors;
}
function v26Plan(){
 if(!P)return '';
 const lines=['AI ANIME FACTORY V26 — РЕЖИССУРА БОЕВЫХ СЦЕН',P.title,''];
 for(const ep of P.episodes)for(const s of ep.scenes){
  if(s.kind!=='fight')continue;
  const a=v26Options(s);
  lines.push('СЕРИЯ '+ep.number+' — '+s.title,
   'Стиль '+a.style+'; сила '+a.intensity+'; трекинг '+a.tracking+
   '; акцент '+a.impactFocus+'; формат '+a.letterbox+
   '; монтаж '+a.transitions+'; включено '+a.enabled);
  for(const p of [.12,.32,.51,.68,.88]){
   const cam=v26Camera(s,s.duration*p);
   lines.push(Math.round(p*100)+'%: '+cam.shot+
    ', масштаб '+cam.zoom.toFixed(2)+
    ', смещение '+cam.dx.toFixed(3)+'/'+cam.dy.toFixed(3));
  }
  lines.push('');
 }
 return lines.join('\n');
}
function v26FightScenes(){
 const result=[];
 P.episodes.forEach((ep,i)=>ep.scenes.forEach((s,j)=>{
  if(s.kind==='fight')result.push({i,j,n:ep.number,title:s.title});
 }));
 return result;
}
function v26Scene(){
 const v=$('v26-scene').value;
 if(!v)return null;
 const [i,j]=v.split(':').map(Number);
 return P?.episodes[i]?.scenes[j]||null;
}
function v26Show(){
 if(!P)return;
 const all=v26FightScenes(),el=$('v26-scene');
 const previous=el.value;
 el.innerHTML=all.map(v=>'<option value="'+v.i+':'+v.j+'">Серия '+
   v.n+' — '+escapeHTML(v.title)+'</option>').join('');
 if(!all.length){
  $('v26-status').textContent='Нет боевых сцен. Создайте боевую сцену в сценарии.';
  $('v26-qa').textContent='Нет боевых сцен для монтажа.';
  for(const id of ['v26-before','v26-after'])
   $(id).getContext('2d').clearRect(0,0,640,360);
  return;
 }
 const active=epIndex+':'+scIndex;
 el.value=all.some(x=>x.i+':'+x.j===active)?active:
   all.some(x=>x.i+':'+x.j===previous)?previous:all[0].i+':'+all[0].j;
 const a=v26Options(v26Scene());
 $('v26-enabled').checked=a.enabled;$('v26-style').value=a.style;
 for(const key of ['intensity','tracking','impactFocus','letterbox','transitions']){
  $('v26-'+key).value=a[key];
  $('v26-'+key+'-n').textContent=String(a[key]);
 }
 $('v26-qa').textContent=v26QA().slice(0,30).join('\n')||
  'Камера: критических конфликтов параметров не обнаружено.';
 v26Preview();
}
function v26Preview(){
 const s=v26Scene();if(!s)return;
 const a=v26Options(s),t=s.duration*(Number($('v26-position').value)||0)/100;
 const was=a.enabled;
 try{
  a.enabled=false;
  drawScene($('v26-before'),s,t,false);
  a.enabled=was;
  drawScene($('v26-after'),s,t,false);
 }finally{a.enabled=was;}
 const cam=v26Camera(s,t);
 $('v26-status').textContent=s.title+' · '+t.toFixed(2)+
   ' с · '+cam.shot+' · ×'+cam.zoom.toFixed(2);
}
function v26Save(){
 const s=v26Scene();if(!s)return;
 const a=v26Options(s);
 a.enabled=$('v26-enabled').checked;
 a.style=$('v26-style').value;
 for(const key of ['intensity','tracking','impactFocus','letterbox','transitions'])
  a[key]=clamp(Number($('v26-'+key).value)||0,0,100);
 save();v26Show();notify('V26: камера и монтаж сохранены.');
}
function v26Preset(){
 const s=v26Scene();if(!s)return;
 Object.assign(v26Options(s),{enabled:true,style:'dynamic',intensity:85,
  tracking:78,impactFocus:82,letterbox:67,transitions:34});
 save();v26Show();notify('V26: кинематографичный профиль применён.');
}
async function v26Sheet(){
 await preloadArtwork();
 const s=v26Scene();if(!s)return;
 const out=document.createElement('canvas'),scratch=document.createElement('canvas');
 out.width=1280;out.height=720;scratch.width=640;scratch.height=360;
 const g=out.getContext('2d');
 for(const [i,pct] of [.13,.35,.60,.86].entries()){
  drawScene(scratch,s,s.duration*pct,false);
  const x=i%2*640,y=Math.floor(i/2)*360;
  g.drawImage(scratch,x,y);
  g.fillStyle='rgba(4,12,26,.85)';g.fillRect(x+8,y+9,220,28);
  g.fillStyle='#e7ddc9';g.font='bold 14px Arial';
  g.fillText('V26 '+Math.round(pct*100)+'% '+v26Camera(s,s.duration*pct).shot,
    x+14,y+28,208);
 }
 download('V26_SHOT_BOARD_'+slug(s.title)+'.png',await blobPNG(out));
 notify('V26: 4 режиссёрских кадра сохранены.');
}
$('v26-scene').onchange=e=>{
 const [i,j]=e.target.value.split(':').map(Number);
 selectScene(i,j);show('cinematic-v26');
};
$('v26-position').oninput=v26Preview;
$('v26-style').onchange=()=>{$('v26-status').textContent='Нажмите «Сохранить» для применения стиля.';};
$('v26-enabled').onchange=()=>{$('v26-status').textContent='Нажмите «Сохранить» для применения изменений.';};
$('v26-save').onclick=v26Save;$('v26-preset').onclick=v26Preset;
$('v26-sheet').onclick=async()=>{try{await v26Sheet();}catch(e){notify('V26 PNG: '+e.message);}};
$('v26-plan').onclick=()=>download('V26_SHOT_LIST_RU.txt',
 new Blob([v26Plan()],{type:'text/plain;charset=utf-8'}));
for(const k of ['intensity','tracking','impactFocus','letterbox','transitions'])
 $('v26-'+k).oninput=e=>{$('v26-'+k+'-n').textContent=e.target.value;};
