/* Deterministic off-line production-engine regression. No npm dependencies. */
const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const file=path.resolve(__dirname,'../anime-factory/engine/anime_production_engine_v45.js');
const js=fs.readFileSync(file,'utf8');
const ctx={};vm.createContext(ctx);
vm.runInContext(js+'\nthis.engine=AnimeProductionEngineV45;',ctx);
const e=ctx.engine;
assert.equal(e.VERSION,'45.0.0');
assert.equal(e.DOMAINS.story,'ready');
assert.equal(e.DOMAINS.voice,'v47_integration');
assert.equal(e.DOMAINS.threeD,'separate_after_v50');
const project={
 title:'Тайна рассвета',seed:6060,
 characters:[{id:'0',name:'Акира',role:'Герой',goal:'Защитить мир'},
  {id:'1',name:'Мира',role:'Союзница',goal:'Спасти друга'}],
 lore:[{rule:'Магия расходует энергию'}],
 episodes:[{number:1,title:'Пробуждение',
 scenes:[
  {kind:'friendship',title:'Встреча',place:'Лес',duration:5,lines:[]},
  {kind:'romance',title:'Обещание',place:'Мост',duration:6,lines:[]},
  {kind:'betrayal',title:'Обман',place:'Замок',duration:4,lines:[]},
  {kind:'fight',title:'Бой',place:'Замок',duration:7,
   beats:[{actor:'hero',outcome:'block',label:'Защита'}],lines:[]}
 ]}],
};
const source=JSON.stringify(project);
const assets=[{name:'Акира',kind:'character-cutout',rights:'My art',width:640,
 height:960,alpha:true,layers:[{name:'arms',pivot:{x:15,y:-70},active:true}]}];
const snap=e.snapshot(project,assets);
assert.equal(snap.audit.ok,true,JSON.stringify(snap.audit));
assert.equal(snap.episodes[0].shots.length,4);
assert.equal(snap.episodes[0].duration,22);
assert.equal(snap.world.locations.length,3);
assert.equal(snap.relationships[1].after.affection,30);
assert.equal(snap.relationships[2].after.trust,34);
assert.equal(snap.assets[0].layers[0].pivot.y,-70);
assert.equal(e.combatPlan(project.episodes[0].scenes[3])[0].result,'block');
assert.equal(e.combatPlan(project.episodes[0].scenes[3])[0].authoritative,false);
assert.equal(e.validate({characters:[],episodes:[]}).ok,false);
assert.equal(JSON.stringify(e.snapshot(project,assets)),JSON.stringify(snap));
assert.equal(JSON.stringify(project),source,'Planning engine MUST NOT alter the old project');
console.log('ANIME PRODUCTION ENGINE V45 PASSED: world, camera, relations, canonical combat, assets, pure snapshot.');
