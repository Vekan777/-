/* True 3D vertices rendered on 2D Canvas using CPU projection and depth sorting.
   Works without GPU/WebGL; color cel-shading approximate. Used when GPU path is denied. */
(function(root){'use strict';const C=root.C4Core;
class Software3DRenderer{
 constructor(canvas){this.canvas=canvas;this.ctx=canvas.getContext('2d');if(!this.ctx)throw Error('Нет ни WebGL, ни 2D Canvas');let e=new C.MeshBuilder();C.createEnvironment(e,0);this.static=e.arr();this.sceneTriangles=e.triangles;this.lastStats={};this.kind='software';}
 size(w,h){this.canvas.width=w;this.canvas.height=h}
 model(b,key,pos,t,imports){let imp=imports?.[key];if(imp){b.group(C.poseM([pos.x,0,pos.z],[0,pos.turn,0]),()=>b.fromOBJ(imp.v,imp.f,key==='hero'?[.19,.46,.85]:[.86,.22,.3]))}else C.actor(b,key,pos,t)}
 render(project,t,imports){let dyn=new C.MeshBuilder(),a=C.battleAt(t);this.model(dyn,'hero',a.hero,t,imports);this.model(dyn,'enemy',a.enemy,t,imports);C.effects(dyn,a);let cam=C.cameraFor(project,t,this.canvas.width/this.canvas.height);let vp=C.mul(cam.projection,cam.view),ctx=this.ctx,W=this.canvas.width,H=this.canvas.height;
 ctx.fillStyle='#090f1d';ctx.fillRect(0,0,W,H);
 const polygons=[];for(let arr of [this.static,dyn.arr()])for(let i=0;i<arr.length;i+=27){let pts=[],depth=0,ok=true,n=[arr[i+3],arr[i+4],arr[i+5]],color=[arr[i+6],arr[i+7],arr[i+8]];for(let j=0;j<3;j++){const off=i+j*9,x=arr[off],y=arr[off+1],z=arr[off+2];let w=vp[3]*x+vp[7]*y+vp[11]*z+vp[15];if(w<.06){ok=false;break}let px=(vp[0]*x+vp[4]*y+vp[8]*z+vp[12])/w,py=(vp[1]*x+vp[5]*y+vp[9]*z+vp[13])/w,pz=(vp[2]*x+vp[6]*y+vp[10]*z+vp[14])/w;pts.push([(px+1)*W/2,(1-py)*H/2]);depth+=pz;if(Math.abs(px)>4||Math.abs(py)>4){ok=false;break}}
 if(!ok)continue;let area=(pts[1][0]-pts[0][0])*(pts[2][1]-pts[0][1])-(pts[1][1]-pts[0][1])*(pts[2][0]-pts[0][0]);if(Math.abs(area)<.05)continue;
 let bright=Math.max(0,n[0]*-.46+n[1]*.64+n[2]*.59);let band=bright>.75?1.08:bright>.4?.89:bright>.13?.7:.55;let fog=Math.max(0,Math.min(.58,(depth-1)/1.9));let rgb=color.map((v,i)=>Math.max(0,Math.min(255,Math.round(255*(v*band*(1-fog)+[.09,.10,.17][i]*fog)))));polygons.push({pts,z:depth/3,color:`rgb(${rgb.join(',')})`})}
 polygons.sort((a,b)=>b.z-a.z);for(const p of polygons){ctx.beginPath();ctx.moveTo(...p.pts[0]);ctx.lineTo(...p.pts[1]);ctx.lineTo(...p.pts[2]);ctx.closePath();ctx.fillStyle=p.color;ctx.fill()}
 // Vignette gives concept blocking atmosphere (not a substitute for original backgrounds).
 const shade=ctx.createLinearGradient(0,0,0,H);shade.addColorStop(0,'rgba(1,3,12,.18)');shade.addColorStop(.6,'rgba(1,3,12,0)');shade.addColorStop(1,'rgba(0,0,10,.45)');ctx.fillStyle=shade;ctx.fillRect(0,0,W,H);
 return this.lastStats={triangles:this.sceneTriangles+dyn.triangles,mode:'Software 3D (CPU perspective)',camera:cam.shot.camera,event:a.name,time:t,collision:a.impact,objects:imports?Object.keys(imports).length:0}
 }
}
root.C4Fallback={Software3DRenderer};
})(typeof window!=='undefined'?window:globalThis);
