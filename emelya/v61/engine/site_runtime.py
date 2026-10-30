"""Local catalogue CMS + 3 template render modes. Python 3.10+, Pillow only for uploads.
Not internet-deployment audited. Runs only on 127.0.0.1 by default.
"""
from __future__ import annotations
import base64, csv, hashlib, hmac, html, io, json, mimetypes, os, re, secrets, sqlite3, threading, time, urllib.parse, zipfile
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from http.cookies import SimpleCookie

BASE=Path(__file__).resolve().parent
CONF=json.loads((BASE/'project.json').read_text(encoding='utf-8'))
DB=BASE/'data'/'catalog.sqlite'; DB.parent.mkdir(exist_ok=True,parents=True)
MEDIA=BASE/'media';MEDIA.mkdir(exist_ok=True)
SESSIONS={}; FAILURES={};LOCK=threading.RLock(); MAX_BODY=8*1024*1024


def conn():
 db=sqlite3.connect(DB,timeout=15)
 db.execute('PRAGMA foreign_keys=ON');db.row_factory=sqlite3.Row
 return db


def init_db():
 with conn() as db:
  db.execute('CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT NOT NULL)')
  db.execute('CREATE TABLE IF NOT EXISTS categories(id TEXT PRIMARY KEY,name TEXT NOT NULL,icon TEXT NOT NULL)')
  db.execute('CREATE TABLE IF NOT EXISTS products(id TEXT PRIMARY KEY,category_id TEXT NOT NULL REFERENCES categories(id),name TEXT NOT NULL,price_cents INTEGER,stock INTEGER,image TEXT NOT NULL DEFAULT "", demo INTEGER NOT NULL DEFAULT 0, CHECK (price_cents IS NULL OR price_cents>=0), CHECK(stock IS NULL OR stock>=0))')
  db.execute('CREATE INDEX IF NOT EXISTS products_by_category ON products(category_id)')
  row=db.execute('SELECT value FROM settings WHERE key="password_hash"').fetchone()
  if row is None:
   secret=os.environ.get('EMELYA_ADMIN_PASSWORD') or secrets.token_urlsafe(18)
   salt=secrets.token_bytes(16);k=hashlib.pbkdf2_hmac('sha256',secret.encode(),salt,600_000)
   db.execute('INSERT INTO settings(key,value) VALUES(?,?)',('password_hash',salt.hex()+':'+k.hex()))
   f=BASE/'ADMIN_FIRST_LOGIN.txt';f.write_text('СЕКРЕТ — НЕ ЗАГРУЖАТЬ НА САЙТ И НЕ ПЕРЕСЫЛАТЬ!\nАдминка http://127.0.0.1:8781/admin\nПароль: '+secret+'\n',encoding='utf-8')
   try:os.chmod(f,0o600)
   except OSError:pass
   print('Первый запуск: пароль сохранён в',f)
  is_new = db.execute('SELECT value FROM settings WHERE key="seed_complete"').fetchone() is None
  if is_new:
   if CONF.get('premium_demo') or CONF.get('content_demo'):
    content=json.loads((BASE/'premium_seed.json').read_text(encoding='utf-8'))
    for c in content['categories']:
     db.execute('INSERT INTO categories(id,name,icon) VALUES (?,?,?)',(c['id'],c['name'],c['icon']))
    for p in content['products']:
     db.execute('INSERT INTO products(id,category_id,name,price_cents,stock,image,demo) VALUES (?,?,?,NULL,NULL,?,1)',(p['id'],p['category_id'],p['name'],p['image']))
    db.execute('INSERT INTO settings(key,value) VALUES (?,?)',('banner',content['banner']))
   else:
    for slug,name,emoji in [('food','Продукты','🥖'),('home','Для дома','🏠'),('clean','Бытовая химия','🧴'),('tools','Хозтовары','🧰')]:
     db.execute('INSERT INTO categories(id,name,icon) VALUES (?,?,?)',(slug,name,emoji))
    if CONF.get('demo',False):
     for i,(cat,title) in enumerate([('food','Хлеб — пример товара'),('food','Молоко — пример товара'),('food','Крупа — пример товара'),('food','Чай — пример товара'),('clean','Средство для уборки — пример'),('clean','Стиральный порошок — пример'),('home','Контейнер — пример'),('home','Салфетки — пример'),('tools','Губки — пример'),('tools','Перчатки — пример'),('food','Сахар — пример'),('home','Лампа — пример')]):
      db.execute('INSERT INTO products(id,category_id,name,price_cents,stock,demo) VALUES (?,?,?,NULL,NULL,1)',(f'demo{i+1}',cat,title))
    photo=CONF.get('initial_banner','')
    if isinstance(photo,str) and photo.startswith('/media/') and (MEDIA/photo.rsplit('/',1)[-1]).is_file():
     db.execute('INSERT INTO settings(key,value) VALUES(?,?)',('banner',photo))
   db.execute('INSERT INTO settings(key,value) VALUES(?,?)',('seed_complete','1'))


def h(s):return html.escape(str(s),quote=True)

def site_settings():
 d={k:CONF.get(k,'') for k in ('store_name','description','address','hours','contact','telegram','max')}
 d['banner']=''
 with conn() as db:
  for row in db.execute("SELECT key,value FROM settings WHERE key IN ('store_name','description','address','hours','contact','telegram','max','banner')"):
   d[row['key']]=row['value']
 return d

