/* Original offline procedurally synthesized battle Foley (not Russian voice generation). */
(function(root){'use strict';
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
const HITS=[{t:2.65,type:'dash'},{t:4.43,type:'slash'},{t:5.62,type:'metal'},{t:7.5,type:'dash'},{t:9.85,type:'slash'},{t:11.35,type:'metal'},{t:12.18,type:'slash'},{t:13.56,type:'impact'}];
const rate=22050;
function render(duration=16,level=.65){duration=clamp(duration,1,120);level=clamp(level,0,1);const n=Math.ceil(duration*rate),data=new Float32Array(n);let seed=2398571;const noise=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return(seed/4294967295)*2-1};
 const notes=[55,69.3,82.4,73.4];for(let i=0;i<n;i++){let t=i/rate,drone=Math.sin(2*Math.PI*notes[0]*t)*.037+Math.sin(2*Math.PI*notes[1]*t)*.019;let pulse=(Math.sin(Math.PI*2*t*.87)>.81?.018:0)*Math.sin(2*Math.PI*notes[2]*t);data[i]=drone+pulse;}
 for(const {t,type} of HITS){let onset=Math.floor(t*rate),period=type==='dash'?.4:type==='impact'?.70:.5;
  for(let k=0;k<period*rate&&onset+k<n;k++){let sec=k/rate,env=Math.exp(-sec*(type==='impact'?7:13));let nse=noise(),s=0;
   if(type==='dash')s=nse*.14*Math.sin(Math.PI*sec/period)+Math.sin(2*Math.PI*(310-210*sec/period)*sec)*.04;
   if(type==='slash')s=nse*.27+Math.sin(2*Math.PI*(900-600*sec/period)*sec)*.1;
   if(type==='metal')s=Math.sin(2*Math.PI*1172*sec)*.28+Math.sin(2*Math.PI*1763*sec)*.17+nse*.07;
   if(type==='impact')s=nse*.26+Math.sin(2*Math.PI*(80-35*sec)*sec)*.4;
   data[onset+k]+=env*s;
  }
 }
 for(let i=0;i<n;i++)data[i]=Math.tanh(data[i]*1.65)*level;return data;}
function wav(duration=16,level=.65){const pcm=render(duration,level),b=new ArrayBuffer(44+pcm.length*2),v=new DataView(b),text=(p,s)=>{for(let i=0;i<s.length;i++)v.setUint8(p+i,s.charCodeAt(i))};
 text(0,'RIFF');v.setUint32(4,b.byteLength-8,true);text(8,'WAVE');text(12,'fmt ');v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,1,true);v.setUint32(24,rate,true);v.setUint32(28,rate*2,true);v.setUint16(32,2,true);v.setUint16(34,16,true);text(36,'data');v.setUint32(40,pcm.length*2,true);
 for(let i=0;i<pcm.length;i++)v.setInt16(44+2*i,Math.round(clamp(pcm[i],-1,1)*32767),true);return new Blob([b],{type:'audio/wav'});}
function buffer(ctx,duration=16,level=.65){const pcm=render(duration,level),a=ctx.createBuffer(1,pcm.length,rate);a.copyToChannel(pcm,0);return a;}
function playInto(ctx,destination,duration=16,level=.65){const s=ctx.createBufferSource();s.buffer=buffer(ctx,duration,level);s.connect(destination);s.start(0);return s;}
function speakRussian(text){if(!root.speechSynthesis||!root.SpeechSynthesisUtterance)throw Error('Браузер не поддерживает speechSynthesis');root.speechSynthesis.cancel();let u=new SpeechSynthesisUtterance(text);u.lang='ru-RU';u.rate=.93;root.speechSynthesis.speak(u);return u;}
root.C5Audio={rate,HITS,render,wav,buffer,playInto,speakRussian};
})(typeof window!=='undefined'?window:globalThis);
