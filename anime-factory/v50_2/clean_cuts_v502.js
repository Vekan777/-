/* V50.2 CLEAN CUTS — optional quality patch for existing V50.2 Motion Rig.
 * Removes semitransparent portraits over rigged characters. Illustrated shots
 * are independent opaque still frames with mild editorial panning — NOT
 * full character animation. All V19–V50.2 scene/plot data remains unchanged.
 */
(function(){
'use strict';
const images=Object.create(null),src=window.v502IllustrationData||{};
let loaded=0,failed=0;
for(const key of Object.keys(src)){
 const img=new Image();images[key]=img;
 img.onload=()=>loaded++;img.onerror=()=>failed++;
 img.src=src[key];
}
const keyed=[
 {hero:'akira',partner:'saira',over:'world'},
 {hero:'akira',partner:'ren_worried',over:'ren'},
 {hero:'akira_screaming',partner:'guardian',impact:'battle',aftermath:'akira_power'},
 {hero:'akira',partner:'miyu_worried',over:'miyu'},
 {hero:'akira_power',partner:'ren_worried',detail:'ren',over:'ren_worried'},
 {hero:'akira',partner:'miyu',over:'portal'}
];
const before=v501SceneDraw;
function opaqueCut(g,img,w,h,sec,sceneId,shotKey){
 const t=Math.max(0,Math.min(1,sec));
 g.save();g.globalAlpha=1;g.globalCompositeOperation='source-over';
 g.fillStyle='#070e1e';g.fillRect(0,0,w,h);
 const portrait=img.naturalWidth/img.naturalHeight<1.48;
 const base=Math.max(w/img.naturalWidth,h/img.naturalHeight);
 const scale=base*(1.03+t*.045);
 const sw=img.naturalWidth*scale,sh=img.naturalHeight*scale;
 const shiftX=Math.sin(t*2.15+sceneId*.9)*Math.max(0,sw-w)*.32;
 const shiftY=Math.cos(t*1.4+sceneId*.55)*Math.max(0,sh-h)*.28;
 if(portrait){
   // Preserve the entire face: naive portrait cover cropped it to the jaw.
   g.save();g.filter='blur(20px) brightness(.35) saturate(1.15)';
   g.drawImage(img,(w-sw)/2+shiftX,(h-sh)/2+shiftY,sw,sh);g.restore();
   g.fillStyle='#0814268c';g.fillRect(0,0,w,h);
   const frontScale=Math.min((w-120)/img.naturalWidth,(h-57)/img.naturalHeight)*(1+t*.015);
   const fw=frontScale*img.naturalWidth,fh=frontScale*img.naturalHeight;
   const anchor=(sceneId%2===0?.46:.56)*w;
   const px=Math.max(18,Math.min(w-fw-18,anchor-fw*.5));
   const py=(h-fh)/2+6;
   g.save();g.shadowColor='#020713';g.shadowBlur=32;
   g.drawImage(img,px,py,fw,fh);g.restore();
 } else {
   g.filter='saturate(1.06) contrast(1.04)';
   g.drawImage(img,(w-sw)/2+shiftX,(h-sh)/2+shiftY,sw,sh);
   g.filter='none';
 }
 const rim=g.createRadialGradient(w*.5,h*.47,w*.2,w*.5,h*.47,w*.82);
 rim.addColorStop(0,'#00000000');rim.addColorStop(1,'#0309177c');
 g.fillStyle=rim;g.fillRect(0,0,w,h);
 // A previous 100% black fade at t=0 caused blank combat frames.
 // Keep each shot's artwork visible even on the exact edit boundary.
 const edge=Math.min(1,t/.055,(1-t)/.055);
 if(edge<1){g.globalAlpha=.08*Math.max(0,1-edge);
   g.fillStyle='#030714';g.fillRect(0,0,w,h)}
 g.globalAlpha=1;g.fillStyle='#071024';
 g.fillRect(0,0,w,22);g.fillRect(0,h-25,w,25);
 g.fillStyle='#dfebf4';g.font='600 12px Arial,sans-serif';
 g.fillText('ОСКОЛКИ ЗАБЫТОЙ КЛЯТВЫ',22,15);
 g.textAlign='right';g.fillText(shotKey==='impact'?'УДАР':shotKey==='detail'?'УЛИКА':'АНИМАТИК · ПЛАН',w-22,15);
 g.textAlign='left';g.restore();
}
v501SceneDraw=function(g,ei,scene,sec){
 const inPilot=ei>=0&&ei<2&&scene?.pilotV50&&P?.v502Director?.enabled;
 const index=inPilot?P.episodes[ei].scenes.indexOf(scene):-1;
 const total=Math.max(.1,Number(scene?.duration)||1);
 const frac=Math.min(.99999,Math.max(0,sec/total));
 const shot=inPilot?window.v502Director?.active(ei,index,sec):null;
 const plan=keyed[index],image=plan&&images[plan[shot]];
 const canCut=!!P?.v502CleanCuts?.enabled&&!!P?.v502Art?.enabled&&
              !!image?.complete&&!!image?.naturalWidth&&!!shot;
 if(!canCut)return before(g,ei,scene,sec);
 const shots=window.v502Director.shotPlan(scene.kind);
 const entry=shots.find(s=>s.kind===shot&&frac>=s.from&&frac<s.to);
 const t=entry?(frac-entry.from)/Math.max(.0001,entry.to-entry.from):.5;
 return opaqueCut(g,image,960,540,t,index,shot);
};
const previousSettings=v502Settings;
v502Settings=function(){
 previousSettings();
 if(!P)return;
 if(!P.v502CleanCuts)P.v502CleanCuts={enabled:true,quality:'ILLUSTRATED_STILLS_NOT_FRAME_ANIMATION'};
 const toggle=document.getElementById('v502-cleancuts');
 if(toggle)toggle.checked=!!P.v502CleanCuts.enabled;
};
const panel=document.getElementById('v502-panel');
if(panel){
 const label=document.createElement('label');
 label.style.cssText='display:flex;align-items:center;gap:8px;border:1px solid #70839d;padding:9px;margin:8px 0;border-radius:7px';
 label.innerHTML='<input id="v502-cleancuts" type="checkbox" style="width:auto"> CLEAN CUTS: убрать двойные силуэты на иллюстрированных планах';
 panel.appendChild(label);
 label.querySelector('input').addEventListener('change',function(){
  if(!P)return;
  P.v502CleanCuts={enabled:this.checked,quality:'ILLUSTRATED_STILLS_NOT_FRAME_ANIMATION'};
  save();if(typeof v48Draw==='function')v48Draw();
 });
}
window.v502CleanCutsQA=Object.freeze({
 loaded:()=>loaded,failed:()=>failed,keys:Object.keys(src),
 status:'TECHNICAL_PREVIEW_NOT_ART_FINAL',
 setEnabled:(enabled)=>{
  if(!P)return false;
  P.v502CleanCuts={...(P.v502CleanCuts||{}),enabled:!!enabled};
  const toggle=document.getElementById('v502-cleancuts');
  if(toggle)toggle.checked=!!enabled;
  return P.v502CleanCuts.enabled;
 },
 compare:(ei,time)=>{
  const ep=P?.episodes?.[ei];if(!ep)throw Error('Episode missing');
  const old=P.v502CleanCuts?.enabled;P.v502CleanCuts={enabled:true};
  try{const c=document.createElement('canvas');c.width=960;c.height=540;
      v35Frame(c,ep,time);if(typeof v37Paint==='function')v37Paint(c,ep,time);
      return c.toDataURL('image/png');}
  finally{P.v502CleanCuts.enabled=old;}
 }
});
if(P)v502Settings(); // Sync startup checkbox for preloaded offline pilot.
})();
