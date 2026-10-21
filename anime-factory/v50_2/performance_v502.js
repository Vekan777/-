/* V50.2 performance pass: 6 episodes, original generated particles/light,
 * scene-specific action beats, expressive portrait camera. Procedural art,
 * NOT facial-rig animation or licensed actor recording.
 */
(function(){
'use strict';
const previous=v35Frame;
const pal=[['#79b9f4','#ca85fa'],['#f5b487','#83ddf7'],
 ['#9dafff','#6cdbc6'],['#f8ad7c','#ec8292'],
 ['#86ddba','#b984f1'],['#d3b6ee','#a4e4ff']];
const clamp=x=>Math.max(0,Math.min(1,x));
const hash=x=>{let h=Math.sin(x*127.1+19.7)*43758.5453;return h-Math.floor(h);};
function find(ep,time){
 const f=v35Find(ep,time);if(!f?.row)return null;
 const scene=f.row.scene,start=f.t-f.row.start;
 return {scene,index:ep.scenes.indexOf(scene),sec:Math.max(0,start),
         fraction:clamp(start/Math.max(.01,scene.duration))};
}
function particles(g,w,h,t,ei,si,kind){
 g.save();
 const N=kind==='fight'?35:kind==='betrayal'?22:16;
 for(let i=0;i<N;i++){
  const seed=(ei+1)*27+(si+1)*13+i*9;
  const x=((hash(seed*2)+t*(kind==='fight'?.071:.016)*(i%3+1))%1)*w;
  const y=((hash(seed*3)-t*.012*(i%4+1))%1+1)%1*h;
  const size=(.5+hash(seed*5)*2.2)*w/960;
  g.globalAlpha=(kind==='fight'?.17:.09)*(.8+Math.sin(t+i)**2);
  g.fillStyle=i%4===0?pal[ei][1]:pal[ei][0];
  g.beginPath();g.ellipse(x,y,size,size*(kind==='fight'?2.6:1.1),
                           -.14,0,Math.PI*2);g.fill();
 }
 g.restore();
}
function impact(g,w,h,t,ei,si,f){
 const beat=f>.6&&f<.82?Math.sin((f-.6)/.22*Math.PI):0;
 if(beat<=0)return;
 const cx=w*.59,cy=h*.57;
 g.save();g.globalAlpha=beat*.28;g.lineCap='round';
 const glow=g.createRadialGradient(cx,cy,0,cx,cy,w*.38);
 glow.addColorStop(0,'#f2f9ff5e');glow.addColorStop(.45,pal[ei][0]+'29');
 glow.addColorStop(1,pal[ei][0]+'00');g.fillStyle=glow;g.fillRect(0,0,w,h);
 g.shadowColor='#d6f6ff';g.shadowBlur=w*.008;
 for(let i=0;i<14;i++){
  const a=hash(ei*31+si*17+i)*Math.PI*2;
  const rr=w*(.06+.21*beat)*(1+hash(i+22)*.4);
  g.lineWidth=(1+i%3)*w/960;g.strokeStyle=i%4?'#a1efff':'#ffedb9';
  g.beginPath();g.moveTo(cx+Math.cos(a)*rr*.34,cy+Math.sin(a)*rr*.34);
  g.lineTo(cx+Math.cos(a)*rr,cy+Math.sin(a)*rr);g.stroke();
 }
 g.restore();
}
function sceneAccent(g,w,h,t,ei,si,st){
 const f=st.fraction,kind=st.scene.kind;
 if(kind==='fight')return impact(g,w,h,t,ei,si,f);
 if(kind==='betrayal'){
  g.save();g.strokeStyle=pal[ei][1];g.lineWidth=w/1200;
  g.globalAlpha=.07+.045*Math.sin(t*2)**2;
  for(let i=0;i<7;i++){
   const x=w*(.81+.16*hash(i+si)),y=h*(.15+.7*hash(i*3+ei));
   const d=w*(.01+.007*hash(i*9));
   g.beginPath();g.moveTo(x,y-d);g.lineTo(x+d*.5,y+d);
   g.lineTo(x-d*.6,y+d*.6);g.closePath();g.stroke();
  }g.restore();
 }else if(kind==='opening'||kind==='ending'){
  g.save();g.translate(w*.77,h*.52);g.rotate(t*.08);
  g.globalAlpha=kind==='ending'?.065:.038;
  g.strokeStyle=pal[ei][0];g.lineWidth=w/850;
  for(let i=0;i<2;i++){
   g.setLineDash(i?[3,9]:[9,6]);
   g.beginPath();g.arc(0,0,w*(.08+i*.035),0,Math.PI*2);g.stroke();
  }g.restore();
 }else if(kind==='romance'){
  const shade=g.createLinearGradient(0,h*.23,w,h*.79);
  shade.addColorStop(0,'#ffd1ad00');shade.addColorStop(.62,'#ffd1ad11');
  shade.addColorStop(1,'#ffd1ad00');
  g.fillStyle=shade;g.fillRect(0,0,w,h);
 }
}
v35Frame=function(canvas,episode,sec){
 const result=previous(canvas,episode,sec);
 const ei=P?.episodes?.indexOf(episode)??-1;
 if(!P?.v502Performance?.enabled||ei<0||ei>5||
    !P?.v502MotionRig?.enabled||!episode?.pilotV50)return result;
 const st=find(episode,sec);if(!st)return result;
 const g=canvas.getContext('2d'),w=canvas.width,h=canvas.height;
 g.save();g.setTransform(1,0,0,1,0,0);
 particles(g,w,h,st.sec,ei,st.index,st.scene.kind);
 sceneAccent(g,w,h,st.sec,ei,st.index,st);
 g.restore();
 return result;
};
const panel=document.getElementById('v502-panel');
if(panel){
 const label=document.createElement('label');
 label.style.cssText='display:flex;align-items:center;gap:8px;padding:10px;border:1px solid #738fa3;margin:8px 0';
 label.innerHTML='<input id="v502-performance-toggle" type="checkbox" style="width:auto"> PERFORMANCE: атмосфера, свет, боевые акценты во всех шести сериях';
 panel.appendChild(label);
 const toggle=label.querySelector('input'),oldSettings=v502Settings;
 v502Settings=function(){oldSettings();if(P)toggle.checked=!!P.v502Performance?.enabled;};
 toggle.onchange=()=>{if(!P)return;
  P.v502Performance={enabled:toggle.checked,artApproval:false,
    status:'TECHNICAL_2D_ANIMATIC_NOT_STUDIO_FINAL'};
  save();if(typeof v48Draw==='function')v48Draw();
 };
 if(P)v502Settings();
}
window.v502PerformanceQA=Object.freeze({
 status:'TECHNICAL_2D_EFFECTS_NOT_PROFESSIONAL_CHARACTER_ANIMATION',
 enabled:()=>!!P?.v502Performance?.enabled,
 setEnabled:enabled=>{
  if(!P)return false;
  P.v502Performance={enabled:!!enabled,artApproval:false,
    status:'TECHNICAL_2D_ANIMATIC_NOT_STUDIO_FINAL'};
  const input=document.getElementById('v502-performance-toggle');
  if(input)input.checked=!!enabled;
  return !!enabled;},
 active:(ep,time)=>{const e=P?.episodes?.[ep];return e?find(e,time):null;},
 frame:(ep,time,width=960)=>{
  const e=P?.episodes?.[ep];if(!e)throw Error('No staged episode');
  const c=document.createElement('canvas');c.width=width;c.height=Math.round(width*9/16);
  v35Frame(c,e,time);
  if(typeof v37Paint==='function')v37Paint(c,e,time);
  return c.toDataURL('image/png');}
});
})();
