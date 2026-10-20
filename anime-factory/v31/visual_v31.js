/* AI Anime Factory V31 — actual Canvas frame analysis and modest color finishing.
   Preserves original artwork and V19–V30. Uses pixel-level luma measurements,
   not AI face recognition, art scoring or a claim of professional quality.
*/
function v31Of(s){
 if(!s.finishV31||typeof s.finishV31!=='object'||Array.isArray(s.finishV31))s.finishV31={};
 const o=s.finishV31;
 for(const [k,d] of [['exposure',51],['contrast',54],['saturation',55],['vignette',22]]){
  o[k]=Number.isFinite(Number(o[k]))?clamp(Number(o[k]),0,100):d;
 }
 o.enabled=o.enabled!==false;
 return o;
}
function v31Grade(g,w,h,s){
 const o=v31Of(s);if(!o.enabled)return;
 const exposure=(o.exposure-50)*.70,contrast=1+(o.contrast-50)*.0065;
 const saturation=1+(o.saturation-50)*.009,vig=o.vignette/100*.23;
 if(exposure===0&&contrast===1&&saturation===1&&vig===0)return;
 let image;
 try{image=g.getImageData(0,0,w,h);}
 catch(error){return;} // Tainted third-party images must never crash a render.
 const data=image.data;
 // Lookup tables avoid a floating point power operation for every pixel.
 const lut=new Float32Array(256);
 for(let c=0;c<256;c++)lut[c]=(c-127.5)*contrast+127.5+exposure;
 const stride=w*4;
 for(let y=0;y<h;y++){
  const dy=(y/h-.5)*2;
  for(let x=0;x<w;x++){
   const i=y*stride+x*4,r=lut[data[i]],g0=lut[data[i+1]],b=lut[data[i+2]];
   const lum=.2126*r+.7152*g0+.0722*b;
   const dx=(x/w-.5)*2;
   const v=Math.max(.76,1-vig*Math.min(1,(dx*dx+dy*dy)*.62));
   data[i]=clamp((lum+(r-lum)*saturation)*v,0,255);
   data[i+1]=clamp((lum+(g0-lum)*saturation)*v,0,255);
   data[i+2]=clamp((lum+(b-lum)*saturation)*v,0,255);
  }
 }
 g.putImageData(image,0,0);
}
function v31Metrics(canvas){
 const sample=document.createElement('canvas');
 sample.width=160;sample.height=90;
 const c=sample.getContext('2d',{willReadFrequently:true});
 c.drawImage(canvas,0,0,160,90);
 const pixels=c.getImageData(0,0,160,90).data;
 let n=0,sum=0,sq=0,black=0,white=0,midSum=0,midN=0,edges=0;
 const prev=new Float32Array(160);
 for(let y=0;y<90;y++){
  let last=0;
  for(let x=0;x<160;x++){
   const i=(y*160+x)*4;
   const l=.2126*pixels[i]+.7152*pixels[i+1]+.0722*pixels[i+2];
   n++;sum+=l;sq+=l*l;
   if(l<24)black++;
   if(l>235)white++;
   if(x>=40&&x<120&&y>=18&&y<75){midSum+=l;midN++;}
   if(x>0&&Math.abs(l-last)>31)edges++;
   if(y>0&&Math.abs(l-prev[x])>31)edges++;
   last=l;prev[x]=l;
  }
 }
 const mean=sum/n,contrast=Math.sqrt(Math.max(0,sq/n-mean*mean));
 return {mean:+mean.toFixed(2),contrast:+contrast.toFixed(2),
  dark:+(black/n).toFixed(3),bright:+(white/n).toFixed(3),
  center:+(midSum/midN).toFixed(2),
  edges:+(edges/(n*2)).toFixed(3)};
}
function v31Assess(metrics){
 const issues=[];
 for(const [i,m] of metrics.entries()){
  const t='Кадр '+(i+1)+': ';
  if(m.mean<56)issues.push(t+'возможна слишком низкая яркость.');
  if(m.mean>207)issues.push(t+'возможна пересветка.');
  if(m.contrast<27)issues.push(t+'низкий измеренный контраст.');
  if(m.dark>.64)issues.push(t+'большая доля глубоких теней.');
  if(m.bright>.42)issues.push(t+'много пересвеченных областей.');
  if(m.center<49)issues.push(t+'центральная зона тёмная — проверить читаемость героев.');
  if(m.edges<.013)issues.push(t+'низкая плотность видимых границ.');
 }
 for(let i=1;i<metrics.length;i++)
  if(Math.abs(metrics[i].mean-metrics[i-1].mean)>64)
   issues.push('Кадры '+i+'–'+(i+1)+': большая перемена общей яркости; проверить монтаж.');
 return issues;
}
function v31SceneReview(s){
 const frames=[],samples=[.14,.38,.64,.88];
 const canvas=document.createElement('canvas');canvas.width=480;canvas.height=270;
 for(const p of samples){
  drawScene(canvas,s,Math.max(.001,Number(s.duration)||1)*p,false);
  frames.push(v31Metrics(canvas));
 }
 return {title:s.title,kind:s.kind,
  settings:{...v31Of(s)},metrics:frames,issues:v31Assess(frames)};
}
function v31ReviewProject(){
 if(!P)return {scenes:[],issues:['Проект не открыт'],sampled:0,total:0};
 const source=P.episodes.flatMap((e,i)=>e.scenes.map((s,j)=>({s,i,j})));
 const scenes=[],issues=[];
 // Bound worst-case work for lower-end Windows 10 laptops.
 for(const {s,i,j} of source.slice(0,24)){
  try{
   const result=v31SceneReview(s);
   scenes.push({episode:i+1,scene:j+1,...result});
   result.issues.forEach(text=>issues.push('Серия '+(i+1)+', сцена '+(j+1)+': '+text));
  }catch(error){
   issues.push('Серия '+(i+1)+', сцена '+(j+1)+': ошибка анализа пикселей: '+String(error.message||error));
  }
 }
 if(source.length>24)issues.push('Проверены первые 24 из '+source.length+' сцен. Остальные проверьте отдельно.');
 return {scenes,issues,sampled:Math.min(source.length,24),total:source.length};
}
function v31UpdateUI(){
 if(!P)return;
 const sel=$('v31-scene'),value=sel.value;
 sel.innerHTML=qualitySceneList();
 const current=epIndex+':'+scIndex;
 sel.value=[...sel.options].some(o=>o.value===value)?value:current;
 const s=v31Selected(),o=v31Of(s);
 $('v31-enabled').checked=o.enabled;
 for(const k of ['exposure','contrast','saturation','vignette']){
  $('v31-'+k).value=o[k];$('v31-'+k+'-n').textContent=String(o[k]);
 }
 v31Preview();
}
function v31Selected(){
 const value=$('v31-scene').value;
 if(!value)return scene();
 const [i,j]=value.split(':').map(Number);
 return P.episodes[i]?.scenes[j]||scene();
}
function v31Preview(){
 const s=v31Selected();if(!s)return;
 const o=v31Of(s),time=Number($('v31-position').value||35)/100*s.duration;
 const was=o.enabled;
 try{
  o.enabled=false;drawScene($('v31-before'),s,time,false);
  o.enabled=was;drawScene($('v31-after'),s,time,false);
 }finally{o.enabled=was;}
 $('v31-caption').textContent=s.title+' · '+time.toFixed(2)+' с';
}
function v31Save(){
 const s=v31Selected(),o=v31Of(s);
 o.enabled=$('v31-enabled').checked;
 for(const k of ['exposure','contrast','saturation','vignette'])
  o[k]=clamp(Number($('v31-'+k).value)||0,0,100);
 save();v31UpdateUI();notify('V31: цветокоррекция этой сцены сохранена.');
}
function v31Preset(){
 const o=v31Of(v31Selected());
 Object.assign(o,{enabled:true,exposure:54,contrast:59,saturation:57,vignette:21});
 save();v31UpdateUI();notify('V31: мягкая художественная цветокоррекция применена.');
}
function v31ReviewSelected(){
 if(!P)return;
 const s=v31Selected();
 let report;
 try{report=v31SceneReview(s);}
 catch(error){
  $('v31-result').textContent='Ошибка чтения Canvas: '+String(error.message||error);return;
 }
 $('v31-result').textContent=report.metrics.map((m,i)=>
  'Кадр '+(i+1)+': яркость '+m.mean+' · контраст '+m.contrast+
  ' · тёмные '+Math.round(m.dark*100)+'% · светлые '+Math.round(m.bright*100)+
  '% · центр '+m.center).join('\n')+
  '\n\n'+(report.issues.length?report.issues.join('\n'):'Пороговых визуальных предупреждений не найдено.')+
  '\n\nПоказатели — эвристики. Они не измеряют качество лица или художественную привлекательность.';
}
function v31ReviewAll(){
 const report=v31ReviewProject();
 $('v31-result').textContent='Изучено сцен '+report.sampled+' из '+report.total+
  '\n\n'+(report.issues.join('\n')||'Пороговых предупреждений не обнаружено.');
}
function v31DownloadReport(){
 const report=v31ReviewProject();
 const body=['AI ANIME FACTORY V31 — РЕАЛЬНЫЙ АНАЛИЗ КАДРОВ',
  'Проверено сцен: '+report.sampled+' из '+report.total,''];
 for(const s of report.scenes){
  body.push('Серия '+s.episode+', сцена '+s.scene+': '+s.title);
  s.metrics.forEach((m,i)=>body.push('Кадр '+(i+1)+': Y='+m.mean+
   ' C='+m.contrast+' dark='+m.dark+' bright='+m.bright+
   ' center='+m.center+' edges='+m.edges));
  body.push(...s.issues,'');
 }
 body.push('Ограничение: анализ пикселей не равен оценке качества аниме.');
 download('V31_VISUAL_PRODUCTION_QA_RU.txt',
  new Blob([body.join('\n')],{type:'text/plain;charset=utf-8'}));
}
function v31DownloadJSON(){
 download('V31_VISUAL_PRODUCTION_METRICS.json',
  new Blob([JSON.stringify(v31ReviewProject(),null,2)],
    {type:'application/json;charset=utf-8'}));
}
async function v31Sheet(){
 await preloadArtwork();
 const s=v31Selected(),board=document.createElement('canvas');
 board.width=1280;board.height=720;
 const frame=document.createElement('canvas');frame.width=640;frame.height=360;
 const g=board.getContext('2d');
 for(const [i,t] of [.14,.38,.64,.88].entries()){
  drawScene(frame,s,s.duration*t,false);
  const x=i%2*640,y=Math.floor(i/2)*360;
  g.drawImage(frame,x,y);g.fillStyle='rgba(2,9,21,.8)';g.fillRect(x+9,y+9,220,28);
  g.fillStyle='#f4e3ca';g.font='bold 14px Arial';
  g.fillText('V31 КАДР '+(i+1)+' — '+Math.round(t*100)+'%',x+16,y+28);
 }
 download('V31_REAL_FRAMES_'+slug(s.title)+'.png',await blobPNG(board));
 notify('V31: экспортировано четыре реальных кадра.');
}
$('v31-scene').onchange=v31UpdateUI;
$('v31-position').oninput=v31Preview;
$('v31-save').onclick=v31Save;$('v31-preset').onclick=v31Preset;
$('v31-analyze').onclick=v31ReviewSelected;
$('v31-all').onclick=v31ReviewAll;
$('v31-report').onclick=v31DownloadReport;
$('v31-json').onclick=v31DownloadJSON;
$('v31-sheet').onclick=async()=>{try{await v31Sheet();}catch(e){notify('V31 PNG: '+e.message);}};
for(const key of ['exposure','contrast','saturation','vignette'])
 $('v31-'+key).oninput=e=>{$('v31-'+key+'-n').textContent=e.target.value;};
