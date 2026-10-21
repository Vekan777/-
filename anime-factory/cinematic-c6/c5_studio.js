/* C5 animation / Foley / Russian lines controls. Uses the existing C4 camera and 3D renderers. */
(function(root){'use strict';
const C=root.C4Core,M=root.C5Motion,A=root.C5Audio,$=id=>document.getElementById(id);
const get=()=>root.__C4_TEST__?.project;
let selectedRole='hero',selectedIndex=0,scorePlayer=null,scoreURL=null;
function msg(s){$('c5-pose-status').textContent=s}
function dl(blob,name){let url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),10000)}
function projectQA(){const p=get();if(!p)return;let e=C.validateProject(p);msg(e.length?'Ошибки: '+e.slice(0,8).join('; '):'Параметры движения сохранены в полном C5 JSON. Данные C1–C4 не перезаписываются.')}
function setMotion(){let p=get();if(!p)return;let e=M.validateConfig(p.motion,p.duration);if(e.length){msg('Ошибка: '+e.join('; '));return;}M.setConfig(p.motion);root.__C4_TEST__.renderScene();projectQA()}
function currentKeys(){return get()?.motion?.keys?.[selectedRole]||[]}
function redrawKeyMenu(){let keys=currentKeys(),sel=$('c5-key');sel.replaceChildren();keys.forEach((k,i)=>{let o=document.createElement('option');o.value=String(i);o.textContent=`${String(i+1).padStart(2,'0')}: ${k.t.toFixed(2)} с`;sel.appendChild(o)});selectedIndex=Math.max(0,Math.min(keys.length-1,selectedIndex));sel.value=String(selectedIndex);refreshChannels()}
function refreshChannels(){let k=currentKeys()[selectedIndex],area=$('c5-pose-fields');area.replaceChildren();if(!k)return;
 const labels={swing:'Замах / клинок',guard:'Защита / блок',step:'Шаг / перенос веса',crouch:'Приседание',lean:'Наклон корпуса',look:'Поворот головы'};
 for(let name of M.channels){let field=document.createElement('div');field.className='field';let lab=document.createElement('label');lab.textContent=labels[name]+' · ';let out=document.createElement('b');out.textContent=k[name].toFixed(2);lab.appendChild(out);let input=document.createElement('input');input.type='range';input.min=name==='crouch'||name==='guard'?0:-2;input.max=name==='crouch'||name==='guard'?1.5:2;input.step=.05;input.value=k[name];input.dataset.channel=name;input.addEventListener('input',()=>{k[name]=Number(input.value);out.textContent=k[name].toFixed(2);setMotion()});field.append(lab,input);area.appendChild(field)}
}
function refreshDialog(){const p=get(),sel=$('c5-line');sel.replaceChildren();for(let [i,subtitle] of p.subtitles.entries()){let op=document.createElement('option');op.value=String(i);op.textContent=`${subtitle.start.toFixed(1)}с ${subtitle.text.slice(0,34)}`;sel.appendChild(op)}sel.value='0';showDialog()}
function showDialog(){let p=get(),i=Number($('c5-line').value)||0,line=p.subtitles[i];if(!line)return;$('c5-text').value=line.text;$('c5-speaker').value=p.dialogue[i]?.speaker||'';}
function saveDialog(){let p=get(),i=Number($('c5-line').value)||0,text=$('c5-text').value.trim();if(!text){$('c5-audio-status').textContent='Текст реплики не может быть пустым';return;}p.subtitles[i].text=text;p.dialogue[i]={...p.subtitles[i],speaker:$('c5-speaker').value.trim()||'Персонаж'};refreshDialog();$('c5-line').value=String(i);showDialog();root.__C4_TEST__.renderScene();$('c5-audio-status').textContent='Русская реплика и субтитр сохранены в проекте.'}
function stopScore(){if(scorePlayer){scorePlayer.pause();scorePlayer=null}if(scoreURL){URL.revokeObjectURL(scoreURL);scoreURL=null}}
function startScore(t=0){stopScore();const p=get();if(!p?.audioScore?.enabled)return;scoreURL=URL.createObjectURL(A.wav(p.duration,p.audioScore.level));scorePlayer=new Audio(scoreURL);scorePlayer.currentTime=Math.max(0,Math.min(p.duration-.05,t));scorePlayer.play().catch(e=>{$('c5-audio-status').textContent='Браузер заблокировал автоматический звук: '+e.message});}
function refresh(){let p=get();if(!p)return;try{M.setConfig(p.motion)}catch(e){msg(e.message);return}
 $('c5-power').value=p.motion.intensity;$('c5-acting').value=p.motion.acting;$('c5-power-value').textContent=p.motion.intensity.toFixed(2);$('c5-acting-value').textContent=p.motion.acting.toFixed(2);
 $('c5-gain').value=p.audioScore?.level??.65;$('c5-gain-value').textContent=Number(p.audioScore?.level??.65).toFixed(2);$('c5-foley').checked=!!p.audioScore?.enabled;
 selectedRole=$('c5-actor').value||'hero';selectedIndex=0;redrawKeyMenu();refreshDialog();projectQA()}