def snapshot():
 with conn() as db:
  cats=[dict(x) for x in db.execute('SELECT id,name,icon FROM categories ORDER BY rowid')]
  products=[]
  for p in db.execute('SELECT * FROM products ORDER BY rowid ASC'):
   d=dict(p);d['price']=None if d['price_cents'] is None else f"{d['price_cents']/100:.2f}";del d['price_cents']
   products.append(d)
  return {'categories':cats,'products':products, 'site':site_settings()}

def is_logged(handler):
 cookie=SimpleCookie()
 try:cookie.load(handler.headers.get('Cookie',''))
 except Exception:return None
 session_id=cookie.get('em_sid')
 if not session_id:return None
 with LOCK:
  session=SESSIONS.get(session_id.value)
  if session and session['expiry']>time.time():return session
 return None

def layout_for(mode):
 try:return json.loads((BASE/('layout_'+mode+'.json')).read_text(encoding='utf-8'))
 except FileNotFoundError:return json.loads((BASE/('layout_'+CONF['modes'][0]+'.json')).read_text(encoding='utf-8'))


def render_generic_page(mode,page='home'):
 lay=layout_for(mode); family=lay['family'];p=lay['palette'];settings=site_settings();name=settings['store_name'];title='Товары и категории' if page=='catalog' else settings['description']
 styles=';'.join('--'+k+':'+str(v) for k,v in p.items())
 q='?mode='+urllib.parse.quote(mode)
 intro='Мы рядом — продукты и товары для дома. Наполнение каталога и цены задаются в админке.'
 art=('<img src="'+h(settings['banner'])+'" alt="Фотография магазина">') if settings['banner'] else '<div class="art-label">Всё нужное рядом</div>'
 hero=f'<section class="hero"><div class="hero-copy"><div class="eyebrow">Магазин у дома</div><h1>{h(title)}</h1><p>{h(intro)}</p><div class="hero-cta"><a class="action" href="/catalog{q}">Открыть каталог →</a><a class="subaction" href="#contacts">Контакты</a></div></div><div class="hero-art">{art}</div></section>'
 if page=='catalog':hero=f'<section class="catalog-top"><span class="eyebrow">Все разделы</span><h1>Каталог товаров</h1><p class="hint">Товары, изображения и цены добавляются владельцем через админку.</p></section>'
 sidebar='<aside class="sidebar"><h3>Разделы</h3><a href="/catalog'+q+'">Все товары</a><a href="#categories">Категории</a><a href="#products">Товары</a></aside>'
 sections=f'''<div class="main-grid">{sidebar}<div class="main-content"><section class="section" id="categories"><div class="sectionhead"><div><span class="eyebrow">Удобный выбор</span><h2>Категории товаров</h2></div><span class="hint">Выберите раздел</span></div><div class="categories" id="categories"></div></section><section class="section" id="product-section"><div class="sectionhead"><div><span class="eyebrow">Каталог</span><h2>Товары магазина</h2></div></div><div class="filters" id="filters"></div><div class="products" id="products"></div><button id="more" class="action" hidden>Показать ещё</button></section></div></div>'''
 sections=sections.replace('id="categories"><div class="sectionhead"','id="category-section"><div class="sectionhead"')
 if page=='home':sections=sections.replace('<div class="filters" id="filters"></div>','')
 features='''<section class="features section"><div class="feature"><b>Простой каталог</b><p>Товары и категории обновляются в административной панели.</p></div><div class="feature"><b>Цены указывает владелец</b><p>Тестовые продукты не выдаются за настоящие предложения.</p></div><div class="feature"><b>Работает на телефоне</b><p>Готовая адаптивная сетка с переключением меню.</p></div></section>'''
 footer=f'<footer class="site-foot" id="contacts"><div class="wrap"><div class="footgrid"><div><b class="brand">{h(name)}</b><p>{h(settings['description'])}</p></div><div><b>Адрес</b><p>{h(settings.get('address','Адрес уточняется'))}</p></div><div><b>Режим работы</b><p>{h(settings.get('hours','08:00–19:00'))}</p></div></div><div class="copyright">© {datetime.now().year} {h(name)}. Локальная версия для проверки; нет оплаты и настоящего онлайн-заказа.</div></div></footer>'
 return f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="{h(settings['description'])}"><meta name="robots" content="noindex,nofollow"><title>{h(name)} — {h(title)}</title><link rel="stylesheet" href="/site.css"></head><body class="layout-{h(family)} mode-{h(mode)}" style="{h(styles)}"><header class="mast"><div class="wrap mast-inner"><a class="brand" href="/{q}">{h(name)}<small>ВСЁ НУЖНОЕ РЯДОМ</small></a><button class="mobile-toggle" id="mobile-toggle" aria-expanded="false" aria-controls="main-menu" aria-label="Открыть меню">☰ Меню</button><nav class="menu" id="main-menu"><a href="/{q}">Главная</a><a href="/catalog{q}">Каталог товаров</a><a href="#contacts">Контакты</a></nav></div></header><div class="bar"><div class="wrap"><span>Продукты · Бытовая химия · Товары для дома</span><span>Демонстрационная сборка</span></div></div><main class="wrap">{hero}<form class="search-line" action="/catalog" method="get"><input type="hidden" name="mode" value="{h(mode)}"><input id="search" aria-label="Поиск по товарам" type="search" placeholder="Поиск товаров…"><button type="button" onclick="document.getElementById('products').scrollIntoView()">Найти</button></form>{sections}{features}<div class="notice">Это тестовая версия шаблона. Реальные товары, цены и фотографии добавляет владелец через админку. Настоящие заказы и платежи не подключены.</div></main>{footer}<script>window.MODE={json.dumps(mode)};</script><script src="/site.js" defer></script></body></html>'''


def social_buttons(settings,tag=''):
 telegram=settings.get('telegram','').strip(); maxlink=settings.get('max','').strip()
 def safe(url,host):
  try:
   p=urllib.parse.urlparse(url)
   return url if p.scheme=='https' and p.hostname in host else ''
  except Exception:return ''
 tg=safe(telegram,('t.me','telegram.me'))
 mx=safe(maxlink,('max.ru',))
 a=('<a class="social tg" href="'+h(tg)+'" target="_blank" rel="noopener noreferrer">✈ Telegram</a>' if tg else '<span class="social tg disabled" title="Ссылка Telegram пока не указана; настройте её в админке">✈ Telegram</span>')
 b=('<a class="social max" href="'+h(mx)+'" target="_blank" rel="noopener noreferrer">◉ Мы в MAX</a>' if mx else '<span class="social max disabled">◉ Мы в MAX</span>')
 return '<div class="socials socials-'+tag+'">'+a+b+'</div>'

def premium_page(mode,page,settings,lay):
 phone_link='tel:'+re.sub(r'[^+0-9]','',settings.get('contact',''))
 name=settings['store_name'];desc=settings['description'];q='?mode='+urllib.parse.quote(mode)
 p=lay['palette'];styles=';'.join('--'+k+':'+str(v) for k,v in p.items())
 seed=json.loads((BASE/'premium_seed.json').read_text(encoding='utf-8'))
 logo=seed['logo']
 banner=settings.get('banner') or seed['banner']
 logohtml='<img class="logo-img" src="'+h(logo)+'" alt="Магазин ЕМЕЛЯ — Всё нужное рядом">'
 heading='''<div class="hero-copy"><svg class="hero-leaves" viewBox="0 0 360 270" aria-hidden="true" xmlns="http://www.w3.org/2000/svg"><g fill="none" stroke="#527d32" stroke-width="4" stroke-linecap="round" opacity=".76"><path d="M18 12Q80 70 142 120T295 227"/><path d="M66 51Q88 5 136 8"/><path d="M106 93Q142 51 190 56"/><path d="M170 146Q218 115 264 128"/><path d="M220 191Q268 160 320 177"/></g><g fill="#77aa39" opacity=".85"><ellipse cx="80" cy="26" rx="32" ry="14" transform="rotate(-35 80 26)"/><ellipse cx="130" cy="8" rx="38" ry="15" transform="rotate(8 130 8)"/><ellipse cx="137" cy="75" rx="35" ry="14" transform="rotate(-33 137 75)"/><ellipse cx="193" cy="52" rx="32" ry="12" transform="rotate(11 193 52)"/><ellipse cx="244" cy="115" rx="35" ry="14" transform="rotate(-16 244 115)"/><ellipse cx="287" cy="174" rx="30" ry="13" transform="rotate(-14 287 174)"/></g><g fill="#b8cc47" opacity=".65"><ellipse cx="33" cy="52" rx="30" ry="11" transform="rotate(37 33 52)"/><ellipse cx="88" cy="112" rx="28" ry="12" transform="rotate(37 88 112)"/><ellipse cx="175" cy="164" rx="31" ry="11" transform="rotate(40 175 164)"/><ellipse cx="238" cy="213" rx="30" ry="11" transform="rotate(44 238 213)"/></g></svg><span class="eyebrow">МАГАЗИН У ДОМА</span><h1><span class="hero-title-first">Продукты и товары</span> <em>для всей семьи</em></h1><div class="hero-art-ornament" aria-hidden="true"><svg viewBox="0 0 80 32" xmlns="http://www.w3.org/2000/svg"><path d="M6 27Q31 25 64 3" fill="none" stroke="#be8734" stroke-width="2.4" stroke-linecap="round"/><path d="M18 22Q5 12 10 4Q28 9 18 22Z"/><path d="M35 15Q26 3 34 1Q47 6 35 15Z"/><path d="M47 11Q51 0 62 2Q61 11 47 11Z"/><path d="M59 5Q67 0 76 4Q72 13 59 5Z"/></svg></div><p>Знакомый магазин в селе Степановка. Свежие продукты, товары для дома и всё необходимое рядом с вами.</p><div class="hero-cta"><a class="action" href="/catalog'''+q+'''">Выбрать категорию →</a><a class="subaction" href="#how">Как выбрать товары →</a></div></div>'''
 # For the enhanced artistic modes, show curated licensed-by-user visual concept only when the admin has not replaced banner.
 if mode in ('faithful','refined','author') and banner==seed['banner']:
  banner=seed.get('creative_banners',{}).get(mode,banner)
 photo='<div class="hero-photo"><img src="'+h(banner)+'" alt="Художественная иллюстрация фасада магазина с деревьями, не документальная фотография" loading="eager"></div>'
 if mode=='author' and page=='home':
  photos=[seed['products'][j] for j in (0,2,3)]
  inset=''.join('<div class="cover-product"><img src="'+h(p['image'])+'" alt="'+h(p['name'])+'"><small>'+h(p['name'])+'</small></div>' for p in photos)
  photo=photo.replace('</div>','<div class="cover-products">'+inset+'</div></div>',1)
 hero='<section class="hero">'+heading+photo+'</section>' if page=='home' else '<section class="catalog-top"><div class="eyebrow">УДОБНЫЙ ВЫБОР</div><h1>Каталог товаров</h1><p>Изображения и названия — демонстрация. Актуальные цены и наличие устанавливает владелец магазина.</p></section>'
 benefits='''<div class="advantages"><div><span>🛒</span><strong>Удобный каталог</strong><small>Быстрый поиск товаров</small></div><div><span>♡</span><strong>Всё рядом</strong><small>Для семьи и дома</small></div><div><span>📦</span><strong>Самовывоз</strong><small>После подтверждения</small></div><div><span>📍</span><strong>Наше село</strong><small>Степановка</small></div></div>'''
 categories='''<section class="section category-section" id="category-section"><div class="sectionhead"><div><span class="eyebrow">УДОБНЫЙ ВЫБОР</span><h2>Выберите категорию</h2></div><a class="section-more" href="/catalog'''+q+'''">Смотреть весь каталог →</a></div><div class="categories" id="categories"></div></section>'''
 products='''<section class="section product-section" id="product-section"><div class="sectionhead"><div><span class="eyebrow">СМОТРИТЕ В КАТАЛОГЕ</span><h2>Товары магазина</h2></div><span class="hint">Демонстрационные товары · цена уточняется</span></div>'''+('' if page=='home' else '<div class="filters" id="filters"></div>')+'''<div class="products" id="products"></div><button class="action" id="more" hidden>Показать ещё</button></section>'''
 how='''<section class="how" id="how"><h2>Как сделать заказ?</h2><div class="steps"><div><span>01</span><b>🛒 Выберите товары</b><small>Добавьте нужное в свой список</small></div><div><span>02</span><b>☎️ Уточните наличие</b><small>Свяжитесь с магазином</small></div><div><span>03</span><b>✔️ Подтверждение</b><small>Сотрудник подтвердит товары</small></div><div><span>04</span><b>🛍️ Самовывоз</b><small>Заберите в удобное время</small></div></div><p class="how-disclaimer">Онлайн-оплата и отправка заявок в этой демонстрационной версии не подключены.</p></section>'''
 footer='''<footer class="site-foot" id="contacts"><div class="wrap"><div class="footgrid"><a href="/'''+q+'''" class="footer-brand">'''+logohtml+'''</a><div><b>📍 Наш адрес</b><p>'''+h(settings['address'])+'''</p></div><div><b>☎ Телефон</b><p><a href="'''+h(phone_link)+'''">'''+h(settings['contact'])+'''</a></p></div><div><b>◷ Режим работы</b><p>'''+h(settings['hours'])+'''</p></div>'''+social_buttons(settings,'foot')+'''</div><div class="foot-bottom"><span>© 2026 «ЕМЕЛЯ». Демонстрационный сайт, предложения не являются публичной офертой.</span><a href="/catalog'''+q+'''">Каталог</a><a href="#how">Как заказать</a><a href="/admin">Админка</a></div></div></footer>'''
 # Completely distinct information architecture for author's editorial template; same CMS data.
 if mode=='refined' and page=='home':
  picks=[seed['products'][i] for i in (3,6,1,10,7,0)]
  tiles=''.join('<figure><img src="'+h(p['image'])+'" alt="'+h(p['name'])+'" loading="lazy"><figcaption>'+h(p['name'])+'<small>Демонстрационное фото · цена в магазине</small></figcaption></figure>' for p in picks)
  editorial='<section class="refined-gallery"><div class="refined-kicker">СОБРАНО С ЗАБОТОЙ</div><h2>Вкусные привычки и уютные покупки</h2><p class="refined-intro">Настоящие продукты, которые приятно выбирать. Фотографии демонстрационные — свои товары, цены и остатки вы сможете указать в админке.</p><div class="refined-mosaic">'+tiles+'</div></section>'
  main=hero+benefits+editorial+categories+products+how
 elif mode=='author':
  main=hero+benefits+'<div class="author-shopping-layout">'+categories+products+'</div>'+how
 else:
  main=hero+benefits+categories+products+how
 return '''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>'''+h(name)+''' — всё нужное рядом</title><link rel="stylesheet" href="/site.css"><link rel="stylesheet" href="/premium.css"><link rel="stylesheet" href="/art_direction_v61.css"></head><body class="premium mode-'''+h(mode)+'''" style="'''+h(styles)+'''"><header class="mast"><div class="wrap mast-inner"><button id="mobile-toggle" class="mobile-toggle" aria-controls="main-menu" aria-expanded="false" aria-label="Открыть меню">☰</button><a class="brand" href="/'''+q+'''">'''+logohtml+'''</a><div class="top-search"><label for="search">⌕</label><input id="search" type="search" placeholder="Найти: хлеб, молоко, овощи…" aria-label="Поиск по товарам"></div><div class="top-contacts"><span>📍 '''+h(settings['address'])+'''</span><strong>☎ <a href="'''+h(phone_link)+'''">'''+h(settings['contact'])+'''</a></strong><span>◷ '''+h(settings['hours'])+'''</span></div>'''+social_buttons(settings,'head')+'''</div><nav class="menu" id="main-menu"><div class="wrap menu-inner"><a href="/catalog'''+q+'''">▦ Каталог</a><a href="/'''+q+'''">О магазине</a><a href="#how">Как заказать</a><a href="#contacts">Доставка и самовывоз</a><a href="#contacts">Контакты</a></div></nav></header><main class="wrap">'''+main+'''</main>'''+footer+'''<script>window.MODE='''+json.dumps(mode)+''';</script><script src="/site.js" defer></script></body></html>'''


_render_generic_page_v53 = render_generic_page
def render_generic_page(mode,page='home'):
 html=_render_generic_page_v53(mode,page)
 if CONF.get('content_demo'):
  seed=json.loads((BASE/'premium_seed.json').read_text(encoding='utf-8'))
  image='<img class="brand-logo" src="'+h(seed['logo'])+'" alt="Логотип магазина ЕМЕЛЯ">'
  html=html.replace('<small>ВСЁ НУЖНОЕ РЯДОМ</small>',image+'<small>ВСЁ НУЖНОЕ РЯДОМ</small>',1)
  html=html.replace('</nav></div></header>', '</nav>'+social_buttons(site_settings(),'head')+'</div></header>',1)
  html=html.replace('<div class="copyright">',social_buttons(site_settings(),'foot')+'<div class="copyright">',1)
 return html

def render_external_page(mode,page='home'):
 """Licensed Commerce CSS with first-party CMS. Never serve downloaded HTML/JS/checkout."""
 lay=layout_for(mode);p=lay['palette'];settings=site_settings();name=settings['store_name']
 q='?mode='+urllib.parse.quote(mode)
 style=';'.join('--'+k+':'+str(v) for k,v in p.items())
 logo="<span class='external-mark'>ЕМ</span>"
 image='<img class="external-facade" src="'+h(settings['banner'])+'" alt="Фасад магазина ЕМЕЛЯ целиком">' if settings.get('banner') else ''
 links=[]
 for key,label in (('telegram','Telegram'),('max','MAX')):
  val=settings.get(key,'')
  if val.startswith('https://'):
   links.append('<a class="external-social" rel="noopener noreferrer" target="_blank" href="'+h(val)+'">'+label+'</a>')
  else:links.append('<span class="external-social disabled" title="Укажите ссылку через админку">'+label+'</span>')
 socials=''.join(links)
 categories='<section class="section" id="category-section"><div class="external-heading"><span>Удобный выбор</span><h2>Категории товаров</h2></div><div class="categories" id="categories"></div></section>'
 products='<section class="section" id="product-section"><div class="external-heading"><span>Наш ассортимент</span><h2>Товары магазина</h2><small>Демонстрационные позиции: цену уточняйте</small></div>'+('' if page=='home' else '<div class="filters" id="filters"></div>')+'<div class="products" id="products"></div><button id="more" class="external-more" hidden>Показать ещё</button></section>'
 hero='<section class="hero external-hero"><div class="external-hero-copy"><span class="external-label">ВСЁ НУЖНОЕ РЯДОМ</span><h1>Продукты и товары для всей семьи</h1><p>Ваш магазин у дома: продукты питания, товары для быта и всё необходимое каждый день.</p><div class="external-actions"><a class="external-action" href="/catalog'+q+'">Открыть каталог</a><a class="external-outline" href="#contacts">Наши контакты</a></div></div><div class="external-hero-art">'+image+'</div></section>' if page=='home' else '<section class="external-cataloghead"><h1>Каталог товаров</h1><p>Выберите категорию или воспользуйтесь поиском.</p></section>'
 foot='<footer class="external-footer" id="contacts"><div class="wrap external-footgrid"><div><b>'+h(name)+'</b><p>Продукты и товары для всей семьи</p></div><div><b>Адрес</b><p>'+h(settings['address'])+'</p></div><div><b>Телефон</b><p>'+h(settings['contact'])+'</p></div><div><b>График</b><p>'+h(settings['hours'])+'</p></div><div><b>Сообщества</b><div class="external-socials">'+socials+'</div></div></div><div class="wrap external-copyright">Демонстрационная версия · Настоящие цены и наличие добавляются через админку · Онлайн-оплата не подключена</div></footer>'
 return f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>{h(name)} — каталог</title><link rel="stylesheet" href="/external/assets/vendor/bootstrap6/css/bootstrap.min.css"><link rel="stylesheet" href="/external/assets/css/base.css"><link rel="stylesheet" href="/external/assets/css/style.css"><link rel="stylesheet" href="/site.css"><link rel="stylesheet" href="/external_bridge.css"></head><body class="external-commerce mode-{h(mode)}" style="{h(style)}"><div class="announce">Магазин рядом · {h(settings['hours'])}</div><header class="site-header"><div class="wrap external-header"><a class="external-brand" href="/{q}">{logo}<span>{h(name)}</span></a><button class="mobile-toggle" id="mobile-toggle" aria-expanded="false" aria-controls="main-menu">☰ Меню</button><nav id="main-menu" class="menu"><a href="/{q}">Главная</a><a href="/catalog{q}">Каталог</a><a href="#contacts">Контакты</a></nav><div class="external-socials">{socials}</div></div></header><main class="wrap"><div class="external-kicker">📍 {h(settings['address'])} · ☎ {h(settings['contact'])}</div>{hero}<form class="search-line" role="search" onsubmit="event.preventDefault();document.getElementById('product-section').scrollIntoView()"><label class="visually-hidden" for="search">Поиск товара</label><input id="search" type="search" placeholder="Поиск товаров…" aria-label="Поиск по каталогу"><button type="submit">Найти</button></form>{categories}{products}<div class="external-note">Цены, наличие и фотографии настоящих товаров владелец настраивает в админке. Список покупок сохраняется только в вашем браузере.</div></main>{foot}<script>window.MODE={json.dumps(mode)};</script><script src="/site.js" defer></script></body></html>''' 

