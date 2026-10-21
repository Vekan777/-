/* V50.2 ACTING: speaker-aware original art + blink + amplitude mouth,
 * no copied frames during battle. THIS IS NOT PHONEME-ALIGNED LIP SYNC. */
(function(){
'use strict';
const old=v35Frame, images={};
for(const [k,url] of Object.entries(window.v502IllustrationData||{})){
 const img=new Image();img.src=url;images[k]=img;
}
const portraits={
 'Акира':['akira','akira_power','akira_screaming'],
 'Мию':['miyu','miyu_worried'],'Рэн':['ren','ren_worried'],
 'Сайра':['saira','saira_detail'],'Архонт':['guardian']
};
const marks={akira:[132,143,[[148,75]]],akira_power:[170,85,[[126,39]]],
 akira_screaming:[150,81,[[136,41],[189,37]]],miyu:[206,153,[[150,118],[207,119]]],
 miyu_worried:[190,86,[[132,46],[194,47]]],ren:[117,145,[[125,108]]],
 ren_worried:[133,78,[[126,44]]],saira:[119,124,[[133,103]]],
 saira_detail:[198,78,[[169,48]]],guardian:[128,88,[[111,58],[149,56]]]};
const cast={hero:'Акира',miyu:'Мию',ren:'Рэн',saira:'Сайра',archon:'Архонт'};
const clamp=x=>Math.max(0,Math.min(1,x));
function view(episode,sec){const st=v35Find(episode,sec);if(!st?.row)return null;
 return {scene:st.row.scene,index:episode.scenes.indexOf(st.row.scene),
 local:Math.max(0,st.t-st.row.start),f:clamp((st.t-st.row.start)/
 Math.max(.01,st.row.scene.duration))};}
function speakerAt(scene,t){const v=scene.audioV36?.voice||{},offset=Number(v.offset)||0;
 const live=(v.segmentsV501||[]).find(s=>t>=offset+s.start&&t<offset+s.end);
 return live?cast[live.role]||'Акира':scene.lines?.[t<scene.duration*.5?0:1]?.speaker||'Акира';}
function v504Cue(scene,t,speaker){
 const role=Object.fromEntries(Object.entries(cast).map(([k,v])=>[v,k]))[speaker];
 const lip=scene.v504Lip?.cues||[];
 return lip.find(c=>c.role===role&&t>=c.start&&t<c.end)?.shape||null;
}
function energy(scene,t){const v=scene.audioV36?.voice||{},index=Math.floor(
 (t-(Number(v.offset)||0))*(Number(v.sampleRateV47)||50));
 return index<0?0:clamp(Number(v.waveV47?.[index])||0);}
let closeups=0,frames=0;const used={};
function portrait(ctx,scene,ei,si,t,f,speaker,amount,w,h){
 const choices=portraits[speaker]||portraits['Акира'];
 const alternate=(scene.kind==='romance'||scene.kind==='betrayal'||scene.kind==='ending')?1:0;
 const key=choices[(alternate+ei+si)%choices.length];
 const img=images[key];if(!img?.complete||!img.naturalWidth)return false;
 const z0=img.width/img.height<1.35?
 Math.min(w*.86/img.width,h*.88/img.height):Math.max(w*.95/img.width,h*.70/img.height);
 const breath=1+Math.sin(t*2.25+si)*.011+f*.034;
 const z=z0*breath,dw=img.width*z,dh=img.height*z;
 const x=Math.max(7,Math.min(w-dw-7,w*(si%2===0?.49:.53)-dw*.5+
 Math.sin(t*.43+ei)*w*.009));
 const y=(h-dh)*.53+Math.sin(t*.74)*h*.004;
 ctx.save();ctx.setTransform(1,0,0,1,0,0);
 ctx.fillStyle=scene.kind==='betrayal'?'#211a30':'#0b2035';ctx.fillRect(0,0,w,h);
 const back=Math.max(w/img.width,h/img.height)*1.09;
 ctx.globalAlpha=.21;ctx.filter='blur(16px) brightness(.70)';
 ctx.drawImage(img,(w-img.width*back)/2,(h-img.height*back)/2,
 img.width*back,img.height*back);
 ctx.filter='none';ctx.globalAlpha=1;ctx.drawImage(img,x,y,dw,dh);
 const p=marks[key];
 if(p){
  // Movement is aligned to the audio amplitude, not to text/phonemes.
  const [mx,my,eyes]=p;
  const blinkPhase=(t+si*1.9+ei*.8)%4.3;
  const blink=blinkPhase<.22?Math.sin(Math.PI*blinkPhase/.22):0;
  if(blink>.12){ctx.lineCap='round';ctx.strokeStyle=speaker==='Мию'?'#8e7294':'#332538';
   ctx.lineWidth=Math.max(1.4,z*1.9*blink);
   for(const [ex,ey] of eyes){ctx.beginPath();ctx.moveTo(x+(ex-8)*z,y+ey*z);
    ctx.quadraticCurveTo(x+ex*z,y+(ey+2)*z,x+(ex+8)*z,y+(ey-1)*z);ctx.stroke();}}
  const cue=v504Cue(scene,t,speaker);
  const poses={A:0,B:.21,C:.48,D:.77,E:.52,F:.34,G:.48,H:.71,X:0};
  const mouth=cue?poses[cue]:clamp((amount-.15)*1.6);
  if(mouth>.07){
   const ow=cue==='D'||cue==='H',ff=cue==='F'||cue==='G';
   const rx=Math.max(2,z*(ow?2.65:cue==='C'?5.5:3.7));
   const ry=Math.max(1,z*(.6+mouth*3.8));
   ctx.save();ctx.globalAlpha=mouth*.69;
   ctx.fillStyle=speaker==='Мию'||speaker==='Сайра'?'#883b59':'#4b2034';
   ctx.beginPath();ctx.ellipse(x+mx*z,y+(my+.5)*z,rx,ry,0,0,2*Math.PI);ctx.fill();
   if(ff){ctx.globalAlpha=.69*mouth;ctx.fillStyle='#edd9d4';
     ctx.fillRect(x+mx*z-rx*.6,y+my*z-ry*.35,rx*1.2,Math.max(1,ry*.38));}
   ctx.restore();
  }
 }
 // Spatially stable captions; actual subtitle text is drawn later by v37Paint.
 const fade=ctx.createLinearGradient(0,h*.75,0,h);fade.addColorStop(0,'#07101c00');
 fade.addColorStop(1,'#070f20d5');ctx.fillStyle=fade;ctx.fillRect(0,0,w,h);
 ctx.fillStyle='#071021';ctx.fillRect(0,0,w,h*.039);ctx.fillRect(0,h*.958,w,h*.042);
 ctx.fillStyle='#eff3fb';ctx.font='600 '+Math.max(11,Math.round(w*.014))+'px Arial';
 ctx.fillText('ОСКОЛКИ ЗАБЫТОЙ КЛЯТВЫ · АКТЁРСКИЙ ПЛАН',w*.027,h*.027);
 ctx.restore();
 used[key]=(used[key]||0)+1;closeups++;return true;
}
function contact(ctx,w,h,f){const impact=Math.max(0,Math.min(1,(f-.655)/.035))*
 (1-Math.max(0,Math.min(1,(f-.73)/.07)));
 if(impact<=.01)return;
 ctx.save();ctx.globalAlpha=impact;
 const x=w*.58,y=h*.51,r=ctx.createRadialGradient(x,y,2,x,y,w*.37);
 r.addColorStop(0,'#f6fcffc4');r.addColorStop(.23,'#b1f5ff55');
 r.addColorStop(1,'#3474e600');ctx.fillStyle=r;ctx.fillRect(0,0,w,h);
 ctx.lineCap='round';ctx.strokeStyle='#cafaff';
 for(let n=0;n<15;n++){const a=n*2.399,rr=w*(.06+.18*impact);
 ctx.lineWidth=(1+n%3)*w/960;ctx.beginPath();
 ctx.moveTo(x+Math.cos(a)*rr*.26,y+Math.sin(a)*rr*.26);
 ctx.lineTo(x+Math.cos(a)*rr,y+Math.sin(a)*rr);ctx.stroke();}
 ctx.restore();}
v35Frame=function(canvas,ep,seconds){
 const ei=P?.episodes?.indexOf(ep)??-1;
 const acting=!!P?.v502Acting?.enabled&&ei>=0&&ei<=5&&!!ep?.pilotV50;
 const state=acting?view(ep,seconds):null;
 let r;
 // Old ART/CLEAN CUTS layers re-showed the SAME still in every battle.
 // Temporarily bypass those layers for this synchronous frame only.
 // This reveals the actual joint-animated fighter; all settings restored.
 if(acting&&state?.scene?.kind==='fight'){
   const prevArt=P.v502Art?.enabled,prevClean=P.v502CleanCuts?.enabled;
   try{
     if(P.v502Art)P.v502Art.enabled=false;
     if(P.v502CleanCuts)P.v502CleanCuts.enabled=false;
     r=old(canvas,ep,seconds);
   }finally{
     if(P.v502Art)P.v502Art.enabled=prevArt;
     if(P.v502CleanCuts)P.v502CleanCuts.enabled=prevClean;
   }
 }else r=old(canvas,ep,seconds);
 if(!acting||!state)return r;
 frames++;const {scene,index,local,f}=state,ctx=canvas.getContext('2d');
 if(scene.kind==='fight'){contact(ctx,canvas.width,canvas.height,f);return r;}
 const shot=window.v502Director?.active(ei,index,local)||'wide';
 if(!['hero','partner','detail'].includes(shot))return r;
 portrait(ctx,scene,ei,index,local,f,speakerAt(scene,local),
 energy(scene,local),canvas.width,canvas.height);return r;
};
const panel=document.getElementById('v502-panel');
if(panel){const box=document.createElement('label');box.style.cssText=
 'display:flex;gap:8px;align-items:center;border:1px solid #6985a0;padding:9px;margin:10px 0';
 box.innerHTML='<input id="v502-acting-toggle" style="width:auto" type="checkbox"> ACTING: разные говорящие, моргание, движение рта и бой';
 panel.appendChild(box);const field=box.querySelector('input');
 field.onchange=()=>{if(!P)return;P.v502Acting={enabled:field.checked,
 artApproval:false,phonemeAligned:false};save();if(typeof v48Draw==='function')v48Draw();};
 const oldSettings=v502Settings;v502Settings=function(){oldSettings();
 if(P)field.checked=!!P.v502Acting?.enabled;};}
window.v502ActingQA=Object.freeze({status:'ANIMATIC_PREVIEW_NOT_TRUE_LIPSYNC',
 phonemeAligned:false,stats:()=>({frames,closeups,variants:{...used}}),
 speaker:(ei,si,t)=>speakerAt(P.episodes[ei].scenes[si],t),
 setEnabled:(v)=>{if(!P)return false;P.v502Acting={enabled:!!v,
 artApproval:false,phonemeAligned:false};return P.v502Acting.enabled;},
 frame:(ei,t,width=640)=>{const ep=P.episodes[ei],cv=document.createElement('canvas');
 cv.width=width;cv.height=Math.round(width*9/16);v35Frame(cv,ep,t);
 if(typeof v37Paint==='function')v37Paint(cv,ep,t);return cv.toDataURL('image/png');}});
if(P)v502Settings();
})();