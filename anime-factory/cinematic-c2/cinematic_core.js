/* AI Anime Factory Cinematic C1 — original combat previsualization, MIT license.
   No third-party anime imagery, dialogue, or protected characters included. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.CinematicCore = factory();
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const smooth = x => { const t = clamp(x, 0, 1); return t*t*(3-2*t); };
  const keys = (arr, t) => {
    if (!Array.isArray(arr) || !arr.length) throw new Error('Нет ключевых кадров');
    if (t <= arr[0].t) return Object.assign({}, arr[0]);
    for (let i = 0; i < arr.length - 1; ++i) {
      const a = arr[i], b = arr[i+1];
      if (t <= b.t) {
        let q = clamp((t-a.t)/(b.t-a.t),0,1);
        q = b.ease === 'linear' ? q : b.ease === 'snap' ? +(q >= 1) : smooth(q);
        const out = Object.assign({}, q < .5 ? a : b);
        ['x','y','rotation','scale'].forEach(prop => {
          if (Number.isFinite(a[prop]) && Number.isFinite(b[prop])) out[prop] = a[prop] + (b[prop]-a[prop])*q;
        });
        out.t = t;
        return out;
      }
    }
    return Object.assign({}, arr[arr.length-1]);
  };
  function makeDemo() {
    return {
      schema: 'ai-anime-cinematic-c1', title: 'ПЕПЕЛЬНЫЙ ДОЗОР — оригинальная боевая сцена', fps: 24, duration: 14,
      description: 'Оригинальная постановочная демонстрация: угроза → атака → защита → контратака → последствия.',
      actors: [{id:'nova',name:'Нова',color:'#79d9f9',w:205,h:440},{id:'warden',name:'Страж',color:'#df9bff',w:252,h:465}],
      tracks: {
        nova: [
          {t:0,x:.30,y:0,pose:'idle',facing:1},{t:2.70,x:.30,y:0,pose:'ready',facing:1},
          {t:3.50,x:.30,y:0,pose:'block',facing:1},{t:3.85,x:.27,y:0,pose:'block',facing:1,ease:'linear'},
          {t:4.35,x:.23,y:0,pose:'dodge',facing:1,ease:'linear'}, {t:4.95,x:.29,y:0,pose:'ready',facing:1},
          {t:5.60,x:.46,y:-.02,pose:'dash',facing:1,ease:'linear'}, {t:5.90,x:.52,y:0,pose:'slash',facing:1,ease:'linear'},
          {t:6.45,x:.49,y:0,pose:'recover',facing:1}, {t:7.70,x:.42,y:0,pose:'ready',facing:1},
          {t:9.20,x:.40,y:0,pose:'ready',facing:1},{t:9.85,x:.46,y:-.015,pose:'slash',facing:1,ease:'linear'},
          {t:10.65,x:.42,y:0,pose:'recover',facing:1},{t:11.6,x:.36,y:0,pose:'ready',facing:1},
          {t:14,x:.36,y:0,pose:'idle',facing:1}
        ],
        warden: [
          {t:0,x:.72,y:0,pose:'idle',facing:-1},{t:2.65,x:.71,y:0,pose:'windup',facing:-1},
          {t:3.35,x:.52,y:0,pose:'dash',facing:-1,ease:'linear'},{t:3.75,x:.43,y:0,pose:'slash',facing:-1,ease:'linear'},
          {t:4.20,x:.44,y:0,pose:'recover',facing:-1},{t:5.45,x:.69,y:0,pose:'ready',facing:-1},
          {t:5.90,x:.68,y:0,pose:'hit',facing:-1},{t:6.45,x:.75,y:0,pose:'hit',facing:-1,ease:'linear'},
          {t:7.35,x:.79,y:0,pose:'recover',facing:-1},{t:8.10,x:.72,y:0,pose:'windup',facing:-1},
          {t:9.35,x:.58,y:0,pose:'dash',facing:-1,ease:'linear'}, {t:9.85,x:.55,y:0,pose:'slash',facing:-1},
          {t:10.35,x:.59,y:0,pose:'hit',facing:-1},{t:11.5,x:.73,y:0,pose:'recover',facing:-1},
          {t:14,x:.73,y:0,pose:'idle',facing:-1}
        ]
      },
      shots: [
        {start:0,end:1.4,kind:'establishing',zoom:1,cx:.50,cy:.52,axis:1},
        {start:1.4,end:2.7,kind:'medium-dialogue',zoom:1.29,cx:.36,cy:.48,axis:1},
        {start:2.7,end:4.25,kind:'enemy-attack',zoom:1.10,cx:.50,cy:.53,axis:1},
        {start:4.25,end:5.35,kind:'breath-after-dodge',zoom:1.30,cx:.34,cy:.49,axis:1},
        {start:5.35,end:6.65,kind:'counterattack',zoom:1.22,cx:.55,cy:.50,axis:1},
        {start:6.65,end:8.1,kind:'reaction',zoom:1.24,cx:.66,cy:.48,axis:1},
        {start:8.1,end:9.55,kind:'threat',zoom:1.12,cx:.55,cy:.52,axis:1},
        {start:9.55,end:10.55,kind:'clash',zoom:1.43,cx:.51,cy:.48,axis:1},
        {start:10.55,end:12.05,kind:'aftermath',zoom:1.1,cx:.53,cy:.54,axis:1},
        {start:12.05,end:14,kind:'resolution',zoom:1.18,cx:.39,cy:.48,axis:1}
      ],
      beats: [
        {id:'b01',t:0.15,action:'standoff',actor:'nova',target:'warden',intent:'Показать конфликт и расстояние'},
        {id:'b02',t:1.6,action:'dialogue',actor:'nova',text:'Назад. Это место закрыто.',intent:'Ставка до атаки'},
        {id:'b03',t:2.74,action:'telegraph',actor:'warden',target:'nova',intent:'Заметная подготовка удара'},
        {id:'b04',t:3.75,action:'block',actor:'warden',target:'nova',reach:.20,contact:'blocked',intent:'Удар в пределах дистанции, защита поставлена'},
        {id:'b05',t:4.30,action:'dodge',actor:'nova',target:'warden',intent:'Переход на выгодную дистанцию'},
        {id:'b06',t:5.90,action:'slash',actor:'nova',target:'warden',reach:.21,contact:'hit',reaction:'warden',intent:'Ответ после уклонения'},
        {id:'b07',t:6.55,action:'recoil',actor:'warden',target:'nova',intent:'Враг вынужденно отходит'},
        {id:'b08',t:7.3,action:'dialogue',actor:'warden',text:'Я не отступлю!',intent:'Угроза повышается'},
        {id:'b09',t:8.15,action:'telegraph',actor:'warden',target:'nova',intent:'Враг собирает силы'},
        {id:'b10',t:9.85,action:'clash',actor:'nova',target:'warden',reach:.17,contact:'blocked',intent:'Оружие встречается с оружием'},
        {id:'b11',t:10.28,action:'recoil',actor:'warden',target:'nova',intent:'Читаемое последствие'},
        {id:'b12',t:12.1,action:'dialogue',actor:'nova',text:'Тогда придётся закончить бой.',intent:'Эмоциональная развязка'}
      ],
      media: {images:{background:null,foreground:null,nova:null,warden:null},audio:{nova:null,warden:null}},
      rights: {originalStory:true,importedAssetsVerified:false}
    };
  }
  function shotAt(p,t){ return p.shots.find(s=>t>=s.start && t<s.end) || p.shots[p.shots.length-1]; }
  function stateAt(p,time) {
    const t=clamp(time,0,p.duration);
    const actors={}; p.actors.forEach(a=>{actors[a.id]=keys(p.tracks[a.id],t);});
    const shot=shotAt(p, Math.min(t,p.duration-0.00001));
    const hits=p.beats.filter(b=>b.contact && Math.abs(t-b.t)<.19).map(b=>({id:b.id,dt:t-b.t,contact:b.contact,actor:b.actor,target:b.target}));
    const dialogue=p.beats.filter(b=>b.action==='dialogue' && t>=b.t && t<b.t+1.55).slice(-1)[0] || null;
    return {t,actors,shot,hits,dialogue};
  }
  function audit(p) {
    const issues=[];
    const err=(type,msg,ref)=>issues.push({severity:type,message:msg,ref});
    if(p.schema!=='ai-anime-cinematic-c1')err('error','Несовместимая схема','schema');
    if(!Number.isFinite(p.duration)||p.duration<=0||p.duration>180)err('error','Длительность 0–180 сек','duration');
    if(![12,24,30].includes(p.fps))err('warning','Рекомендуется 12/24/30 FPS','fps');
    const ids=new Set();
    for(const a of p.actors||[]){if(ids.has(a.id))err('error','Повтор ID персонажа',a.id);ids.add(a.id);
      const ts=p.tracks&&p.tracks[a.id];if(!ts||ts.length<2)err('error','Нет дорожки движения',a.id);
      else for(let i=1;i<ts.length;i++)if(ts[i].t<=ts[i-1].t)err('error','Некорректный порядок ключей',a.id);
      if(!p.media||!p.media.images||!p.media.images[a.id])err('warning','Нет настоящего арта персонажа',a.id);
    }
    const shots=p.shots||[];
    if(!shots.length || Math.abs(shots[0].start)>1e-6 || Math.abs(shots[shots.length-1].end-p.duration)>1e-5)err('error','Съёмка не закрывает всю сцену','shots');
    for(let i=0;i<shots.length;i++){
      if(shots[i].end<=shots[i].start)err('error','Нулевой план',i);
      if(i>0 && Math.abs(shots[i].start-shots[i-1].end)>1e-5)err('error','Разрыв/перекрытие плана',i);
      if(i>0 && shots[i].axis!==shots[i-1].axis)err('warning','Возможно нарушена ось действия (180°)',i);
    }
    const beatIDs=new Set();let prev=-1;
    for(const b of p.beats||[]){
      if(beatIDs.has(b.id))err('error','Повтор события',b.id);beatIDs.add(b.id);
      if(!Number.isFinite(b.t)||b.t<0||b.t>p.duration||b.t<prev)err('error','Неверный таймкод действия',b.id);
      prev=b.t;
      if(!ids.has(b.actor)||(b.target&&!ids.has(b.target)))err('error','Неизвестный персонаж',b.id);
      if(b.contact){
        if(!Number.isFinite(b.reach)||b.reach<=0)err('error','У контакта нет заданной дистанции',b.id);
        else if(p.tracks&&p.tracks[b.actor]&&p.tracks[b.target]){
          const gap=Math.abs(keys(p.tracks[b.actor],b.t).x-keys(p.tracks[b.target],b.t).x);
          if(gap>b.reach+0.001)err('error',`Невозможное попадание: дистанция ${gap.toFixed(3)} > ${b.reach}`,b.id);
        }
        if(b.contact==='hit' && !b.reaction)err('error','Попадание без указанной реакции',b.id);
        if(b.contact!=='hit' && b.contact!=='blocked')err('error','Неверный тип контакта',b.id);
      }
      if(b.action==='dialogue'&&!b.text)err('error','Реплика пустая',b.id);
    }
    if(!p.media||!p.media.images||!p.media.images.background)err('warning','Нет настоящего художественного фона','background');
    if(!p.rights||!p.rights.importedAssetsVerified)err('warning','Не подтверждены права на загружаемые материалы','rights');
    (p.beats||[]).filter(b=>b.action==='dialogue').forEach(b=>{if(!p.media||!p.media.audio||!p.media.audio[b.id])err('warning','Не загружена запись русской реплики',b.id);});
    return {ok:!issues.some(i=>i.severity==='error'),issues,errors:issues.filter(i=>i.severity==='error').length,warnings:issues.filter(i=>i.severity==='warning').length};
  }
  function exportPlan(p){return p.beats.map(b=>({timecode:`${Math.floor(b.t/60).toString().padStart(2,'0')}:${(b.t%60).toFixed(2).padStart(5,'0')}`,id:b.id,action:b.action,actor:b.actor,target:b.target||null,meaning:b.intent||'',shot:shotAt(p,b.t).kind,dialogue:b.text||'',contact:b.contact||null}));}
  function subtitleSrt(p){ const d=p.beats.filter(b=>b.action==='dialogue'&&b.text); const fmt=t=>{const ms=Math.round(t*1000);return `${String(Math.floor(ms/3600000)).padStart(2,'0')}:${String(Math.floor(ms/60000)%60).padStart(2,'0')}:${String(Math.floor(ms/1000)%60).padStart(2,'0')},${String(ms%1000).padStart(3,'0')}`;};return d.map((b,i)=>`${i+1}\n${fmt(b.t)} --> ${fmt(Math.min(p.duration,b.t+1.55))}\n${p.actors.find(a=>a.id===b.actor)?.name||b.actor}: ${b.text}\n`).join('\n'); }
  return {makeDemo,clamp,smooth,keys,shotAt,stateAt,audit,exportPlan,subtitleSrt};
});
