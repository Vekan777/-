/* Standalone browser extension for the existing C1 battle editor.
   Extends original C1 scene, never overwrites or silently mutates its story/beat tracks. */
'use strict';
(function(){
 const A=window.CharacterCoreC2;
 if(!A||typeof p==='undefined'||typeof paintFigure!=='function')throw Error('C2 requires existing C1 editor and character_core_c2.js');
 const q=id=>document.getElementById(id);
 const viewsRU={front:'Анфас',threequarter:'¾',profile:'Профиль'};
 const poseRU={idle:'Покой',ready:'Стойка',windup:'Замах',dash:'Рывок',slash:'Удар',block:'Блок',dodge:'Уклонение',hit:'Попадание',recover:'Возврат'};
 const palette=['hair','eye','skin','primary','accent','shadow','weapon'];
 const labels={hair:'Волосы / шлем',eye:'Глаза',skin:'Кожа',primary:'Костюм / броня',accent:'Акцент',shadow:'Тени',weapon:'Оружие'};
 const cached=new Map(),onloadPending=new Set();let lastPrint='';
 function activate(){ A.ensure(p);renderGallery();updateInputs();c2Audit();render(t); }
 function actor(){return q('c2-actor').value||p.actors[0]?.id;}
 function syncActorOptions(){const sel=q('c2-actor'),old=sel.value;sel.replaceChildren();p.actors.forEach(a=>{const o=document.createElement('option');o.value=a.id;o.textContent=a.name;sel.appendChild(o)});if(p.actors.some(a=>a.id===old))sel.value=old;}
 function kit(){A.ensure(p);return p.c2.kits[actor()];}
 function clearCache(){cached.clear();onloadPending.clear();}
 function renderGallery(){
   A.ensure(p);
   const target=q('c2-gallery'); target.replaceChildren();
   for(const view of A.VIEWS){
     const box=document.createElement('div');box.className='c2-gallery-card';
     const img=document.createElement('img');img.alt=`${kit().name}, ${viewsRU[view]}, ${q('c2-pose').value}`;
     const slot=A.selectSprite(p,actor(),view,q('c2-pose').value);img.src=slot?.src||A.makeSprite(kit(),view,q('c2-pose').value,q('c2-expression').value);
     const sub=document.createElement('div');sub.textContent=`${viewsRU[view]} · ${slot?(slot.exact?'Загружен точный':'Подстановка '+slot.key):'Оригинальный SVG-черновик'}`;box.append(img,sub);target.appendChild(box);
   }
   q('c2-fingerprint').textContent=`ID внешности: ${A.fingerprint(kit())}. Все ракурсы получают один набор цветов и признаков.`;
 }
 function updateInputs(){
   A.ensure(p);const c=kit();q('c2-name').value=p.actors.find(a=>a.id===actor())?.name||c.name;
   q('c2-signature').value=c.signature||'';q('c2-archetype').value=c.archetype;q('c2-note').value=p.c2.notes||'';
   for(const name of palette)q('c2-'+name).value=c[name];
   q('c2-human-reviewed').checked=!!p.c2.draftReview[actor()]?.approved;
 }
 function updateDesign(){
   const c=kit(),n=q('c2-name').value.trim(); if(!n){alert('У персонажа должно быть имя');return;}
   c.name=n;c.signature=q('c2-signature').value.trim();c.archetype=q('c2-archetype').value;c.silhouette=['guardian','mechanist'].includes(c.archetype)?'broad':c.archetype==='ranger'?'medium':'slim';
   for(const name of palette)c[name]=q('c2-'+name).value;
   c.revision=(Number(c.revision)||0)+1;p.actors.find(a=>a.id===actor()).name=n;syncActorOptions();
   p.c2.draftReview[actor()]={approved:false,note:'Изменена внешность: предыдущая художественная приёмка больше не действительна'};
   q('c2-human-reviewed').checked=false;clearCache();renderGallery();c2Audit();render(t);
 }
 function c2Audit(){
   A.ensure(p);const a=A.audit(p),box=q('c2-issues');box.replaceChildren();
   q('c2-result').textContent=`Контроль идентичности: ошибок ${a.errors}; замечаний ${a.warnings}. ${a.ok?'Структура корректна.':'Есть ошибки, исправьте.'} Художественное качество не определяется автоматически.`;
   q('c2-result').style.color=a.ok?'#b9f0d2':'#ff9d9d';
   for(const x of a.issues){const el=document.createElement('div');el.className='issue '+(x.severity==='error'?'err':'');el.textContent=`${x.ref}: ${x.message}`;box.append(el);}
   if(!a.issues.length)box.textContent='Структурных замечаний нет. Ручная художественная приёмка всё ещё обязательна.';
   return a;
 }
 const oldPaint=paintFigure;
 paintFigure=function(id,model,cam,W,H,tm){
   // Imported original art from C1 remains the preference when a C2 pose slot is absent.
   A.ensure(p);const c=p.c2.kits[id];if(!c)return oldPaint(id,model,cam,W,H,tm);
   const pose=A.poseForState(model),view=A.viewForShot(cam),expr=p.c2.faces[id]?.[pose]||A.expressionForPose(pose);
   const slot=A.selectSprite(p,id,view,pose);
   if(!slot&&images[id])return oldPaint(id,model,cam,W,H,tm);
   const sig=A.fingerprint(c),key=slot?`import/${id}/${slot.key}/${slot.src.length}/${A.hash(slot.src.slice(-500))}`:`generated/${id}/${sig}/${view}/${pose}/${expr}`;
   let img=cached.get(key);
   if(!img){img=new Image();cached.set(key,img);onloadPending.add(key);img.onload=()=>{onloadPending.delete(key);if(!recording)render(t);};img.onerror=()=>{onloadPending.delete(key);cached.delete(key);};img.src=slot?.src||A.makeSprite(c,view,pose,expr);}
   if(!img.complete||!img.naturalWidth){return oldPaint(id,model,cam,W,H,tm);}
   const x=model.x*W,y=H*(.84+model.y),unit=W/1280,renderH=(p.actors.find(a=>a.id===id)?.h||440)*unit,renderW=renderH*(img.naturalWidth/img.naturalHeight);
   ctx.save();ctx.translate(x,y);ctx.scale(model.facing||1,1);
   ctx.fillStyle='#03091688';ctx.beginPath();ctx.ellipse(0,0,70*unit,11*unit,0,0,Math.PI*2);ctx.fill();
   let bend=pose==='dash'?.07:pose==='hit'?-.045:pose==='slash'?.025:0;
   ctx.rotate(bend);ctx.drawImage(img,-renderW/2,-renderH*(530/560),renderW,renderH);ctx.restore();
 };
 const previousRefresh=refreshMedia;
 refreshMedia=async function(){await previousRefresh();A.ensure(p);syncActorOptions();clearCache();renderGallery();updateInputs();c2Audit();};
 const oldValidate=validate;
 validate=function(){const original=oldValidate();c2Audit();return original;};
 async function uploadSprite(){
   const f=q('c2-import').files?.[0];if(!f)return;
   try{
     if(!['image/png','image/webp'].includes(f.type))throw Error('Для персонажей разрешены только PNG/WebP (SVG не импортируется).');
     if(f.size>12*1024*1024)throw Error('Максимум 12 МБ на файл');
     const data=await fileData(f),img=await imageFromData(data);
     const tmp=document.createElement('canvas');tmp.width=img.naturalWidth;tmp.height=img.naturalHeight;
     if(tmp.width>4096||tmp.height>4096||tmp.width<16||tmp.height<16)throw Error('Размер изображения от 16 до 4096 px');
     const g=tmp.getContext('2d',{willReadFrequently:true});g.drawImage(img,0,0);
     const pixels=g.getImageData(0,0,tmp.width,tmp.height).data;
     const pt=(x,y)=>pixels[(y*tmp.width+x)*4+3];let alpha=false;
     for(const [x,y] of [[0,0],[tmp.width-1,0],[0,tmp.height-1],[tmp.width-1,tmp.height-1]])if(pt(x,y)<245)alpha=true;
     const status=q('c2-asset-rights').checked?'verified':'not-reviewed';
     A.recordSprite(p,actor(),q('c2-view').value,q('c2-pose').value,data,{width:tmp.width,height:tmp.height,alpha,rights:status,source:f.name.slice(0,100)});
     clearCache();renderGallery();c2Audit();render(t);
     q('c2-upload-result').textContent=`Загружено: ${f.name} (${tmp.width}×${tmp.height}); прозрачность на углах: ${alpha?'да':'не обнаружена'}. ${status==='verified'?'Вы подтвердили наличие прав — лицензия автоматически не проверяется.':'Права пока не подтверждены.'}`;
   }catch(e){q('c2-upload-result').textContent='Ошибка импорта: '+e.message;}
   q('c2-import').value='';
 }
 function saveReview(){A.ensure(p);p.c2.draftReview[actor()]={approved:q('c2-human-reviewed').checked,note:'Подтверждение пользователя, не независимая оценка изображения',at:new Date().toISOString(),fingerprint:A.fingerprint(kit())};q('c2-upload-result').textContent=q('c2-human-reviewed').checked?'Отметка художественной проверки сохранена в проекте (проверка выполнена пользователем).':'Художественная проверка отменена.';}
 q('c2-add-actor').addEventListener('click',()=>{
  A.ensure(p);if(p.actors.length>=12){alert('Максимум 12 героев для этой версии');return;}
  const name=q('c2-new-actor-name').value.trim();if(!name){alert('Введите имя нового оригинального персонажа');return;}
  const id='actor_'+String(p.actors.length+1).padStart(2,'0');if(p.actors.some(a=>a.id===id)){alert('ID уже занят, сохраните и проверьте список');return;}
  const n=p.actors.length,x=Math.max(.12,Math.min(.9,.18+n*.055));
  p.actors.push({id,name,w:208,h:420,color:'#bdc9e2'});
  p.tracks[id]=[{t:0,x,y:0,pose:'idle',facing:n%2?-1:1},{t:p.duration,x,y:0,pose:'idle',facing:n%2?-1:1}];
  p.media.images[id]=null;A.ensure(p);p.c2.kits[id].name=name;
  syncActorOptions();q('c2-actor').value=id;q('c2-new-actor-name').value='';
  clearCache();updateInputs();renderGallery();validate();render(t);
  q('c2-upload-result').textContent='Герой создан. Для движения добавьте ключи в JSON проекта; C3 добавит графический редактор движений. Старые события не изменены.';
 });
 q('c2-actor').addEventListener('change',()=>{updateInputs();renderGallery()});
 for(const id of ['c2-view','c2-pose','c2-expression'])q(id).addEventListener('change',renderGallery);
 q('c2-apply').addEventListener('click',updateDesign);
 q('c2-add-sprite').addEventListener('click',uploadSprite);
 q('c2-human-reviewed').addEventListener('change',saveReview);
 q('c2-export-sheet').addEventListener('click',()=>{
    let kits=p.c2.kits;download('CINEMATIC_C2_CHARACTER_BIBLE.json','application/json;charset=utf-8',JSON.stringify({schema:p.c2.schema,project:p.title,characters:kits,audit:A.audit(p),notes:p.c2.notes,disclaimer:'Technical identity checks are not visual art approval.'},null,2));
 });
 q('c2-save-notes').addEventListener('click',()=>{p.c2.notes=q('c2-note').value;q('c2-upload-result').textContent='Режиссёрские заметки сохранены в полном JSON проекта.';});
 q('c2-contact-png').addEventListener('click',async()=>{
   const savedActor=actor(),c=kit(),poses=['idle','ready','slash'],views=A.VIEWS;
   const sheet=document.createElement('canvas');sheet.width=960;sheet.height=1710;
   const g=sheet.getContext('2d');g.fillStyle='#142138';g.fillRect(0,0,sheet.width,sheet.height);
   for(let y=0;y<poses.length;y++)for(let x=0;x<views.length;x++){
      const view=views[x],pose=poses[y],slot=A.selectSprite(p,savedActor,view,pose);
      const el=await imageFromData(slot?.src||A.makeSprite(c,view,pose,A.expressionForPose(pose)));
      g.save();g.translate(x*320,y*570);g.fillStyle='#253651';g.fillRect(3,3,314,563);
      const scale=Math.min(300/el.naturalWidth,515/el.naturalHeight),w=el.naturalWidth*scale,h=el.naturalHeight*scale;
      g.drawImage(el,(320-w)/2,7,w,h);g.fillStyle='#d9f5ff';g.font='16px sans-serif';g.textAlign='center';g.fillText(`${viewsRU[view]} • ${poseRU[pose]}`,160,548);g.restore();
   }
   sheet.toBlob(b=>{if(b)download(`C2_${savedActor}_POSE_SHEET.png`,'image/png',b);},'image/png');
 });

 q('export-json').addEventListener('click',ev=>{ev.stopImmediatePropagation();A.ensure(p);p.c2.notes=q('c2-note').value;download('CINEMATIC_C2_FULL_PROJECT.json','application/json;charset=utf-8',JSON.stringify(p,null,2));},true);
 function initialize(){
   A.ensure(p);syncActorOptions();updateInputs();renderGallery();c2Audit();render(t);
 }
 initialize();
})();
