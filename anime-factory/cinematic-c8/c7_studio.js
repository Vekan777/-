/* C7 visual studio for true skinned GLB/auto Russian TTS in episode batch.
 * No plugins, external imports or fake artwork. Every GLB is retained within scene JSON. */
(function(root){'use strict';const $=id=>document.getElementById(id),api=root.__C4_TEST__,K=root.C7Rig;
if(!api||!K)throw Error('C7 requires C4/C5/C6 studios');
const choice={hero:'Герой',enemy:'Противник'};
function state(){let p=api.project;if(!p.c7Rig)p.c7Rig={enabled:true};if(!p.c7Voice)p.c7Voice={enabled:true,volume:.85};return p;}
function log(s){$('c7-status').textContent=s}
function refresh(){const p=state();$('c7-rig-enabled').checked=p.c7Rig.enabled!==false;$('c7-voice-enabled').checked=p.c7Voice.enabled!==false;$('c7-voice-volume').value=String(p.c7Voice.volume??.85);$('c7-voice-number').textContent=String(Number(p.c7Voice.volume??.85).toFixed(2));
let lines=[];for(const name of['hero','enemy']){try{let m=K.parse64(p.c7Rig[name]?.base64||root.C7EmbeddedModels[name]);lines.push(`${choice[name]}: ${m.joints.length} костей / ${m.total} полигонов / ${m.tracks.length} анимационных каналов`)}catch(e){lines.push(`${choice[name]}: ОШИБКА ${e.message}`)}}$('c7-model-report').textContent=lines.join('\n');}
function currentRig(){return state().c7Rig}
function arrayToB64(bytes){let out='';for(let i=0;i<bytes.length;i+=16000)out+=String.fromCharCode(...bytes.subarray(i,i+16000));return btoa(out)}
async function importFile(file,side){if(!file)return;try{
if(!file.name.toLowerCase().endsWith('.glb'))throw Error('Только один бинарный файл .glb glTF 2.0 с костями; OBJ не имеет skinning');
if(file.size>4*1024*1024)throw Error('Для слабого ПК установлено ограничение 4 МБ на модель');
const bytes=new Uint8Array(await file.arrayBuffer()),m=K.parseBytes(bytes),encoded=arrayToB64(bytes);
const src=state().c7Rig,updated={...src,[side]:{base64:encoded,file:file.name,joints:m.joints.length,triangles:m.total},enabled:true};
if(JSON.stringify(root.C6Studio.project).length+encoded.length>39_000_000)throw Error('Размер полного сезона достиг лимита 40 МБ');
api.project.c7Rig=updated;api.renderScene();refresh();log(`${file.name} импортирован: ${m.joints.length} костей, ${m.total} треугольников; модель сохранена в полной JSON сцены`);
}catch(e){log('Импорт модели отклонён, предыдущая сохранена: '+e.message)}}
for(const side of['hero','enemy']){
$('c7-model-'+side).addEventListener('change',async e=>{const f=e.target.files?.[0];if(f)await importFile(f,side);e.target.value=''});
$('c7-reset-'+side).addEventListener('click',()=>{delete currentRig()[side];api.renderScene();refresh();log('Восстановлен оригинальный 3D-персонаж с настоящим скелетом')});}
$('c7-rig-enabled').addEventListener('change',e=>{currentRig().enabled=e.target.checked;api.renderScene();refresh();log(e.target.checked?'Скелетные GLB-модели включены':'Переключение на старые процедурные C5-риги')});
$('c7-voice-enabled').addEventListener('change',e=>{state().c7Voice.enabled=e.target.checked;log(e.target.checked?'Автосинтез русской речи ВКЛЮЧЁН для пакетного MP4':'Синтез русской речи выключен для этой сцены')});
$('c7-voice-volume').addEventListener('input',e=>{state().c7Voice.volume=Number(e.target.value);refresh()});
$('c7-preview-ru').addEventListener('click',()=>{const p=api.project;const d=(p.dialogue||p.subtitles||[])[0];if(!d){log('Добавьте реплику в панели C5');return}if(!('speechSynthesis' in root)){log('Браузер не предоставляет TTS; пакетный TTS всё равно работает при установленном eSpeak NG');return}let utt=new SpeechSynthesisUtterance(d.text);utt.lang='ru-RU';utt.rate=.9;let voice=speechSynthesis.getVoices().find(v=>v.lang.toLowerCase().startsWith('ru'));if(voice)utt.voice=voice;speechSynthesis.cancel();speechSynthesis.speak(utt);log('Браузерное прослушивание (НЕ записывается в WebM). Реальная речь в MP4: RUN_BATCH_WINDOWS.bat через русский offline TTS.')});
$('c7-audit').addEventListener('click',()=>{refresh();let p=api.project,r=C7Rig.lastError;log((r?'Рендер замечание: '+r+'\n':'')+'GLB-риггинг: '+$('c7-model-report').textContent+'\nАвтоголос: '+(p.c7Voice?.enabled!==false?'включён':'выключен')+' (синтезируется в MP4 пакетным скриптом).')});
['c6-ep','c6-scene'].forEach(x=>$(x).addEventListener('change',()=>setTimeout(refresh,0)));
refresh();log('C7: 14-костные оригинальные GLB загружены. Можно импортировать собственные анимированные GLB с весами. Озвучка автоматически формируется в пакетном MP4 при наличии eSpeak NG или Piper.');
root.C7Studio={refresh,importFile,state,model:()=>K.parse64(root.C7EmbeddedModels.hero)};
})(window);
