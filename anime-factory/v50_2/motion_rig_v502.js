/* AI Anime Factory V50.2 MOTION RIG — articulated Canvas character bodies.
 * DRAW REAL FRAME-ANIMATED LIMBS. Not a scanned anime frame; not a final rig.
 * Opt-in, nondestructive. Existing v501/502 engine and all canon preserved.
 * License: original procedural graphics. NO external pose/model dependencies.
 */
(function(){
'use strict';
const oldScene=v502Scene,oldActor=v501Actor;
let current=null;
const mix=(a,b,f)=>a+(b-a)*Math.max(0,Math.min(1,f));
const clamp=(f)=>Math.max(0,Math.min(1,f));
const smooth=(a,b,x)=>{let t=clamp((x-a)/Math.max(.0001,b-a));return t*t*(3-2*t)};
const ink='#091324';
function shape(g,xy,color,line=ink,thickness=3){
 if(xy.length<3)return;
 g.beginPath();g.moveTo(xy[0][0],xy[0][1]);
 for(let i=1;i<xy.length;i++)g.lineTo(xy[i][0],xy[i][1]);
 g.closePath();g.fillStyle=color;g.fill();
 if(line){g.strokeStyle=line;g.lineWidth=thickness;g.lineJoin='round';g.stroke()}
}
function link(g,a,b,w0,w1,color,shadow,edge){
 const angle=Math.atan2(b[1]-a[1],b[0]-a[0]);const cs=Math.cos(angle),sn=Math.sin(angle);
 const point=(xy,n)=>[xy[0]-sn*n,xy[1]+cs*n];
 const pts=[point(a,-w0),point(b,-w1),point(b,w1),point(a,w0)];
 shape(g,pts,color,edge||ink,3);
 shape(g,[point(a,w0*.27),point(b,w1*.26),point(b,w1*.63),point(a,w0*.63)],shadow,null);
}
function oval(g,x,y,rx,ry,fill,stroke=ink,angle=0,lw=2){
 g.beginPath();g.ellipse(x,y,rx,ry,angle,0,Math.PI*2);g.fillStyle=fill;g.fill();
 if(stroke){g.lineWidth=lw;g.strokeStyle=stroke;g.stroke()}
}
function strand(g,pts,color,lw){
 g.strokeStyle=color;g.lineWidth=lw;g.lineCap='round';g.lineJoin='round';
 g.beginPath();g.moveTo(pts[0][0],pts[0][1]);for(let i=1;i<pts.length;i++)g.lineTo(...pts[i]);g.stroke();
}
const specs={
 hero:{body:'#172f4d',shade:'#09192e',edge:'#4dc9f3',panel:'#246f95',hair:'#0c2037',hairlight:'#315884',skin:'#eebca5',eye:'#6df0ff',cape:'#123a56',weapon:'sword'},
 lover:{body:'#60426b',shade:'#372e58',edge:'#e4aede',panel:'#b78ac3',hair:'#c5ccf0',hairlight:'#f5ecff',skin:'#f9d2c7',eye:'#9472ce',cape:'#eac5ea',weapon:'staff'},
 friend:{body:'#233e35',shade:'#142d2e',edge:'#bad4a3',panel:'#5f896e',hair:'#392d24',hairlight:'#a88264',skin:'#deb39a',eye:'#d7ab61',cape:'#1d514a',weapon:'dagger'},
 rival:{body:'#5d334a',shade:'#341b37',edge:'#ef9775',panel:'#a95965',hair:'#23182e',hairlight:'#65435e',skin:'#eab8a2',eye:'#f0bf91',cape:'#712f55',weapon:'spear'},
 enemy:{body:'#311c35',shade:'#1c122f',edge:'#f06a9c',panel:'#783d6b',hair:'#241b2c',hairlight:'#743a5b',skin:'#ab98a6',eye:'#f7a1b2',cape:'#4c1e3c',weapon:'staff'},
 guardian:{body:'#2b3548',shade:'#151e30',edge:'#f85c90',panel:'#686b7f',hair:'#161928',hairlight:'#7e8097',skin:'#515b75',eye:'#ff557e',cape:'#151a2a',weapon:'axe'}
};
function combatPose(f,foe){
 // Each beat independently solves wrist, elbow, planted feet and torso.
 const phase=f<.17?'faceoff':f<.29?'advance':f<.48?'windup':
     f<.61?'counter':f<.79?'strike':f<.88?'knockback':'recover';
 const move=foe?-1:1;
 const lift=(f>.18&&f<.35)?Math.sin((f-.18)/.17*Math.PI)*42:0;
 const attack=smooth(.58,.695,f)*(1-smooth(.74,.84,f));
 const guard=smooth(.18,.28,f)*(1-smooth(.52,.62,f));
 const recoil=smooth(.675,.73,f)*(1-smooth(.84,.96,f));
 return {
  phase,attack,guard,recoil,lift,
  shoulder:move*(foe?9:18)*guard,
  torso:(foe?-.27:.37)*attack+(foe?.26:-.11)*recoil,
  rightW:foe?[64+guard*12,-170-guard*80+recoil*54]:
    [95+guard*55+attack*122,-138-guard*161-attack*61],
  rightE:foe?[99+guard*14,-207-guard*20]:
    [103+guard*33+attack*32,-225-guard*52],
  leftW:foe?[-22+guard*26,-136-guard*92]:
    [-95+guard*68,-139-guard*122],
  leftE:foe?[-93+guard*40,-212-guard*24]:
    [-102+guard*29,-199-guard*30],
  step:Math.sin(f*27)*(foe?3:8)*(1-attack),
  face:attack>.5?'shout':guard>.3?'frown':recoil>.3?'pain':'focus'
 };
}
function idlePose(sec,index,kind){
 const step=Math.sin(sec*2.8+index*1.1)*2.4;
 const talk=current?.talk?.speaker;
 const isTalk=talk===current?.actors?.[index]?.[0];
 const emphasis=isTalk?.42:.12;
 const f=Math.sin(sec*2+index*2.2);
 return {phase:'dialogue',attack:0,guard:0,recoil:0,lift:0,torso:0,
  rightW:[100+f*emphasis*40,-156+f*emphasis*33],
  rightE:[95+f*emphasis*19,-222],
  leftW:[-86,-152+f*emphasis*23],leftE:[-92,-204],step,
  face:isTalk?'talk':kind==='betrayal'?'concern':'focus'};
}
function leg(g,side,pose,spec,hasCape){
 const stride=pose.step*side,run=pose.attack>.2||pose.guard>.2;
 const forward=side===1?1:-1;
 const hip=[side*29,-132],knee=[side*37+stride+(run?forward*pose.attack*12:0),-70];
 const foot=[side*43+stride*(side===1?1.1:-.4)+(run?forward*pose.attack*17:0),
          (pose.lift&&side===1)?-pose.lift:0];
 link(g,hip,knee,22,17,spec.body,spec.shade,spec.edge);
 oval(g,...knee,18,15,spec.panel,spec.edge,0,2);
 link(g,knee,[foot[0],foot[1]-19],17,12,spec.shade,spec.body,spec.edge);
 shape(g,[[foot[0]-23,foot[1]-21],[foot[0]+17,foot[1]-22],
          [foot[0]+26,foot[1]-5],[foot[0]+23,foot[1]+2],
          [foot[0]-26,foot[1]+2]],spec.shade,spec.edge,3);
 strand(g,[[foot[0]-14,foot[1]-10],[foot[0]+16,foot[1]-10]],spec.panel,3);
}
function chest(g,id,spec,pose,sec){
 const gradient=g.createLinearGradient(-90,-300,85,-135);
 gradient.addColorStop(0,spec.panel);gradient.addColorStop(.39,spec.body);
 gradient.addColorStop(1,spec.shade);
 shape(g,[[-55,-286],[0,-304],[56,-285],[73,-228],
          [49,-130],[19,-116],[-44,-127],[-69,-230]],gradient,spec.edge,4);
 // Asymmetric coat, folds and unique silhouette (no identical stick torso).
 shape(g,[[-54,-270],[-18,-284],[0,-230],[-21,-150],[-61,-134],[-73,-227]],
       spec.shade,spec.edge,2);
 shape(g,[[53,-272],[12,-281],[1,-240],[20,-165],[49,-135],[71,-235]],
       spec.body,spec.edge,3);
 for(let n=0;n<3;n++)strand(g,[[-37,-238+n*32],[0,-245+n*32],[33,-236+n*32]],spec.panel,2);
 shape(g,[[-54,-143],[54,-143],[52,-126],[-56,-125]],spec.panel,spec.edge,2);
 oval(g,0,-138,8,8,spec.edge,null);
 if(id==='hero'){
  shape(g,[[-75,-275],[-31,-294],[14,-284],[26,-268],[-46,-263]],'#1d92af','#92efff',3);
  shape(g,[[-72,-261],[-94,-218],[-71,-139],[-45,-240]],'#16799d','#79eeff',3);
  strand(g,[[-45,-223],[-34,-202],[-28,-180]],'#87deff',3);
 }
 if(id==='lover'){
  shape(g,[[-49,-177],[-89,-67],[-13,-77],[14,-90],[83,-65],[47,-180]],
       '#aa7aab','#f7d2e7',3);
  shape(g,[[-25,-280],[0,-250],[25,-280],[14,-227],[-14,-227]],'#f1bfde',null);
 }
 if(id==='friend'){
  shape(g,[[-53,-254],[-43,-300],[-20,-310],[-26,-270]],'#a18f4f','#e6d39a',2);
  shape(g,[[-11,-230],[18,-230],[25,-205],[-17,-204]],'#b6d4a5',null);
 }
 if(id==='rival'){
  shape(g,[[-30,-291],[40,-287],[60,-256],[-18,-253]],'#8b303b','#edbc9b',3);
  shape(g,[[12,-259],[27,-248],[17,-193],[-1,-188]],'#e6a9a3',null);
 }
 if(id==='guardian'){
  for(let n=0;n<3;n++)shape(g,[[-44,-259+n*38],[0,-266+n*38],
    [48,-255+n*38],[38,-239+n*38],[-38,-236+n*38]],
    n%2?'#4d5164':'#35364e','#b86184',3);
  oval(g,0,-221,14,20,'#fe568e','#f5a4cb',0,2);
 }
}
function arm(g,a,e,w,spec,weaponArm){
 oval(g,...a,29,27,spec.panel,spec.edge,0,3);
 link(g,a,e,22,18,spec.body,spec.shade,spec.edge);
 oval(g,...e,18,17,spec.panel,spec.edge,0,2);
 link(g,e,w,18,12,spec.body,spec.shade,spec.edge);
 // wrist cuff and connected hand
 oval(g,...w,15,13,spec.edge,ink,0,2);
 oval(g,w[0]+3,w[1]-4,11,11,spec.skin,ink,0,2);
}
function weapon(g,id,spec,hand,pose){
 const strike=pose.attack;
 // Swing arc is referenced to the WRIST; never an unanchored sword.
 let angle=-.78-strike*.86+(pose.guard||0)*.65;
 if(id==='guardian')angle=-1.02+pose.recoil*.9;
 const dir=[Math.cos(angle),Math.sin(angle)];
 const px=(r)=>hand[0]+dir[0]*r,py=(r)=>hand[1]+dir[1]*r;
 g.save();g.shadowBlur=pose.attack*21;g.shadowColor=spec.edge;
 if(spec.weapon==='sword'){
  strand(g,[[px(-17),py(-17)],[px(36),py(36)]],spec.panel,10);
  strand(g,[[px(7)-17,py(7)-12],[px(7)+17,py(7)+12]],'#c6ba95',9);
  shape(g,[[px(32)-7,py(32)+6],[px(176)-1,py(176)+2],
    [px(190),py(190)],[px(176)+8,py(176)-3],
    [px(38)+7,py(38)-6]],'#92dff7','#f6fcff',2);
  strand(g,[[px(44),py(44)],[px(179),py(179)]],'#f9ffff',2);
 }else if(spec.weapon==='spear'||spec.weapon==='staff'){
  strand(g,[[px(-80),py(-80)],[px(156),py(156)]],spec.edge,10);
  shape(g,[[px(139)-12,py(139)+8],[px(178),py(178)],
    [px(142)+12,py(142)-8]],spec.weapon==='spear'?'#f7d2bd':'#ffdaed','#fff6ed',2);
  oval(g,px(148),py(148),11,14,spec.eye,null);
 }else if(spec.weapon==='dagger'){
  strand(g,[[px(-19),py(-19)],[px(30),py(30)]],'#d0b57a',9);
  shape(g,[[px(30)-6,py(30)+8],[px(89),py(89)],[px(30)+8,py(30)-7]],
   '#d7f1e0','#fff',2);
 }else{
  strand(g,[[px(-20),py(-20)],[px(130),py(130)]],'#9b99aa',11);
  shape(g,[[px(109)-30,py(109)+8],[px(153)-24,py(153)+11],
   [px(169)+27,py(169)-22],[px(116)+31,py(116)-18]],'#515a6c',spec.edge,4);
 }
 g.restore();
}
function face(g,id,spec,pose,sec,local){
 const fight=current?.kind==='fight';
 const neckY=-301;
 shape(g,[[-21,-292],[23,-292],[19,-323],[-20,-321]],spec.skin,ink,2);
 if(id==='guardian'){
  shape(g,[[-57,-324],[-61,-368],[-40,-401],[40,-401],[61,-365],
           [48,-326],[21,-309],[-34,-308]],spec.body,spec.edge,5);
  shape(g,[[-59,-369],[-32,-394],[9,-387],[-15,-353]],spec.shade,null);
  strand(g,[[-33,-354],[-10,-345],[8,-345],[33,-354]],spec.eye,8);
  oval(g,0,-379,6,10,spec.edge,null);
 }else{
  const pointy=id==='rival'||id==='hero';
  shape(g,[[-45,-321],[-51,-357],[-35,-387],[19,-394],
          [49,-367],[44,-324],[11,pointy?-299:-306],[-18,-300]],
        spec.skin,'#604358',2.5);
  // nose shadow, ears, eyelash silhouette; brows express the hit.
  oval(g,-43,-348,9,17,spec.skin,'#b88788',-.23,1);
  oval(g,45,-349,10,17,spec.skin,'#b88788',.23,1);
  const narrowed=fight||pose.face==='frown';
  const blink=((sec*.9+(id==='hero'?1.2:2.7))%4.7)<.13;
  for(const side of [-1,1]){
   const cx=side*21;
   const eyeY=-351;
   const browY=narrowed?(side===-1?-365:-370):-369;
   strand(g,[[cx-15,browY-2],[cx+8,browY+2]],spec.hair,4.5);
   shape(g,[[cx-15,eyeY-4],[cx-6,eyeY-(blink?0:10)],[cx+12,eyeY-6],
            [cx+17,eyeY-2],[cx+4,eyeY+4],[cx-12,eyeY+3]],'#f6f5f4','#272136',2);
   if(!blink){
     oval(g,cx+1,eyeY-1,6,7,spec.eye,'#232d3f',0,1.5);
     oval(g,cx+2,eyeY,2,5,'#152336',null);
     oval(g,cx-1,eyeY-4,1.8,2.4,'#fff',null);
   }
  }
  strand(g,[[1,-344],[-1,-333],[9,-332]],'#b98084',2);
  let amp=local?.speaker===id?(local.energy||0):0;
  let mouth=pose.face==='shout'?9:2+amp*8;
  if(pose.face==='pain')mouth=7;
  oval(g,6,-315,9,mouth,'#854a57','#c78c8f',0,1.5);
  if(id==='hero')strand(g,[[36,-333],[44,-325]],'#ac6a7c',2);
  if(id==='friend')strand(g,[[35,-327],[48,-331]],'#875d60',3);
 }
 // Hair is anchored to the face, with cloth/hair movement independent of torso.
 const wind=Math.sin(sec*5+id.length)*4;
 const hair=spec.hair,h2=spec.hairlight;
 if(id==='lover'){
  shape(g,[[-60,-372],[-79,-322],[-102+wind,-183],[-56,-223],
           [-52,-348],[32,-373],[65,-327],[85+wind,-202],
           [76,-333],[59,-387],[-34,-404]],hair,h2,3);
  for(let i=0;i<4;i++)strand(g,[[-53+i*19,-393],[-53+i*19+wind*.2,-360],
                                 [-53+i*19+wind,-315]],i%2?h2:hair,6);
  oval(g,-68,-355,13,12,'#dfa2d4','#fff0ec',0,2);
 }else if(id==='guardian'){
  for(let i=0;i<4;i++)shape(g,[[-56+i*31,-382],[-52+i*29,-428-i%2*10],
                           [-31+i*26,-380]],hair,spec.edge,2);
 }else{
  shape(g,[[-61,-376],[-76,-393],[-47,-406],[-28,-420],
            [32,-410],[64,-393],[75,-380],[44,-358],[-13,-364],
            [-50,-359]],hair,h2,3);
  for(let i=0;i<6;i++)shape(g,[[-59+i*22,-384],[-59+i*22-wind*.3,-339],
                          [-39+i*20,-367]],i%2?hair:h2,null);
 }
}
function actor(g,id,x,y,scale,dir,pose,sec,local,index){
 const spec=specs[id]||specs.hero;
 const battle=current?.kind==='fight',f=current?.fraction||0;
 const anim=battle?combatPose(f,id==='guardian'):idlePose(sec,index||0,current?.kind);
 const breathe=Math.sin(sec*2.6+id.length*1.1)*2;
 const torso=anim.torso+(pose.lean||0)*.28;
 const bob=(battle?Math.sin(sec*11)*2:Math.sin(sec*2.3)*1.7);
 g.save();g.translate(x,y+bob);g.scale((dir||1)*scale*.92,scale*.92);
 oval(g,0,5,67,9,'#0209139a',null);
 // Background aura behind the whole person; low alpha avoids whiteouts.
 v501Glow(g,0,-223,160,spec.edge,battle?.13:.07);
 // Lower-body independent foot plant; shadows stay on the ground.
 g.save();g.translate(0,0);leg(g,-1,anim,spec);leg(g,1,anim,spec);g.restore();
 // Cape anchored to shoulder, independently swept by motion.
 const wind=Math.sin(sec*5+id.length)*13+(battle?anim.attack*44:0);
 shape(g,[[-58,-279],[-99,-198],[-144-wind,-42],[-86,-77],[-11,-99],
          [46,-89],[108+wind,-57],[77,-264]],spec.cape,spec.edge,4);
 for(let k=0;k<3;k++)strand(g,[[-66,-256+k*26],[-100-wind*.3,-120+k*10],
                              [-116-wind,-52]],spec.panel,2);
 // Arm separation and shoulder movement; off-hand used to parry.
 g.save();g.translate(0,-3+breathe);g.rotate(torso*.3);
 const leftS=[-60,-255],rightS=[63,-255];
 arm(g,leftS,anim.leftE,anim.leftW,spec,false);
 chest(g,id,spec,anim,sec);
 // Head reacts after torso but has its own angle. Hair avoids face occlusion.
 g.save();g.translate(0,-297);g.rotate(-torso*.16+Math.sin(sec*2.0)*.012);
 g.translate(0,297);face(g,id,spec,anim,sec,local);g.restore();
 arm(g,rightS,anim.rightE,anim.rightW,spec,true);
 weapon(g,id,spec,anim.rightW,anim);
 g.restore();g.restore();
}
function v502MotionScene(g,ei,scene,sec){
 const si=P.episodes[ei].scenes.indexOf(scene);
 current={kind:scene.kind,scene:si,fraction:clamp(sec/Math.max(.001,scene.duration)),
   actors:v502Cast(si),talk:v502GetSpeaker(scene,sec)};
 try{return oldScene(g,ei,scene,sec)}finally{current=null}
}
// Existing V50.2 visuals still work when motion is disabled.
v501Actor=function(g,id,x,y,scale,dir,pose,sec,local){
 if(!P?.v502MotionRig?.enabled||!current)return oldActor(g,id,x,y,scale,dir,pose,sec,local);
 const index=(current.actors||[]).findIndex(a=>a[0]===id);
 return actor(g,id,x,y,scale,dir,pose,sec,local,index<0?0:index);
};
v502Scene=function(g,ei,scene,sec){
 if(!P?.v502MotionRig?.enabled || ei>1 || !scene?.pilotV50)
   return oldScene(g,ei,scene,sec);
 return v502MotionScene(g,ei,scene,sec);
};
// Strictly opt in, old projects still render through existing artist/rig.
const panel=document.getElementById('v502-panel');
if(panel){
 const wrapper=document.createElement('label');wrapper.style.cssText='display:flex;align-items:center;gap:10px;border:1px solid #6585a5;padding:8px 10px;border-radius:8px;margin:10px 0';
 wrapper.innerHTML='<input type="checkbox" id="v502-motion-enabled" style="width:auto"> MOTION RIG V50.2: независимые суставы, опорные ноги, замах, удар, отдача';
 panel.appendChild(wrapper);
 const toggle=document.getElementById('v502-motion-enabled');
 toggle.onchange=()=>{
  if(!P)return;
  P.v502MotionRig={enabled:!!toggle.checked,status:'ANIMATED_PROCEDURAL_TEST',artApproval:false};
  save();if(typeof v48Draw==='function')v48Draw();
 };
 const prev=v502Settings;
 v502Settings=function(){prev();if(P)toggle.checked=!!P.v502MotionRig?.enabled};
}
window.v502Motion=Object.freeze({version:'V50.2-MOTION-PASS',source:'Original procedural articulated 2D',
 licensedActors:false,humanArtApproval:false,originalCanonPreserved:true,
 poseAt:(fraction,foe=false)=>combatPose(clamp(fraction),foe),
 sceneFrame:(episode,time,width=960)=>{
  const ep=P?.episodes?.[episode];if(!ep)throw Error('Bad episode');
  const canvas=document.createElement('canvas');canvas.width=width;canvas.height=Math.round(width*9/16);
  v35Frame(canvas,ep,time);
  if(typeof v37Paint==='function')v37Paint(canvas,ep,time);
  return canvas.toDataURL('image/png');
 }});
})();