function attach(){
 $('c5-actor').addEventListener('change',e=>{selectedRole=e.target.value;selectedIndex=0;redrawKeyMenu()});
 $('c5-key').addEventListener('change',e=>{selectedIndex=Number(e.target.value);refreshChannels();const k=currentKeys()[selectedIndex];if(k)root.__C4_TEST__.setTime(k.t)});
 for(let [id,name,out] of [['c5-power','intensity','c5-power-value'],['c5-acting','acting','c5-acting-value']])$(''+id).addEventListener('input',e=>{let p=get(),val=Number(e.target.value);p.motion[name]=val;$(out).textContent=val.toFixed(2);setMotion()});
 $('c5-add-key').addEventListener('click',()=>{try{let p=get(),t=Number($('scrub').value),idx=M.addKey(p.motion,selectedRole,t);selectedIndex=idx;redrawKeyMenu();setMotion();msg('Новый ключ создан: '+t.toFixed(2)+' с')}catch(e){msg('Нельзя добавить ключ: '+e.message)}});
 $('c5-delete-key').addEventListener('click',()=>{let keys=currentKeys();if(keys.length<=2){msg('Два ключа обязательны');return}keys.splice(selectedIndex,1);selectedIndex=Math.max(0,selectedIndex-1);redrawKeyMenu();setMotion()});
 $('c5-pose-export').addEventListener('click',()=>dl(new Blob([JSON.stringify(get().motion,null,2)],{type:'application/json'}),'C5_JOINT_ANIMATION.json'));
 $('c5-line').addEventListener('change',showDialog);$('c5-line-save').addEventListener('click',saveDialog);
 $('c5-speak').addEventListener('click',()=>{try{A.speakRussian($('c5-text').value);$('c5-audio-status').textContent='Речь ru-RU воспроизводится браузером, НЕ записывается в WebM. Для видео импортируйте WAV/MP3.'}catch(e){$('c5-audio-status').textContent=e.message}});
 $('c5-gain').addEventListener('input',e=>{let p=get();p.audioScore.level=Number(e.target.value);$('c5-gain-value').textContent=p.audioScore.level.toFixed(2);stopScore();projectQA()});
 $('c5-foley').addEventListener('change',e=>{get().audioScore.enabled=e.target.checked;stopScore();projectQA()});
 $('c5-wav').addEventListener('click',()=>dl(A.wav(get().duration,get().audioScore.level),'C5_ORIGINAL_BATTLE_FOLEY.wav'));
 $('c5-preview').addEventListener('click',()=>{startScore(0);$('c5-audio-status').textContent='Проигрывается синтезированная дорожка боя: звуки без русских голосов.'});
}
try{if(!get())throw Error('C4 base editor not initialized');attach();refresh();root.C5Studio={refresh,stopScore,startScore,get project(){return get()}};}catch(e){console.error('C5 controls failed',e);let k=$('c5-pose-status');if(k)k.textContent='Ошибка C5: '+e.message}
})(window);
