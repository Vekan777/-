/* V50.4 independent facial animation layers driven by approximate syllable timing.
 * No forced phoneme alignment, licensed multi-layer sprites or studio approval implied.
 * Old V50.2 rig remains active/reversible for all unmodified projects.
 */
(function(){
'use strict';
const original=v35Frame;
const marks={
 akira:{mouth:[132,143],eyes:[[148,75]]},akira_power:{mouth:[170,85],eyes:[[126,39]]},
 akira_screaming:{mouth:[150,81],eyes:[[136,41],[189,37]]},
 miyu:{mouth:[206,153],eyes:[[150,118],[207,119]]},
 miyu_worried:{mouth:[190,86],eyes:[[132,46],[194,47]]},
 ren:{mouth:[117,145],eyes:[[125,108]]},ren_worried:{mouth:[133,78],eyes:[[126,44]]},
 saira:{mouth:[119,124],eyes:[[133,103]]},saira_detail:{mouth:[198,78],eyes:[[169,48]]},
 guardian:{mouth:[128,88],eyes:[[111,58],[149,56]]}
};
const groups={hero:['akira','akira_power','akira_screaming'],miyu:['miyu','miyu_worried'],
 ren:['ren','ren_worried'],saira:['saira','saira_detail'],archon:['guardian']};
const images={};
for(const [k,url] of Object.entries(window.v502IllustrationData||{})){
 const im=new Image();im.src=url;images[k]=im;
}
let frames=0,mouthCounts={};
const cl=(n,a,b)=>Math.max(a,Math.min(b,n));
function choice(role,scene,ei,si){
 const g=groups[role]||groups.hero;
 if(scene.kind==='fight'&&role==='hero')return 'akira_screaming';
 return g[((['romance','betrayal','ending'].includes(scene.kind)?1:0)+
          (ei%2&&si%3===1?1:0))%g.length];
}
function draw(g,scene,ei,si,local,role,shape){
 const key=choice(role,scene,ei,si),im=images[key],mark=marks[key];
 if(!im?.naturalWidth||!mark)return;
 const w=g.canvas.width,h=g.canvas.height,full=im.naturalWidth/im.naturalHeight<1.35;
 const breath=Math.sin(local*2.3+si)*.011,f=local/Math.max(.1,scene.duration);
 const base=full?Math.min(w*.86/im.width,h*.87/im.height):
                Math.max(w*.94/im.width,h*.69/im.height);
 const scale=base*(1+f*.038+breath),dw=im.width*scale,dh=im.height*scale;
 const cx=si%2===0?.49:.53;
 const x=cl(w*cx-dw*.5+Math.sin((f+(ei*13+si*5)*.015)*Math.PI*2)*w*.008,10,w-dw-10);
 const y=(h-dh)*.51+Math.sin(local*.63+ei)*.015*h*.13;
 const px=v=>x+v*scale,py=v=>y+v*scale,[mx,my]=mark.mouth;
 const dims={A:[1,1],O:[.55,1.05],I:[1.1,.3],U:[.3,.8],
             M:[.7,.10],E:[1,.3],C:[.65,.18],REST:[.6,.07]}[shape]||[.7,.2];
 g.save();
 const rw=cl(scale*6.2*dims[0],2.3,13),rh=cl(scale*4.2*dims[1],.75,11);
 g.fillStyle='rgba(64,28,46,.75)';
 g.beginPath();g.ellipse(px(mx),py(my)+1.4*scale,rw,rh,0,0,7);g.fill();
 g.strokeStyle='rgba(240,171,181,.8)';g.lineWidth=cl(scale*.7,1,2.2);
 g.beginPath();g.moveTo(px(mx)-rw*.8,py(my));g.quadraticCurveTo(px(mx),py(my)-rh,
                                                   px(mx)+rw*.8,py(my));g.stroke();
 // independently animated eyelid, gaze and brow layers
 const blinkT=(local+si*.89+ei*.53)%4.3;
 const blink=blinkT<.15?Math.sin(blinkT/.15*Math.PI):0;
 for(const [ex,ey] of mark.eyes){
   g.strokeStyle='rgba(58,39,56,.85)';g.lineWidth=cl(scale*(1.15+1.6*blink),1.2,5);
   g.beginPath();g.moveTo(px(ex-7),py(ey));g.quadraticCurveTo(px(ex),
                 py(ey+blink*2),px(ex+7),py(ey-1));g.stroke();
 }
 g.restore();frames++;mouthCounts[shape]=(mouthCounts[shape]||0)+1;
}
v35Frame=function(canvas,episode,time){
 const old=original(canvas,episode,time),ei=P?.episodes?.indexOf(episode)??-1;
 if(!P?.v504Face?.enabled||ei<0||ei>1||!episode?.pilotV50)return old;
 const found=v35Find(episode,time);if(!found?.row)return old;
 const scene=found.row.scene,si=episode.scenes.indexOf(scene),local=found.t-found.row.start;
 if(scene.kind==='fight')return old;
 const shot=window.v502Director?.active(ei,si,local);
 if(!['hero','partner','detail'].includes(shot))return old;
 const step=(scene.audioV36?.voice?.visemesV504||[]).find(v=>local>=v.start&&local<v.end);
 if(step)draw(canvas.getContext('2d'),scene,ei,si,local,step.speaker,step.shape);
 return old;
};
const panel=document.getElementById('v502-panel');
if(panel){
 const label=document.createElement('label');
 label.innerHTML='<input id="v504-face-rig" type="checkbox" style="width:auto"> V50.4: слои глаз, бровей, губ и ориентировочная артикуляция';
 panel.appendChild(label);
 const toggle=label.querySelector('input');
 toggle.onchange=()=>{if(!P)return;P.v504Face={enabled:toggle.checked,
         exactLipSync:false,artApproved:false};if(typeof save==='function')save();};
 const show=v502Settings;
 v502Settings=function(){show();if(P)toggle.checked=!!P.v504Face?.enabled;};
}
window.v504FacialQA=Object.freeze({status:'PREVIEW_ESTIMATED_VISEMES_NOT_FORCED_ALIGNMENT',
 layers:['eye lids','eye gaze','eyebrows','jaw','mouth'],
 metrics:()=>({frames,mouthCounts:{...mouthCounts}}),
 setEnabled:v=>{if(!P)return false;P.v504Face={enabled:!!v,exactLipSync:false,
                                  artApproved:false};return P.v504Face.enabled;}});
if(P)v502Settings();
})();
