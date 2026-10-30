"""Local visual Template-First factory, no external accounts, no downloads performed automatically."""
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from pathlib import Path
import base64,html,json,mimetypes,secrets,shutil,io,urllib.parse,zipfile
from template_engine import ROOT,registry,make_project,build_three,parse_id,safe_zip
from screenshot_matcher import match_bytes

PAGE='''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Фабрика сайтов — Template First</title><style>*{box-sizing:border-box}body{font:15px system-ui,Arial,sans-serif;margin:0;background:#f4f7fb;color:#192e4a}header{padding:25px;background:#173a70;color:white}header p{opacity:.85}.container{max-width:1210px;margin:20px auto;padding:0 14px}.box{background:white;border:1px solid #dce4ee;border-radius:15px;padding:20px;margin:17px 0}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px}.card{border:2px solid #e1e7ef;border-radius:12px;overflow:hidden;background:white;cursor:pointer;position:relative}.card.selected{border-color:#2465d2;box-shadow:0 0 0 2px #a2c3fd}.card img{display:block;width:100%;aspect-ratio:16/10;object-fit:cover;object-position:top;background:#edf2fa}.card div{padding:10px}.card h3{font-size:14px;margin:2px 0}.card small{color:#607184}button{background:#245cbd;color:white;border:0;border-radius:8px;padding:11px 16px;font:inherit;cursor:pointer}button:disabled{opacity:.5}input,select{font:inherit;border:1px solid #a6b5c9;border-radius:8px;padding:11px;max-width:100%}input[type=text]{width:min(460px,100%)}label{display:block;margin:12px 0 6px;font-weight:700}.sticky{position:sticky;bottom:0;background:#fffffff5;border-top:1px solid #ddd;padding:12px 0;z-index:5}.cols{display:grid;grid-template-columns:1fr 1fr;gap:20px}.muted{font-size:13px;color:#5c6b7f}.result a{display:inline-block;margin:8px;padding:8px 11px;background:#e7f0ff;color:#245cbd;border-radius:8px;text-decoration:none}.badge{font-size:12px;color:#136b46}#matches button{background:#e7f0ff;color:#245cbd;margin:4px}a{color:#245cbd}@media(max-width:720px){.cols{grid-template-columns:1fr}}</style></head><body><header><div class="container"><h1>Фабрика сайтов — Template First V60</h1><p>96 пресетов · 16 структур × 6 оформлений · Три варианта сайта · Локальная админка товаров</p></div></header><div class="container"><div class="box cols"><section><h2>1. Загрузите макет</h2><p>PNG/JPG, скриншот сайта на ПК. Поиск сравнивает цветовые области и структуру. Это ориентировочное ранжирование, не профессиональное зрительное распознавание.</p><input type="file" id="reference" accept="image/jpeg,image/png,image/webp"><button id="match">Найти похожие</button><p id="matches" class="muted"></p></section><section><h2>2. Заполните основу</h2><label>Название магазина</label><input id="brand" type="text" value="Магазин ЕМЕЛЯ" maxlength="80"><label>Выбранный пресет</label><input id="selected" type="text" readonly value="classic-blue"><p class="muted">Фабрика создаст три сайта. Для названия «ЕМЕЛЯ» все пресеты сразу заполняются 117 демонстрационными товарами, фотографиями, полным фасадом и контактами. Для других магазинов каталог заполняется через админку.</p><button id="build">Создать три варианта ZIP</button><div id="output" class="result" role="status"></div></section></div><div class="box"><h2>★ Полноценная витрина «ЕМЕЛЯ» — утверждённые 3 дизайна V60</h2><p>Три утверждённых визуальных референса с индивидуальными правилами композиции, шрифтами и декоративными элементами. Проверенные браузерные превью ниже. Данные товаров единые для трёх сайтов; цены вводятся через админку.</p><div class="grid"><div class="card"><img src="/premium-preview/faithful.png"><div><b>Максимально близко к макету</b></div></div><div class="card"><img src="/premium-preview/refined.png"><div><b>Улучшенный</b></div></div><div class="card"><img src="/premium-preview/author.png"><div><b>Авторский</b></div></div></div><p><button id="build-premium">Создать три заполненных сайта «ЕМЕЛЯ»</button></p><div id="premium-output" class="result"></div></div><div class="box" id="design-engine"><h2>Дизайн-конвейер V60: утверждённые эталоны и художественная приёмка</h2><p>Для «ЕМЕЛИ» три дизайна собираются на основе <b>разных композиций</b>, 6 одобренных референсов, 3 художественных изображений и общих данных каталога. Движок сохраняет контрольные суммы, проверяет права на материалы и отклоняет невалидные исходники. Это алгоритмическая автоматизация дизайна, не автономная генеративная нейросеть.</p><p>Проверить три дизайн-контракта: <a href="/api/design-audit" target="_blank">Отчёт целостности</a>. Для подбора открытых фотографий: запустить <code>ПОИСК_ОТКРЫТЫХ_ФОТО_WINDOWS.bat</code> с интернетом, затем вручную подтвердить происхождение и права. Автоматическая замена фотографий без подтверждения отключена.</p><p class="muted">Сайт-скриншоты в блоке выше сделаны браузером. Концепты — отдельные художественные изображения, не скриншоты работающего сайта.</p></div><div class="box"><h2>Библиотека готовых схем</h2><div class="cols"><label>Тип страницы<select id="family"><option value="">Все структуры</option></select></label><label>Оформление<select id="skin"><option value="">Все оформления</option></select></label></div><p class="muted">Превью отрисованы из настоящих локальных HTML/CSS. Внешние наборы с лицензиями хранятся отдельно в документации.</p><div class="grid" id="catalog"></div></div><div class="box"><h2>Как пользоваться после сборки</h2><p>Распакуйте ZIP сайта, нажмите <b>ЗАПУСТИТЬ_САЙТ_WINDOWS.bat</b>, откройте адрес <b>127.0.0.1:8781</b>, а через <b>/admin</b> добавьте свои товары, изображения и цены. Каждый ZIP запускается отдельно; не запускайте три сайта одновременно на одном порту.</p><p>Никакого автоматического выхода в интернет, платежей или реальных заказов. Сначала нужно испытать сайт и настроить публичное HTTPS-размещение.</p></div></div><script>
const presets=__PRESETS__;let chosen='classic-blue';const el=i=>document.getElementById(i);
function select(id){chosen=id;el('selected').value=id;document.querySelectorAll('.card').forEach(x=>x.classList.toggle('selected',x.dataset.id===id));}
function render(){const fam=el('family').value,skin=el('skin').value;el('catalog').replaceChildren();presets.filter(t=>(!fam||t.family===fam)&&(!skin||t.skin===skin)).forEach(t=>{const card=document.createElement('div');card.className='card'+(t.id===chosen?' selected':'');card.dataset.id=t.id;card.onclick=()=>select(t.id);const img=document.createElement('img');img.src=t.family==='external-commerce'?'/preview/panorama-blue-desktop.png':'/preview/'+t.id+'-desktop.png';img.loading='lazy';img.alt='Скриншот шаблона '+t.title;const d=document.createElement('div'),h=document.createElement('h3'),desc=document.createElement('small');h.textContent=t.title;desc.textContent=t.description;d.append(h,desc);card.append(img,d);el('catalog').append(card)})}
new Set(presets.map(x=>x.family)).forEach(x=>{const o=document.createElement('option');o.value=x;o.textContent=x;el('family').append(o)});new Set(presets.map(x=>x.skin)).forEach(x=>{const o=document.createElement('option');o.value=x;o.textContent=x;el('skin').append(o)});el('family').onchange=render;el('skin').onchange=render;render();
async function post(path,data){const r=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});const j=await r.json();if(!r.ok)throw Error(j.error||'Ошибка');return j}
el('match').onclick=async()=>{try{const file=el('reference').files[0];if(!file)throw Error('Выберите изображение');if(file.size>8*1024*1024)throw Error('Изображение больше 8 МБ');el('matches').textContent='Сравниваю…';const b64=await new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(reader.result.split(',')[1]);reader.onerror=reject;reader.readAsDataURL(file)});const matches=(await post('/api/match',{image:b64})).matches;el('matches').replaceChildren();matches.forEach(m=>{const b=document.createElement('button');b.textContent=m.title+' (разница '+m.distance+')';b.onclick=()=>{if(m.kind==='filled-demo'){document.getElementById('build-premium').scrollIntoView({behavior:'smooth',block:'center'});return}el('family').value='';el('skin').value='';render();select(m.id);document.querySelector('[data-id="'+m.id+'"]').scrollIntoView({behavior:'smooth',block:'center'})};el('matches').append(b)});if(matches.length&&matches[0].kind!=='filled-demo')select(matches[0].id)}catch(e){el('matches').textContent=e.message}};
el('build-premium').onclick=async()=>{let box=el('premium-output');box.textContent='Сборка…';try{let j=await post('/api/build-premium',{});box.replaceChildren();j.files.forEach(f=>{let a=document.createElement('a');a.href='/download-premium/'+encodeURIComponent(f);a.download=f;a.textContent='Скачать '+f;box.append(a)})}catch(e){box.textContent=e.message}};
el('build').onclick=async()=>{el('build').disabled=true;el('output').textContent='Собираю архивы…';try{const j=await post('/api/build',{template:chosen,brand:el('brand').value});el('output').replaceChildren();j.files.forEach(f=>{const a=document.createElement('a');a.href='/download/'+encodeURIComponent(f);a.download=f;a.textContent='Скачать '+f;el('output').append(a)})}catch(e){el('output').textContent=e.message}finally{el('build').disabled=false}};
</script></body></html>'''

