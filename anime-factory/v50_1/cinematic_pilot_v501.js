/* AI Anime Factory V50.1 — cinematic pilot renderer.
 * A genuine new Canvas frame pipeline for the two canon pilot episodes.
 * The old V19-V50 renderer remains the fallback for every other project.
 * Characters are intentionally different silhouettes, proportions, outfits
 * and weapons. Battle takes place across a timed 10-beat choreography.
 * Artwork is hand-coded vector illustration, NOT neural anime illustration.
 */
const v501Profiles=Object.freeze({
 hero:{id:'hero',hair:'#172a50',edge:'#3a78b9',eye:'#5af2ff',coat:'#112846',trim:'#63dcef',skin:'#f0c0a6',aura:'#4be4ff',length:0.97,head:0.96,weapon:'sword'},
 lover:{id:'lover',hair:'#e3e6f1',edge:'#af9aca',eye:'#905aa8',coat:'#493454',trim:'#efafcc',skin:'#f7d1c4',aura:'#ffc5ea',length:0.91,head:0.92,weapon:'staff'},
 friend:{id:'friend',hair:'#27362b',edge:'#619177',eye:'#e5ba7b',coat:'#253f37',trim:'#b2be8f',skin:'#dab59b',aura:'#b8ffc1',length:1.02,head:0.96,weapon:'dagger'},
 rival:{id:'rival',hair:'#281c33',edge:'#a65468',eye:'#e8ac79',coat:'#593044',trim:'#d8a579',skin:'#e2b19c',aura:'#ffaa83',length:1.04,head:0.94,weapon:'spear'},
 enemy:{id:'enemy',hair:'#251d2b',edge:'#863c69',eye:'#ff6669',coat:'#28192d',trim:'#bc667b',skin:'#a8939d',aura:'#f45f9d',length:1.14,head:1,weapon:'staff'},
 guardian:{id:'guardian',hair:'#101922',edge:'#455265',eye:'#ff515e',coat:'#151f2f',trim:'#a14356',skin:'#333c48',aura:'#ff5d78',length:1.05,head:1.04,weapon:'axe'}
});
const v501Ease=t=>{t=Math.max(0,Math.min(1,t));return t*t*(3-2*t);};
const v501Lerp=(a,b,t)=>a+(b-a)*v501Ease(t);
function v501Shape(g,points,fill,stroke,width=2){
 g.beginPath();points.forEach((p,i)=>i?g.lineTo(p[0],p[1]):g.moveTo(p[0],p[1]));g.closePath();
 g.fillStyle=fill;g.fill();if(stroke){g.strokeStyle=stroke;g.lineWidth=width;g.stroke();}
}
function v501Line(g,points,stroke,width=3){
 g.beginPath();points.forEach((p,i)=>i?g.lineTo(p[0],p[1]):g.moveTo(p[0],p[1]));
 g.strokeStyle=stroke;g.lineWidth=width;g.lineCap='round';g.lineJoin='round';g.stroke();
}
function v501Glow(g,x,y,r,color,alpha=.5){
 g.save();g.globalAlpha=alpha;const l=g.createRadialGradient(x,y,0,x,y,r);
 l.addColorStop(0,color);l.addColorStop(.35,color+'77');l.addColorStop(1,color+'00');
 g.fillStyle=l;g.beginPath();g.arc(x,y,r,0,7);g.fill();g.restore();
}
function v501Backdrop(g,ei,si,t){
 const kinds=['city','bridge','battle','memory','secret','gate'];
 const kind=kinds[si]||'city';
 const moods=[
 ['#07172b','#254769','#cb947c'],['#111d2a','#394b58','#8e9c92'],
 ['#170e22','#592c46','#f5a27a'],['#151c38','#583852','#e6a8a2'],
 ['#080f1e','#263342','#77a1a4'],['#0a142b','#263965','#9c86ad']
 ];
 const [a,b,c]=moods[si];const gr=g.createLinearGradient(0,0,0,540);
 gr.addColorStop(0,a);gr.addColorStop(.68,b);gr.addColorStop(1,c);
 g.fillStyle=gr;g.fillRect(0,0,960,540);
 // Thin-crescent moon/sun light and atmospheric volume
 const sunX=si===3?742:718,sunY=si===3?136:100;
 v501Glow(g,sunX,sunY,si===3?235:170,si===3?'#ffd2aa':'#8fd6ff',si===3?.29:.16);
 g.fillStyle=si===3?'#ffe2c8':'#a9c5db';g.globalAlpha=.48;g.beginPath();
 g.arc(sunX,sunY,si===3?56:43,0,7);g.fill();g.globalAlpha=1;
 // Parallax clouds and distant ruined skyline
 for(let layer=0;layer<3;layer++){
   const span=45+layer*29,base=300+layer*32;
   for(let i=-1;i<15;i++){
     const x=i*(span+14)+(layer%2)*17+Math.sin(i*11+ei)*9-t*(2+layer);
     const height=40+Math.abs(Math.sin(i*7.31+ei*2))*115;
     g.fillStyle=['#101b2a44','#121a33aa','#101e30ed'][layer];
     g.fillRect(x,base-height,span,215);
     g.strokeStyle='#c4d6ec10';g.lineWidth=1;
     for(let n=0;n<3;n++)g.strokeRect(x+10+n*12,base-height+15,6,11);
   }
 }
 // Location-specific architecture (not a recycled rectangle background)
 if(kind==='bridge'){
   g.save();g.strokeStyle='#b1c6c855';g.lineWidth=7;
   g.beginPath();g.moveTo(-10,300);g.quadraticCurveTo(480,427,970,298);g.stroke();
   for(let i=0;i<11;i++){const x=i*100;
     v501Line(g,[[x,290],[x+20,425]],'#172a33',7);}
   v501Line(g,[[-10,437],[960,437]],'#d0e8ce66',4);
   g.restore();
 } else if(kind==='battle'){
   for(let i=0;i<7;i++){
     const x=65+i*142;
     v501Shape(g,[[x-30,403],[x-12,170],[x+18,156],[x+37,398]],'#283041','#85909a77',2);
     g.strokeStyle='#b1516388';g.lineWidth=5;g.beginPath();g.arc(x+5,197,23,0,Math.PI*2);g.stroke();
   }
 } else if(kind==='memory'){
   for(let i=0;i<7;i++){
     const x=20+i*151;
     v501Shape(g,[[x,420],[x+30,275],[x+88,275],[x+112,420]],'#43304388','#ffdfb22a');
   }
   for(let i=0;i<9;i++)v501Glow(g,(i*171+30)%960,190+i%4*52,38,'#f7ccaf',.2);
 } else if(kind==='secret'){
   g.fillStyle='#111b26';g.fillRect(0,170,950,245);
   for(let i=0;i<8;i++){
      const x=i*135;v501Shape(g,[[x,396],[x+14,120],[x+58,120],[x+72,396]],'#26323b','#53737d55');
   }
   v501Glow(g,475,238,160,'#93d6b1',.15);
 } else if(kind==='gate'){
   g.save();g.translate(470,316);g.strokeStyle='#b8dcff77';g.lineWidth=14;
   g.beginPath();g.ellipse(0,0,214,210,0,Math.PI,2*Math.PI);g.lineTo(214,175);
   g.lineTo(-214,175);g.closePath();g.stroke();
   for(let i=0;i<4;i++){g.beginPath();g.ellipse(0,-2,65+i*36,86+i*36,0,0,7);g.strokeStyle='#95cae5'+['70','50','30','20'][i];g.lineWidth=2;g.stroke();}
   g.restore();
 } else {
   for(let i=0;i<6;i++){
     let x=i*190;
     v501Shape(g,[[x,421],[x+28,175],[x+45,90],[x+67,168],[x+91,421]],'#263c4a','#94b8bf26');
     g.strokeStyle='#c6d1d428';g.strokeRect(x+21,208,42,80);
   }
 }
 // Perspective ground and foreground fog
 const ground=g.createLinearGradient(0,399,0,540);ground.addColorStop(0,'#10152455');ground.addColorStop(1,'#050b14f7');
 g.fillStyle=ground;g.fillRect(0,390,960,150);
 g.strokeStyle='#b7c2cc22';g.lineWidth=2;
 for(let i=-5;i<9;i++)v501Line(g,[[480,390],[480+(i*170),540]],'#9daab922',1);
 for(let y=402;y<545;y+=32) v501Line(g,[[0,y],[960,y]],'#9daab91a',1);
 for(let i=0;i<65;i++){
   const x=(i*157.21+ei*73+si*29)%960,y=(i*91.23+si*101+t*(4+i%6))%540;
   const r=i%9===0?2.2:1;
   g.fillStyle=i%4?'#cdd8e844':'#eab7a977';g.fillRect(x,y,r,r);
 }
}
function v501Eye(g,x,y,color,blink){
 g.save();g.translate(x,y);g.scale(1,Math.max(.14,1-blink));
 v501Shape(g,[[-17,-2],[-8,-8],[5,-7],[16,-1],[5,5],[-9,4]],'#f1e5dc','#253047',1.3);
 g.fillStyle=color;g.beginPath();g.ellipse(1,0,5,7,0,0,7);g.fill();
 g.fillStyle='#0a2035';g.beginPath();g.ellipse(1,0,2,5,0,0,7);g.fill();
 g.fillStyle='#fff';g.beginPath();g.arc(-1,-2,2,0,7);g.fill();g.restore();
}
function v501Hair(g,id,p,t){
 const hairGr=g.createLinearGradient(0,-395,55,-330);
 hairGr.addColorStop(0,p.edge);hairGr.addColorStop(.5,p.hair);hairGr.addColorStop(1,'#142539');
 // Clear facial recognition zone: do not put hair over eyes or mouth.
 if(id==='lover'){
   v501Shape(g,[[-62,-352],[-85,-248],[-64,-125],[-50,-188],
     [-46,-343],[40,-345],[62,-175],[88,-144],[69,-335]],hairGr,'#d7badb',2);
   v501Shape(g,[[-55,-366],[-39,-394],[28,-395],[58,-369],
      [49,-355],[25,-362],[-25,-356]],hairGr,p.edge,1.4);
 }else if(id==='friend'){
   v501Shape(g,[[-66,-353],[-71,-391],[-45,-407],[32,-402],[68,-375],
      [57,-350],[20,-360],[-20,-352]],hairGr,p.edge,2);
   v501Shape(g,[[-50,-366],[-25,-348],[-8,-356],[5,-343],
      [20,-360],[36,-348],[50,-360],[27,-380],[-30,-377]],hairGr,p.edge,1.5);
 }else if(id==='rival'){
   v501Shape(g,[[-59,-357],[-75,-295],[-61,-217],[-48,-262],[-45,-355],
      [38,-352],[55,-228],[74,-217],[64,-344]],hairGr,p.edge,2);
   v501Shape(g,[[-55,-373],[-20,-399],[40,-391],[58,-367],
      [27,-357],[2,-368],[-34,-357]],hairGr,p.edge,2);
 }else if(id==='guardian'){
   for(let n=0;n<5;n++)
     v501Shape(g,[[n*23-58,-363],[n*25-65,-410-n%2*10],
       [n*24-43,-368]],p.hair,p.edge,2);
 }else{
   v501Shape(g,[[-67,-370],[-87,-381],[-53,-390],[-28,-405],
     [23,-404],[52,-386],[79,-379],[56,-360],[17,-366],[-31,-354]],
     hairGr,p.edge,2);
   for(let n=0;n<5;n++)
     v501Shape(g,[[-53+n*23,-381],[-61+n*23,-344],
       [-32+n*23,-359]],n%2?p.hair:p.edge);
 }
}
function v501Weapon(g,p,attack=0){
 // Every weapon grip stays connected to the right hand near local (20,110).
 g.save();g.rotate(attack*.6);
 if(p.weapon==='sword'){
   v501Line(g,[[18,117],[49,70]],'#273c53',11);
   v501Line(g,[[23,91],[68,102]],'#b5a477',8);
   v501Shape(g,[[49,71],[125,-37],[143,-56],[133,-18],
     [61,79]],'#77d8eb','#e8ffff',2.5);
   v501Line(g,[[60,64],[133,-39]],'#d7ffff',2);
   v501Glow(g,132,-31,23,'#59e4f9',.23);
 }else if(p.weapon==='staff'){
   v501Line(g,[[23,136],[89,-110]],'#ad9bb7',10);
   v501Shape(g,[[90,-146],[73,-113],[89,-92],[107,-115]],
      '#ffe2e9','#fff0ef',2);
   v501Glow(g,89,-118,31,'#ffd7fa',.33);
 }else if(p.weapon==='dagger'){
   v501Line(g,[[19,118],[45,79]],'#b2a883',10);
   v501Shape(g,[[40,85],[90,20],[86,45],[54,92]],
     '#bfe4ce','#f5fff0',2);
 }else if(p.weapon==='spear'){
   v501Line(g,[[25,141],[94,-115]],'#b0907c',9);
   v501Shape(g,[[95,-158],[78,-113],[94,-103],[113,-117]],
      '#f5dcb6','#fff7dd',2.2);
 }else{
   v501Line(g,[[22,126],[66,9]],'#929ba7',13);
   v501Shape(g,[[68,-14],[116,-48],[149,-11],[128,51],[76,36]],
      '#444959',p.trim,4);
   v501Line(g,[[80,24],[123,-5]],'#e0abba',2);
 }
 g.restore();
}
function v501Actor(g,id,x,y,scale,dir,pose,sec,local){
 const p=v501Profiles[id]||v501Profiles.hero;
 const bob=Math.sin(sec*2.7+(id.length*.91))*1.8;
 const blink=((Math.sin(sec*1.79+id.length*2.8)+1)/2)>.991?.92:0;
 g.save();g.translate(x,y+bob);g.scale((dir||1)*scale*p.length,scale*p.length);
 const lean=pose.lean||0;
 g.rotate(lean);
 v501Glow(g,0,-180,190,p.aura,.18);
 // grounded shadow
 g.save();g.scale(1,1/scale);
 g.fillStyle='#02070ba0';g.beginPath();g.ellipse(0,0,78,10,0,0,7);g.fill();g.restore();
 const leftStep=pose.step||0;
 // legs with articulated knee and feet
 for(let sign of [-1,1]){
   let lx=sign*24+leftStep*sign,ly=-81;
   v501Shape(g,[[lx-18,ly],[lx+16,ly],[lx+10,-40],[lx+20+sign*6,-10],[lx-22+sign*4,-10]],p.coat,p.trim,2);
   v501Shape(g,[[lx-28+sign*4,-16],[lx+25+sign*7,-16],[lx+29+sign*7,1],[lx-27,1]],'#15202d','#8fa6a9',2);
   v501Line(g,[[lx-14,-52],[lx+15,-44]],p.trim,3);
 }
 const cp=g.createLinearGradient(-85,-240,110,-52);cp.addColorStop(0,p.hair);
 cp.addColorStop(.3,p.coat);cp.addColorStop(.7,'#0b1524');cp.addColorStop(1,p.edge);
 // flowing distinctive cape silhouette
 const cape=pose.cape||0;
 v501Shape(g,[[-54,-254],[-95,-182],[-127-cape,-35],[-38,-77],[45,-71],[112+cape,-38],[81,-232]],cp,p.trim,3);
 if(id==='friend'){
   v501Shape(g,[[-80,-273],[-98,-319],[-44,-343],[68,-342],[94,-286],[58,-241],[-54,-239]],'#1c352e','#9eb494',3);
 }
 // torso armor/tunic with waist piece and edge patterns
 v501Shape(g,[[-66,-238],[-49,-276],[50,-275],[69,-235],[48,-100],[-45,-100]],p.coat,p.trim,4);
 v501Shape(g,[[-47,-259],[-4,-234],[45,-262],[29,-135],[3,-101],[-32,-136]],'#18334a99',p.edge,2.5);
 v501Line(g,[[-52,-143],[54,-143]],p.trim,6);
 g.fillStyle=p.trim;g.beginPath();g.arc(0,-143,8,0,7);g.fill();
 for(let i=0;i<4;i++){v501Line(g,[[-33,-211+i*23],[-20,-202+i*23]],p.edge,2);}
 if(id==='lover'){
   v501Shape(g,[[-48,-152],[-95,-62],[3,-25],[101,-62],[48,-152]],'#5e4268','#f6c5e4',3);
   v501Line(g,[[-68,-80],[69,-80]],'#f2b5db',3);
 }else if(id==='rival'){
   v501Shape(g,[[-40,-211],[7,-220],[42,-206],[35,-164],[-35,-165]],'#b9a1a0',p.trim,3);
   v501Shape(g,[[-15,-236],[15,-236],[9,-161],[-13,-161]],'#bf5563',null);
 }else if(id==='guardian'){
   for(let i=0;i<3;i++)v501Shape(g,[[-42,-240+i*45],[0,-250+i*45],[42,-240+i*45],[30,-223+i*45],[-33,-223+i*45]],'#505463',p.trim,3);
   v501Shape(g,[[-84,-255],[-105,-285],[-67,-305],[-36,-276]],'#525a68','#c96772',4);
 }
 // left arm: sheath or guarding stance
 g.save();g.translate(-62,-242);g.rotate((pose.arm||0)*.72-.06);
 v501Shape(g,[[-14,0],[16,2],[21,87],[-18,97]],p.coat,p.trim,4);
 v501Shape(g,[[-18,93],[22,83],[23,114],[-7,125]],p.skin,'#ab8276',2);
 g.restore();
 // right arm and weapon
 g.save();g.translate(61,-245);g.rotate(-(pose.arm||0)*1.05-.12);
 v501Shape(g,[[-13,0],[18,-1],[28,94],[-11,98]],p.coat,p.trim,3);
 v501Shape(g,[[-12,90],[30,87],[30,112],[-13,119]],p.skin,'#ab8276',2);
 v501Weapon(g,p,pose.attack||0);
 g.restore();
 // neck, jaw, face with individualized shape & expressive brows
 v501Shape(g,[[-22,-273],[22,-273],[20,-303],[-20,-303]],p.skin);
 if(id==='guardian'){
   v501Shape(g,[[-59,-306],[-65,-353],[-34,-384],[38,-382],[61,-349],[52,-312],[18,-287],[-30,-287]],'#303948','#cb677c',4);
   g.fillStyle=p.eye;v501Line(g,[[-40,-340],[-12,-333],[13,-337],[40,-342]],p.eye,7);
 }else{
   const face=id==='lover'?
      [[-43,-322],[-52,-353],[-34,-388],[25,-393],[47,-356],[42,-320],[7,-289],[-14,-291]]:
      id==='friend'?[[-52,-329],[-58,-356],[-29,-383],[36,-386],[53,-355],[47,-320],[20,-298],[-22,-303]]:
      id==='rival'?[[-45,-319],[-53,-354],[-37,-393],[31,-394],[51,-355],[46,-318],[16,-286],[-19,-294]]:
      [[-48,-322],[-56,-356],[-35,-388],[29,-389],[52,-357],[45,-317],[14,-286],[-21,-291]];
   v501Shape(g,face,p.skin,'#9a747a',2);
   g.fillStyle='#d58d9066';g.beginPath();g.ellipse(-33,-322,14,7,0,0,7);g.fill();
   g.beginPath();g.ellipse(33,-321,14,7,0,0,7);g.fill();
   g.save();if(id==='lover')g.scale(1,1.15);if(id==='friend')g.scale(1,.82);
   const eyeY=id==='lover'?-305:id==='friend'?-420:-347;
   v501Eye(g,-23,eyeY,p.eye,blink);v501Eye(g,24,eyeY,p.eye,blink);
   g.restore();
   v501Line(g,[[-37,-364],[-12,-371]],p.hair,id==='rival'?5:3);
   v501Line(g,[[12,-370],[38,-365]],p.hair,id==='rival'?5:3);
   v501Line(g,[[2,-343],[-2,-324],[8,-323]],'#b97c7d',1.5);
   const speaker=local?.speaker===id;
   const energy=speaker?(local?.energy ?? 0):0;
   g.fillStyle='#74383c';g.beginPath();
   g.ellipse(4,-308,9,1.5+(speaker?4*energy:0),0,0,7);g.fill();
   if(id==='hero')v501Line(g,[[36,-324],[49,-332]],'#ad8490',3);
   if(id==='friend')v501Shape(g,[[38,-332],[57,-330],[50,-316]],'#9a7762');
 }
 v501Hair(g,id,p,sec);
 if(id==='hero'){
   // signature asymmetrical cyan scarf and cloak crest
   v501Shape(g,[[-43,-276],[31,-281],[41,-255],[16,-239],[-39,-249]],'#237d9a','#b5f5ff',3);
   v501Shape(g,[[-41,-256],[-73,-237],[-55,-148],[-18,-221]],'#247e96','#9efaff',2);
 }else if(id==='lover'){
   v501Shape(g,[[-69,-340],[-81,-371],[-65,-378],[-51,-349]],'#df7fa8','#fff0e8');
   v501Glow(g,0,-209,26,'#ffe1b9',.3);
 }else if(id==='friend'){
   v501Shape(g,[[34,-295],[59,-293],[63,-272],[38,-269]],'#ae8e50','#e7c57b',2);
 }else if(id==='rival'){
   v501Shape(g,[[51,-276],[82,-250],[96,-188],[51,-234]],'#a84954','#e1a47a',3);
 }
 g.restore();
}
function v501Battle(f){
 // Grounded positions from the same left-right staging axis across beats.
 const knots=[
 [0,.26,.77,0,0,0],[.13,.27,.70,-.08,0,.1],
 [.24,.43,.63,.27,.75,.5],[.36,.48,.62,-.13,.4,.23],
 [.48,.37,.68,-.32,0,.3],[.60,.43,.67,.1,.4,.3],
 [.73,.57,.63,.46,1,.85],[.82,.44,.78,-.17,0,.4],
 [1,.37,.76,-.15,0,.08]
 ];
 let idx=0;while(idx<knots.length-2&&f>knots[idx+1][0])idx++;
 let a=knots[idx],b=knots[idx+1],t=(f-a[0])/(b[0]-a[0]||1);
 return {heroX:v501Lerp(a[1],b[1],t),foeX:v501Lerp(a[2],b[2],t),
   lean:v501Lerp(a[3],b[3],t),attack:v501Lerp(a[4],b[4],t),
   fx:v501Lerp(a[5],b[5],t),beat:idx};
}
function v501BattleFX(g,f,motion,sec){
 if(f>.19&&f<.37 || f>.64&&f<.81){
   const px=motion.heroX*960+125,py=260;
   const alpha=f>.64&&f<.81?Math.sin((f-.64)/.17*Math.PI):Math.sin((f-.19)/.18*Math.PI);
   g.save();g.globalAlpha=Math.max(.12,alpha);g.strokeStyle='#9dfaff';g.lineWidth=18;g.shadowBlur=32;g.shadowColor='#56e2f7';
   g.beginPath();g.ellipse(px,py,115,155,1.2,-2.5,1.13);g.stroke();g.restore();
 }
 if(f>.63&&f<.82){const u=(f-.63)/.19;
   v501Glow(g,(motion.heroX+motion.foeX)*480,260,180*u+20,'#8befff',.3*(1-u));
   for(let i=0;i<32;i++){
     let angle=i*2.399,dist=20+u*(i%9)*17;
     const px=(motion.heroX+motion.foeX)*480+Math.cos(angle)*dist;
     const py=265+Math.sin(angle)*dist*.7;
     v501Line(g,[[px,py],[px+Math.cos(angle)*19,py+Math.sin(angle)*19]],i%3?'#fff8c0':'#6efbff',2.5);
   }
 }
 if(f>.79){const a=Math.min(1,(f-.79)*9);
   g.save();g.fillStyle='rgba(8,15,25,'+(a*.20)+')';g.fillRect(0,0,960,540);g.restore();
 }
}
function v501SceneDraw(g,ei,scene,localTime){
 const si=(P.episodes[ei]?.scenes||[]).indexOf(scene);
 const f=Math.max(0,Math.min(1,localTime/Math.max(.1,scene.duration)));
 v501Backdrop(g,ei,si,localTime);
 let actors=[['hero',.36],['rival',.7]];
 if(si===1)actors=[['hero',.34],['friend',.67]];
 if(si===2)actors=[['hero',.29],['guardian',.75]];
 if(si===3)actors=[['hero',.36],['lover',.67]];
 if(si===4)actors=[['friend',.48],['hero',.79]];
 if(si===5)actors=[['hero',.36],['lover',.68]];
 const lines=scene.lines||[],active=lines.find(l=>localTime>=l.start&&localTime<l.start+l.duration);
 const name=active?.speaker||'';
 const role=P.characters.find(c=>c.name===name)?.id||'';
 const config=scene.audioV36?.voice||{},offset=Number(config.offset)||0;
 const segment=(config.segmentsV501||[]).find(q=>
   localTime>=offset+q.start && localTime<offset+q.end);
 const alias={hero:'hero',miyu:'lover',ren:'friend',saira:'rival',archon:'enemy'};
 const speaker=segment?(alias[segment.role]||''):role;
 const wave=config.waveV47||[],sampleRate=Number(config.sampleRateV47)||50;
 const ii=Math.max(0,Math.floor((localTime-offset)*sampleRate));
 const energy=Math.min(1,Math.max(0,Number(wave[ii])||0));
 const v501Local={speaker,energy};
 const motion=si===2?v501Battle(f):null;
 // Lens direction varied by scene; no same 2-shot in every scene.
 g.save();
 const zoom=si===3?1.16:si===4?1.19:si===2?1.02:si===0?1.0:1.07;
 const drift=Math.sin(f*Math.PI)*(si===2?4:si===4?-16:10);
 g.translate(480,270);g.scale(zoom,zoom);g.translate(-480+drift,-270);
 for(let i=0;i<actors.length;i++){
   const [key,x]=actors[i];const px=(si===2?(i===0?motion.heroX:motion.foeX):x)*960;
   const py=473+Math.sin(localTime*2+i)*1.4;
   let p={step:Math.sin(localTime*(si===2?12:3.2)+i)*3,
          arm:si===2?(i===0?motion.attack:-motion.attack*.35):(.10*Math.sin(localTime*1.9+i)),
          cape:Math.sin(localTime*3+i)*6};
   if(si===2){
     p.lean=i===0?motion.lean:-motion.lean*.3;
     p.attack=motion.attack;
     if(i===0&&f>.82)p.lean=-.24;
   }
   if(si===3)p.arm=.05+Math.sin(f*3.14)*.10;
   if(si===4&&i===0)p.lean=.06;
   const sc=si===2&&i===1?0.85:key==='guardian'?0.86:si===3?0.9:0.94;
   v501Actor(g,key,px,py,sc,i===0?1:-1,p,localTime,v501Local);
 }
 if(si===2)v501BattleFX(g,f,motion,localTime);
 if(si===4){ // tangible betrayal clue
    v501Glow(g,446,353,20,'#c5eeaf',.38);
    g.strokeStyle='#b4d3ba';g.lineWidth=3;g.beginPath();g.arc(446,353,13,0,7);g.stroke();
 }
 g.restore();
 // Poster-like cinematic letterboxing and discreet scene identity.
 g.fillStyle='#060b16';g.fillRect(0,0,960,24);g.fillRect(0,512,960,28);
 g.font='600 13px Segoe UI, sans-serif';g.fillStyle='#d7dbe3';
 g.fillText('ОСКОЛКИ ЗАБЫТОЙ КЛЯТВЫ  /  ЭПИЗОД '+(ei+1),28,16);
 const title=(scene.title||'').slice(0,44);
 g.textAlign='right';g.fillText(title,932,16);g.textAlign='left';
}
const v501OlderFrame=v35Frame;
v35Frame=function(canvas,ep,seconds){
 if(!P?.v501Visual?.enabled || !ep?.pilotV50 || !(P.episodes||[]).slice(0,2).includes(ep))
   return v501OlderFrame(canvas,ep,seconds);
 const state=v35Find(ep,seconds),g=canvas.getContext('2d');
 const w=canvas.width,h=canvas.height;
 g.save();g.setTransform(1,0,0,1,0,0);
 g.clearRect(0,0,w,h);
 g.scale(w/960,h/540);
 const row=state.row;
 if(row){
   const ei=P.episodes.indexOf(ep);
   v501SceneDraw(g,ei,row.scene,Math.max(0,Math.min(row.duration,state.t-row.start)));
 }
 g.restore();
 if(typeof v48DrawCredits==='function')v48DrawCredits(canvas,ep,seconds);
 return state;
};
/* Pilot-specific subtitle overlay: readable Russian text without a giant
 * opaque black rectangle hiding the character animation. Old V37 untouched
 * outside these first two pilot episodes.
 */
