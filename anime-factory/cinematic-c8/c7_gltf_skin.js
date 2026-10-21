/* CINEMATIC C7: self-contained glTF 2.0 GLB skinning for portable offline WebGL1/Canvas.
 * Supports embedded BIN mesh, up to 60 joints, JOINTS_0/WEIGHTS_0, keyframed TRS, skin inverse-bind matrices.
 * Does not silently pretend OBJ or unrigged meshes are animated: absent skin = explicit error.
 * Mesh uses CPU vertex-skinning so the existing renderer and its CPU fallback share the same pose.
 */
(function(root){'use strict';
const C=root.C4Core,clamp=C.clamp,MAX=4*1024*1024;
const cache=new Map(), identities=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1];
function mul(a,b){return C.mul(a,b)}
function decode(base64){if(typeof base64!=='string'||base64.length>MAX*1.37+64||!(/^[A-Za-z0-9+/]*={0,2}$/).test(base64))throw Error('GLB превышает 4 МБ или base64 повреждён');let s=atob(base64),b=new Uint8Array(s.length);for(let i=0;i<s.length;i++)b[i]=s.charCodeAt(i);return b}
function parseBytes(bytes){if(!(bytes instanceof Uint8Array)||bytes.byteLength>MAX||bytes.byteLength<32)throw Error('GLB: размер 32 байта — 4 МБ');let dv=new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength);
 const read32=o=>dv.getUint32(o,true);if(read32(0)!==0x46546c67||read32(4)!==2||read32(8)!==bytes.length)throw Error('GLB должен соответствовать glTF 2.0');let offset=12,doc=null,bin=null;
 while(offset+8<=bytes.length){let l=read32(offset),type=read32(offset+4);offset+=8;if(l>bytes.length-offset)throw Error('GLB: повреждена длина chunk');if(type===0x4e4f534a){doc=JSON.parse(new TextDecoder().decode(bytes.slice(offset,offset+l)).trim());}else if(type===0x004e4942)bin=bytes.slice(offset,offset+l);offset+=l}
 if(offset!==bytes.length||!doc||!bin||doc.asset?.version!=='2.0')throw Error('GLB: отсутствует JSON/BIN или версия 2.0');
 if(doc.extensionsRequired?.length)throw Error('GLB: пока не поддерживаются обязательные расширения '+doc.extensionsRequired.join(','));
 if(!doc.skins?.length||!doc.skins[0]?.joints?.length)throw Error('GLB: нет skin/joints. Экспортируйте модель с арматурой и весами из Blender');
 if(doc.skins[0].joints.length>60)throw Error('GLB: максимум 60 костей для экономичного CPU-рендера');
 if(!doc.meshes?.length)throw Error('GLB: нет mesh');
 const nodeMesh=(doc.nodes||[]).findIndex(n=>n.mesh===0&&n.skin===0);if(nodeMesh<0)throw Error('GLB: ожидается skinned mesh node, связанный с первым skin');
 if(doc.nodes[nodeMesh].translation||doc.nodes[nodeMesh].rotation||doc.nodes[nodeMesh].scale||doc.nodes[nodeMesh].matrix)throw Error('GLB: примените трансформации объекта mesh в Blender (Ctrl+A) до экспорта');
 function accessor(idx){let a=doc.accessors?.[idx];if(!a||a.sparse)throw Error('GLB: отсутствующий или sparse accessor');let v=doc.bufferViews?.[a.bufferView];if(!v||v.buffer!==0)throw Error('GLB: нужны встроенные BIN bufferViews');let arity={SCALAR:1,VEC2:2,VEC3:3,VEC4:4,MAT4:16}[a.type];let format={5126:[4,'getFloat32'],5125:[4,'getUint32'],5123:[2,'getUint16'],5122:[2,'getInt16'],5121:[1,'getUint8'],5120:[1,'getInt8']}[a.componentType];if(!arity||!format||a.count>50000||a.count<1)throw Error('GLB: недопустимый accessor / лимит 50k');let [size,get]=format,stride=v.byteStride||arity*size;let base=(v.byteOffset||0)+(a.byteOffset||0);if(stride<arity*size||base<0||base+stride*(a.count-1)+arity*size>bin.length)throw Error('GLB: accessor вне диапазона');let view=new DataView(bin.buffer,bin.byteOffset,bin.byteLength),out=new Array(a.count*arity);
 for(let i=0;i<a.count;i++)for(let j=0;j<arity;j++){let q=view[get](base+i*stride+j*size,true);if(a.normalized&&a.componentType!==5126){q=a.componentType===5121?q/255:a.componentType===5123?q/65535:a.componentType===5120?Math.max(-1,q/127):Math.max(-1,q/32767)}out[i*arity+j]=q}return{values:out,count:a.count,arity}}
 const inverse=doc.skins[0].inverseBindMatrices!=null?accessor(doc.skins[0].inverseBindMatrices).values:null;
 if(inverse&&inverse.length!==doc.skins[0].joints.length*16)throw Error('GLB: inverse bind matrices не совпадают с костями');
 const primitives=[];let total=0;
 for(let p of doc.meshes[0].primitives||[]){if(p.mode!==undefined&&p.mode!==4)throw Error('GLB: поддерживается только TRIANGLES');let attrs=p.attributes||{};
 if(attrs.POSITION==null||attrs.JOINTS_0==null||attrs.WEIGHTS_0==null)throw Error('GLB: нужны POSITION, JOINTS_0, WEIGHTS_0');let pos=accessor(attrs.POSITION),joint=accessor(attrs.JOINTS_0),weight=accessor(attrs.WEIGHTS_0),ind=p.indices!=null?accessor(p.indices).values:Array.from({length:pos.count},(_,i)=>i);
 if(pos.count!==joint.count||pos.count!==weight.count||pos.arity!==3||joint.arity!==4||weight.arity!==4||ind.length%3!==0||ind.length>180000)throw Error('GLB: атрибуты skin или треугольники повреждены');
 for(let i=0;i<joint.values.length;i++){if(!Number.isInteger(joint.values[i])||joint.values[i]<0||joint.values[i]>=doc.skins[0].joints.length)throw Error('GLB: JOINTS_0 ссылается за пределы skeleton')}
 for(let x of ind)if(!Number.isInteger(x)||x<0||x>=pos.count)throw Error('GLB: индекс грани вне диапазона');
 let mat=doc.materials?.[p.material??-1]?.pbrMetallicRoughness?.baseColorFactor||[.75,.76,.8,1];
 const targets=(p.targets||[]).map(target=>{let a=target.POSITION!=null?accessor(target.POSITION):null;if(a&&(a.count!==pos.count||a.arity!==3))throw Error('GLB: некорректный morph POSITION');return a?a.values:new Array(pos.values.length).fill(0)});
 if(targets.length>8)throw Error('GLB: экономичный лимит 8 morph targets');
 primitives.push({pos:pos.values,joints:joint.values,weights:weight.values,indices:ind,color:mat.slice(0,3),targets});total+=ind.length/3}
 if(total>35000)throw Error('GLB: максимум 35 000 треугольников');
 let tracks=[];for(let animation of (doc.animations||[]).slice(0,1)){for(const ch of animation.channels||[]){let target=ch.target||{};if(!['rotation','translation','scale'].includes(target.path))continue;let s=animation.samplers?.[ch.sampler];if(!s||!['LINEAR','STEP',undefined].includes(s.interpolation))throw Error('GLB: поддерживается LINEAR/STEP, не CUBICSPLINE');const times=accessor(s.input).values,values=accessor(s.output).values;let size=target.path==='rotation'?4:3;
 if(times.some((q,i)=>!Number.isFinite(q)||(i&&q<=times[i-1]))||values.length!==times.length*size)throw Error('GLB: анимационные ключи повреждены');tracks.push({node:target.node,path:target.path,times,values,size,step:s.interpolation==='STEP'});}}
 let model={doc,primitives,inverse,tracks,joints:doc.skins[0].joints,total,format:'glTF 2.0 GLB skin + morph',name:doc.nodes[nodeMesh]?.name||'Rigged character',morphNames:doc.meshes[0].extras?.targetNames||[],morphCount:Math.max(...primitives.map(p=>p.targets.length),0)};return model}
