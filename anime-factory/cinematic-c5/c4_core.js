/* AI ANIME FACTORY C4 HYBRID 3D / Original open source WebGL prototype. No third-party runtime. */
(function(root){'use strict';
const PI=Math.PI, TAU=2*PI;
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x)),mix=(a,b,t)=>a+(b-a)*t,smooth=t=>{t=clamp(t,0,1);return t*t*(3-2*t)};
const length=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1],a[2]-b[2]);
const identity=()=>[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1];
function mul(a,b){const c=Array(16).fill(0);for(let j=0;j<4;j++)for(let i=0;i<4;i++)for(let k=0;k<4;k++)c[i+j*4]+=a[i+k*4]*b[k+j*4];return c;}
function translate(x=0,y=0,z=0){let a=identity();a[12]=x;a[13]=y;a[14]=z;return a;}
function scale(x=1,y=1,z=1){let a=identity();a[0]=x;a[5]=y;a[10]=z;return a;}
function rotX(v){let a=identity(),c=Math.cos(v),s=Math.sin(v);a[5]=c;a[9]=-s;a[6]=s;a[10]=c;return a;}
function rotY(v){let a=identity(),c=Math.cos(v),s=Math.sin(v);a[0]=c;a[8]=s;a[2]=-s;a[10]=c;return a;}
function rotZ(v){let a=identity(),c=Math.cos(v),s=Math.sin(v);a[0]=c;a[4]=-s;a[1]=s;a[5]=c;return a;}
function poseM(pos=[0,0,0],angles=[0,0,0],size=[1,1,1]){return mul(mul(mul(mul(translate(...pos),rotY(angles[1])),rotZ(angles[2])),rotX(angles[0])),scale(...size));}
function tr(m,p){let x=p[0],y=p[1],z=p[2];return[m[0]*x+m[4]*y+m[8]*z+m[12],m[1]*x+m[5]*y+m[9]*z+m[13],m[2]*x+m[6]*y+m[10]*z+m[14]];}
function normal(m,p){let n=[m[0]*p[0]+m[4]*p[1]+m[8]*p[2],m[1]*p[0]+m[5]*p[1]+m[9]*p[2],m[2]*p[0]+m[6]*p[1]+m[10]*p[2]],l=Math.hypot(...n)||1;return n.map(x=>x/l);}
function lookAt(e,c,up=[0,1,0]){let z=unit(sub(e,c)),x=unit(cross(up,z)),y=cross(z,x);return[x[0],y[0],z[0],0,x[1],y[1],z[1],0,x[2],y[2],z[2],0,-dot(x,e),-dot(y,e),-dot(z,e),1];}
function perspective(fovy,aspect,near,far){let f=1/Math.tan(fovy/2),nf=1/(near-far);return[f/aspect,0,0,0,0,f,0,0,0,0,(far+near)*nf,-1,0,0,2*far*near*nf,0];}
const sub=(a,b)=>a.map((v,i)=>v-b[i]),cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]],dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0),unit=a=>{let l=Math.hypot(...a)||1;return a.map(v=>v/l)};
class MeshBuilder{
 constructor(){this.data=[];this.matrix=identity();this.stack=[];this.triangles=0;}
 push(m){this.stack.push(this.matrix);this.matrix=mul(this.matrix,m);}
 pop(){this.matrix=this.stack.pop();}
 group(m,fn){this.push(m);try{fn()}finally{this.pop()}}
 tri(a,b,c,col){const n=unit(cross(sub(b,a),sub(c,a)));for(const p of[a,b,c])this.vertex(p,n,col);this.triangles++}
 vertex(p,n,c){let pos=tr(this.matrix,p),nn=normal(this.matrix,n);this.data.push(...pos,...nn,...c)}
 face(a,b,c,d,col){this.tri(a,b,c,col);this.tri(a,c,d,col)}
 box(x,y,z,col){let a=x/2,b=y/2,c=z/2;const p=[[-a,-b,-c],[a,-b,-c],[a,b,-c],[-a,b,-c],[-a,-b,c],[a,-b,c],[a,b,c],[-a,b,c]],f=[[0,3,2,1],[4,5,6,7],[0,4,7,3],[1,2,6,5],[3,7,6,2],[0,1,5,4]];for(let q of f)this.face(...q.map(i=>p[i]),col)}
 cylinder(r0,r1,h,col,steps=10){for(let i=0;i<steps;i++){let a=i*TAU/steps,b=(i+1)*TAU/steps;let p0=[r0*Math.cos(a),0,r0*Math.sin(a)],p1=[r0*Math.cos(b),0,r0*Math.sin(b)],q0=[r1*Math.cos(a),h,r1*Math.sin(a)],q1=[r1*Math.cos(b),h,r1*Math.sin(b)];this.face(p0,p1,q1,q0,col);if(r0>0)this.tri([0,0,0],p1,p0,col);if(r1>0)this.tri([0,h,0],q0,q1,col)}}
 sphere(rx,ry,rz,col,steps=9,rings=6){for(let j=0;j<rings;j++){let v=j*PI/rings,w=(j+1)*PI/rings;for(let i=0;i<steps;i++){let a=i*TAU/steps,b=(i+1)*TAU/steps;function xyz(k,t){return[rx*Math.sin(t)*Math.cos(k),ry*Math.cos(t),rz*Math.sin(t)*Math.sin(k)]}let A=xyz(a,v),B=xyz(b,v),C=xyz(b,w),D=xyz(a,w);this.face(A,B,C,D,col)}}}
 tetra(h,r,col){let a=[0,h,0],b=[-r,0,r],c=[r,0,r],d=[0,0,-r];this.tri(a,b,c,col);this.tri(a,c,d,col);this.tri(a,d,b,col);this.tri(b,d,c,col)}
 ribbon(points,width,color){for(let i=1;i<points.length;i++){let p=points[i-1],q=points[i],w=width*(1-i/(points.length*1.2));this.face([p[0],p[1]-w,p[2]],[q[0],q[1]-w,p[2]],[q[0],q[1]+w,q[2]],[p[0],p[1]+w,p[2]],color)}}
 fromOBJ(vertices,faces,color){for(let f of faces){for(let i=1;i<f.length-1;i++){const a=vertices[f[0]],b=vertices[f[i]],c=vertices[f[i+1]];this.tri(a,b,c,color)}}}
 arr(){return new Float32Array(this.data)}
}
const C={floor:[.12,.18,.24],tile:[.16,.24,.31],tileAlt:[.10,.15,.21],dark:[.09,.11,.2],stone:[.31,.35,.44],mortar:[.09,.11,.19],silver:[.62,.74,.82],steel:[.22,.30,.44],black:[.065,.085,.17],cloth:[.09,.14,.33],hair:[.025,.05,.105],skin:[.91,.66,.55],eye:[.16,.76,.98],white:[.92,.89,.8],gold:[.83,.6,.3],scarlet:[.8,.11,.2],redMetal:[.43,.09,.19],ember:[1,.37,.1],cyan:[.15,.78,1],purple:[.43,.25,.87],torch:[.92,.47,.18]};
function battleAt(t){t=clamp(t,0,16);let phases=[['Вступление',0,2],['Рывок',2,4],['Первый удар',4,5.4],['Блок и искры',5.4,7],['Уклонение',7,9],['Ответный выпад',9,11],['Комбинация',11,13.2],['Финальный удар',13.2,16]];let index=phases.findIndex(p=>t>=p[1]&&t<p[2]);if(index<0)index=7;const [name,start,end]=phases[index],p=smooth((t-start)/(end-start));let ax=-1.55,bx=1.55,az=0,bz=0;const anim={hero:{x:ax,z:az,bend:0,stride:0,attack:0,block:0,hurt:0,turn:-1.1,jump:0},enemy:{x:bx,z:bz,bend:0,stride:0,attack:0,block:0,hurt:0,turn:1.45,jump:0},name,index,t,phase:p,impact:false};
 if(index===1){anim.hero.x=mix(-1.55,-.6,p);anim.hero.stride=Math.sin(t*13)*.6;anim.hero.bend=.25;anim.enemy.x=mix(1.55,1.0,p)}
 if(index===2){anim.hero.x=-.6;anim.enemy.x=1;anim.hero.attack=Math.sin(p*PI);anim.hero.bend=.3;anim.enemy.block=smooth(p*1.5);anim.impact=p>.6&&p<.9}
 if(index===3){anim.hero.x=-.45;anim.enemy.x=.95;anim.enemy.block=1;anim.hero.attack=.6;anim.impact=p<.23}
 if(index===4){anim.hero.x=mix(-.6,-.9,p);anim.hero.z=-.9*Math.sin(p*PI);anim.enemy.x=.95;anim.enemy.attack=.95;anim.enemy.bend=.22;anim.hero.turn=-1.1+.3*Math.sin(PI*p);anim.hero.stride=.4}
 if(index===5){anim.hero.x=-.8;anim.hero.z=-.2;anim.enemy.x=mix(.95,.3,p);anim.enemy.attack=Math.sin(PI*p);anim.hero.block=p<.7?1:.2;anim.hero.hurt=p>.45?.22:0;anim.impact=p>.4&&p<.7}
 if(index===6){anim.hero.x=mix(-.75,.25,p);anim.enemy.x=mix(.8,1.05,p);anim.hero.attack=Math.abs(Math.sin(p*PI*2.5));anim.enemy.block=.5*Math.sin(p*PI);anim.enemy.hurt=p>.5?.35:0;anim.impact=Math.sin(p*PI*5)>.7}
 if(index===7){anim.hero.x=.2;anim.enemy.x=mix(1.05,2.3,p);anim.hero.attack=mix(1,0,p);anim.enemy.hurt=Math.sin(p*PI)*.9;anim.enemy.bend=mix(0,-.8,p);anim.impact=p>.12&&p<.34}
 return anim}
