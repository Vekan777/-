/* V50.2 Season Story Stage: scenes 3-6 use actual director/rig when scripted.
 * First two episodes and non-pilot projects retain the prior renderer.
 * Illustration closeups remain STILL art, not animated anime performances.
 */
(function(){
'use strict';
const fallbackFrame=v35Frame;
const gallery=Object.create(null);
for(const [key,url] of Object.entries(window.v502IllustrationData||{})){
 const img=new Image();gallery[key]=img;img.src=url;
}
const castRole={hero:'hero',miyu:'lover',ren:'friend',saira:'rival',archon:'enemy'};
const keyRole={hero:'akira',lover:'miyu',friend:'ren',rival:'saira',enemy:'guardian'};
function actorsFor(scene,si){
 if(si===2){
  const have=(scene.scriptV502?.roleOrder||[]).includes('archon');
  return [['hero',.30],[have?'enemy':'guardian',.75]];
 }
 const roles=scene.scriptV502?.roleOrder||[];
 const first=castRole[roles[0]]||'hero',second=castRole[roles[1]]||'lover';
 return [[first,.34],[second,.68]];
}
function seasonArt(g,episode,scene,t,pairs){
 if(!P?.v502Art?.enabled||!P?.v502CleanCuts?.enabled)return;
 const shots=window.v502Director?.shotPlan(scene.kind)||[];
 const f=Math.max(0,Math.min(.999, t/Math.max(.01,scene.duration)));
 const active=shots.find(x=>f>=x.from&&f<x.to);
 if(!active || !['hero','partner','over','impact'].includes(active.kind))return;
 const key=active.kind==='hero'?keyRole[pairs[0][0]]:
   active.kind==='partner'?keyRole[pairs[1][0]]:
   active.kind==='impact'?'battle':(episode===4?'portal':'world');
 const img=gallery[key];if(!img?.complete||!img?.naturalWidth)return;
 const local=(f-active.from)/Math.max(.0001,active.to-active.from);
 const W=960,H=540;
 g.save();g.globalAlpha=1;
 const fill=Math.max(W/img.naturalWidth,H/img.naturalHeight)*(1.02+local*.018);
 const cw=img.naturalWidth*fill,ch=img.naturalHeight*fill;
 g.fillStyle='#091223';g.fillRect(0,0,W,H);
 if(['world','portal','battle'].includes(key)){
  g.drawImage(img,(W-cw)/2,(H-ch)/2,cw,ch);
 }else{
  g.save();g.filter='blur(17px) brightness(.41)';
  g.drawImage(img,(W-cw)/2,(H-ch)/2,cw,ch);g.restore();
  const contain=Math.min((W-115)/img.naturalWidth,(H-58)/img.naturalHeight);
  const iw=img.naturalWidth*contain,ih=img.naturalHeight*contain;
  const x=active.kind==='hero'?W*.17:W*.67;
  g.drawImage(img,Math.max(5,Math.min(W-iw-5,x-iw*.48)),(H-ih)*.51,iw,ih);
 }
 g.fillStyle='#071225';g.fillRect(0,0,W,22);g.fillRect(0,H-25,W,25);
 g.font='600 12px sans-serif';g.fillStyle='#e9eef9';
 g.fillText('ОСКОЛКИ ЗАБЫТОЙ КЛЯТВЫ · СЦЕНАРНЫЙ АНИМАТИК',20,15);
 g.restore();
}
function drawStaged(g,ei,scene,time){
 const si=P.episodes[ei].scenes.indexOf(scene);
 const pairs=actorsFor(scene,si);
 // The legacy director/MOTION layer queries this mutable stage function.
 // Switch it only during this one synchronous draw, restore afterwards.
 const originalCast=v502Cast;
 try{
  v502Cast=()=>pairs;
  v502Scene(g,ei,scene,time);
 }finally{v502Cast=originalCast;}
 seasonArt(g,ei,scene,time,pairs);
}
v35Frame=function(canvas,episode,seconds){
 const ei=P?.episodes?.indexOf(episode)??-1;
 if(!P?.seasonScriptV502 || !P?.v502SeasonStage?.enabled ||
    ei<2 || ei>5 || !episode?.pilotV50)
    return fallbackFrame(canvas,episode,seconds);
 const state=v35Find(episode,seconds),g=canvas.getContext('2d');
 g.save();g.setTransform(1,0,0,1,0,0);
 g.clearRect(0,0,canvas.width,canvas.height);
 g.scale(canvas.width/960,canvas.height/540);
 if(state.row)drawStaged(g,ei,state.row.scene,
                         Math.max(0,Math.min(state.row.duration,state.t-state.row.start)));
 g.restore();
 if(typeof v48DrawCredits==='function')v48DrawCredits(canvas,episode,seconds);
 return state;
};
const originalSubtitles=v37Paint;
v37Paint=function(canvas,episode,seconds){
 const ei=P?.episodes?.indexOf(episode)??-1;
 if(ei<2||ei>5||!P?.seasonScriptV502||!P?.v502SeasonStage?.enabled)
   return originalSubtitles(canvas,episode,seconds);
 const active=v37Active(episode,seconds).slice(0,1);
 if(!active.length)return active;
 const g=canvas.getContext('2d'),w=canvas.width,h=canvas.height,scale=w/640;
 const sub=active[0].text;
 g.save();g.setTransform(1,0,0,1,0,0);
 g.font='600 '+Math.max(13,Math.round(19*scale))+'px Segoe UI,Arial,sans-serif';
 const lines=v37Lines(g,sub,w*.81,2),lh=27*scale;
 const bh=(lines.length*lh)+12*scale,top=h-18*scale-bh;
 g.fillStyle='rgba(3,10,24,.70)';
 g.fillRect(w*.09,top,w*.82,bh);
 g.textBaseline='middle';g.textAlign='center';g.fillStyle='#fff';
 g.shadowColor='#000';g.shadowBlur=3*scale;
 for(let i=0;i<lines.length;i++)g.fillText(lines[i],w/2,top+11*scale+(i+.5)*lh);
 g.restore();return active;
};
const panel=document.getElementById('v502-panel');
if(panel){
 const holder=document.createElement('label');
 holder.style.cssText='display:flex;align-items:center;gap:8px;padding:8px;border:1px solid #788ba6;margin:8px 0';
 holder.innerHTML='<input type="checkbox" id="v502-seasonstage-toggle" style="width:auto"> Поставить серии 3–6: герои, суставы, крупные планы и русский текст';
 panel.appendChild(holder);
 const input=holder.querySelector('input');
 const oldSettings=v502Settings;
 v502Settings=function(){oldSettings();if(P)input.checked=!!P.v502SeasonStage?.enabled};
 input.onchange=()=>{if(!P)return;
  P.v502SeasonStage={enabled:input.checked,scriptStatus:'DRAFT'};save();
  if(typeof v48Draw==='function')v48Draw();};
 if(P)v502Settings();
}
window.v502SeasonStageQA=Object.freeze({
 version:'V50.2 screenplay stage',professionalArtApproved:false,
 actorsFor:(episode,scene)=>actorsFor(P.episodes[episode].scenes[scene],scene),
 active:()=>!!P?.seasonScriptV502&&!!P?.v502SeasonStage?.enabled,
 sourceEpisodes:[3,4,5,6]
});
})();