function parse64(encoded){let p=cache.get(encoded);if(p)return p;p=parseBytes(decode(encoded));if(cache.size>=4)cache.delete(cache.keys().next().value);cache.set(encoded,p);return p}
function quatMatrix(q){let [x,y,z,w]=q,s=2;return[1-s*(y*y+z*z),s*(x*y+z*w),s*(x*z-y*w),0,s*(x*y-z*w),1-s*(x*x+z*z),s*(y*z+x*w),0,s*(x*z+y*w),s*(y*z-x*w),1-s*(x*x+y*y),0,0,0,0,1]}
function transform(t=[0,0,0],q=[0,0,0,1],s=[1,1,1]){return mul(mul(C.translate(...t),quatMatrix(q)),C.scale(...s))}
function slerp(a,b,u){let dot=a.reduce((n,v,i)=>n+v*b[i],0);if(dot<0){b=b.map(v=>-v);dot=-dot}if(dot>.9995){let q=a.map((v,i)=>v+(b[i]-v)*u),l=Math.hypot(...q)||1;return q.map(v=>v/l)}let th=Math.acos(clamp(dot,-1,1)),h=Math.sin(th);return a.map((v,i)=>Math.sin((1-u)*th)/h*v+Math.sin(u*th)/h*b[i])}
function frame(model,t){let nodes=model.doc.nodes||[],duration=Math.max(.001,...model.tracks.map(a=>a.times.at(-1))),local=nodes.map(n=>({translation:n.translation||[0,0,0],rotation:n.rotation||[0,0,0,1],scale:n.scale||[1,1,1],matrix:n.matrix||null}));let tt=((t%duration)+duration)%duration;
 for(let a of model.tracks){let i=0;while(i+1<a.times.length&&a.times[i+1]<tt)i++;let j=Math.min(i+1,a.times.length-1),dt=a.times[j]-a.times[i],u=(j===i||a.step)?0:clamp((tt-a.times[i])/dt,0,1);let va=a.values.slice(i*a.size,(i+1)*a.size),vb=a.values.slice(j*a.size,(j+1)*a.size);let vv=a.path==='rotation'?slerp(va,vb,u):va.map((v,k)=>v+(vb[k]-v)*u);if(local[a.node])local[a.node][a.path]=vv}
 let parents=nodes.map(()=>-1);nodes.forEach((n,i)=>(n.children||[]).forEach(j=>{parents[j]=i}));let memo=[];
 function world(i,depth=0){if(memo[i])return memo[i];if(depth>64||!local[i])throw Error('GLB: цикл / неверный node');let n=local[i],m=n.matrix||transform(n.translation,n.rotation,n.scale);return memo[i]=parents[i]<0?m:mul(world(parents[i],depth+1),m)}
 return model.joints.map((j,i)=>mul(world(j),model.inverse?model.inverse.slice(i*16,(i+1)*16):identities))}
