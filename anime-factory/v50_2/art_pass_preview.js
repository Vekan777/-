/* V50.2 ART PASS: OPTIONAL original AI-generated illustration cuts.
 * Art data is supplied by a self-contained Windows pilot HTML and is NOT
 * present in the source checkout. No art/copyright/episode sign-off implied.
 * Use as an experimental storyboard layer; the full V19–V50.2 stays intact.
 */
(function(){
  const sources=window.v502IllustrationData||{},images={};
  let ready=0;
  for(const [key,url] of Object.entries(sources)){
    const image=new Image();images[key]=image;
    image.onload=()=>ready++;
    image.onerror=()=>{images[key]=null;};
    image.src=url;
  }
  const plan={
    0:{hero:'akira',partner:'saira',over:'world'},
    1:{hero:'akira',partner:'ren_worried',over:'ren'},
    2:{hero:'akira_screaming',partner:'guardian',impact:'battle',aftermath:'akira_power'},
    3:{hero:'akira',partner:'miyu_worried',over:'miyu'},
    4:{hero:'akira_power',partner:'ren_worried',detail:'ren',over:'ren_worried'},
    5:{hero:'akira',partner:'miyu',over:'portal'}
  };
  const previous=v501SceneDraw;
  v501SceneDraw=function(ctx,episode,scene,sec){
    previous(ctx,episode,scene,sec);
    if(!P?.v502Director?.enabled||!P?.v502Art?.enabled||
        episode>1||!scene?.pilotV50)return;
    const index=P.episodes[episode].scenes.indexOf(scene);
    const phase=Math.max(0,Math.min(.99999,sec/Math.max(.1,scene.duration)));
    const shot=window.v502Director.active(episode,index,sec);
    const key=plan[index]?.[shot],img=images[key];
    if(!img?.complete||!img?.naturalWidth)return;
    const segment=window.v502Director.shotPlan(scene.kind).find(s=>
      s.kind===shot&&phase>=s.from&&phase<s.to);
    if(!segment)return;
    const strength=Math.max(0,Math.min((phase-segment.from)*10,
                                     (segment.to-phase)*10,1));
    if(!strength)return;
    ctx.save();ctx.globalAlpha=.96*strength;
    const W=960,H=540;
    function cover(){
      const scale=Math.max(W/img.width,H/img.height)*(1.04+.065*phase);
      const dw=img.width*scale,dh=img.height*scale;
      ctx.drawImage(img,(W-dw)/2+Math.sin(phase*2.3)*(dw-W)*.16,
                      (H-dh)/2-dh*.025,dw,dh);
    }
    if(['world','portal','battle'].includes(key))cover();
    else{
      ctx.save();ctx.filter='blur(22px) brightness(.55) saturate(1.25)';
      cover();ctx.restore();
      const scale=Math.max(W*.68/img.width,H*.92/img.height)*(1+.055*phase);
      const dw=img.width*scale,dh=img.height*scale;
      const hero=shot==='hero';
      const x=hero?W*.18-dw*.14:W*.77-dw*.52;
      ctx.save();ctx.shadowBlur=34;
      ctx.shadowColor=hero?'#63c1ff8f':'#ffc3dba6';
      ctx.drawImage(img,x,H-dh+15+Math.sin(sec*.5)*4,dw,dh);
      ctx.restore();
      const fade=ctx.createLinearGradient(0,H*.58,0,H);
      fade.addColorStop(0,'#030c2000');fade.addColorStop(1,'#050a1c88');
      ctx.fillStyle=fade;ctx.fillRect(0,0,W,H);
    }
    ctx.restore();
  };
  const holder=document.getElementById('v502-panel');
  const wrapper=document.createElement('label');
  wrapper.style.cssText='display:flex;align-items:center;gap:9px;margin:12px 0;padding:10px;border:1px solid #567494;border-radius:8px;';
  wrapper.innerHTML='<input type="checkbox" id="v502-art-enabled" style="width:auto">Экспериментальные иллюстрированные планы V50.2';
  if(holder)holder.appendChild(wrapper);
  const toggle=document.getElementById('v502-art-enabled');
  if(toggle)toggle.onchange=()=>{
    P.v502Art={...(P.v502Art||{}),enabled:toggle.checked,
      artReviewApproved:false,status:'EXPERIMENTAL_STORYBOARD_NOT_FINAL'};
    save();if(typeof v48Draw==='function')v48Draw();
  };
  const show=v502Settings;
  v502Settings=function(){show();if(toggle&&P)toggle.checked=!!P.v502Art?.enabled;};
  window.v502ArtPass=Object.freeze({
    status:()=>({count:Object.keys(sources).length,loaded:ready}),
    artKeys:Object.keys(sources),originalUnmodified:true,
    humanApprovalRequired:true,
    frame:(episode,time,width=640)=>{
      const ep=P?.episodes?.[episode];if(!ep)throw Error('No episode');
      const c=document.createElement('canvas');c.width=width;c.height=width*9/16;
      v35Frame(c,ep,time);
      if(typeof v37Paint==='function')v37Paint(c,ep,time);
      return c.toDataURL('image/jpeg',.84);
    }
  });
})();
