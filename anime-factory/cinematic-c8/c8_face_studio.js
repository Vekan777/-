/* CINEMATIC C8 original facial morph targets + Russian audio driven jaw envelope.
 * The audio-driven amplitude envelope is produced by batch_render_c8.py.
 * Text timing fallback is approximate and MUST NOT be called phoneme-accurate.
 */
(function(root){'use strict';
const clamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v)), $=id=>document.getElementById(id);
function state(project){if(!project)return{};if(!project.c8Facial)project.c8Facial={enabled:true,material:'etched',strength:1,expression:'focused'};return project.c8Facial}
function lineBelongs(line,role){let sp=String(line.speaker||'').toLowerCase().trim();if(!sp)return role==='hero';return role==='hero'?(/аран|герой|hero|мечник|главн/.test(sp)):(/страж|enemy|враг|противник|монстр/.test(sp))}
function sampleTrack(track,time){if(!Array.isArray(track)||!track.length)return null;if(time<track[0][0]||time>track[track.length-1][0])return 0;let l=0,h=track.length-1;while(l<h){let m=(l+h)>>1;if(track[m][0]<time)l=m+1;else h=m}let q=track[l],p=track[Math.max(0,l-1)],u=q[0]===p[0]?0:(time-p[0])/(q[0]-p[0]);return clamp((p[1]+(q[1]-p[1])*u)*1.08)}
function heuristic(project,time,role){let lines=project?.dialogue||project?.subtitles||[];for(let l of lines){if(!lineBelongs(l,role)||time<l.start||time>l.end)continue;let txt=String(l.text||''),duration=l.end-l.start;if(!txt||!duration)return 0;let u=clamp((time-l.start)/duration),characters=[...txt].filter(c=>/[а-яё]/i.test(c));let c=characters[Math.min(characters.length-1,Math.floor(u*characters.length))]||'';if(!c)return 0;let wide=/[аоэеыя]/i.test(c)?0.74:/[уию]/i.test(c)?.55:/[бпмфв]/i.test(c)?.15:.36;return clamp(wide*(.84+.16*Math.sin(time*14)));}return 0}
function weights(project,time,role,model){let conf=state(project),count=model?.morphCount||0,defaultWeights=model?.doc?.meshes?.[0]?.weights||[];if(!conf.enabled||!count)return defaultWeights.slice();let tr=conf.audioTracks?.[role];let jaw=sampleTrack(tr,time);if(jaw===null)jaw=heuristic(project,time,role);let blink=.0,cycle=(time+(role==='enemy'?1.3:0))%4.3;if(cycle>3.81&&cycle<4.04)blink=Math.sin((cycle-3.81)/.23*Math.PI);let frown=conf.expression==='anger'?.93:conf.expression==='focused'?.28:0;let names=model.morphNames||[];return Array.from({length:count},(_,i)=>{let n=String(names[i]||['MouthOpen','Blink','BrowFrown'][i]||'').toLowerCase();return clamp(n.includes('mouth')||n.includes('jaw')?jaw*(conf.strength??1):n.includes('blink')||n.includes('eyeclose')?blink:n.includes('brow')||n.includes('frown')?frown:Number(defaultWeights[i])||0)})}
function materialMode(project){return state(project).material||'flat'}
function probe(project,role){let encoded=project?.c7Rig?.[role]?.base64||root.C7EmbeddedModels?.[role];let m=root.C7Rig.parse64(encoded);return {name:m.name,joints:m.joints.length,triangles:m.total,morphs:m.morphCount,names:m.morphNames}}
function init(){if(!root.__C4_TEST__||!$('c8-status'))return;let api=root.__C4_TEST__;const cfg=()=>state(api.project),redraw=()=>api.renderScene();
$('c8-face-enabled').onchange=e=>{cfg().enabled=e.target.checked;redraw();audit()};
$('c8-face-strength').oninput=e=>{cfg().strength=Number(e.target.value);$('c8-strength-value').textContent=e.target.value;redraw()};
$('c8-expression').onchange=e=>{cfg().expression=e.target.value;redraw()};
$('c8-material').onchange=e=>{cfg().material=e.target.value;redraw()};
$('c8-audit').onclick=audit;
function audit(){try{const a=probe(api.project,'hero'),b=probe(api.project,'enemy'),p=cfg();let problems=[];
for(let x of[a,b]){if(!x.morphs)problems.push(x.name+': нет facial morph targets; без морфов lip-sync НЕ сработает');if(x.triangles<5000)problems.push(x.name+': стилизованная низкая геометрическая детализация (<5000 треугольников)');}
let timed=p.audioTracks&&(p.audioTracks.hero?.length||p.audioTracks.enemy?.length);
$('c8-status').textContent=`Герой: ${a.joints} костей / ${a.triangles} треугольников / ${a.morphs} facial morphs\nПротивник: ${b.joints} костей / ${b.triangles} треугольников / ${b.morphs} facial morphs\nLip-sync: ${timed?'по амплитуде синтезированного аудио (НЕ фонемный)':'приблизительно по буквам текста (в браузере)'}\nРежим материала: ${p.material}\n`+(problems.length?'Требует доработки:\n'+problems.join('\n'):'Структурно поддерживает facial morphs; художественная приёмка не пройдена');}
catch(e){$('c8-status').textContent='C8 QA: '+e.message}}
let p=cfg();$('c8-face-enabled').checked=p.enabled!==false;$('c8-face-strength').value=p.strength??1;$('c8-strength-value').textContent=String(p.strength??1);$('c8-expression').value=p.expression||'focused';$('c8-material').value=p.material||'etched';$('c6-scene').addEventListener('change',()=>setTimeout(audit,0));audit()}
root.C8Face={state,weights,sampleTrack,heuristic,materialMode,probe,init};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})(window);
