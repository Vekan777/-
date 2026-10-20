/* AI ANIME FACTORY V33 — ACTING AND EXPRESSIONS
 * Timed acting cues are deterministic and additive to V19–V32.
 * Facial direction, brows, eyes, gesture and breathing are applied to the
 * procedural character rig itself, not painted over imported artwork.
 */
function v33Of(s){
 if(!s.actingV33||typeof s.actingV33!=='object'||Array.isArray(s.actingV33))s.actingV33={};
 const o=s.actingV33;
 for(const [k,d] of [['gaze',72],['emotion',79],['gesture',73],
                      ['breathing',51],['transitions',76]]){
  o[k]=Number.isFinite(Number(o[k]))?clamp(Number(o[k]),0,100):d;
 }
 if(!['cinematic','subtle','expressive'].includes(o.style))o.style='cinematic';
 o.enabled=o.enabled!==false;
 return o;
}
function v33Ease(x){const t=clamp(x,0,1);return t*t*(3-2*t);}
function v33Mood(s,t,role){
 // Existing acting/canon modules supply emotions; do not invent a new plot.
 const m=v22Mood(s,role,t,qualityMood(s,role));
 return typeof m==='string'?m:'determined';
}
function v33Signal(s,t,role){
 const o=v33Of(s),duration=Math.max(.1,Number(s.duration)||1);
 const phase=clamp(t/duration,0,1),key=v32Cue(s,t);
 if(!o.enabled)return {active:false,key:0,talk:0,beat:0,
   mood:'',direction:0,soft:0,energy:0};
 const ease=o.transitions/100;
 const body=v33Ease(Math.min(phase/.08,(1-phase)/.09,1));
 const soft=.25+.75*ease;
 // Time from earlier V32 keyframes, without discontinuous beat switching.
 const beat=key*body*soft;
 const line=typeof activeLine==='function'?activeLine(s,t):null;
 const dialogue=!!line&&(s.kind!=='fight');
 const talk=dialogue?(Math.sin(t*4.4)*.5+.5)*beat:0;
 const mood=v33Mood(s,t,role);
 const style=o.style==='expressive'?1.30:o.style==='subtle'?.46:1;
 const energy=clamp((.47+.53*key)*style,0,1.4);
 // Slow eye target switch per pose, blended through sinusoidal saccade.
 // Opposing characters look inward by default, not at camera constantly.
 const sign=role==='hero'?1:-1;
 const direction=sign*clamp(.46+.23*Math.sin(t*.91+sign*.7),.15,.84);
 return {active:true,key:beat,talk,beat,mood,direction,soft,energy};
}
function v33Act(s,t,role){
 const z={rootY:0,rootX:0,headTilt:0,headX:0,
   elbowLX:0,elbowLY:0,elbowRX:0,elbowRY:0,
   handLX:0,handLY:0,handRX:0,handRY:0};
 const o=v33Of(s),v=v33Signal(s,t,role);
 if(!v.active)return z;
 const amp=v.beat*v.energy,gesture=o.gesture/100,breath=o.breathing/100;
 const emot=o.emotion/100,m=v.mood;
 const sorrow=m==='sad'||m==='gentle',tense=m==='angry'||m==='determined';
 const rise=Math.sin(t*2.1+(role==='hero'?0:1.1))*breath*1.35;
 const talk=v.talk*gesture;
 return {
  rootX:(role==='hero'?1:-1)*talk*1.3,
  rootY:rise*.7+talk*.45,
  headTilt:clamp(((sorrow?.026:tense?-.031:.009)*emot+
    Math.sin(t*1.1)*.009)*amp,-.08,.08),
  headX:(v.direction*.8+Math.sin(t*1.48)*.6)*amp*emot,
  elbowLX:-2.8*gesture*amp,elbowLY:-rise*.20,
  elbowRX:3.3*gesture*amp,elbowRY:-rise*.18,
  handLX:-6.2*gesture*amp-talk*2.9,handLY:-rise*.32-talk*3.0,
  handRX:6.9*gesture*amp+talk*4.7,
  handRY:-rise*.38-talk*6.0
 };
}
function v33Face(s,t,role,f){
 const o=v33Of(s),v=v33Signal(s,t,role);
 if(!v.active)return f;
 const emot=o.emotion/100,focus=o.gaze/100,amp=v.beat*v.energy;
 const sorrow=v.mood==='sad',shocked=v.mood==='shocked';
 const warm=v.mood==='gentle';
 const brow=(shocked?.35:sorrow?-.18:warm?-.10:.18)*emot*amp;
 const eye=shocked?.17*emot*amp:sorrow?-.12*emot*amp:.06*emot*amp;
 const smile=warm?.21*emot*amp:sorrow?-.15*emot*amp:0;
 const saccade=Math.sin(t*1.21+(role==='hero'?1.1:2.1))*.12;
 return {...f,
  gaze:clamp((Number(f.gaze)||0)*.48+
       (v.direction+saccade)*focus*amp,-1,1),
  brow:clamp((Number(f.brow)||0)+brow,-1.6,1.6),
  eye:clamp((Number(f.eye)||1)+eye,.15,1.65),
  smile:clamp((Number(f.smile)||0)+smile,-1.4,1.4)};
}
function v33Selected(){
 if(!P)return null;
 const raw=String($('v33-scene').value||epIndex+':'+scIndex);
 const [i,j]=raw.split(':').map(Number);
 return P.episodes[i]?.scenes[j]||scene();
}
function v33Show(){
 if(!P)return;
 const sel=$('v33-scene'),old=sel.value;
 const all=P.episodes.flatMap((e,i)=>e.scenes.map((s,j)=>({e,i,j,s})));
 sel.innerHTML=all.map(x=>'<option value="'+x.i+':'+x.j+'">Серия '+
  x.e.number+' — '+escapeHTML(x.s.title)+'</option>').join('');
 const choice=all.some(x=>x.i+':'+x.j===old)?old:epIndex+':'+scIndex;
 sel.value=choice;
 const s=v33Selected(),o=v33Of(s);
 $('v33-enabled').checked=o.enabled;
 $('v33-style').value=o.style;
 for(const k of ['gaze','emotion','gesture','breathing','transitions']){
  $('v33-'+k).value=o[k];$('v33-'+k+'-n').textContent=o[k];
 }
 v33Preview();
}
function v33Preview(){
 const s=v33Selected();if(!s)return;
 const t=s.duration*(Number($('v33-position').value)||0)/100;
 const o=v33Of(s),previous=o.enabled;
 try{
  o.enabled=false;drawScene($('v33-before'),s,t,false);
  o.enabled=previous;drawScene($('v33-after'),s,t,false);
 }finally{o.enabled=previous;}
 const a=v33Signal(s,t,'hero');
 $('v33-caption').textContent=s.title+' · '+t.toFixed(2)+' с · эмоция: '+
  v33Mood(s,t,'hero')+' · сила актёрского сигнала: '+Math.round(a.beat*100)+'%';
}
function v33Save(){
 const s=v33Selected();if(!s)return;
 const o=v33Of(s);o.enabled=$('v33-enabled').checked;
 o.style=$('v33-style').value;
 for(const k of ['gaze','emotion','gesture','breathing','transitions'])
  o[k]=clamp(Number($('v33-'+k).value)||0,0,100);
 save();v33Show();notify('V33: актёрская анимация персонажей сохранена для сцены.');
}
function v33Preset(){
 const s=v33Selected();if(!s)return;
 Object.assign(v33Of(s),{enabled:true,style:'expressive',gaze:82,
  emotion:88,gesture:86,breathing:54,transitions:83});
 save();v33Show();notify('V33: выразительная режиссура актёрской игры установлена.');
}
function v33QA(){
 if(!P)return [];
 const issues=[];
 for(const e of P.episodes)for(const s of e.scenes){
  const o=v33Of(s);if(!o.enabled)continue;
  if(o.transitions<15&&o.gesture>90)
   issues.push('Серия '+e.number+', '+s.title+': слишком резкий жест при слабых переходах.');
  if(o.emotion<15)issues.push('Серия '+e.number+', '+s.title+': крайне слабая мимика.');
  if(o.gaze<10)issues.push('Серия '+e.number+', '+s.title+': почти отсутствует направление взгляда.');
 }
 return issues;
}
function v33Plan(){
 if(!P)return '';
 const a=['AI ANIME FACTORY V33 — АКТЁРСКИЕ ЭМОЦИИ И ПЕРЕХОДЫ',P.title,''];
 for(const e of P.episodes)for(const s of e.scenes){
  const o=v33Of(s);
  a.push('Серия '+e.number+' — '+s.title,
   'Стиль: '+o.style+'; взгляд '+o.gaze+'; эмоции '+o.emotion+
   '; жест '+o.gesture+'; дыхание '+o.breathing+'; переходы '+o.transitions);
  for(const p of [.12,.38,.62,.86])
   a.push('Ключ '+Math.round(p*100)+'%: '+v33Mood(s,s.duration*p,'hero')+
    ', сигнал '+Math.round(v33Signal(s,s.duration*p,'hero').beat*100)+'%');
  a.push('');
 }
 a.push('Мимика регулируется только на процедурном 2D-риге. Пользовательские PNG не перерисовываются.');
 return a.join('\n');
}
async function v33Sheet(){
 await preloadArtwork();
 const s=v33Selected();if(!s)return;
 const frame=document.createElement('canvas'),board=document.createElement('canvas');
 frame.width=640;frame.height=360;board.width=1280;board.height=720;
 const g=board.getContext('2d');
 for(const [i,p] of [.12,.38,.62,.86].entries()){
  drawScene(frame,s,s.duration*p,false);
  const x=(i%2)*640,y=Math.floor(i/2)*360;g.drawImage(frame,x,y);
  g.fillStyle='rgba(3,10,22,.85)';g.fillRect(x+8,y+8,230,27);
  g.fillStyle='#f8e2bb';g.font='bold 13px Arial';
  g.fillText('V33 ЭМОЦИЯ '+(i+1)+' • '+Math.round(p*100)+'%',x+16,y+26);
 }
 download('V33_ACTING_FOUR_FRAMES_'+slug(s.title)+'.png',await blobPNG(board));
 notify('V33: четыре кадра мимики и жестов сохранены.');
}
$('v33-scene').onchange=v33Show;
$('v33-position').oninput=v33Preview;
$('v33-save').onclick=v33Save;$('v33-preset').onclick=v33Preset;
$('v33-qa').onclick=()=>{$('v33-report').textContent=v33QA().join('\n')||
 'Критичных эвристических замечаний нет.';};
$('v33-plan').onclick=()=>download('V33_ACTING_PLAN_RU.txt',
 new Blob([v33Plan()],{type:'text/plain;charset=utf-8'}));
$('v33-sheet').onclick=async()=>{try{await v33Sheet();}catch(e){notify('V33 PNG: '+e.message);}};
for(const k of ['gaze','emotion','gesture','breathing','transitions'])
 $('v33-'+k).oninput=e=>{$('v33-'+k+'-n').textContent=e.target.value;};
