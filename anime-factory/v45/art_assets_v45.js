/* V45 2D Art & Assets Studio.
 * Actual imported multilayer cutout and scene backgrounds render through
 * original V15 drawProductionPerson()/V19 drawScene() sites.
 * Asset PNG bytes are embedded in portable project JSON. No remote APIs.
 */
const v45Parts=['legs','cape','torso','arms','face','hair','weapon'];
let v45Selected=0;
const v45BgCache=new Map();
function v45Character(){return P?.characters?.[v45Selected]||null;}
function v45Scene(){return P?.episodes?.[epIndex]?.scenes?.[scIndex]||null;}
function v45Rig(c){
 if(!c.artV45||typeof c.artV45!=='object'||Array.isArray(c.artV45))
  c.artV45={pivots:{}};
 if(!c.artV45.pivots||typeof c.artV45.pivots!=='object')
  c.artV45.pivots={};
 return c.artV45;
}
function v45PivotFor(c,part){
 const p=v45Rig(c).pivots?.[part]||{};
 const finite=(v)=>Number.isFinite(Number(v))?Number(v):0;
 return {x:clamp(finite(p.x),-125,125),
  y:clamp(finite(p.y),-260,260),
  angle:clamp(finite(p.angle),-120,120)};
}
function v45OfBackground(s){
 if(!s.bgV45||typeof s.bgV45!=='object'||Array.isArray(s.bgV45))
  s.bgV45={image:'',name:'',rights:'',enabled:false};
 return s.bgV45;
}
function v45DrawBackground(g,w,h,s,sec){
 const bg=v45OfBackground(s);
 if(!bg.enabled||!/^data:image\/(png|jpeg|webp);base64,/.test(bg.image||''))return false;
 const key=bg.image.length+':'+bg.image.slice(-70);
 let img=v45BgCache.get(key);
 if(!img){
  img=new Image();img.onload=()=>{
   if(P&&currentPage==='art-assets-v45')v45Preview();
  };
  img.onerror=()=>notify('V45: фон не читается, показан стандартный.');
  img.src=bg.image;v45BgCache.set(key,img);
  return false;
 }
 if(!img.complete||!img.naturalWidth)return false;
 const ratio=Math.max(w/img.naturalWidth,h/img.naturalHeight);
 const iw=img.naturalWidth*ratio,ih=img.naturalHeight*ratio;
 g.drawImage(img,(w-iw)/2,(h-ih)/2,iw,ih);
 return true;
}
function v45LayerAssetDescriptor(c){
 const rig=productionOf(c);
 return {id:String(c.id),name:c.name,kind:'character-cutout',
  rights:rig.rights||'',width:640,height:960,alpha:true,
  layers:v45Parts.map(name=>({
   name,pivot:v45PivotFor(c,name),active:!!rig.parts[name]?.image
  }))};
}
function v45EngineSnapshot(){
 const assets=P.characters.map(v45LayerAssetDescriptor);
 for(const ep of P.episodes)for(const s of ep.scenes){
  const bg=v45OfBackground(s);
  if(bg.image)assets.push({id:'bg-'+ep.number+'-'+s.title,
   name:bg.name||s.title,kind:'background',
   rights:bg.rights,width:640,height:360,alpha:false,layers:[]});
 }
 return AnimeProductionEngineV45.snapshot(P,assets);
}
function v45Show(){
 if(!P)return;
 const el=$('v45-character'),old=Number(el.value);
 el.innerHTML=P.characters.map((c,i)=>
  '<option value="'+i+'">'+escapeHTML(c.name)+'</option>').join('');
 v45Selected=Number.isInteger(old)&&old>=0&&old<P.characters.length?old:0;
 el.value=String(v45Selected);v45Controls();
}
function v45Controls(){
 v45Selected=Number($('v45-character').value)||0;
 const c=v45Character();if(!c)return;
 const rig=productionOf(c);
 const name=$('v45-layer').value||'torso',p=rig.parts[name];
 const extra=v45PivotFor(c,name);
 $('v45-rights').value=rig.rights||'';
 $('v45-background-rights').value=v45OfBackground(v45Scene()).rights||'';
 $('v45-use-bg').checked=v45OfBackground(v45Scene()).enabled;
 $('v45-x').value=p.x;$('v45-y').value=p.y;
 $('v45-scale').value=p.scale;$('v45-angle').value=p.angle;
 $('v45-pivot-x').value=extra.x;$('v45-pivot-y').value=extra.y;
 $('v45-pivot-angle').value=extra.angle;
 const loaded=v45Parts.filter(n=>!!rig.parts[n]?.image);
 $('v45-status').textContent=c.name+': '+loaded.length+
  '/7 PNG слоёв • '+(p.image?'PNG активен':'векторный запасной слой')+
  ' • '+(rig.rights?'источник указан':'не указан источник прав');
 const bg=v45OfBackground(v45Scene());
 $('v45-background-status').textContent=bg.image?
  'Фон: '+bg.name+' • '+(bg.enabled?'включён':'отключён'):
  'Фон ещё не загружен: остаётся прежнее процедурное окружение.';
 v45Preview();
}
function v45SaveLayer(){
 const c=v45Character(),part=$('v45-layer').value;
 if(!c||!v45Parts.includes(part))return;
 const rig=productionOf(c),p=rig.parts[part];
 rig.enabled=true;rig.rights=$('v45-rights').value.trim().slice(0,500);
 p.x=clamp(Number($('v45-x').value),-100,100);
 p.y=clamp(Number($('v45-y').value),-100,100);
 p.scale=clamp(Number($('v45-scale').value),.5,1.5);
 p.angle=clamp(Number($('v45-angle').value),-45,45);
 v45Rig(c).pivots[part]={
  x:clamp(Number($('v45-pivot-x').value),-125,125),
  y:clamp(Number($('v45-pivot-y').value),-260,260),
  angle:clamp(Number($('v45-pivot-angle').value),-120,120)};
 save();v45Controls();notify('V45: слой и точка поворота сохранены.');
}
function v45Preview(){
 const s=v45Scene();if(!P||!s)return;
 const value=Number($('v45-time').value)||30;
 drawScene($('v45-preview'),s,s.duration*value/100);
 $('v45-timestamp').textContent='Сцена '+s.title+
  ' • '+(s.duration*value/100).toFixed(2)+' сек.';
}
async function v45ReadCanvas(file,width,height){
 if(!file||file.size>6*1024*1024)throw Error('Файл больше 6 МБ');
 if(!['image/png','image/webp','image/jpeg'].includes(file.type))
  throw Error('Разрешены только PNG, WebP, JPEG');
 const raw=URL.createObjectURL(file);
 try{
  const img=new Image();img.src=raw;
  await img.decode();
  if(!img.naturalWidth||!img.naturalHeight||
    img.naturalWidth>8192||img.naturalHeight>8192)
   throw Error('Размер изображения вне диапазона 1–8192 пикселей');
  const canvas=document.createElement('canvas');
  canvas.width=width;canvas.height=height;
  const g=canvas.getContext('2d');
  const k=Math.min(width/img.naturalWidth,height/img.naturalHeight);
  const w=img.naturalWidth*k,h=img.naturalHeight*k;
  g.drawImage(img,(width-w)/2,(height-h)/2,w,h);
  return canvas.toDataURL('image/png');
 }finally{URL.revokeObjectURL(raw);}
}
async function v45ImportLayer(){
 const file=$('v45-file').files?.[0],c=v45Character();
 if(!file||!c)return;
 try{
  const data=await v45ReadCanvas(file,640,960),part=$('v45-layer').value;
  productionOf(c).parts[part].image=data;
  productionOf(c).enabled=true;
  productionCache.clear();save();v45Controls();
  notify('V45: настоящий PNG-слой '+part+' подключён. Укажите права.');
 }catch(err){notify('V45 импорт слоя: '+err.message);}
 finally{$('v45-file').value='';}
}
async function v45ImportBackground(){
 const file=$('v45-bg-file').files?.[0],s=v45Scene();if(!file||!s)return;
 try{
  const data=await v45ReadCanvas(file,1280,720);
  const bg=v45OfBackground(s);
  bg.image=data;bg.name=file.name.slice(0,150);
  bg.rights=$('v45-background-rights').value.trim().slice(0,500);
  bg.enabled=true;v45BgCache.clear();
  save();v45Controls();notify('V45: изображение фона включено в проект.');
 }catch(err){notify('V45 импорт фона: '+err.message);}
 finally{$('v45-bg-file').value='';}
}
function v45BackgroundSave(){
 const s=v45Scene();if(!s)return;
 const b=v45OfBackground(s);
 b.enabled=$('v45-use-bg').checked;
 b.rights=$('v45-background-rights').value.trim().slice(0,500);
 save();v45Controls();
}
async function v45GenerateLayers(){
 const c=v45Character();if(!c)return;
 try{
  const rig=productionOf(c);rig.enabled=true;
  // Genuine editable PNG layers from original V19 vector art at a consistent anchor.
  for(const part of v45Parts){
   const img=document.createElement('canvas');
   img.width=640;img.height=960;
   drawCharacterPNG(img,c,part,.35);
   rig.parts[part].image=img.toDataURL('image/png');
  }
  rig.rights='Создано встроенным редактором AI Anime Factory (проверьте права на оригинальные исходные материалы)';
  productionCache.clear();save();v45Controls();
  notify('V45: создан настоящий набор 7 редактируемых PNG-слоёв.');
 }catch(err){notify('V45 создание 7 слоёв: '+err.message);}
}
async function v45ExportSheet(){
 await preloadArtwork();
 const s=v45Scene();if(!s)return;
 const raw=document.createElement('canvas'),sheet=document.createElement('canvas');
 raw.width=640;raw.height=360;sheet.width=1280;sheet.height=720;
 const ctx=sheet.getContext('2d');
 for(let i=0;i<4;i++){
  drawScene(raw,s,s.duration*(.12+i*.23));
  ctx.drawImage(raw,(i%2)*640,Math.floor(i/2)*360);
 }
 download('V45_FOUR_REAL_ASSET_FRAMES.png',await blobPNG(sheet));
}
async function v45ExportProject(){
 // Full JSON includes original PNG and background data as data URLs; no file paths.
 const text=JSON.stringify(P,null,2);
 download('V45_PORTABLE_2D_PROJECT.json',
   new Blob([text],{type:'application/json;charset=utf-8'}));
}
function v45Audit(){
 const result=v45EngineSnapshot();
 $('v45-report').textContent='ANIME PRODUCTION ENGINE V45\n'+
  'Персонажей: '+result.audit.characterCount+'; серий: '+
  result.audit.episodeCount+'; изображений: '+result.assets.length+
  '\nСостояние: '+(result.audit.ok?'структурная проверка успешна':'ошибки')+
  '\n\nОшибки:\n'+(result.audit.errors.join('\n')||'нет')+
  '\n\nПредупреждения:\n'+(result.audit.warnings.join('\n')||'нет')+
  '\n\nДвижок: сценарий/мир/отношения/события/кадры/ассеты доступны.'+
  '\nПолноценный анимационный редактор V46, аудио V47, рендер V48 и FINAL V50 пока НЕ завершены.';
}
$('v45-character').onchange=v45Controls;
$('v45-layer').onchange=v45Controls;
$('v45-save').onclick=v45SaveLayer;
$('v45-file').onchange=v45ImportLayer;
$('v45-bg-file').onchange=v45ImportBackground;
$('v45-bg-save').onclick=v45BackgroundSave;
$('v45-make').onclick=v45GenerateLayers;
$('v45-time').oninput=v45Preview;
$('v45-frame').onclick=async()=>{try{await v45ExportSheet();}catch(e){notify('V45 PNG: '+e.message);}};
$('v45-project').onclick=v45ExportProject;
$('v45-plan').onclick=()=>download('V45_ENGINE_PRODUCTION_PLAN.json',
 new Blob([JSON.stringify(v45EngineSnapshot(),null,2)],{type:'application/json;charset=utf-8'}));
$('v45-audit').onclick=v45Audit;
