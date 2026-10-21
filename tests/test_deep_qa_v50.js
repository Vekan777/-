/* V50 deep QA adversarial test: deliberately corrupted projects cannot pass.
 * Run with Node.js, no npm dependencies or browser mocking.
 */
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const code=fs.readFileSync(path.join(__dirname,'../anime-factory/v50/deep_qa_v50.js'),'utf8');
const methods=code.split('function v50SelectedEpisode(){')[0];
const ctx={};vm.createContext(ctx);vm.runInContext(methods,ctx);
const audit=project=>JSON.parse(JSON.stringify(vm.runInContext(
 'v50AuditProject('+JSON.stringify(project)+')',ctx)));
const obj={
 title:'История двух персонажей',
 characters:[
  {id:'1',name:'Акира',productionRig:{rights:'Авторская графика',
    parts:{face:{image:'data:image/png;base64,YWJj'}}}},
  {id:'2',name:'Мира',productionRig:{rights:'Авторская графика',
    parts:{face:{image:'data:image/png;base64,YWJj'}}}}
 ],
 episodes:[{title:'Пробуждение',storyV20:{wound:'Усталость',payoff:'Перемирие'},
  scenes:[{title:'На рассвете',kind:'friendship',duration:4,
   beats:[],animationV46:{tracks:{hero:{
     face:[{t:0,x:0,y:0,angle:0,scale:1},
       {t:1,x:0,y:0,angle:10,scale:1}]}}},
   audioV36:{voice:{name:'line.wav',embeddedV47:'data:audio/wav;base64,YWJj',
    waveV47:[.2,.6,1],gain:1,offset:0}},
   subtitlesV37:{cues:[{start:.5,end:1.5,text:'Договорились'}]},
   bgV45:{image:'data:image/png;base64,YWJj',rights:'Авторский фон'}
  }]}]
};
const copy=JSON.stringify(obj),ok=audit(obj);
assert.strictEqual(ok.status,'technical-review');
assert.strictEqual(ok.passed,true);
assert.strictEqual(ok.errors.length,0);
assert.strictEqual(ok.animatedScenes,1);
assert.strictEqual(ok.voiceScenes,1);
assert.strictEqual(ok.subtitleScenes,1);
assert.strictEqual(ok.manualAcceptanceRequired,true);
assert.strictEqual(JSON.stringify(obj),copy,'Auditor may NEVER mutate project');
const clone=()=>JSON.parse(copy);
const cases=[
 ['duplicate_id',p=>{p.characters[1].id='1'},'Повтор ID'],
 ['duplicate_name',p=>{p.characters[1].name='Акира'},'Повтор имени'],
 ['bad_duration',p=>{p.episodes[0].scenes[0].duration=NaN},'длительность'],
 ['broken_art',p=>{p.characters[0].productionRig.parts.face.image='https://malicious.example/a.png'},'data URL'],
 ['broken_background',p=>{p.episodes[0].scenes[0].bgV45.image='unsafe'},'повреждён'],
 ['duplicate_key',p=>{p.episodes[0].scenes[0].animationV46.tracks.hero.face[1].t=0},'ключи'],
 ['bad_voice',p=>{p.episodes[0].scenes[0].audioV36.voice.embeddedV47='invalid'},'аудиоданные'],
 ['bad_wave',p=>{p.episodes[0].scenes[0].audioV36.voice.waveV47=[.2,5]},'диапазона'],
 ['bad_gain',p=>{p.episodes[0].scenes[0].audioV36.voice.gain=-3},'громкости'],
 ['bad_subtitle',p=>{p.episodes[0].scenes[0].subtitlesV37.cues[0].end=5},'таймкод'],
 ['lost_combat',p=>{p.episodes[0].scenes[0].kind='fight';delete p.episodes[0].scenes[0].beats},'боевые'],
 ['empty_episode',p=>{p.episodes[0].scenes=[]},'без сцен']
];
for(const [name,mutate,token] of cases){
 const p=clone();mutate(p);
 const result=audit(p);
 assert.equal(result.passed,false,name+': corrupt case marked passed');
 assert(result.errors.some(x=>x.problem.includes(token)),name+': no explanatory error '+token+
   ': '+JSON.stringify(result.errors));
}
const noEpisode=audit({episodes:[]});assert.equal(noEpisode.passed,false);
const noMouth=clone();delete noMouth.episodes[0].scenes[0].audioV36.voice.embeddedV47;
const warn=audit(noMouth);
assert.equal(warn.passed,true,'missing optional voice must warn, not erase canonical plot');
assert(warn.warnings.some(x=>x.stage==='audio'));
assert.equal(JSON.stringify(audit(obj)),JSON.stringify(ok),'deterministic deep QA');
console.log('V50 DEEP QA PASSED: 12 deliberate corruption cases, audit purity, legacy story, media safety and honest signoff.');