# Safe explanatory panel: installed license sources are opt-in, not bundled silently.
PAGE=PAGE.replace('</header>', '</header><div class="container"><div class="box"><b>Внешний MIT Commerce (опционально)</b><p class="muted">На Windows запустите <code>УСТАНОВИТЬ_COLORLIB_COMMERCE_WINDOWS.bat</code> и перезапустите фабрику. После проверки лицензии появятся три дополнительных оформления Colorlib Commerce. Bootstrap 6 alpha требует Edge/Chrome 130+. Исходные демонстрационные изображения и платёжная форма не переносятся. Шаблон Stylish в генератор не включён из-за условий распространителя.</p></div></div>')

class H(BaseHTTPRequestHandler):
 def send(self,code,content,typ='text/html; charset=utf-8'):
  if isinstance(content,str):content=content.encode('utf-8')
  self.send_response(code);self.send_header('Content-Type',typ);self.send_header('Content-Length',str(len(content)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(content)
 def json(self,code,obj):self.send(code,json.dumps(obj,ensure_ascii=False),'application/json; charset=utf-8')
 def do_GET(self):
  path=urllib.parse.urlparse(self.path).path
  if path=='/':return self.send(200,PAGE.replace('__PRESETS__',json.dumps(registry(),ensure_ascii=False)))
  if path=='/api/design-audit':
   from design_autopilot import source_contract
   return self.json(200,source_contract())
  if path=='/api/external-status':
   from external_templates import is_installed
   return self.json(200,{'colorlib_commerce_installed':is_installed(),'stylish':'blocked_by_distributor_generator_terms'})
  if path.startswith('/premium-preview/'):
   name=path.split('/')[-1];p=ROOT/'previews'/'premium'/name
   if name in ('faithful.png','refined.png','author.png') and p.is_file():return self.send(200,p.read_bytes(),'image/png')
  if path.startswith('/download-premium/'):
   name=path.split('/')[-1];p=ROOT/'outputs'/'premium'/name
   if name in ('EMELYA_V60_faithful_SITE.zip','EMELYA_V60_refined_SITE.zip','EMELYA_V60_author_SITE.zip') and p.is_file():return self.send(200,p.read_bytes(),'application/zip')
  if path.startswith('/preview/'):
   name=path.split('/')[-1];p=ROOT/'previews'/name
   if name.endswith('.png') and p.is_file() and p.parent==ROOT/'previews':return self.send(200,p.read_bytes(),'image/png')
  if path.startswith('/download/'):
   name=path.split('/')[-1];p=ROOT/'outputs'/'latest'/name
   if name in ('SITE_faithful.zip','SITE_refined.zip','SITE_author.zip') and p.is_file():return self.send(200,p.read_bytes(),'application/zip')
  return self.send(404,'Не найдено')
 def do_POST(self):
  try:
   origin=self.headers.get('Origin','');host=self.headers.get('Host','')
   if origin and urllib.parse.urlparse(origin).netloc!=host:raise ValueError('Запрос из другого источника')
   length=int(self.headers.get('Content-Length',0))
   if not 0<length<=12*1024*1024:raise ValueError('Слишком большой запрос')
   if not self.headers.get('Content-Type','').startswith('application/json'):raise ValueError('Требуется JSON')
   d=json.loads(self.rfile.read(length))
   if self.path=='/api/match':
    raw=base64.b64decode(d.get('image',''),validate=True)
    return self.json(200,{'matches':match_bytes(raw)})
   if self.path=='/api/build-premium':
    from build_emelya_premium import all_three
    files=all_three(ROOT/'outputs'/'premium')
    return self.json(200,{'ok':True,'files':[Path(x).name for x in files]})
   if self.path=='/api/build':
    t=parse_id(str(d.get('template','')));brand=str(d.get('brand','')).strip()
    if not 2<=len(brand)<=80:raise ValueError('Название: от 2 до 80 символов')
    out=ROOT/'outputs'/'latest'
    # only fixed output, never user-defined filesystem paths
    if out.exists():shutil.rmtree(out)
    generated=build_three(out,t['id'],brand)
    return self.json(200,{'ok':True,'files':[Path(x).name for x in generated]})
   return self.json(404,{'error':'Операция не найдена'})
  except Exception as e:return self.json(400,{'error':str(e)[:150]})
 def log_message(self,*a):pass

if __name__=='__main__':
 import webbrowser
 host='127.0.0.1';port=8780
 print('Фабрика: http://127.0.0.1:8780')
 try:webbrowser.open('http://127.0.0.1:8780')
 except Exception:pass
 ThreadingHTTPServer((host,port),H).serve_forever()