/* V32 KEYFRAME READABILITY — real procedural rig edits (V19–V31 preserved).
   Four independently tunable authored key poses per scene. Their smooth
   interpolation controls silhouette, wrist separation, head expression
   and planted feet. Existing fight outcomes are never changed.
*/
function v32Of(s){
 if(!s.readabilityV32||typeof s.readabilityV32!=='object'||Array.isArray(s.readabilityV32))s.readabilityV32={};
 const o=s.readabilityV32;
 for(const [k,v] of [['silhouette',77],['gesture',75],['expression',70],['hold',70],['anticipation',73]]){
  o[k]=Number.isFinite(Number(o[k]))?clamp(Number(o[k]),0,100):v;
 }
 const defaults=[48,80,100,64];
 if(!Array.isArray(o.keyframes)||o.keyframes.length!==4)o.keyframes=defaults.slice();
 o.keyframes=o.keyframes.map((v,i)=>Number.isFinite(Number(v))?clamp(Number(v),0,100):defaults[i]);
 if(!['readable','subtle','action'].includes(o.style))o.style='readable';
 o.enabled=o.enabled!==false;
 return o;
}
const V32_KEY_TIMES=[.12,.38,.62,.86];
function v32Smooth(v){const x=clamp(v,0,1);return x*x*(3-2*x);}
function v32Cue(s,t){
 const o=v32Of(s),p=clamp(t/Math.max(.01,Number(s.duration)||1),0,1);
 if(p<=V32_KEY_TIMES[0])return o.keyframes[0]/100;
 for(let i=1;i<4;i++){
  if(p<=V32_KEY_TIMES[i]){
   const w=v32Smooth((p-V32_KEY_TIMES[i-1])/(V32_KEY_TIMES[i]-V32_KEY_TIMES[i-1]));
   return (o.keyframes[i-1]*(1-w)+o.keyframes[i]*w)/100;
  }
 }
 return o.keyframes[3]/100;
}
function v32Pose(s,t,role){
 const zero={lean:0,rootX:0,rootY:0,elbowLX:0,elbowLY:0,
  elbowRX:0,elbowRY:0,handLX:0,handLY:0,handRX:0,handRY:0,
  stance:0,headX:0,headTilt:0,eye:0,brow:0,smile:0};
 const o=v32Of(s);if(!o.enabled)return zero;
 const cue=v32Cue(s,t);
 const silhouette=o.silhouette/100,gesture=o.gesture/100,
  expression=o.expression/100,anticipation=o.anticipation/100,
  hold=o.hold/100;
 const style=o.style==='action'?1.2:o.style==='subtle'?.50:1;
 const beat=s.kind==='fight'?v29Beat(s,t):null;
 const attacking=beat?.active&&beat.actor===role;
 const defending=beat?.active&&beat.actor!==role;
 const release=attacking?beat.release:0;
 const preparation=attacking?beat.anticipation:0;
 const reaction=defending?Math.max(beat.contact,beat.guard,beat.dodge):0;
 // Slightly sustained key poses remain smooth over the whole shot.
 const key=cue*(.40+.60*hold)*style;
 const drive=clamp(.42+release*.8+preparation*.35+reaction*.6,.3,1.4);
 const force=key*drive;
 const sign=role==='hero'?1:-1;
 const open=force*silhouette;
 const motion=force*gesture;
 return {
  lean:clamp((release*.052-preparation*.023-reaction*.030)*anticipation*key,-.09,.09),
  rootX:sign*(release*3.1-preparation*.7-reaction*1.6)*motion,
  rootY:(-release*1.7+reaction*1.6)*motion,
  elbowLX:-9*open,elbowLY:-3.8*open,
  elbowRX:10*open+release*5*motion,elbowRY:-5*open,
  handLX:-13*open-preparation*3*motion,handLY:-6*motion,
  handRX:15*open+release*11*motion,handRY:-8*motion-release*7*motion,
  stance:7.5*open,headX:(-preparation+reaction)*1.6*motion,
  headTilt:clamp((preparation*.028-release*.034+reaction*.035)*key,-.06,.06),
  eye:clamp((.10+release*.11+reaction*.15)*key*expression,0,.32),
  brow:clamp((release*.16+preparation*.21+reaction*.25)*key*expression,0,.5),
  smile:-clamp((release*.04+reaction*.13)*key*expression,0,.30)
 };
}
function v32Foot(s,t,role,side,point){
 const o=v32Of(s);if(!o.enabled)return point;
 const pose=v32Pose(s,t,role),dir=side==='left'?-1:1;
 const ground=v29Actor(s,t,role).footLock;
 const stable=clamp(o.hold/100*(.4+ground*.6),0,1);
 // An open planted stance, without replacing V24 or V29 limb kinematics.
 return [point[0]+dir*pose.stance,point[1]+
  Math.max(0,4-point[1])*stable*.48];
}
function v32Face(s,t,role,f){
 const o=v32Of(s);if(!o.enabled)return f;
 const p=v32Pose(s,t,role);
 return {...f,eye:clamp((Number(f.eye)||1)*(1+p.eye),.22,1.65),
  brow:clamp((Number(f.brow)||0)+p.brow,-1.6,1.6),
  smile:clamp((Number(f.smile)||0)+p.smile,-1.4,1.4)};
}
function v32SceneList(){
 const items=[];
 P.episodes.forEach((e,i)=>e.scenes.forEach((s,j)=>
  items.push({i,j,number:e.number,title:s.title})));
 return items;
}
function v32Selected(){
 if(!P)return null;
 const [i,j]=String($('v32-scene').value||epIndex+':'+scIndex).split(':').map(Number);
 return P.episodes[i]?.scenes[j]||scene();
}
function v32Show(){
 if(!P)return;
 const sel=$('v32-scene'),old=sel.value,items=v32SceneList();
 sel.innerHTML=items.map(x=>'<option value="'+x.i+':'+x.j+'">Серия '+
  x.number+' — '+escapeHTML(x.title)+'</option>').join('');
 const current=epIndex+':'+scIndex;
 sel.value=items.some(x=>x.i+':'+x.j===old)?old:current;
 if(!sel.value&&items.length)sel.value=items[0].i+':'+items[0].j;
 const o=v32Of(v32Selected());
 $('v32-enabled').checked=o.enabled;$('v32-style').value=o.style;
 for(const k of ['silhouette','gesture','expression','hold','anticipation']){
  $('v32-'+k).value=o[k];$('v32-'+k+'-n').textContent=o[k];
 }
 v32KeySelection();v32Preview();
}
function v32KeySelection(){
 const s=v32Selected();if(!s)return;
 const index=clamp(Number($('v32-keyframe').value)||0,0,3);
 const value=v32Of(s).keyframes[index];
 $('v32-key-value').value=value;
 $('v32-key-value-n').textContent=String(value);
 $('v32-position').value=Math.round(V32_KEY_TIMES[index]*100);
}
function v32Preview(){
 const s=v32Selected();if(!s)return;
 const t=s.duration*(Number($('v32-position').value)||0)/100;
 const o=v32Of(s),before=o.enabled;
 try{
  o.enabled=false;drawScene($('v32-before'),s,t,false);
  o.enabled=before;drawScene($('v32-after'),s,t,false);
 }finally{o.enabled=before;}
 $('v32-caption').textContent=s.title+' · '+t.toFixed(2)+
  ' с · сила ключевого положения '+Math.round(v32Cue(s,t)*100)+'%';
}
function v32Save(){
 const s=v32Selected();if(!s)return;
 const o=v32Of(s);o.enabled=$('v32-enabled').checked;
 o.style=$('v32-style').value;
 for(const k of ['silhouette','gesture','expression','hold','anticipation'])
  o[k]=clamp(Number($('v32-'+k).value)||0,0,100);
 const index=clamp(Number($('v32-keyframe').value)||0,0,3);
 o.keyframes[index]=clamp(Number($('v32-key-value').value)||0,0,100);
 save();v32Show();notify('V32: поза, силуэт и ключевые моменты сохранены.');
}
function v32Preset(){
 const s=v32Selected();if(!s)return;
 Object.assign(v32Of(s),{enabled:true,style:'readable',silhouette:86,
  gesture:81,expression:79,hold:77,anticipation:83,
  keyframes:[53,85,100,69]});
 save();v32Show();notify('V32: выразительные четыре ключевые позы установлены.');
}
function v32Quality(){
 const s=v32Selected();if(!s)return [];
 const o=v32Of(s),out=[];
 if(o.silhouette<18)out.push('Малая разводка рук: силуэт может читаться хуже.');
 if(o.expression<20)out.push('Низкая выразительность мимики процедурного лица.');
 if(o.keyframes.every(v=>Math.abs(v-o.keyframes[0])<3))
  out.push('Все четыре ключевые позы почти одинаковые; нет выделенного момента.');
 if(o.gesture>92&&o.hold<16)out.push('Резкие движения при слабой фиксации опорной фазы.');
 if(!out.length)out.push('Основные параметры силуэта и ключевых поз согласованы.');
 return out;
}
function v32Plan(){
 if(!P)return '';
 const lines=['AI ANIME FACTORY V32 — КЛЮЧЕВЫЕ ПОЗЫ И СИЛУЭТЫ',P.title,''];
 P.episodes.forEach(e=>e.scenes.forEach(s=>{
  const o=v32Of(s);
  lines.push('Серия '+e.number+' · '+s.title+' ('+s.kind+')',
   'стиль '+o.style+'; силуэт '+o.silhouette+'; жест '+o.gesture+
   '; мимика '+o.expression+'; фиксация '+o.hold+
   '; предварительное движение '+o.anticipation);
  lines.push('ключевые кадры: '+o.keyframes.map((v,i)=>
   Math.round(V32_KEY_TIMES[i]*100)+'%='+v).join(' · '),'');
 }));
 lines.push('Изменения относятся к процедурному ригу. Авторские PNG не перерисовываются.');
 return lines.join('\n');
}
async function v32Sheet(){
 await preloadArtwork();
 const s=v32Selected(),board=document.createElement('canvas'),
  frame=document.createElement('canvas');
 board.width=1280;board.height=720;
 frame.width=640;frame.height=360;
 const g=board.getContext('2d');
 for(const [i,phase] of V32_KEY_TIMES.entries()){
  drawScene(frame,s,s.duration*phase,false);
  const x=i%2*640,y=Math.floor(i/2)*360;
  g.drawImage(frame,x,y);
  g.fillStyle='rgba(4,10,23,.82)';g.fillRect(x+9,y+9,205,28);
  g.fillStyle='#f4e6c8';g.font='bold 14px Arial';
  g.fillText('V32 ПОЗА '+(i+1)+' · '+Math.round(phase*100)+'%',x+16,y+28);
 }
 download('V32_FOUR_KEY_POSES_'+slug(s.title)+'.png',await blobPNG(board));
 notify('V32: четыре ключевые позы экспортированы PNG.');
}
$('v32-scene').onchange=()=>v32Show();
$('v32-keyframe').onchange=()=>{v32KeySelection();v32Preview();};
$('v32-position').oninput=v32Preview;
$('v32-save').onclick=v32Save;
$('v32-preset').onclick=v32Preset;
$('v32-sheet').onclick=async()=>{try{await v32Sheet();}catch(e){notify('V32 PNG: '+e.message);}};
$('v32-plan').onclick=()=>download('V32_KEYFRAME_PLAN_RU.txt',
 new Blob([v32Plan()],{type:'text/plain;charset=utf-8'}));
$('v32-qa').onclick=()=>{$('v32-report').textContent=v32Quality().join('\n');};
$('v32-key-value').oninput=e=>{$('v32-key-value-n').textContent=e.target.value;};
for(const k of ['silhouette','gesture','expression','hold','anticipation'])
 $('v32-'+k).oninput=e=>{$('v32-'+k+'-n').textContent=e.target.value;};