function createEnvironment(m,t){m.group(poseM([0,-.22,0]),()=>{m.box(27,.36,27,C.floor)});
 for(let x=-13;x<14;x++)for(let z=-13;z<14;z++){let c=(x+z)%2?C.tile:C.tileAlt;m.group(poseM([x+.5,-.033,z+.5]),()=>m.box(.98,.018,.98,c));}
 for(let side of[-1,1])for(let i=0;i<6;i++){let x=side*7.4,z=-8+i*3.2;m.group(poseM([x,0,z]),()=>{m.cylinder(.68,.58,.42,C.stone,12);m.group(poseM([0,.43,0]),()=>m.cylinder(.35,.35,4.2,C.stone,10));m.group(poseM([0,4.6,0]),()=>m.box(1.08,.36,1.1,C.silver));m.group(poseM([0,4.85,0]),()=>m.tetra(.6,.65,C.dark));});}
 for(let z of[-10,10]){m.group(poseM([0,4.6,z]),()=>m.box(16,.55,.5,C.stone));m.group(poseM([0,.7,z]),()=>m.box(16,1.35,.5,C.steel))}
 // Torches and 3D flame clusters in courtyard
 for(let x of[-4.8,4.8])for(let z of[-5,4.4])m.group(poseM([x,0,z]),()=>{m.cylinder(.12,.12,1.3,C.steel,7);m.group(poseM([0,1.2,0]),()=>m.tetra(.4,.3,C.ember));m.group(poseM([0,1.5+Math.sin(t*9+x)*.06,0]),()=>m.tetra(.35,.21,C.torch))});
 // Stairs to throne
 for(let k=0;k<5;k++)m.group(poseM([0,k*.22,-11+k*.9]),()=>m.box(6,k*.4+.24,1.0,C.stone));
}
function actor(m,kind,s,t){const hero=kind==='hero',colors=hero?{armor:C.cloth,trim:C.cyan,pants:C.black,skin:C.skin,head:C.hair,metal:C.silver,cloak:C.dark}:{armor:C.redMetal,trim:C.gold,pants:C.steel,skin:C.steel,head:C.scarlet,metal:C.silver,cloak:C.black};const sway=Math.sin(t*3.8+ (hero?0:1.6))*.028,legSwing=s.stride||0,atk=s.attack||0,blk=s.block||0,hurt=s.hurt||0;
 m.group(poseM([s.x,s.jump+sway,s.z],[0,s.turn+(hero?-.25:0)+(s.hurt||0)*.15,0]),()=>{
 // rotating chest and full 3d geometry
 m.group(poseM([0,.98,0],[s.bend||0,0,hero?-.08-hurt*.22:hurt*.34]),()=>{
 // shoulder and chest armor are actual volumes
 m.group(poseM([0,.32,0]),()=>m.cylinder(.26,.42,.65,colors.armor,11));
 m.group(poseM([0,.62,-.01]),()=>m.box(.82,.46,.37,colors.armor));
 for(let side of[-1,1])m.group(poseM([side*.31,.53,-.07],[0,0,side*.08]),()=>m.box(.22,.56,.48,colors.trim));
 m.group(poseM([0,.22,-.24]),()=>m.box(.52,.11,.06,colors.trim));
 m.group(poseM([0,.77,0]),()=>m.cylinder(.15,.14,.14,colors.skin,8));
 // anime-style head with nose and shining eyes on local front (-Z)
 m.group(poseM([0,.98,0]),()=>{m.sphere(.235,.285,.205,colors.skin,12,8);m.group(poseM([0,-.05,-.199]),()=>m.tetra(.065,.045,colors.skin));if(hero){
 m.group(poseM([0,.21,.03]),()=>m.sphere(.25,.15,.24,colors.head,13,6));for(let i=-2;i<=2;i++)m.group(poseM([i*.103,.19,-.16],[Math.sin(i)*.4,0,0]),()=>m.tetra(.24,.087,colors.head));
 }else{m.group(poseM([0,.08,0]),()=>m.cylinder(.27,.19,.32,colors.head,8));for(let a of[-1,1])m.group(poseM([a*.2,.22,0],[0,0,-a*.5]),()=>m.tetra(.48,.09,colors.trim));}
 for(let side of[-1,1]){m.group(poseM([side*.087,.04,-.199]),()=>m.sphere(.061,.034,.026,hero?C.white:C.ember,8,5));m.group(poseM([side*.087,.042,-.219]),()=>m.sphere(.02,.038,.009,hero?C.eye:C.white,7,5));m.group(poseM([side*.085,.092,-.213],[0,0,side*.17]),()=>m.box(.12,.024,.025,colors.head));}m.group(poseM([0,-.16,-.203]),()=>m.box(.085,.011,.014,C.dark));});
 // Cape panels animated naturally but remain rigid polygons (not cloth simulation)
 if(hero)for(let i=-2;i<=2;i++)m.group(poseM([i*.16,.57,.26],[.15+Math.sin(t*4+i*.9)*.15,0,Math.sin(t*2+i)*.07]),()=>{m.box(.16,.87,.07,C.dark);m.group(poseM([0,-.42,0]),()=>m.box(.16,.09,.08,C.purple))});
 else for(let side of[-1,1])m.group(poseM([side*.42,.47,0],[0,0,side*.1]),()=>m.box(.25,.18,.55,colors.trim));
 // arms articulated at shoulders, sword in right hand
 for(let side of[-1,1]){const weapon=side===1;let rz=side*(.21+(weapon?atk*.65:blk*.6));let rx=(weapon?-.25+atk*1.3:-.14-blk*1.0);m.group(poseM([side*.52,.61,0],[rx,0,rz]),()=>{
 m.group(poseM([0,-.22,0]),()=>m.cylinder(.115,.15,.38,colors.armor,8));m.group(poseM([0,-.48,-.015],[weapon?-.36+atk*.65:blk*.7,0,0]),()=>{
 m.cylinder(.11,.12,.31,C.steel,8);m.group(poseM([0,-.28,-.015]),()=>m.sphere(.125,.11,.13,colors.skin,8,5));
 if(weapon){m.group(poseM([0,-.35,-.08],[PI/2-.1-atk*.9,0,0]),()=>{
 m.cylinder(.04,.05,.26,C.black,7);m.group(poseM([0,.22,0]),()=>m.box(.34,.045,.14,colors.trim));m.group(poseM([0,.34,0]),()=>m.box(.095,.46,.085,colors.metal));m.group(poseM([0,.6,0]),()=>m.tetra(.24,.055,C.white));});}
 });});}
 });
 // pelvis legs connected 3D segments
 m.group(poseM([0,1.05,0]),()=>m.box(.58,.29,.39,colors.pants));
 for(let side of[-1,1]){const legrot=(side===1?1:-1)*legSwing*.7;
 m.group(poseM([side*.24,1,0],[legrot,0,side*.05]),()=>{
 m.group(poseM([0,-.25,0]),()=>m.cylinder(.16,.21,.48,colors.pants,9));m.group(poseM([0,-.54,0],[-legrot*.6,0,0]),()=>{
 m.cylinder(.12,.15,.42,C.steel,9);m.group(poseM([0,-.37,-.08]),()=>m.box(.27,.18,.49,colors.armor));});});}
 });
}
function effects(m,anim){let t=anim.t,p=anim.phase;if(anim.impact){m.group(poseM([.22,1.7,0]),()=>{for(let i=0;i<11;i++){let a=i*TAU/11+t,mr=mix(.22,.88,p);m.group(poseM([Math.cos(a)*mr,Math.sin(a)*mr,Math.sin(a*2)*.22],[a,a*.5,a]),()=>m.tetra(.2,.026,i%2?C.ember:C.cyan))}})}
 if([2,3,5,6,7].includes(anim.index)){let a=anim.hero;const pts=[];for(let i=0;i<18;i++){let rad=(i/17)*PI*1.25+t*2.3;pts.push([a.x+.43+Math.cos(rad)*.75,1.7+Math.sin(rad)*.8,a.z-.4+Math.sin(rad)*.2])}m.ribbon(pts,.11,anim.index===6?C.purple:C.cyan)}
 // visible anticipation / dash trails
 if(anim.index===1||anim.index===6)for(let i=0;i<5;i++){let s=anim.hero;m.group(poseM([s.x-.3-i*.3,.5+i*.07,s.z+.3]),()=>m.box(.2,.04,.02,C.cyan))}
}
function validateProject(p){let issues=[];if(!p||typeof p!=='object'||p.schema!=='anime-c4-hybrid-3d-v1')issues.push('Неизвестный формат C4');if(!Array.isArray(p?.shots)||!p.shots.length)issues.push('Нет планов камеры');for(let [i,s] of (p?.shots||[]).entries()){if(!Number.isFinite(s.start)||!Number.isFinite(s.end)||s.start<0||s.end<=s.start||s.end>120)issues.push(`Некорректный интервал плана ${i+1}`);if(!['wide','track','low','close','orbit'].includes(s.camera))issues.push(`Недопустимый тип камеры ${i+1}`);if(i&&s.start<p.shots[i-1].end)issues.push(`Пересекающиеся планы ${i+1}`)}if(!Number.isFinite(p?.duration)||p.duration<1||p.duration>120)issues.push('Неверная продолжительность');if(typeof p?.title!=='string'||p.title.trim().length===0)issues.push('Не указано название');return issues;}
function defaultProject(){return{schema:'anime-c4-hybrid-3d-v1',version:'C4',title:'Пепельный дозор — гибридная 3D-сцена',duration:16,fps:12,quality:'eco',shots:[{start:0,end:2,camera:'wide',label:'Вступление'},{start:2,end:4,camera:'track',label:'Рывок'},{start:4,end:5.4,camera:'low',label:'Удар'},{start:5.4,end:7,camera:'close',label:'Блок'},{start:7,end:9,camera:'orbit',label:'Уклонение'},{start:9,end:11,camera:'low',label:'Контратака'},{start:11,end:13.2,camera:'track',label:'Комбинация'},{start:13.2,end:16,camera:'wide',label:'Финал'}],subtitles:[{start:0.5,end:2,text:'Никто не отступит.'},{start:4.2,end:5.8,text:'Держи удар!'},{start:8.2,end:9.5,text:'Слишком медленно.'},{start:13.4,end:15.2,text:'На этом всё.'}],characters:[{id:'hero',name:'Аран',color:'#233d65'},{id:'enemy',name:'Страж',color:'#a52b39'}],settings:{cameraYaw:0,cameraDistance:1},legacy:null};}
function adaptC3(data){if(!data||typeof data!=='object')throw Error('Пустой/неверный JSON');let p=defaultProject();if(data.schema==='anime-c4-hybrid-3d-v1'){let problems=validateProject(data);if(problems.length)throw Error(problems.join('; '));return structuredClone(data)}
 // legacy C1/C2/C3 are preserved as payload, only known metadata is migrated
 if(!Array.isArray(data.beats)||!Array.isArray(data.shots))throw Error('Требуется JSON проекта C1–C3 с beats и shots');p.legacy=structuredClone(data);p.title=(typeof data.title==='string'&&data.title.trim()?data.title:p.title);return p;}
