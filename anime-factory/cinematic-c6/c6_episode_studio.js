/* C6 integrated nonlinear edit and timed whole-episode playback.
   Do not overwrite prior episode scene before successfully loading a new one. */
(function(root){'use strict';
const K=root.C6Core,api=root.__C4_TEST__,$=id=>document.getElementById(id);
if(!K||!api)throw Error('C6: сначала должны загрузиться C5 Studio + EpisodeCore');
let pack=K.demo(api.project),epIndex=0,sceneIndex=0,active=null,watching=false,playhead=0,prevTime=0,lastRender=0;
const clone=K.clone;
function report(s){$('c6-status').textContent=s}
function episode(){return pack.episodes[epIndex]}
function scene(){return episode().scenes[sceneIndex]}
function captureActive(){if(active){let e=pack.episodes[active.ep],s=e?.scenes[active.sc];if(s&&s.id===active.id)s.project=clone(api.project);}}
function loadScene(e=epIndex,s=sceneIndex){let target=pack.episodes[e]?.scenes[s];if(!target)throw Error('Нет такой сцены');
  let previous=active,previousData=previous&&pack.episodes[previous.ep]?.scenes[previous.sc]?.project;
  if(previous&&previous.id===target.id){epIndex=e;sceneIndex=s;return;}
  captureActive();try{api.stopPlayback();api.loadCandidate(target.project);}
  catch(error){if(previous&&previousData){try{api.loadCandidate(previousData)}catch(_e){}}throw error}
  epIndex=e;sceneIndex=s;active={ep:e,sc:s,id:target.id};root.C5Studio?.refresh();
}
function paintMenus(){let p=$('c6-ep'),s=$('c6-scene');p.replaceChildren();pack.episodes.forEach((e,i)=>{let opt=new Option(e.name,String(i));p.add(opt)});p.value=String(epIndex);s.replaceChildren();episode().scenes.forEach((v,i)=>{let opt=new Option(`${i+1}: ${v.name} (${K.runtime(v).toFixed(1)}с)`,String(i));s.add(opt)});s.value=String(sceneIndex);
 const z=scene();$('c6-season-title').value=pack.seasonTitle;$('c6-ep-title').value=episode().name;$('c6-scene-title').value=z.name;$('c6-in').value=z.in.toFixed(2);$('c6-out').value=z.out.toFixed(2);$('c6-timeline').max=String(K.duration(episode()));$('c6-time-label').textContent=playhead.toFixed(2)+' / '+K.duration(episode()).toFixed(2)+' с';}
function audit(){captureActive();const r=K.scan(pack);$('c6-qa').textContent=(r.errors.length?'ОШИБКИ:\n'+r.errors.join('\n'):'Нет структурных ошибок C6.')+'\nПредупреждения ('+r.warnings.length+'):\n'+r.warnings.slice(0,7).join('\n');return r;}
function setEpisodeTime(t,force=false){let ep=episode(),dur=K.duration(ep);playhead=Math.min(dur,Math.max(0,t));let item=K.locate(ep,playhead);if(!active||active.id!==item.scene.id){loadScene(epIndex,item.index);paintMenus()}
 api.setTime(item.local);$('c6-timeline').value=playhead;$('c6-time-label').textContent=playhead.toFixed(2)+' / '+dur.toFixed(2)+' с';return item;}
function stop(){watching=false;$('c6-play').textContent='▶ Смотреть целую серию'}
function tick(now){requestAnimationFrame(tick);if(!watching){prevTime=now;return}let dt=Math.max(0,Math.min((now-prevTime)/1000,.25));prevTime=now;playhead+=dt;const dur=K.duration(episode());if(playhead>=dur){playhead=dur;stop()}
 if(now-lastRender>120||!watching){lastRender=now;try{setEpisodeTime(playhead)}catch(e){stop();report(e.message)}}}
function trigger(blob,name){let url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),12000)}
function selectEp(n){stop();captureActive();let old=epIndex;try{loadScene(n,0);playhead=0;paintMenus();setEpisodeTime(0);audit()}catch(e){epIndex=old;paintMenus();report('Ошибка: '+e.message)}}
function selectScene(n){stop();captureActive();let old=sceneIndex;try{loadScene(epIndex,n);let st=episode().scenes.slice(0,n).reduce((t,s)=>t+K.runtime(s),0);playhead=st;paintMenus();setEpisodeTime(playhead);audit()}catch(e){sceneIndex=old;paintMenus();report('Ошибка: '+e.message)}}
function saveCut(){stop();captureActive();let s=scene(),name=$('c6-scene-title').value.trim(),title=$('c6-ep-title').value.trim(),a=Number($('c6-in').value),b=Number($('c6-out').value);if(!name||!title||!Number.isFinite(a)||!Number.isFinite(b)||a<0||b<=a||b>s.project.duration||b-a<.2){report('Ошибка: название обязательное, фрагмент минимум 0,2 с в пределах исходной сцены');return}let prev=[s.name,episode().name,s.in,s.out];s.name=name;episode().name=title;s.in=a;s.out=b;let res=K.scan(pack);if(res.errors.length){[s.name,episode().name,s.in,s.out]=prev;report('Исправьте ошибки: '+res.errors[0]);return}playhead=0;paintMenus();audit();report('Изменения сцены сохранены')}
function addEpisode(){stop();captureActive();if(pack.episodes.length>=12){report('Максимум 12 серий');return}let n=pack.episodes.length+1;pack.episodes.push({id:`ep-${String(n).padStart(2,'0')}`,name:`${String(n).padStart(2,'0')} · Новая серия`,scenes:[K.makeScene(api.project,'Сцена 1',0,Math.min(8,api.project.duration))]});selectEp(n-1);report('Новая серия добавлена; далее редактируйте кадры и голоса.')}
function addScene(){stop();captureActive();let e=episode();if(e.scenes.length>=120){report('Максимум 120 сцен в серии');return}let p=clone(api.project),s=K.makeScene(p,'Новая сцена '+(e.scenes.length+1),0,Math.min(8,p.duration));e.scenes.splice(sceneIndex+1,0,s);selectScene(sceneIndex+1);report('Сцена создана на базе прежней, параметры можно менять отдельно')}
function deleteScene(){stop();captureActive();let e=episode();if(e.scenes.length===1){report('Последнюю сцену удалять нельзя');return}let idx=sceneIndex;e.scenes.splice(idx,1);active=null;selectScene(Math.max(0,idx-1));report('Сцена удалена только из C6; резерв JSON не затронут')}
function move(n){stop();captureActive();let e=episode(),k=sceneIndex,j=k+n;if(j<0||j>=e.scenes.length)return;[e.scenes[k],e.scenes[j]]=[e.scenes[j],e.scenes[k]];active=null;selectScene(j);report('Порядок монтажа обновлён')}
async function importFull(file){let text=await file.text();if(text.length>42e6){report('Проект слишком большой для браузерного импорта');return}let raw;try{raw=JSON.parse(text)}catch(e){report('Повреждённый JSON отклонён: '+e.message);return}let candidate;
 try{candidate=raw.schema===K.SCHEMA?raw:K.importC5(raw);let r=K.scan(candidate);if(r.errors.length)throw Error(r.errors.slice(0,5).join('; '));let first=candidate.episodes[0].scenes[0];root.C4Core.adaptC3(first.project);}
 catch(e){report('Импорт отклонён; данные не менялись: '+e.message);return}
 stop();let old=pack;captureActive();try{api.loadCandidate(candidate.episodes[0].scenes[0].project);pack=candidate;epIndex=0;sceneIndex=0;active={ep:0,sc:0,id:pack.episodes[0].scenes[0].id};playhead=0;root.C5Studio?.refresh();paintMenus();setEpisodeTime(0);audit();report('Полный C6 проект импортирован. Исторический C5 JSON сохранён в составе сцены.')}
 catch(e){pack=old;report('Импорт не применён: '+e.message)}}
