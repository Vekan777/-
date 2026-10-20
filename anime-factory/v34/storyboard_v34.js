/* AI ANIME FACTORY V34 — STORYBOARD & SHOT CONTINUITY.
   Shot planning is deterministic and non-destructive. Scene tracks and
   historical combat/plot outcomes always remain authoritative. */
const V34_SHOTS={wide:1,medium:1.115,close:1.225};
const V34_TIMES=[.12,.5,.88];
function v34Of(s){
 if(!s.storyboardV34||typeof s.storyboardV34!=='object'||Array.isArray(s.storyboardV34))
  s.storyboardV34={};
 const o=s.storyboardV34;
 if(!Array.isArray(o.shots)||o.shots.length!==3)o.shots=['wide','medium','close'];
 o.shots=o.shots.map(v=>Object.hasOwn(V34_SHOTS,v)?v:'medium');
 for(const [k,v] of [['strength',76],['tracking',52],['smoothness',82]])
  o[k]=Number.isFinite(Number(o[k]))?clamp(Number(o[k]),0,100):v;
 if(!['center','hero','partner'].includes(o.focus))o.focus='center';
 if(!['left','right','neutral'].includes(o.axis))o.axis='neutral';
 o.enabled=o.enabled!==false;
 return o;
}
function v34Ease(x){const t=clamp(x,0,1);return t*t*(3-2*t);}
function v34ShotBlend(s,t){
 const a=v34Of(s),p=clamp(t/Math.max(.01,Number(s.duration)||1),0,1);
 if(p<=V34_TIMES[0])return V34_SHOTS[a.shots[0]];
 for(let i=1;i<3;i++){
  if(p<=V34_TIMES[i]){
   const raw=(p-V34_TIMES[i-1])/(V34_TIMES[i]-V34_TIMES[i-1]);
   const f=(1-a.smoothness/100)*raw+(a.smoothness/100)*v34Ease(raw);
   return V34_SHOTS[a.shots[i-1]]*(1-f)+V34_SHOTS[a.shots[i]]*f;
  }
 }
 return V34_SHOTS[a.shots[2]];
}
function v34ShotName(s,t){
 const o=v34Of(s),p=clamp(t/Math.max(.01,Number(s.duration)||1),0,1);
 return o.shots[p<.30?0:p<.69?1:2];
}
function v34Camera(s,t){
 const base={zoom:1,dx:0,dy:0,shot:'До V34'};
 const a=v34Of(s);if(!a.enabled)return base;
 const p=clamp(t/Math.max(.01,Number(s.duration)||1),0,1);
 const amount=a.strength/100,tracking=a.tracking/100;
 const zoom=clamp(1+(v34ShotBlend(s,t)-1)*amount,1,1.23);
 let focusX=.5;
 if(a.focus!=='center'&&s.tracks?.[a.focus]){
  try{const track=interpolate(s.tracks[a.focus],p);
   if(Number.isFinite(track.x))focusX=clamp(track.x,.12,.88);
  }catch(e){focusX=.5;}
 }
 // The subject's original V8 positional track controls subtle screen
 // centring. We never flip image/axis or rewrite the track.
 const dx=clamp((focusX-.5)*.17*tracking*amount,-.07,.07);
 const dy=clamp(-.012*(zoom-1)/.23*amount,-.014,0);
 return {zoom,dx,dy,shot:v34ShotName(s,t)};
}
function v34All(){
 if(!P)return [];
 return P.episodes.flatMap((e,i)=>e.scenes.map((s,j)=>({e,i,j,s})));
}
function v34Selected(){
 if(!P)return null;
 const [i,j]=String($('v34-scene').value||epIndex+':'+scIndex).split(':').map(Number);
 return P.episodes[i]?.scenes[j]||scene();
}
function v34Review(){
 if(!P)return [];
 const warnings=[];
 for(const e of P.episodes){
  const sc=Array.isArray(e.scenes)?e.scenes:[];
  for(let j=1;j<sc.length;j++){
   const before=sc[j-1],after=sc[j];
   const a=v34Of(before),b=v34Of(after);
   if(!a.enabled||!b.enabled)continue;
   const end=v34Camera(before,before.duration*.999);
   const beginning=v34Camera(after,after.duration*.001);
   const gap=Math.abs(end.zoom-beginning.zoom);
   if(gap>.16)warnings.push('Серия '+e.number+', сцены '+j+'/'+(j+1)+
    ': скачок масштаба между кадрами '+gap.toFixed(2)+'.');
   if(a.axis!=='neutral'&&b.axis!=='neutral'&&a.axis!==b.axis)
    warnings.push('Серия '+e.number+', сцены '+j+'/'+(j+1)+
     ': изменён монтажный ориентир («ось 180°»). Проверьте экранные направления.');
   if(a.focus!==b.focus&&a.shots[2]==='close'&&b.shots[0]==='close')
    warnings.push('Серия '+e.number+', сцены '+j+'/'+(j+1)+
      ': резко сменился объект двух соседних крупных планов.');
  }
 }
 return warnings;
}
function v34StoryboardText(){
 if(!P)return '';
 const rows=['AI ANIME FACTORY V34 — РАСКАДРОВКА И СОГЛАСОВАННОСТЬ ПЛАНОВ',P.title,''];
 for(const {e,i,j,s} of v34All()){
  const o=v34Of(s);
  rows.push('Серия '+e.number+' · сцена '+(j+1)+' · '+s.title+
   ' · длительность '+Number(s.duration||0).toFixed(2)+' с',
   'Ось '+o.axis+' · герой кадра '+o.focus+' · сила '+o.strength+
    '% · трекинг '+o.tracking+'% · плавность '+o.smoothness+'%');
  for(let k=0;k<3;k++){
   const camera=v34Camera(s,s.duration*V34_TIMES[k]);
   rows.push(Math.round(V34_TIMES[k]*100)+'%: '+o.shots[k]+
    ' · ×'+camera.zoom.toFixed(3)+' · кадр '+camera.dx.toFixed(3));
  }
  rows.push('');
 }
 const issues=v34Review();
 rows.push('ПРОВЕРКА СТЫКОВ СЦЕН:',...(issues.length?issues:['Автоматических замечаний не обнаружено.']),
  '','Анализ проверяет параметры камеры/монтажа, а не гарантирует художественную выразительность.');
 return rows.join('\n');
}
function v34Show(){
 if(!P)return;
 const selector=$('v34-scene'),old=selector.value;
 const all=v34All();
 selector.innerHTML=all.map(({e,i,j,s})=>
  '<option value="'+i+':'+j+'">Серия '+e.number+
  ', сцена '+(j+1)+' — '+escapeHTML(s.title)+'</option>').join('');
 const now=epIndex+':'+scIndex;
 selector.value=all.some(x=>x.i+':'+x.j===old)?old:now;
 if(!selector.value&&all.length)selector.value=all[0].i+':'+all[0].j;
 const s=v34Selected();if(!s)return;
 const a=v34Of(s);
 $('v34-enabled').checked=a.enabled;
 $('v34-focus').value=a.focus;$('v34-axis').value=a.axis;
 for(const k of ['strength','tracking','smoothness']){
  $('v34-'+k).value=a[k];$('v34-'+k+'-n').textContent=a[k];
 }
 v34KeySelection();v34Preview();
}
function v34KeySelection(){
 const s=v34Selected();if(!s)return;
 const n=clamp(Number($('v34-beat').value)||0,0,2);
 $('v34-shot').value=v34Of(s).shots[n];
 $('v34-position').value=Math.round(V34_TIMES[n]*100);
}
function v34Preview(){
 const s=v34Selected();if(!s)return;
 const t=s.duration*(Number($('v34-position').value)||0)/100;
 const a=v34Of(s),was=a.enabled;
 try{
  a.enabled=false;drawScene($('v34-before'),s,t,false);
  a.enabled=was;drawScene($('v34-after'),s,t,false);
 }finally{a.enabled=was;}
 const camera=v34Camera(s,t);
 $('v34-caption').textContent=s.title+' · '+t.toFixed(2)+' с · '+
  camera.shot+' · ×'+camera.zoom.toFixed(2);
}
function v34Save(){
 const s=v34Selected();if(!s)return;
 const a=v34Of(s);a.enabled=$('v34-enabled').checked;
 a.focus=$('v34-focus').value;a.axis=$('v34-axis').value;
 for(const k of ['strength','tracking','smoothness'])
  a[k]=clamp(Number($('v34-'+k).value)||0,0,100);
 const n=clamp(Number($('v34-beat').value)||0,0,2);
 a.shots[n]=$('v34-shot').value;
 save();v34Show();notify('V34: раскадровка сохранена без изменения сюжета.');
}
function v34Preset(){
 const s=v34Selected();if(!s)return;
 Object.assign(v34Of(s),{enabled:true,focus:'center',axis:'neutral',
  shots:['wide','medium','close'],strength:81,tracking:56,smoothness:86});
 save();v34Show();notify('V34: профиль общий → средний → крупный применён.');
}
function v34RunReview(){
 const issues=v34Review();
 $('v34-report').textContent=issues.length?issues.join('\n'):
  'Эвристических проблем с крупностью и экранной осью между сценами не найдено.';
}
async function v34Sheet(){
 await preloadArtwork();
 const a=v34All(),s=v34Selected();
 if(!s||!a.length)return;
 const index=a.findIndex(x=>x.s===s);
 const prev=a[index-1]?.e===a[index]?.e?a[index-1].s:null;
 const next=a[index+1]?.e===a[index]?.e?a[index+1].s:null;
 const frames=[
  {s:prev||s,p:prev ? .94 : .12,title:prev?'Предыдущая / конец':'Текущая / начало'},
  {s,p:.12,title:'Текущая / общий'},
  {s,p:.50,title:'Текущая / средний'},
  {s,p:.88,title:'Текущая / крупный'},
  {s:next||s,p:next ? .06 : .88,title:next?'Следующая / начало':'Текущая / конец'},
  {s,p:.99,title:'Текущая / финал'}
 ];
 const frame=document.createElement('canvas'),board=document.createElement('canvas');
 frame.width=640;frame.height=360;board.width=1920;board.height=720;
 const g=board.getContext('2d');
 for(const [i,item] of frames.entries()){
  drawScene(frame,item.s,Math.max(0,item.s.duration*item.p),false);
  const x=i%3*640,y=Math.floor(i/3)*360;
  g.drawImage(frame,x,y);
  g.fillStyle='rgba(2,9,22,.86)';g.fillRect(x+8,y+8,290,28);
  g.fillStyle='#f3e6ce';g.font='bold 14px Arial';
  g.fillText('V34 '+item.title,x+15,y+27);
 }
 download('V34_STORYBOARD_'+slug(s.title)+'.png',await blobPNG(board));
 notify('V34: контакт-лист смежных планов экспортирован.');
}
$('v34-scene').onchange=v34Show;
$('v34-beat').onchange=()=>{v34KeySelection();v34Preview();};
$('v34-position').oninput=v34Preview;
$('v34-save').onclick=v34Save;$('v34-preset').onclick=v34Preset;
$('v34-audit').onclick=v34RunReview;
$('v34-plan').onclick=()=>download('V34_SHOT_CONTINUITY_RU.txt',
 new Blob([v34StoryboardText()],{type:'text/plain;charset=utf-8'}));
$('v34-sheet').onclick=async()=>{try{await v34Sheet();}catch(e){notify('V34 PNG: '+e.message);}};
for(const k of ['strength','tracking','smoothness'])
 $('v34-'+k).oninput=e=>{$('v34-'+k+'-n').textContent=e.target.value;};