function parseOBJ(src){if(typeof src!=='string'||src.length>2e6)throw Error('OBJ слишком большой (ограничение: 2 МБ)');let v=[],f=[];for(const ln of src.split(/\r?\n/)){let a=ln.trim().split(/\s+/);if(a[0]==='v'&&a.length>=4){let p=a.slice(1,4).map(Number);if(p.every(Number.isFinite))v.push(p)}if(a[0]==='f'&&a.length>=4){let face=a.slice(1).map(k=>Number(k.split('/')[0]));if(face.every(k=>Number.isInteger(k)&&k>0&&k<=v.length))f.push(face.map(k=>k-1))}if(v.length>14000||f.length>14000)throw Error('OBJ: слишком много граней или вершин для слабого ПК');}if(!v.length||!f.length)throw Error('OBJ должен содержать вершины v и грани f');let mn=[Infinity,Infinity,Infinity],mx=[-Infinity,-Infinity,-Infinity];for(let q of v)for(let j=0;j<3;j++){mn[j]=Math.min(mn[j],q[j]);mx[j]=Math.max(mx[j],q[j])}let cent=mn.map((a,j)=>(a+mx[j])/2),size=Math.max(...mn.map((a,j)=>mx[j]-a),.001);return{v:v.map(q=>q.map((a,j)=>(a-cent[j])*3/size +(j===1?1.5:0))),f};}
function cameraFor(project,t,aspect){let shot=project.shots.find(s=>t>=s.start&&t<s.end)||project.shots.at(-1),p=smooth((t-shot.start)/(shot.end-shot.start)),b=battleAt(t),x=(b.hero.x+b.enemy.x)/2,follow=x;let type=shot.camera,offset=[0,3.25,8.8],target=[follow,1.35,0],y=project.settings.cameraYaw||0,d=project.settings.cameraDistance||1;
 if(type==='track'){offset=[-3.2,2.5,7];target=[follow,1.55,0]}if(type==='close'){offset=[1.3,2.1,4.0];target=[follow,1.75,0]}if(type==='low'){offset=[2.0,1.2,6.6];target=[follow,1.8,0]}if(type==='orbit'){offset=[Math.sin(p*PI)*5,3.1,Math.cos(p*PI)*7];target=[follow,1.55,0]}if(type==='wide'){offset=[0,3.45,9.0];target=[follow,1.5,-.1]}
 let rotated=[Math.sin(y)*offset[2]+Math.cos(y)*offset[0],offset[1],Math.cos(y)*offset[2]-Math.sin(y)*offset[0]];let pos=[target[0]+rotated[0]*d,target[1]+rotated[1]*d,target[2]+rotated[2]*d];return{eye:pos,target,projection:perspective(50*PI/180,aspect,.075,85),view:lookAt(pos,target),shot};}
function secondsToSRT(t){const ms=Math.max(0,Math.round(t*1000)),h=Math.floor(ms/3600000),m=Math.floor(ms/60000)%60,s=Math.floor(ms/1000)%60,mm=ms%1000;return`${('0'+h).slice(-2)}:${('0'+m).slice(-2)}:${('0'+s).slice(-2)},${('00'+mm).slice(-3)}`}
function exportSRT(subtitles){return subtitles.map((s,i)=>`${i+1}\n${secondsToSRT(s.start)} --> ${secondsToSRT(s.end)}\n${s.text}`).join('\n\n')+'\n'}
root.C4Core={PI,clamp,mix,smooth,identity,mul,translate,scale,rotX,rotY,rotZ,poseM,tr,normal,lookAt,perspective,MeshBuilder,C,battleAt,createEnvironment,actor,effects,defaultProject,validateProject,adaptC3,parseOBJ,cameraFor,exportSRT};
})(typeof window!=='undefined'?window:globalThis);
if(typeof module!=='undefined')module.exports=globalThis.C4Core;
