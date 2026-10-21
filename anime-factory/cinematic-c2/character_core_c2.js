/* AI Anime Factory CINEMATIC C2 — deterministic original character art and identity QA. MIT.
   This is an offline vector-character builder, NOT a neural text-to-image generator. */
(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory();else root.CharacterCoreC2=factory();})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const VIEWS=['front','threequarter','profile'];
const POSES=['idle','ready','windup','dash','slash','block','dodge','hit','recover'];
const EXPRESSIONS=['neutral','focused','angry','hurt','confident'];
const HEX=/^#[0-9a-fA-F]{6}$/;
const escapeXml=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));
const color=(c,defaultColor)=>HEX.test(c||'')?c:defaultColor;
const hash=s=>{let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619);}return (h>>>0).toString(16).padStart(8,'0');};
const newPresets=[
 {archetype:'mystic',hair:'#f3c9f7',eye:'#e8a8ff',skin:'#f4d0c0',primary:'#46346a',accent:'#9f8ff6',shadow:'#1d1740',weapon:'#eeeeff',silhouette:'slim'},
 {archetype:'duelist',hair:'#e9b28f',eye:'#b9f2ee',skin:'#ead0bc',primary:'#582d42',accent:'#ff7e80',shadow:'#271727',weapon:'#fef1db',silhouette:'slim'},
 {archetype:'ranger',hair:'#94ceb5',eye:'#f2dd93',skin:'#e2b999',primary:'#243d3d',accent:'#71bb92',shadow:'#132927',weapon:'#e5d7a4',silhouette:'medium'},
 {archetype:'mechanist',hair:'#eac47e',eye:'#ffc271',skin:'#dec1ab',primary:'#483c3d',accent:'#f5b963',shadow:'#211b28',weapon:'#e6d2a9',silhouette:'broad'}
];
const defaultKit=id=> id==='nova' ? {
  id, archetype:'scout', name:'Нова', signature:'Северный знак / серебряная коса', hair:'#d6edf5',eye:'#71f4ff',skin:'#eecbbf',primary:'#263a61',accent:'#39c9ec',shadow:'#111d38',weapon:'#d2faff', silhouette:'slim',license:'original-procedural-c2',revision:1
} : id==='warden'? {
  id,archetype:'guardian',name:'Страж',signature:'Чёрный шпиль / двойные рога',hair:'#463151',eye:'#fa9eff',skin:'#bca6b5',primary:'#51416b',accent:'#ce91ef',shadow:'#24192f',weapon:'#e8dbf8',silhouette:'broad',license:'original-procedural-c2',revision:1
} : (()=>{const index=parseInt(hash(id).slice(-2),16)%newPresets.length;return {...newPresets[index],id,name:id,signature:'Авторский знак '+id,license:'original-procedural-c2',revision:1};})();
function ensure(project){
 if(!project||project.schema!=='ai-anime-cinematic-c1'||!Array.isArray(project.actors))throw Error('Для C2 нужен корректный проект C1');
 if(!project.c2||project.c2.schema!=='ai-anime-cinematic-c2')project.c2={schema:'ai-anime-cinematic-c2', kits:{},sprites:{},faces:{},assetMeta:{},draftReview:{},notes:'',createdBy:'C2 offline character builder'};
 const c=project.c2;c.kits=c.kits||{};c.sprites=c.sprites||{};c.faces=c.faces||{};c.assetMeta=c.assetMeta||{};c.draftReview=c.draftReview||{};
 for(const a of project.actors){if(!c.kits[a.id])c.kits[a.id]=defaultKit(a.id);if(!c.sprites[a.id])c.sprites[a.id]={};if(!c.faces[a.id])c.faces[a.id]={};}
 return project;
}
function fingerprint(kit){return hash([kit.archetype,kit.silhouette,kit.hair,kit.eye,kit.skin,kit.primary,kit.accent,kit.shadow,kit.weapon,kit.signature].join('|'));}
function viewForShot(shot){const s=(shot?.kind||'').toLowerCase();if(/dialogue|reaction|aftermath|resolution|breath/.test(s))return 'front';if(/clash|dash|enemy-attack|counterattack/.test(s))return 'profile';return 'threequarter';}
function poseForState(model){return POSES.includes(model?.pose)?model.pose:'idle';}
function expressionForPose(pose){return pose==='hit'?'hurt':pose==='slash'||pose==='windup'?'angry':pose==='recover'?'neutral':'focused';}
const spriteKey=(view,pose)=>view+'|'+pose;
function selectSprite(p,id,view,pose){let sprites=p.c2?.sprites?.[id]||{};for(const key of [spriteKey(view,pose),spriteKey(view,'idle'),spriteKey('threequarter',pose),spriteKey('front',pose),spriteKey('front','idle')])if(sprites[key])return {src:sprites[key],key,exact:key===spriteKey(view,pose)};return null;}
function recordSprite(p,id,view,pose,data,meta={}){
 ensure(p);if(!p.c2.kits[id])throw Error('Неизвестный персонаж');
 if(!VIEWS.includes(view)||!POSES.includes(pose))throw Error('Некорректный ракурс/поза');
 if(typeof data!=='string'||!/^data:image\/(png|webp);base64,[A-Za-z0-9+/]+={0,2}$/.test(data))throw Error('Импортируйте PNG/WebP, а не исполняемый SVG/HTML');
 if(data.length>16*1024*1024)throw Error('Превышен лимит: 12 МБ на изображение');
 const key=spriteKey(view,pose),m=p.c2.assetMeta[id]||(p.c2.assetMeta[id]={});
 p.c2.sprites[id][key]=data;m[key]={width:meta.width||0,height:meta.height||0,alpha:meta.alpha===true,rights:meta.rights||'not-reviewed',source:meta.source||'user-import',fingerprint:fingerprint(p.c2.kits[id])};
 return key;
}
function audit(p){
 const issues=[],bad=(severity,ref,message)=>issues.push({severity,ref,message});
 if(!p.c2||p.c2.schema!=='ai-anime-cinematic-c2')return {ok:false,errors:1,warnings:0,issues:[{severity:'error',ref:'c2',message:'Нет C2-схемы'}]};
 const fingerprints=new Map();const ids=new Set();
 for(const a of p.actors||[]){ids.add(a.id);const kit=p.c2.kits?.[a.id];if(!kit){bad('error',a.id,'Отсутствует карточка внешности');continue;}
 if(kit.id!==a.id)bad('error',a.id,'ID карточки не соответствует персонажу');
 if((kit.name||'').trim()!==a.name?.trim())bad('warning',a.id,'Имя расходится с карточкой C1');
 for(const k of ['hair','eye','skin','primary','accent','shadow','weapon'])if(!HEX.test(kit[k]||''))bad('error',a.id,`Неверный цвет ${k}`);
 if(!['scout','guardian','mystic','duelist','ranger','mechanist'].includes(kit.archetype))bad('error',a.id,'Неизвестная модель персонажа');
 if(!(kit.signature||'').trim())bad('warning',a.id,'Нет отличительного признака внешности');
 if(!kit.license)bad('warning',a.id,'Не указано происхождение/лицензия модели');
 const sig=fingerprint(kit);if(fingerprints.has(sig))bad('error',a.id,'Внешность совпадает с '+fingerprints.get(sig));else fingerprints.set(sig,a.id);
 const slots=p.c2.sprites?.[a.id]||{};for(const [slot,data] of Object.entries(slots)){
 const [view,pose]=slot.split('|');if(!VIEWS.includes(view)||!POSES.includes(pose))bad('error',a.id,'Некорректный слот '+slot);
 if(typeof data!=='string'||!/^data:image\/(png|webp);base64,[A-Za-z0-9+/]+={0,2}$/.test(data))bad('error',a.id,'Недопустимый или повреждённый формат изображения '+slot);
 const meta=p.c2.assetMeta?.[a.id]?.[slot]||{};
 if(meta.width&&meta.width<400||meta.height&&meta.height<600)bad('warning',a.id,'Малое разрешение '+slot+' (желательно от 400×600)');
 if(meta.fingerprint&&meta.fingerprint!==sig)bad('warning',a.id,'Изменён дизайн после импорта '+slot+' — проверьте соответствие');
 if(meta.rights!=='verified')bad('warning',a.id,'Не проверены права на импорт '+slot);
 if(meta.alpha===false)bad('warning',a.id,'Нет прозрачности у '+slot+' — возможен фон-прямоугольник');
 }
 if(!Object.keys(slots).length&&!p.media?.images?.[a.id])bad('warning',a.id,'Пока используется процедурная SVG-анимация, не художественно принятый арт');
 const missing=VIEWS.filter(v=>!Object.keys(slots).some(k=>k.startsWith(v+'|')));if(Object.keys(slots).length&&missing.length)bad('warning',a.id,'Не загружены ракурсы: '+missing.join(', '));
 }
 for(const id of Object.keys(p.c2.kits||{}))if(!ids.has(id))bad('warning',id,'Карточка персонажа не используется (сохранена в JSON)');
 return {ok:!issues.some(i=>i.severity==='error'),errors:issues.filter(i=>i.severity==='error').length,warnings:issues.filter(i=>i.severity==='warning').length,issues};
}
function makeSvg(kit,view='threequarter',pose='idle',expression='neutral'){
 if(!VIEWS.includes(view)||!POSES.includes(pose)||!EXPRESSIONS.includes(expression))throw Error('Некорректная поза/ракурс/эмоция');
 const kind=kit.archetype,guardian=kind==='guardian',mystic=kind==='mystic',duelist=kind==='duelist',ranger=kind==='ranger',mechanist=kind==='mechanist',heavy=guardian||mechanist,profile=view==='profile',front=view==='front';
 const w=heavy?118:ranger?102:88,shoulder=heavy?94:ranger?77:60,headW=profile?44:56, lean=pose==='dash'?20:pose==='dodge'?-17:pose==='hit'?-11:pose==='slash'?13:0;
 const hand=({idle:[235,398],ready:[249,359],windup:[242,254],dash:[257,329],slash:[272,298],block:[224,292],dodge:[222,374],hit:[210,410],recover:[230,376]})[pose];
 const accent=color(kit.accent,'#48bcee'),primary=color(kit.primary,'#283c65'),shadow=color(kit.shadow,'#141e3b'),hair=color(kit.hair,'#d5e6fa'),skin=color(kit.skin,'#e9c1b8'),eye=color(kit.eye,'#6de2fa'),weapon=color(kit.weapon,'#f2faff');
 const bright=guardian?'#ffffff':'#e9fbff',side=profile?20:front?0:10,slant=lean/2;
 const circle=(x,y,r,fill)=>`<circle cx="${x}" cy="${y}" r="${r}" fill="${fill}"/>`;
 const path=(d,fill,stroke=shadow,sw=3)=>`<path d="${d}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round"/>`;
 let svg=[];svg.push(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 560" width="320" height="560"><defs><linearGradient id="coat" x2="1" y2="1"><stop stop-color="${accent}" stop-opacity=".76"/><stop offset=".33" stop-color="${primary}"/><stop offset="1" stop-color="${shadow}"/></linearGradient><linearGradient id="steel" x2="1"><stop stop-color="${accent}"/><stop offset=".45" stop-color="${bright}"/><stop offset="1" stop-color="${weapon}"/></linearGradient><filter id="halo" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="6"/></filter></defs>`);
 svg.push(`<ellipse cx="166" cy="520" rx="${guardian?113:84}" ry="14" fill="#091025" opacity=".40"/>`);
 svg.push(`<g transform="translate(${lean+(profile?17:0)},0) rotate(${slant} 155 405) ${profile?'translate(30 0) scale(.83 1)':front?'':'skewY(-1)'}">`);
 // Back cape / hair motion: color, distinct silhouettes, anisotropic detail.
 svg.push(path(heavy?'M92 295 Q39 330 22 489 L91 477 Q144 540 158 478 Q192 536 286 491 L249 311Z':mystic?'M106 306 Q33 360 18 545 Q99 499 159 517 Q247 534 299 545 L226 308Z':ranger?'M120 300 Q46 350 55 469 L102 498 L155 455 L229 492 L255 449 L213 306Z':'M126 313 Q75 361 40 503 Q93 473 122 492 Q157 511 183 478 Q218 493 259 507 L204 312Z','url(#coat)',accent,4));
 svg.push(path(guardian?'M98 343 L71 503 L132 489 L153 365Z':'M116 341 L88 499 L140 481 L152 364Z',shadow,accent,2));
 // Boots and asymmetrical legs
 svg.push(path(`M${149-w*.3} 429 L${148-w*.43} 502 L${125-w*.52} 510 L${107-w*.38} 529 L${161-w*.1} 529 L166 437Z`,shadow,accent,4));
 svg.push(path(`M${165+w*.08} 429 L${178+w*.42} 504 L${198+w*.5} 510 L${199+w*.66} 529 L155 529 L${155+w*.05} 440Z`,primary,accent,4));
 for(const yy of [475,494])svg.push(path(`M100 ${yy} L136 ${yy+3} M181 ${yy+3} L219 ${yy}`, 'none',accent,2));
 // Torso, shoulder plates, plating/fabric, central emblem
 svg.push(path(`M${160-shoulder} 296 Q145 277 161 286 Q194 270 ${160+shoulder} 298 L${171+w*.55} 436 Q155 454 ${160-w*.54} 436Z`,'url(#coat)',accent,4));
 svg.push(path(`M${160-shoulder} 297 Q${130-shoulder} 301 ${130-shoulder} 357 L${160-w*.4} 373 L151 302Z`,guardian?'#5b476e':primary,accent,4));
 svg.push(path(`M${160+shoulder} 297 Q${189+shoulder} 292 ${182+shoulder} 363 L${160+w*.4} 371 L177 302Z`,guardian?'#68547b':primary,accent,4));
 svg.push(path('M145 310 L160 323 L174 310 L180 383 L161 411 L140 384Z',shadow,accent,3));
 svg.push(path('M150 339 L159 326 L169 340 L160 363Z',eye,accent,1));
 for(let y=394;y<=434;y+=13)svg.push(path(`M${160-w*.40} ${y} Q160 ${y-5} ${160+w*.42} ${y}`, 'none',accent,1.5));
 // Left arm with hand guards
 svg.push(path(`M${160-shoulder} 311 L${160-shoulder-19} 375 L${160-shoulder-4} 395 L${160-w*.55} 434 L${160-w*.39} 418 L${160-shoulder+18} 364Z`,primary,accent,4));
 svg.push(path(`M${160-w*.55} 424 L${151-w*.41} 438 L${154-w*.17} 427 L${158-w*.32} 410Z`,skin,shadow,2));
 // Right weapon arm uses pose-specific position; shield/weapon readability
 const hx=hand[0],hy=hand[1];
 svg.push(path(`M${160+shoulder-3} 316 L${guardian?256:226} 348 L${hx-9} ${hy} L${hx+13} ${hy+13} L${guardian?272:243} 375 L${160+shoulder-25} 353Z`,primary,accent,4));
 svg.push(path(`M${hx-8} ${hy-5} l16 -4 l14 15 l-23 13Z`,skin,accent,2));
 // Neck and detailed multi-angle face
 svg.push(path('M141 279 L142 307 Q159 318 177 301 L175 274Z',skin,shadow,3));
 svg.push(path(`M${155-headW+side} 204 Q${151-headW} 226 ${144-headW+side} 255 Q139 288 ${167+side} 288 Q${166+headW} 280 ${161+headW} 248 L${162+headW} 217 Q160 185 ${155-headW+side} 204Z`,skin,shadow,4));
 svg.push(path(`M${163-headW+side} 222 Q152 173 183 174 Q${213+headW} 186 ${166+headW} 242 L${167+headW} 223 Q191 210 188 211 Q165 218 ${164-headW} 230Z`,hair,accent,4));
 for(const [j,offset] of [[0,-32],[1,-7],[2,19]])svg.push(path(`M${159+offset} 186 Q${145+offset} 218 ${138+offset} ${233+j*4} Q${155+offset} 227 ${160+offset} 203`, 'none',guardian?accent:shadow,3));
 if(!profile){
  const angry=expression==='angry'||expression==='focused';
  const eyY=241+(expression==='hurt'?5:0);
  svg.push(path(`M129 ${eyY-7} Q140 ${eyY-(angry?13:10)} 148 ${eyY-6}`,'none',shadow,3));
  svg.push(path(`M168 ${eyY-6} Q181 ${eyY-(angry?13:10)} 192 ${eyY-7}`,'none',shadow,3));
  svg.push(path(`M128 ${eyY} Q139 ${eyY-6} 148 ${eyY} Q140 ${eyY+5} 128 ${eyY}Z`,bright,shadow,2));
  svg.push(path(`M168 ${eyY} Q181 ${eyY-6} 193 ${eyY} Q181 ${eyY+5} 168 ${eyY}Z`,bright,shadow,2));
  svg.push(circle(139,eyY,4,eye));svg.push(circle(181,eyY,4,eye));
 }else{svg.push(path('M185 237 Q198 230 201 238 L189 244Z',eye,shadow,3));svg.push(path('M204 247 L221 258 L204 261Z',skin,shadow,2));}
 svg.push(path(expression==='hurt'?'M153 272 Q160 265 171 270':expression==='confident'?'M151 267 Q164 279 176 265':'M155 267 Q165 268 172 265','none',shadow,2));
 if(guardian){ // helmet and imposing horns distinct from hero
  svg.push(path('M106 218 L88 159 L133 174 L149 190 Q176 162 217 183 L245 155 L235 238 L216 224 L195 197 L158 202 L128 228Z',primary,accent,5));
  svg.push(path('M97 160 L80 113 L130 172Z',shadow,accent,4));svg.push(path('M237 161 L259 116 L221 173Z',shadow,accent,4));
  svg.push(path('M129 239 L189 236 L218 248 L185 259 L153 255Z',shadow,accent,2));
  svg.push(path('M137 244 L152 244 M171 244 L191 242','none',eye,5));
 }else{
  svg.push(path('M116 195 Q91 200 95 266 L108 341 Q122 295 130 252Z',hair,accent,4));
  svg.push(path('M190 197 Q205 249 190 284 Q223 260 224 208Z',hair,accent,3));
  svg.push(path('M113 235 L129 210 L135 235Z',accent,'none',0));
 }
 if(mystic){ // tall curved hat brim and forehead symbol
   svg.push(path('M98 211 Q140 175 176 179 Q215 163 232 218 L270 231 Q160 245 76 229Z',primary,accent,4));
   svg.push(path('M127 184 Q146 101 175 54 Q191 133 203 184Z',shadow,accent,5));
   svg.push(circle(177,173,8,eye));
 }
 if(duelist){ // long sharply angled epaulette and feather
   svg.push(path('M88 300 L34 269 L75 256 L123 300Z',primary,accent,3));
   svg.push(path('M162 198 Q233 112 238 72 Q192 116 184 198', 'none',accent,9));
 }
 if(ranger){ // asymmetric hood and quiver
   svg.push(path('M116 204 Q157 137 218 207 L228 258 L199 224 L170 193 L123 258Z',primary,accent,4));
   svg.push(path('M70 320 L82 210 L103 220 L97 344Z',shadow,accent,3));
   for(let i=0;i<4;i++)svg.push(path(`M${70+i*8} 218 L${62+i*8} 173`, 'none',weapon,3));
 }
 if(mechanist){ // asymmetric machine shoulder and cog
   svg.push(path('M70 289 L32 281 L23 336 L77 349 L114 317Z',primary,accent,4));
   svg.push(circle(65,316,21,shadow));svg.push(circle(65,316,11,accent));svg.push(circle(65,316,4,weapon));
   svg.push(path('M132 196 L127 149 L148 149 L156 197Z',primary,accent,4));
   svg.push(circle(141,140,8,eye));
 }
 // Blade or glaive; weapon tangent varies by pose, visually distinct shapes
 const wx=hx+8,wy=hy-6;
 if(guardian||mechanist){svg.push(path(`M${wx} ${wy+110} L${wx+54} ${wy-111}`, 'none','#b4a5c9',10));svg.push(path(`M${wx+49} ${wy-109} L${wx+90} ${wy-169} L${wx+91} ${wy-110} L${wx+68} ${wy-80}Z`,'url(#steel)',accent,3));}
 else if(ranger){svg.push(path(`M${wx+20} ${wy-95} Q${wx-9} ${wy-13} ${wx+20} ${wy+74}`, 'none',weapon,7));svg.push(path(`M${wx+20} ${wy-95} Q${wx+68} ${wy-9} ${wx+20} ${wy+74}`,'none',accent,3));svg.push(path(`M${wx+14} ${wy-10} L${wx+94} ${wy-10}`, 'none',weapon,3));}
 else if(mystic){svg.push(path(`M${wx+14} ${wy+122} L${wx+34} ${wy-92}`,'none',weapon,10));svg.push(circle(wx+35,wy-104,23,accent));svg.push(circle(wx+35,wy-104,10,eye));}
 else if(duelist){svg.push(path(`M${wx+8} ${wy+7} L${wx+20} ${wy-13}`, 'none',shadow,12));svg.push(path(`M${wx+20} ${wy-13} L${wx+85} ${wy-156}`, 'none',weapon,4));svg.push(path(`M${wx-8} ${wy-16} L${wx+45} ${wy-18}`,'none',accent,5));}
 else{svg.push(path(`M${wx} ${wy} L${wx+30} ${wy-18}`,'none',shadow,12));svg.push(path(`M${wx+22} ${wy-18} Q${wx+55} ${wy-65} ${wx+64} ${wy-100} L${wx+73} ${wy-80} Q${wx+65} ${wy-44} ${wx+22} ${wy-18}Z`,'url(#steel)',accent,2));}
 svg.push(`</g></svg>`);return svg.join('');
}
function dataUri(svg){return 'data:image/svg+xml;charset=utf-8,'+encodeURIComponent(svg);}
function makeSprite(kit,view,pose,expression){return dataUri(makeSvg(kit,view,pose,expression));}
return {VIEWS,POSES,EXPRESSIONS,defaultKit,ensure,fingerprint,viewForShot,poseForState,expressionForPose,spriteKey,selectSprite,recordSprite,audit,makeSvg,dataUri,makeSprite,hash};
});