function skin(model,seconds,faceWeights){let joints=frame(model,seconds),results=[];
 const weights=faceWeights||model.doc.meshes[0].weights||[];
 for(let primitive of model.primitives){let verts=[],ps=primitive.pos;
 for(let v=0;v<ps.length/3;v++){let x=ps[v*3],y=ps[v*3+1],z=ps[v*3+2],px=0,py=0,pz=0,total=0;
 // glTF 2.0: all morph target deltas are added in mesh space BEFORE skeletal skinning.
 for(let ti=0;ti<primitive.targets.length;ti++){let delta=primitive.targets[ti],w=Number(weights[ti])||0;if(w){w=clamp(w,0,1);x+=delta[v*3]*w;y+=delta[v*3+1]*w;z+=delta[v*3+2]*w}}
 for(let k=0;k<4;k++){let w=primitive.weights[v*4+k];if(w<1e-6)continue;let m=joints[primitive.joints[v*4+k]];if(!m)throw Error('GLB: отсутствует кость');px+=(m[0]*x+m[4]*y+m[8]*z+m[12])*w;py+=(m[1]*x+m[5]*y+m[9]*z+m[13])*w;pz+=(m[2]*x+m[6]*y+m[10]*z+m[14])*w;total+=w}
 if(total<.0001){px=x;py=y;pz=z}else{px/=total;py/=total;pz/=total}verts.push([px,py,pz]);}
 results.push({...primitive,verts})}return results}
function emit(b,encoded,body,time,tint,role){const model=parse64(encoded),project=root.__C4_TEST__?.project,
 face=(root.C8Face&&root.C8Face.weights(project,time-(role==='enemy'?.23:0),role,model))||null,mesh=skin(model,time,face),s=tint||[1,1,1];b.group(C.poseM([body.x,body.jump||0,body.z],[0,body.turn||0,0]),()=>{
 for(let primitive of mesh){let col=primitive.color.map((v,i)=>clamp(v*s[i],0,1));for(let ids=primitive.indices,i=0;i<ids.length;i+=3){
 let a=primitive.verts[ids[i]],d=primitive.verts[ids[i+1]],c=primitive.verts[ids[i+2]];
 // Lightweight spatial material detail on every triangle; no claim of UV/PBR texture support.
 let k=1;if(root.C8Face?.materialMode(project)!=='flat'){
  let cx=(a[0]+d[0]+c[0])/3,cy=(a[1]+d[1]+c[1])/3,cz=(a[2]+d[2]+c[2])/3;
  let z=Math.sin(cx*79+cy*43+cz*73)*Math.sin(cx*19-cy*37+cz*31);
  k=1+z*.105;
 }
 b.tri(a,d,c,col.map(v=>clamp(v*k,0,1)))}}});return model}
const previousWebGL=root.C4WebGL?.ThreeDimensionalRenderer?.prototype?.model,previousCPU=root.C4Fallback?.Software3DRenderer?.prototype?.model;
function intercept(original){return function(b,role,pos,t,imports){const project=root.__C4_TEST__?.project;const preset=root.C7EmbeddedModels?.[role];const custom=project?.c7Rig?.[role];let enabled=project?.c7Rig?.enabled!==false;const selected=custom?.base64||preset;
 if(enabled&&selected){try{emit(b,selected,pos,t+(role==='enemy'?.23:0),role==='enemy'?[1,.98,1]:[1,1,1],role);return}catch(err){if(!root.C7Rig.lastError)root.C7Rig.lastError=String(err.message||err);}}
 return original.call(this,b,role,pos,t,imports)}}
if(previousWebGL)root.C4WebGL.ThreeDimensionalRenderer.prototype.model=intercept(previousWebGL);
if(previousCPU)root.C4Fallback.Software3DRenderer.prototype.model=intercept(previousCPU);
root.C7Rig={decode,parseBytes,parse64,frame,skin,emit,cache,lastError:null};
})(typeof window!=='undefined'?window:globalThis);