const v501PriorSubtitles=v37Paint;
v37Paint=function(canvas,episode,seconds){
 if(!P?.v501Visual?.enabled || !episode?.pilotV50 ||
    !(P.episodes||[]).slice(0,2).includes(episode))
   return v501PriorSubtitles(canvas,episode,seconds);
 const active=v37Active(episode,seconds).slice(0,1);
 if(!active.length)return active;
 const g=canvas.getContext('2d'),w=canvas.width,h=canvas.height;
 const scale=w/640,caption=active[0].text;
 g.save();g.setTransform(1,0,0,1,0,0);
 g.font='600 '+Math.max(13,Math.round(19*scale))+'px Segoe UI, Arial, sans-serif';
 const rows=v37Lines(g,caption,w*.82,2);
 const lineH=27*scale,boxH=(rows.length*lineH)+12*scale;
 const top=h-18*scale-boxH, left=w*.10,boxW=w*.80;
 g.fillStyle='rgba(3,10,24,.67)';
 g.beginPath();
 if(typeof g.roundRect==='function')g.roundRect(left,top,boxW,boxH,8*scale);
 else g.rect(left,top,boxW,boxH);
 g.fill();
 g.textAlign='center';g.textBaseline='middle';
 g.fillStyle='#f8f6f5';g.shadowColor='#000';g.shadowBlur=5*scale;
 for(let i=0;i<rows.length;i++)
   g.fillText(rows[i],w/2,top+11*scale+(i+.5)*lineH);
 g.restore();
 return active;
};

window.v501Visual=Object.freeze({
 version:'50.1.0',profiles:Object.keys(v501Profiles),
 pilotOnly:true,renderer:'distinct hand-coded cinematic Canvas actors',
 battleBeats:9,sourceCanonPreserved:true,
 frame:(episode,time)=>{const ep=P?.episodes?.[episode];if(!ep)throw Error('No episode');
   const c=document.createElement('canvas');c.width=960;c.height=540;
   v35Frame(c,ep,time);return c.toDataURL('image/png');}
});
function v501Settings(){
 if(!P)return;
 if(!P.v501Visual)P.v501Visual={enabled:false};
 const box=$('v501-enabled');if(box)box.checked=!!P.v501Visual.enabled;
}
const v501Toggle=$('v501-enabled');
if(v501Toggle)v501Toggle.onchange=()=>{
 if(!P)return;P.v501Visual={enabled:v501Toggle.checked};save();
 if(typeof v48Draw==='function')v48Draw();
 notify('V50.1: '+(P.v501Visual.enabled?'пилотный кино-рендер включён':'исходный V50 рендер восстановлен'));
};
