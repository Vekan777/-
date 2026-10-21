/* V50.2 DIRECTOR / additive shot-by-shot camera animation and staging.
 * All code V19-V50.1 preserved, original scenes fall back without changes.
 * Shots are intentionally discrete editorial CUTS: avoid static side-by-side
 * portraits for every line. This is still procedural vector art, NOT studio art.
 */
const v502ShotTable=Object.freeze({
 opening:[['wide',0,.18],['hero',.18,.49],['partner',.49,.72],['over',.72,1]],
 friendship:[['wide',0,.2],['partner',.2,.44],['hero',.44,.67],['over',.67,1]],
 fight:[['wide',0,.13],['track',.13,.25],['partner',.25,.37],
       ['hero',.37,.54],['wide',.54,.65],['impact',.65,.79],['aftermath',.79,1]],
 romance:[['wide',0,.18],['hero',.18,.43],['partner',.43,.73],['over',.73,1]],
 betrayal:[['wide',0,.14],['partner',.14,.38],['detail',.38,.59],
           ['hero',.59,.77],['over',.77,1]],
 ending:[['wide',0,.23],['partner',.23,.48],['hero',.48,.76],['wide',.76,1]]
});
const v502KeepFrame=v501SceneDraw;
function v502Plan(scene,f){
 const shots=v502ShotTable[scene.kind]||v502ShotTable.opening;
 const match=shots.find(s=>f>=s[1]&&f<s[2])||shots[shots.length-1];
 return {kind:match[0],start:match[1],end:match[2],number:shots.indexOf(match)};
}
function v502Cast(si){
 return [
  [['hero',.36],['rival',.7]],
  [['hero',.34],['friend',.67]],
  [['hero',.29],['guardian',.75]],
  [['hero',.36],['lover',.67]],
  [['friend',.48],['hero',.79]],
  [['hero',.36],['lover',.68]]
 ][si]||[['hero',.35],['lover',.68]];
}
function v502ActorExpression(si,kind,who,f){
 const beat=si===2?v501Battle(f):null;
 let pose={
   step:Math.sin(f*13+who*2)*2.8,
   arm:.07*Math.sin(f*18+who*3),
   cape:Math.sin(f*17+who*3)*9,
   attack:0,lean:0
 };
 if(si===2){
   pose.step=who===0?Math.sin(f*47)*16:Math.sin(f*31)*5;
   pose.arm=who===0?beat.attack*.72:beat.attack*.26;
   pose.attack=who===0?beat.attack:beat.attack*.25;
   pose.lean=who===0?beat.lean:-beat.lean*.28;
   if(f>.81){pose.step=0;pose.lean=who===0?-.16:.22;}
 }
 if(si===3){
   pose.arm=who===0?(.09+.17*Math.sin(Math.PI*f)):-.12;
   pose.lean=.02*Math.sin(f*5+who);
 }
 if(si===4)pose.lean=who===0?-.1:.08;
 if(si===0&&who===0)pose.cape+=10;
 return pose;
}
function v502Lens(shot,cast,si,f){
 const motion=si===2?v501Battle(f):null;
 const xs=cast.map((a,i)=>si===2?(i===0?motion.heroX:motion.foeX)*960:a[1]*960);
 const a=xs[0],b=xs[1];
 const c={cx:480,cy:272,z:1};
 switch(shot.kind){
 case 'hero':c.cx=a;c.cy=250;c.z=1.70;break;
 case 'partner':c.cx=b;c.cy=250;c.z=1.72;break;
 case 'over':c.cx=(a+b)*.5;c.cy=250;c.z=1.17;break;
 case 'track':c.cx=a+76;c.cy=280;c.z=1.19;break;
 case 'impact':c.cx=(a+b)/2;c.cy=250;c.z=1.46;break;
 case 'aftermath':c.cx=500;c.cy=286;c.z=1.04;break;
 case 'detail':c.cx=a;c.cy=350;c.z=2.2;break;
 case 'wide':default:c.cx=480;c.cy=275;c.z=1.02;break;
 }
 // Continuous in-shot camera drift; jump-cuts between shots are intentional.
 const p=(f-shot.start)/Math.max(.01,shot.end-shot.start);
 c.cx+=Math.sin(p*2.8)*7;c.cy-=p*4;c.z*=1+p*.017;
 return c;
}
function v502Dust(g,x,y,strength,seed){
 g.save();g.globalAlpha=.43*strength;
 for(let i=0;i<22;i++){
  const phase=i*2.399+seed,rr=3+i%5*4;
  const dx=Math.cos(phase)*(15+strength*26+i),dy=-Math.abs(Math.sin(phase)*(2+i*.65));
  g.fillStyle=i%3?'#c9b9a2':'#efd0b0';
  g.beginPath();g.ellipse(x+dx,y+dy,rr,rr*.35,phase,0,7);g.fill();
 }
 g.restore();
}
function v502ActionStroke(g,x,y,f){
 const beat=v501Battle(f);
 if(beat.attack<.12)return;
 const glow=Math.min(1,beat.attack*1.4);
 g.save();g.lineCap='round';g.shadowColor='#b8f9ff';g.shadowBlur=17;
 for(let j=0;j<4;j++){
   g.strokeStyle=j%2?'rgba(255,245,193,'+glow*.6+')':'rgba(84,228,244,'+glow*.9+')';
   g.lineWidth=3+j*3;g.beginPath();
   g.arc(x+100,y-130,85+j*11,-2.3+f*.8,.62+f*.8);g.stroke();
 }
 g.restore();
}
function v502Impact(g,x,y,f){
 if(f<.655||f>.81)return;
 const t=(f-.655)/.155,e=Math.sin(t*Math.PI);
 v501Glow(g,x,y,120+200*t,'#f5e8a3',.28*e);
 v501Glow(g,x,y,80+130*t,'#54dbff',.22*e);
 g.save();g.globalAlpha=.6*e;
 for(let i=0;i<25;i++){
  const angle=i*Math.PI*2/25,rr=45+t*235;
  const ox=x+Math.cos(angle)*rr,oy=y+Math.sin(angle)*rr*.68;
  v501Line(g,[[ox,oy],[ox+Math.cos(angle)*(27+i%4*9),
                         oy+Math.sin(angle)*(27+i%4*9)]],
   i%4?'#acf5ff':'#ffe7aa',2+i%3);
 }
 g.restore();
}
function v502CharacterShotOverlay(g,ei,scene,shot,sec,heroName){
 const f=sec/Math.max(.01,scene.duration),kind=shot.kind;
 if(kind==='wide'||kind==='over'||kind==='track'||kind==='aftermath')return;
 // Subtle speed lines only for battle: not over all dialogue frames.
 if(scene.kind==='fight'){
  g.save();g.globalAlpha=.10;g.strokeStyle='#cde9ff';g.lineWidth=2;
  for(let i=0;i<18;i++){
   const k=i*1.7;
   g.beginPath();g.moveTo(-30,k*31);
   g.lineTo(130+Math.sin(i*2)*80,k*31-40);g.stroke();
  }
  g.restore();
 }
 // Subject-centered upper/lower negative space for edits (no false subtitles).
 if(kind==='detail'&&scene.kind==='betrayal'){
   v501Glow(g,480,320,115,'#8cf5b7',.21);
 }
}
function v502GetSpeaker(scene,sec){
 const config=scene.audioV36?.voice||{},off=Number(config.offset)||0;
 const live=(config.segmentsV501||[]).find(s=>sec>=off+s.start&&sec<off+s.end);
 const cast={hero:'hero',miyu:'lover',ren:'friend',saira:'rival',archon:'enemy'};
 const sound=config.waveV47||[],index=Math.floor((sec-off)*(Number(config.sampleRateV47)||50));
 const amplitude=index<0?0:Math.min(1,Math.max(0,Number(sound[index])||0));
 return {speaker:live?(cast[live.role]||''):'',energy:amplitude};
}
function v502Scene(g,ei,scene,sec){
 const ep=P.episodes[ei],si=ep.scenes.indexOf(scene);
 const f=Math.max(0,Math.min(.99999,sec/Math.max(.01,scene.duration)));
 const shot=v502Plan(scene,f),actors=v502Cast(si);
 const motion=si===2?v501Battle(f):null;
 const cam=v502Lens(shot,actors,si,f);
 // Optical shake only AFTER impact and only for ~.12 seconds.
 const shake=si===2&&f>.657&&f<.70?Math.sin(sec*109)*(1-(f-.657)/.043)*7:0;
 g.save();g.translate(480+shake,270);g.scale(cam.z,cam.z);
 g.translate(-cam.cx,-cam.cy);
 v501Backdrop(g,ei,si,sec);
 const mouth=v502GetSpeaker(scene,sec);
 for(let i=0;i<actors.length;i++){
   const [id,stillX]=actors[i];
   const x=si===2?(i===0?motion.heroX:motion.foeX)*960:stillX*960;
   let y=474;
   if(si===2&&f>.17&&f<.37&&i===0)y-=Math.sin((f-.17)/.20*Math.PI)*38;
   if(si===2&&f>.67&&f<.8&&i===1)y+=Math.sin((f-.67)/.13*Math.PI)*15;
   const scl=id==='guardian'?.84:id==='lover'?.90:.94;
   const p=v502ActorExpression(si,shot.kind,i,f);
   // Canvas drawing backwards retains outlined hands and sword orientation.
   v501Actor(g,id,x,y,scl,i===0?1:-1,p,sec,mouth);
   if(si===2&&i===0)v502ActionStroke(g,x,y,f);
 }
 if(si===2){
   v502Impact(g,(motion.heroX+motion.foeX)*480,274,f);
   if(f>.65&&f<.82)v502Dust(g,motion.foeX*960,475,Math.sin((f-.65)/.17*Math.PI),si);
 }
 if(si===4){
   // Story clue: Ren's bracelet and dangerous contact, remains in every shot.
   const rx=actors[0][1]*960;
   v501Glow(g,rx-15,372,46,'#91f8bd',.34);
   g.save();g.strokeStyle='#bcf5cc';g.lineWidth=4;
   g.beginPath();g.arc(rx-15,371,19,0,7);g.stroke();g.restore();
 }
 if(si===3){ // warm light falls between Akira and Miyu
   v501Glow(g,470,260,210,'#fce6c5',.10+f*.09);
 }
 g.restore();
 // Professional-feeling composition tools; simple original graphics remain.
 g.save();g.fillStyle='#040917ed';
 g.fillRect(0,0,960,21);g.fillRect(0,516,960,24);
 g.font='600 12px Segoe UI,Arial';g.fillStyle='#d6e5eb';
 g.fillText('ОСКОЛКИ ЗАБЫТОЙ КЛЯТВЫ  ·  '+('0'+ep.number).slice(-2),22,15);
 g.textAlign='right';g.fillText((scene.title||'').slice(0,42),938,15);
 g.textAlign='left';
 const line=g.createLinearGradient(0,21,960,21);
 line.addColorStop(0,'#75d9ee00');line.addColorStop(.5,'#75d9eeaa');line.addColorStop(1,'#75d9ee00');
 g.fillStyle=line;g.fillRect(0,21,960,1);
 v502CharacterShotOverlay(g,ei,scene,shot,sec);
 g.restore();
}
v501SceneDraw=function(g,ei,scene,sec){
 if(!P?.v502Director?.enabled)return v502KeepFrame(g,ei,scene,sec);
 if(!scene?.pilotV50||ei>1)return v502KeepFrame(g,ei,scene,sec);
 return v502Scene(g,ei,scene,sec);
};
window.v502Director=Object.freeze({
 version:'50.2.0-dev',pilotOnly:true,originalV501Preserved:true,
 shotPlan:(kind)=>v502ShotTable[kind].map(s=>({kind:s[0],from:s[1],to:s[2]})),
 active:(episode,scene,time)=>{
  const ep=P?.episodes?.[episode],sc=ep?.scenes?.[scene];
  if(!sc)return null;
  return v502Plan(sc,time/Math.max(.01,sc.duration)).kind;
 },
 frame:(episode,time)=>window.v501Visual.frame(episode,time)
});
function v502Settings(){
 if(!P)return;
 if(!P.v502Director)P.v502Director={enabled:false,approval:false};
 const el=$('v502-enabled');if(el)el.checked=!!P.v502Director.enabled;
}
const v502Check=$('v502-enabled');
if(v502Check)v502Check.onchange=()=>{
 if(!P)return;
 P.v502Director={...(P.v502Director||{}),enabled:v502Check.checked,
  approval:false};
 save();if(typeof v48Draw==='function')v48Draw();
 notify('V50.2: '+(v502Check.checked?'кинорежиссура включена':
                                     'исходный V50.1-рендер восстановлен'));
};