function bind(){ $('c6-ep').addEventListener('change',e=>selectEp(Number(e.target.value)));$('c6-scene').addEventListener('change',e=>selectScene(Number(e.target.value)));
 $('c6-add-ep').addEventListener('click',addEpisode);$('c6-add-scene').addEventListener('click',addScene);$('c6-delete-scene').addEventListener('click',deleteScene);$('c6-up').addEventListener('click',()=>move(-1));$('c6-down').addEventListener('click',()=>move(1));
 $('c6-save-cut').addEventListener('click',saveCut);$('c6-commit').addEventListener('click',()=>{captureActive();audit();report('Параметры 3D и русская речь сохранены в сцене C6.')});
 $('c6-season-title').addEventListener('change',e=>{pack.seasonTitle=e.target.value.trim();audit()});
 $('c6-timeline').addEventListener('input',e=>{stop();try{setEpisodeTime(Number(e.target.value))}catch(err){report(err.message)}});
 $('c6-play').addEventListener('click',()=>{if(watching){stop();return}if(playhead>=K.duration(episode())-.001)playhead=0;api.stopPlayback();watching=true;prevTime=performance.now();$('c6-play').textContent='❚❚ Пауза серии';report('Просмотр серии; звук русских голосов при пакетном рендере добавляется отдельно')});
 $('c6-export-json').addEventListener('click',()=>{captureActive();pack.seasonTitle=$('c6-season-title').value.trim();let v=audit();if(v.errors.length){report('Исправьте ошибки перед сохранением: '+v.errors[0]);return}trigger(new Blob([JSON.stringify(pack,null,2)],{type:'application/json'}),'PROJECT_C6_SEASON.json');report('Полный сезон JSON скачан; сохраните его отдельно от ZIP.')});
 $('c6-export-srt').addEventListener('click',()=>{captureActive();trigger(new Blob([K.srt(episode())],{type:'text/plain;charset=utf-8'}),`C6_EPISODE_${epIndex+1}_RU.srt`)});
 $('c6-import-json').addEventListener('click',()=>$('c6-file').click());$('c6-file').addEventListener('change',async e=>{let f=e.target.files[0];if(f)await importFull(f);e.target.value=''}) }
try{bind();loadScene(0,0);paintMenus();audit();requestAnimationFrame(tick);report('C6 готова: две демонстрационные серии. Укажите имена и длительность сцен, затем экспортируйте полный сезон JSON.');root.C6Studio={get project(){captureActive();return pack},loadProject:async raw=>{let file={text:async()=>JSON.stringify(raw)};await importFull(file)},setEpisodeTime,selectEp,selectScene,stop,scan:audit};}
catch(e){report('Ошибка запуска C6: '+e.stack);console.error(e)}
})(window);
