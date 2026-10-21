/* AI Anime Factory C5 — original jointed 3D blocking/animatic rig.
 * No bundled licensed assets or pretrained models. Built-in FK geometry + two-bone IK.
 * OBJ fallback remains rigid: no false claim of auto-rigging imported meshes.
 */
(function(root){'use strict';
const C=root.C4Core;
if(!C)throw Error('C4Core must load before C5Motion');
const clamp=C.clamp, lerp=C.mix, PI=Math.PI;
const KEYS={
 hero:[
 {t:0,swing:-.20,guard:.2,step:0,crouch:.05,lean:0,look:0},
 {t:2,swing:-.8,guard:.3,step:-.3,crouch:.3,lean:.17,look:0},
 {t:3.8,swing:-1,guard:0,step:.7,crouch:.23,lean:.28,look:-.1},
 {t:4.7,swing:.95,guard:0,step:.35,crouch:.15,lean:.28,look:.17},
 {t:5.8,swing:.1,guard:.8,step:.05,crouch:.22,lean:.14,look:.14},
 {t:7.6,swing:-.3,guard:1,step:-.7,crouch:.44,lean:-.35,look:-.25},
 {t:9.7,swing:-.45,guard:1,step:-.4,crouch:.37,lean:-.2,look:.1},
 {t:11.6,swing:1,guard:0,step:.65,crouch:.27,lean:.35,look:.2},
 {t:12.7,swing:-.45,guard:.3,step:-.35,crouch:.15,lean:.1,look:0},
 {t:13.8,swing:1,guard:0,step:.85,crouch:.3,lean:.28,look:-.2},
 {t:16,swing:.2,guard:.2,step:0,crouch:.09,lean:0,look:0}],
 enemy:[
 {t:0,swing:.15,guard:.6,step:0,crouch:.06,lean:0,look:0},
 {t:2,swing:0,guard:.5,step:-.1,crouch:.18,lean:-.1,look:0},
 {t:4.3,swing:-.6,guard:1,step:.25,crouch:.2,lean:-.2,look:.2},
 {t:5.8,swing:.2,guard:1,step:-.4,crouch:.4,lean:-.22,look:-.2},
 {t:7.8,swing:-1,guard:0,step:.65,crouch:.21,lean:.25,look:0},
 {t:8.6,swing:1,guard:0,step:.4,crouch:.18,lean:.28,look:.12},
 {t:9.7,swing:.85,guard:0,step:.65,crouch:.3,lean:.28,look:.18},
 {t:11.6,swing:0,guard:.8,step:-.55,crouch:.32,lean:-.25,look:0},
 {t:13.8,swing:-.6,guard:.3,step:-.4,crouch:.3,lean:-.3,look:.35},
 {t:16,swing:0,guard:0,step:0,crouch:.68,lean:-.65,look:0}]
};
const channels=['swing','guard','step','crouch','lean','look'];
let settings=null;
function defaults(){return {intensity:1,acting:1,keys:{hero:structuredClone(KEYS.hero),enemy:structuredClone(KEYS.enemy)}}}
function normalized(src){let p=defaults();if(src&&typeof src==='object'){
 p.intensity=clamp(Number(src.intensity)||1,.1,2);p.acting=clamp(Number(src.acting)||1,.1,2);
 for(let side of ['hero','enemy']){if(Array.isArray(src.keys?.[side]))p.keys[side]=src.keys[side].map(k=>({t:Number(k.t),...Object.fromEntries(channels.map(name=>[name,Number(k[name]??0)]))}));}
 }
 return p;
}
function validateConfig(a,duration=16){let errors=[];if(!a||typeof a!=='object'){return['Отсутствуют настройки 3D-рига C5']}
 if(!Number.isFinite(a.intensity)||a.intensity<.1||a.intensity>2)errors.push('Мощность движения 0.1–2');
 if(!Number.isFinite(a.acting)||a.acting<.1||a.acting>2)errors.push('Сила пластики 0.1–2');
 for(let side of ['hero','enemy']){
 let ks=a.keys?.[side];if(!Array.isArray(ks)||ks.length<2||ks.length>200){errors.push('Ключи '+side+': 2–200 штук');continue;}
 let prev=-Infinity;for(const [i,k] of ks.entries()){
 if(!Number.isFinite(k.t)||k.t<0||k.t>duration||k.t<=prev)errors.push('Время ключа '+side+' #'+i);prev=k.t;
 for(const name of channels)if(!Number.isFinite(k[name])||Math.abs(k[name])>2.5)errors.push('Канал '+name+' у '+side+' #'+i);
 }
 }return errors;
}
function sample(keys,t){let a=keys[0],b=keys.at(-1);if(t<=a.t)return {...a};if(t>=b.t)return {...b};for(let i=1;i<keys.length;i++){if(t<=keys[i].t){a=keys[i-1];b=keys[i];break}}
 let dt=b.t-a.t,u=dt?C.smooth((t-a.t)/dt):0;return{t,...Object.fromEntries(channels.map(n=>[n,lerp(a[n],b[n],u)]))};}
function config(){return settings||defaults()}
function sampleAt(role,t){return sample(config().keys[role],t)}
function setConfig(src){const errors=validateConfig(src);if(errors.length)throw Error(errors.slice(0,5).join('; '));settings=src}
function vec(a,b){return a.map((v,i)=>v-b[i])}function add(a,b){return a.map((v,i)=>v+b[i])}function mult(a,n){return a.map(x=>x*n)}function dot(a,b){return a.reduce((s,v,i)=>s+v*b[i],0)}function cross(a,b){return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]}function mag(a){return Math.hypot(...a)}function norm(a){return mult(a,1/(mag(a)||1))}
function jointMatrix(start,end){let y=norm(vec(end,start)),ref=Math.abs(y[2])>.97?[0,1,0]:[0,0,1],x=norm(cross(ref,y)),z=norm(cross(x,y));return[x[0],x[1],x[2],0,y[0],y[1],y[2],0,z[0],z[1],z[2],0,start[0],start[1],start[2],1]}
function cylinderBetween(m,a,b,r,col){let h=mag(vec(a,b));if(h<.0001)return;m.group(jointMatrix(a,b),()=>m.cylinder(r,r*.91,h,col,9))}
function ball(m,p,r,col){m.group(C.translate(...p),()=>m.sphere(r,r,r,col,9,6))}
function twoBone(start,end,len1,len2,hint){let d=vec(end,start),l=mag(d)||.00001,along=norm(d),dc=clamp(l,.015,len1+len2-.001),proj=(len1*len1-len2*len2+dc*dc)/(2*dc),h=Math.sqrt(Math.max(0,len1*len1-proj*proj));let side=vec(hint,mult(along,dot(hint,along)));side=norm(side);if(mag(side)<.01)side=[0,0,1];return add(add(start,mult(along,proj)),mult(side,h));}
function segmentChain(m,shoulder,hand,hint,L1,L2,r1,r2,color,accent){
 let delta=vec(hand,shoulder),d=mag(delta),reach=Math.min(d,L1+L2-.002);
 let wrist=d>L1+L2-.002?add(shoulder,mult(norm(delta),reach)):hand;
 let elbow=twoBone(shoulder,wrist,L1,L2,hint);
 cylinderBetween(m,shoulder,elbow,r1,color);cylinderBetween(m,elbow,wrist,r2,accent);
 ball(m,shoulder,r1*1.1,color);ball(m,elbow,r1*.88,accent);ball(m,wrist,r2*.9,accent);return{elbow,wrist};} 
const palette={hero:{armor:[.08,.18,.38],trim:[.20,.75,1],pant:[.04,.06,.13],skin:[.93,.70,.56],hair:[.018,.034,.07],steel:[.72,.81,.90]},enemy:{armor:[.42,.10,.16],trim:[.84,.62,.27],pant:[.16,.22,.31],skin:[.43,.51,.61],hair:[.22,.08,.1],steel:[.75,.79,.82]}};
function buildActor(m,role,body,t){const cfg=config(),p=sampleAt(role,t),power=cfg.intensity,acting=cfg.acting,clr=palette[role],dir=role==='hero'?1:-1;
 const crouch=clamp(p.crouch*acting,0,.75),lean=clamp(p.lean*acting,-.85,.85),step=p.step*power,guard=clamp(p.guard,0,1.8),swing=clamp(p.swing*power,-2,2),look=p.look*acting;
 const bob=.017*Math.sin(t*4+(dir>0?0:1.4)),hipY=1.00-crouch*.36,torsoY=hipY+.47;
 m.group(C.poseM([body.x,body.jump||0,body.z],[0,body.turn,0]),()=>{
  // Grounded ankles and IK knees (not simple pose-swapping).
  const pelvis=[0,hipY,0],lh=[-.22,hipY,0],rh=[.22,hipY,0];
  m.group(C.poseM(pelvis,[0,0,lean*.13]),()=>{m.box(.53,.27,.38,clr.pant)});
  for(let side of [-1,1]){
   let h=side===-1?lh:rh,pace=(side===-1?1:-1)*step;
   let ankle=[side*.24,.13,clamp(-pace*.29,-.38,.38)],heel=[side*.24,.12,ankle[2]-.13];
   let knee=segmentChain(m,h,ankle,[0,.04,-.42-side*pace*.05],.56,.48,.145,.112,clr.pant,clr.steel).elbow;
   ball(m,knee,.13,clr.trim);
   m.group(C.poseM([ankle[0],.12,ankle[2]-.11]),()=>m.box(.29,.18,.48,clr.armor));
  }
  // Chest leaning and 3D face; hips remain separate from spine.
  m.group(C.poseM([lean*.10,torsoY+bob,0],[0,look*.13,lean*.28]),()=>{
   m.box(.77,.75,.36,clr.armor);
   m.group(C.poseM([0,.06,-.205]),()=>m.box(.54,.34,.045,clr.trim));
   m.group(C.poseM([0,.42,0]),()=>m.cylinder(.14,.13,.14,clr.skin,9));
   m.group(C.poseM([0,.65,0],[0,look*.25,0]),()=>{
    m.sphere(.235,.28,.21,clr.skin,12,7);
    if(role==='hero'){
     m.group(C.poseM([0,.2,.025]),()=>m.sphere(.245,.13,.23,clr.hair,10,6));
     for(let i=-2;i<=2;i++)m.group(C.poseM([i*.085,.18,-.16],[.16+i*.12,0,0]),()=>m.tetra(.22,.075,clr.hair));
    } else{m.group(C.poseM([0,.12,0]),()=>m.cylinder(.26,.25,.22,clr.hair,9));m.group(C.poseM([0,-.04,-.20]),()=>m.box(.46,.18,.09,clr.steel));}
    for(let side of [-1,1])m.group(C.poseM([side*.088,.02,-.195]),()=>{m.sphere(.051,.03,.022,[.95,.95,.92],8,5);m.group(C.translate(0,0,-.021),()=>m.sphere(.022,.03,.012,role==='hero'?[.12,.68,.92]:[.95,.35,.28],8,5))});
   });
   // Upper torso deltas, independent shoulder-to-wrist IK in local coordinates.
   for(let side of [-1,1]){
    let arm=side>0?'weapon':'guard',sh=[side*.48,.25,0];
    let hand;if(arm==='weapon'){
     // Windup pulls sword above shoulder; contact sweeps down toward centreline.
     hand=[side*(.60-.25*Math.max(0,swing)),.10+.34*(-swing)+.07*guard,-.39-.16*Math.abs(swing)];
    }else hand=[side*(.62-.29*guard),-.10+.46*guard,-.28-.24*guard];
    let hint=[side*.33,.06,-.47];hand=segmentChain(m,sh,hand,hint,.38,.38,.125,.105,clr.armor,clr.steel).wrist;
    if(arm==='weapon'){
     // Sword is parented to moving hand; tracks the actual wrist target.
     let a=hand,blade=[a[0]-.17-.43*swing,a[1]+.75+.15*(-swing),a[2]-.11],guardA=[a[0],a[1]+.12,a[2]];
     cylinderBetween(m,a,guardA,.038,[.09,.12,.17]);
     cylinderBetween(m,guardA,blade,.057,clr.steel);ball(m,guardA,.09,clr.trim);
     const tip=add(blade,mult(norm(vec(blade,guardA)),.16));cylinderBetween(m,blade,tip,.025,[.88,.96,1]);
    }else{
     m.group(C.poseM([hand[0],hand[1],hand[2]-.05],[.25*guard,0,0]),()=>m.box(.28,.40,.075,clr.trim));
    }
   }
   if(role==='hero')for(let k=-2;k<=2;k++)m.group(C.poseM([k*.155,-.23,.28],[.14+.08*Math.sin(t*3+k),0,k*.04]),()=>m.box(.14,.82,.058,[.07,.09,.20]));
  });
 });
}
function addKey(a,role,t){let keys=a.keys[role],s=sample(keys,t);if(keys.some(k=>Math.abs(k.t-t)<.025))throw Error('На этом времени уже есть ключ');keys.push({...s,t});keys.sort((x,y)=>x.t-y.t);if(keys.length>200){keys.splice(keys.findIndex(k=>k.t===t),1);throw Error('Предел: 200 ключей')};return keys.findIndex(k=>k.t===t)}
const oldDefault=C.defaultProject,oldAdapt=C.adaptC3,oldValidate=C.validateProject;
function enhance(p,original){if(p.schema==='anime-c5-hybrid-3d-v1')return p;
 const v={...p,schema:'anime-c5-hybrid-3d-v1',version:'C5',motion:defaults(),audioScore:{enabled:true,level:.65},dialogue:p.subtitles?.map((s,i)=>({...s,speaker:i%2?'Страж':'Аран'}))||[]};
 if(original){v.legacyC4=structuredClone(original);}return v;}
C.defaultProject=()=>enhance(oldDefault(),null);
C.validateProject=p=>{
 if(!p||p.schema!=='anime-c5-hybrid-3d-v1')return ['Неизвестная схема C5'];
 const orig={...p,schema:'anime-c4-hybrid-3d-v1'},issues=oldValidate(orig);
 issues.push(...validateConfig(p.motion,p.duration));
 if(!p.audioScore||!Number.isFinite(p.audioScore.level)||p.audioScore.level<0||p.audioScore.level>1)issues.push('Громкость звуков боя должна быть 0–1');
 if(!Array.isArray(p.dialogue)||p.dialogue.length>400)issues.push('Некорректные реплики');
 else for(let [i,d] of p.dialogue.entries())if(!Number.isFinite(d.start)||!Number.isFinite(d.end)||d.start<0||d.end<=d.start||d.end>p.duration||typeof d.text!=='string'||d.text.length>500)issues.push('Неверная реплика '+(i+1));
 return issues;
};
C.adaptC3=data=>{
 if(data?.schema==='anime-c5-hybrid-3d-v1'){const errs=C.validateProject(data);if(errs.length)throw Error(errs.join('; '));return structuredClone(data)}
 const previous=oldAdapt(data);return enhance(previous,data?.schema==='anime-c4-hybrid-3d-v1'?data:null);
};
C.actor=buildActor;
root.C5Motion={defaults,validateConfig,sample,sampleAt,setConfig,config,addKey,channels,twoBone,jointMatrix,buildActor,KEYS};
})(typeof window!=='undefined'?window:globalThis);