def render_page(mode,page='home'):
 lay=layout_for(mode);settings=site_settings()
 if CONF.get('external_theme')=='colorlib-commerce':return render_external_page(mode,page)
 if CONF.get('premium_demo'):
  return premium_page(mode,page,settings,lay)
 return render_generic_page(mode,page)

class Handler(BaseHTTPRequestHandler):
 server_version='EmelyaTemplateFirst/1.0'
 def log_message(self,fmt,*args): print('[site]',fmt%args)
 def send(self,code,payload,content_type='text/html; charset=utf-8',extra=None):
  if isinstance(payload,str):payload=payload.encode('utf-8')
  self.send_response(code);self.send_header('Content-Type',content_type);self.send_header('Content-Length',str(len(payload)))
  self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff')
  self.send_header('X-Frame-Options','DENY');self.send_header('Referrer-Policy','no-referrer')
  self.send_header('Content-Security-Policy',"default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; object-src 'none'; frame-ancestors 'none'")
  for k,v in (extra or {}).items():self.send_header(k,v)
  self.end_headers();self.wfile.write(payload)
 def js(self,code,obj,extra=None):self.send(code,json.dumps(obj,ensure_ascii=False), 'application/json; charset=utf-8',extra)
 def do_GET(self):
  url=urllib.parse.urlparse(self.path);path=url.path
  if path in ('/','/catalog'):
   mode=urllib.parse.parse_qs(url.query).get('mode',['faithful'])[0]
   if mode not in CONF['modes']:mode=CONF['modes'][0]
   return self.send(200,render_page(mode,'catalog' if path=='/catalog' else 'home'))
  if path=='/api/catalog':return self.js(200,snapshot())
  if path=='/admin':return self.file(BASE/'admin.html')
  if path=='/admin/session':
   s=is_logged(self)
   return self.js(200,{'csrf':s['csrf']}) if s else self.js(401,{'error':'Нужно войти'})
  if path=='/admin/data':
   if not is_logged(self):return self.js(401,{'error':'Доступ запрещён'})
   return self.js(200,snapshot())
  if path=='/admin/backup':
   if not is_logged(self):return self.js(401,{'error':'Доступ запрещён'})
   mem=io.BytesIO()
   with zipfile.ZipFile(mem,'w',zipfile.ZIP_DEFLATED) as z:
    with conn() as db:
     backup=io.BytesIO()
     tempdb=BASE/'data'/'backup_temp.sqlite'
     try:
      with sqlite3.connect(tempdb) as dest:db.backup(dest)
      z.write(tempdb,'catalog.sqlite')
     finally:tempdb.unlink(missing_ok=True)
    for p in MEDIA.glob('*'):
     if p.is_file() and p.suffix=='.webp':z.write(p,'media/'+p.name)
   return self.send(200,mem.getvalue(),'application/zip',{'Content-Disposition':'attachment; filename="catalog-backup.zip"'})
  if path=='/admin/export.csv':
   if not is_logged(self):return self.js(401,{'error':'Доступ запрещён'})
   out=io.StringIO();w=csv.writer(out,lineterminator='\r\n');w.writerow(['id','category_id','name','price_rub','stock','image'])
   for p in snapshot()['products']:
    row=[p['id'],p['category_id'],p['name'],p['price'] or '',p['stock'] if p['stock'] is not None else '',p['image']]
    w.writerow(["'"+str(v) if isinstance(v,str) and v.lstrip().startswith(('=','+','-','@')) else v for v in row])
   return self.send(200,'\ufeff'+out.getvalue(),'text/csv; charset=utf-8',{'Content-Disposition':'attachment; filename="catalog.csv"'})
  if path in ('/site.css','/site.js','/premium.css','/external_bridge.css','/art_direction_v61.css'):return self.file(BASE/path.lstrip('/'))
  if path in ('/external/assets/css/base.css','/external/assets/css/style.css','/external/assets/vendor/bootstrap6/css/bootstrap.min.css'):
   return self.file(BASE/path.lstrip('/'))
  if path.startswith('/media/'):
   name=path[len('/media/'):]
   if name and '/' not in name and name.endswith('.webp') and all(ch in '0123456789abcdef' for ch in name[:-5]):return self.file(MEDIA/name)
  return self.send(404,'Не найдено')
 def file(self,p):
  if not p.is_file():return self.send(404,'Файл не найден')
  typ=mimetypes.guess_type(str(p))[0] or 'application/octet-stream'
  return self.send(200,p.read_bytes(),typ)
 def do_POST(self):
  path=urllib.parse.urlparse(self.path).path
  try:
   size=int(self.headers.get('Content-Length','0'))
   if size<=0 or size>MAX_BODY:raise ValueError('Недопустимый размер запроса')
   if self.headers.get('Content-Type','').split(';')[0].strip()!='application/json':raise ValueError('Ожидается JSON')
   data=json.loads(self.rfile.read(size))
   if not isinstance(data,dict):raise ValueError('Нужен JSON-объект')
   if path=='/admin/login':return self.login(data)
   s=is_logged(self)
   if not s:return self.js(401,{'error':'Требуется вход'})
   if not hmac.compare_digest(self.headers.get('X-CSRF-Token',''),s['csrf']):return self.js(403,{'error':'CSRF: запрос отклонён'})
   if path=='/admin/logout':
    cookie=SimpleCookie();cookie.load(self.headers.get('Cookie',''))
    sid=cookie.get('em_sid')
    if sid:
     with LOCK:SESSIONS.pop(sid.value,None)
    return self.js(200,{'ok':True},{'Set-Cookie':'em_sid=; HttpOnly; SameSite=Strict; Max-Age=0; Path=/'})
   if path=='/admin/category/save':
    name=str(data.get('name','')).strip();icon=str(data.get('icon') or '▣').strip()[:4]
    if not 1<=len(name)<=65:raise ValueError('Название категории: 1–65 символов')
    id=secrets.token_hex(8)
    with conn() as db:db.execute('INSERT INTO categories(id,name,icon) VALUES (?,?,?)',(id,name,icon))
    return self.js(200,{'ok':True,'id':id})
   if path=='/admin/category/delete':
    id=str(data.get('id',''))
    with conn() as db:
     if not db.execute('SELECT 1 FROM categories WHERE id=?',(id,)).fetchone():raise ValueError('Нет такой категории')
     if db.execute('SELECT 1 FROM products WHERE category_id=? LIMIT 1',(id,)).fetchone():raise ValueError('Сначала перенесите или удалите товары этой категории')
     db.execute('DELETE FROM categories WHERE id=?',(id,))
    return self.js(200,{'ok':True})
   if path=='/admin/demo/clear':
    with conn() as db:
     removed=db.execute('DELETE FROM products WHERE demo=1').rowcount
    return self.js(200,{'ok':True,'removed':removed})
   if path=='/admin/catalog/import':return self.import_catalog(data)
   if path=='/admin/site/save':return self.save_site(data)
   if path=='/admin/product/save':return self.save_product(data)
   if path=='/admin/product/delete':
    id=str(data.get('id',''))
    with conn() as db:db.execute('DELETE FROM products WHERE id=?',(id,))
    return self.js(200,{'ok':True})
   return self.js(404,{'error':'Операция не найдена'})
  except (ValueError,TypeError,sqlite3.Error) as e:return self.js(400,{'error':str(e)[:240]})
  except Exception as e:
   print('internal:',repr(e));return self.js(500,{'error':'Внутренняя ошибка'})
 def login(self,data):
  key=self.client_address[0];now=time.time()
  with LOCK:
   fails=[x for x in FAILURES.get(key,[]) if now-x<300]
   if len(fails)>=7:return self.js(429,{'error':'Слишком много попыток. Повторите позднее.'})
  pwd=str(data.get('password',''))
  if len(pwd)>256:raise ValueError('Слишком длинный пароль')
  with conn() as db:stored=db.execute('SELECT value FROM settings WHERE key="password_hash"').fetchone()['value']
  salt,digest=stored.split(':');check=hashlib.pbkdf2_hmac('sha256',pwd.encode(),bytes.fromhex(salt),600_000)
  if not hmac.compare_digest(check.hex(),digest):
   with LOCK:FAILURES.setdefault(key,[]).append(now)
   return self.js(401,{'error':'Неверный пароль'})
  with LOCK:
   FAILURES.pop(key,None);sid=secrets.token_urlsafe(32);csrf=secrets.token_urlsafe(32);SESSIONS[sid]={'csrf':csrf,'expiry':now+8*3600}
  return self.js(200,{'ok':True,'csrf':csrf},{'Set-Cookie':f'em_sid={sid}; HttpOnly; SameSite=Strict; Max-Age=28800; Path=/'})
 def image_from_data(self,raw):
  if not isinstance(raw,str) or not raw.startswith('data:image/') or ',' not in raw:raise ValueError('Неверный формат фото')
  head,b64=raw.split(',',1)
  if head not in ('data:image/png;base64','data:image/jpeg;base64','data:image/webp;base64'):raise ValueError('Допускаются JPG PNG WEBP')
  try:content=base64.b64decode(b64,validate=True)
  except Exception:raise ValueError('Повреждённые данные изображения')
  if len(content)>5*1024*1024:raise ValueError('Фото больше 5 МБ')
  from PIL import Image,ImageOps
  Image.MAX_IMAGE_PIXELS=15_000_000
  try:
   im=Image.open(io.BytesIO(content));im.verify();im=Image.open(io.BytesIO(content))
   if im.width*im.height>15_000_000:raise ValueError('Фото слишком большое')
   im=ImageOps.exif_transpose(im).convert('RGB');im.thumbnail((1400,1400))
   dest=secrets.token_hex(20)+'.webp';im.save(MEDIA/dest,format='WEBP',quality=85)
  except (OSError,ValueError) as e:raise ValueError('Некорректное изображение: '+str(e)[:80])
  return '/media/'+dest
 def import_catalog(self,data):
  text=data.get('csv','')
  if not isinstance(text,str) or len(text.encode('utf8'))>1_000_000:raise ValueError('CSV не должен превышать 1 МБ')
  reader=csv.DictReader(io.StringIO(text.lstrip('\ufeff')))
  required={'category_id','name','price_rub','stock'}
  if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):raise ValueError('Ожидаются столбцы: id, category_id, name, price_rub, stock')
  from decimal import Decimal,InvalidOperation
  items=[]
  with conn() as db:
   valid={x[0] for x in db.execute('SELECT id FROM categories')}
  for index,row in enumerate(reader,1):
   if index>2000:raise ValueError('За одну загрузку не более 2000 строк')
   if None in row:raise ValueError('Лишние столбцы в строке '+str(index))
   cat=str(row.get('category_id') or '').strip()
   if cat not in valid:raise ValueError('Категория не найдена в строке '+str(index)+': '+cat)
   name=str(row.get('name') or '').strip()
   if name.startswith("'") and name[1:2] in ('=','+','-','@'):name=name[1:]
   if not 1<=len(name)<=120:raise ValueError('Название в строке '+str(index)+' вне допустимого диапазона')
   rawprice=str(row.get('price_rub') or '').replace(',','.').strip()
   cents=None
   if rawprice:
    try:
     v=Decimal(rawprice)
     if not v.is_finite() or v<0 or v>10_000_000 or v.as_tuple().exponent < -2:raise ValueError('Цена неверна')
     cents=int(v*100)
    except InvalidOperation:raise ValueError('Цена неверна в строке '+str(index))
   rawstock=str(row.get('stock') or '').strip()
   stock=None
   if rawstock:
    try:stock=int(rawstock)
    except ValueError:raise ValueError('Остаток неверен в строке '+str(index))
    if stock<0 or stock>100_000:raise ValueError('Остаток вне диапазона в строке '+str(index))
   pid=str(row.get('id') or '').strip() or secrets.token_hex(12)
   if len(pid)>64 or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.' for c in pid):raise ValueError('Некорректный ID в строке '+str(index))
   items.append((pid,cat,name,cents,stock))
  if len({v[0] for v in items})!=len(items):raise ValueError('Повторяющиеся ID в CSV')
  with conn() as db:
   for pid,cat,name,cents,stock in items:
    db.execute('INSERT INTO products(id,category_id,name,price_cents,stock,demo) VALUES(?,?,?,?,?,0) ON CONFLICT(id) DO UPDATE SET category_id=excluded.category_id,name=excluded.name,price_cents=excluded.price_cents,stock=excluded.stock,demo=0',(pid,cat,name,cents,stock))
  return self.js(200,{'ok':True,'imported':len(items)})
 def save_site(self,data):
  to_set={}
  for key,max_length in [('store_name',80),('description',160),('address',160),('hours',60),('contact',80)]:
   if key in data:
    val=str(data.get(key,'')).strip()
    if len(val)>max_length:raise ValueError(key+' слишком длинное')
    if key in ('store_name','description') and not val:raise ValueError(key+' не может быть пустым')
    to_set[key]=val
  # Social URLs editable in the protected admin panel, strict HTTPS + host allowlist.
  for key,allowed in [('telegram',('t.me','telegram.me')),('max',('max.ru',))]:
   if key in data:
    url=str(data[key] or '').strip()
    if len(url)>400:raise ValueError('Ссылка '+key+' слишком длинная')
    if url:
     parsed=urllib.parse.urlparse(url)
     if parsed.scheme!='https' or parsed.hostname not in allowed or parsed.username or parsed.password:
      raise ValueError('Недопустимая HTTPS-ссылка '+key)
    to_set[key]=url
  if data.get('banner'):to_set['banner']=self.image_from_data(data['banner'])
  with conn() as db:
   for key,value in to_set.items():db.execute('INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',(key,value))
  return self.js(200,{'ok':True,'site':site_settings()})
 def save_product(self,data):
  name=str(data.get('name','')).strip();cat=str(data.get('category_id',''));id=str(data.get('id') or secrets.token_hex(12))
  if not 1<=len(name)<=120:raise ValueError('Название товара: 1–120 символов')
  if not 1<=len(id)<=64:raise ValueError('Некорректный ID')
  price=data.get('price')
  if price is None or str(price).strip()=='': cents=None
  else:
   from decimal import Decimal, InvalidOperation
   try:
    v=Decimal(str(price).replace(',','.'))
    if not v.is_finite() or v<0 or v>10_000_000 or v.as_tuple().exponent < -2:raise ValueError('Неверная цена (2 знака после запятой)')
    cents=int(v*100)
   except InvalidOperation:raise ValueError('Неверная цена')
  stock=data.get('stock')
  if stock is None or str(stock).strip()=='':stock=None
  else:
   try:stock=int(str(stock))
   except ValueError:raise ValueError('Неверный остаток')
   if not (0<=stock<=100_000):raise ValueError('Остаток вне диапазона')
  with conn() as db:
   if not db.execute('SELECT 1 FROM categories WHERE id=?',(cat,)).fetchone():raise ValueError('Выберите категорию')
   row=db.execute('SELECT image FROM products WHERE id=?',(id,)).fetchone();photo=row['image'] if row else ''
   raw=data.get('image')
   if raw:photo=self.image_from_data(raw)
   db.execute('INSERT INTO products(id,category_id,name,price_cents,stock,image,demo) VALUES(?,?,?,?,?,?,0) ON CONFLICT(id) DO UPDATE SET category_id=excluded.category_id,name=excluded.name,price_cents=excluded.price_cents,stock=excluded.stock,image=excluded.image,demo=0',(id,cat,name,cents,stock,photo))
  return self.js(200,{'ok':True,'id':id})

if __name__=='__main__':
 init_db()
 host=os.environ.get('EMELYA_HOST','127.0.0.1');port=int(os.environ.get('EMELYA_PORT','8781'))
 if host not in ('127.0.0.1','localhost'):
  print('ВНИМАНИЕ: публичный HTTP НЕ проверен для размещения в интернете. Используйте локально или HTTPS reverse proxy после аудита.')
 print(f'Сайт: http://{host}:{port}/   Админка: http://{host}:{port}/admin')
 ThreadingHTTPServer((host,port),Handler).serve_forever()