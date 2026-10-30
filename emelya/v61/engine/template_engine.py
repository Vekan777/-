"""Offline, original layout-based website generator. Python 3.10+; stdlib only for builds."""
from __future__ import annotations
import argparse, hashlib, json, re, shutil, sys, zipfile
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parent.parent
FAMILIES={
 'classic':('Классический магазин','Слева текст, справа изображение, категории ниже','split'),
 'searchbar':('Каталог с поиском','Крупная строка поиска и плотная сетка','dense'),
 'split':('Витрина-половинки','Две равные рекламные области','split'),
 'editorial':('Журнал-магазин','Выразительные заголовки и карточки','editorial'),
 'warehouse':('Оптовый каталог','Компактная лента и акцент на товарах','dense'),
 'tiles':('Плиточная витрина','Мозаика категорий с крупными изображениями','mosaic'),
 'sidebar':('Каталог с меню','Левая колонка разделов и каталог справа','sidebar'),
 'minimal':('Чистая витрина','Воздушная типографика и минимум деталей','minimal'),
 'market':('Семейный маркет','Фото на всю ширину, ниже промо и товары','visual'),
 'compact':('Быстрые покупки','Узкий баннер и плотная сетка товаров','dense'),
 'banner':('Большая акция','Широкий баннер и категории под ним','promo'),
 'boutique':('Акцент на товарах','Асимметричная витрина и крупные карточки','editorial'),
 'panorama':('Панорамная витрина','Снимок фасада целиком и большой каталог','visual'),
 'neighborhood':('Магазин у дома','Контакты и быстрые покупки на первом экране','local'),
 'gallery':('Товары крупным планом','Укрупнённые изображения и акцент на категориях','photos'),
 'district':('Районный маркет','Слева инфоблок, справа большая фотография','local'),
}
SKINS={
 'blue':('Сине-белый', '#245cbd','#eaf2ff','#ffffff','#183054','#f2aa30'),
 'fresh':('Зелёный', '#277458','#eaf7ee','#ffffff','#193d31','#e5a35d'),
 'warm':('Тёплый', '#9a492b','#fff0e3','#fffefb','#462d25','#e8a35b'),
 'night':('Тёмный', '#a6cdfd','#162536','#172b42','#f1f5fb','#ffbf69'),
 'violet':('Фиолетовый', '#6658a6','#f2eefb','#ffffff','#373051','#ffc076'),
 'sand':('Песочный', '#55716a','#f5f0e7','#fffdf9','#333f3d','#c9914a'),
}
RANKING_TAGS={
 'classic':['shop','grocery','hero','logo','header','cards','store'],
 'searchbar':['grocery','shop','search','products','market'],
 'split':['store','hero','promo','shop'],
 'editorial':['fashion','brand','editorial','magazine'],
 'warehouse':['catalog','products','wholesale','filters'],
 'tiles':['categories','images','grid','mosaic'],
 'sidebar':['categories','filters','catalog','sidebar'],
 'minimal':['clean','minimal','premium','typography'],
 'market':['shop','grocery','storefront','photo','market'],
 'compact':['grocery','products','small','dense','catalog'],
 'banner':['hero','wide','shop','sale','categories'],
 'boutique':['photos','products','asymmetric','cards'],
 'panorama':['photo','storefront','full','wide','shop'],
 'neighborhood':['grocery','contacts','local','shop','products'],
 'gallery':['categories','image','cards','photos'],
 'district':['local','shop','photo','info','contacts'],
}

def external_ready():
 try:
  from external_templates import is_installed
  return is_installed()
 except ImportError:return False

def registry():
 own = [{'id':f'{family}-{skin}','family':family,'skin':skin,'title':f'{FAMILIES[family][0]} · {SKINS[skin][0]}',
          'description':FAMILIES[family][1],'tags':RANKING_TAGS[family],'license':'ORIGINAL: owned by generated project; no third-party template code'}
         for family in FAMILIES for skin in SKINS]
 if external_ready():
  own += [{'id':f'colorlib-commerce-{skin}','family':'external-commerce','skin':skin,'title':f'Colorlib Commerce MIT · {SKINS[skin][0]}','description':'Оригинальная CSS-основа Bootstrap 6 alpha + каталог ЕМЕЛЯ','tags':['external','MIT','commerce','grocery','catalog'],'license':'ColorlibHQ/bootstrap-templates MIT; images from store only'} for skin in ('blue','fresh','warm')]
 return own

def parse_id(value):
 for item in registry():
  if item['id']==value: return item
 raise ValueError('Unknown preset: '+str(value))

def metadata(template_id,mode,brand):
 item=parse_id(template_id)
 family=item['family']; skin=item['skin']
 if family=='external-commerce':family='classic'
 if mode=='author': family='gallery' if family not in ('gallery','district') else family
 palette=SKINS[skin]
 return {'id':template_id,'family':family,'skin':skin,'mode':mode,'title':item['title'], 'brand':brand, 'external_theme':'colorlib-commerce' if template_id.startswith('colorlib-commerce-') else '',
         'palette':{'accent':palette[1],'subtle':palette[2],'paper':palette[3],'ink':palette[4],'warm':palette[5]}}

def make_project(out,template_id='classic-blue',brand='Магазин ЕМЕЛЯ',modes=('faithful','refined','author'),demo=True):
 out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
 src=ROOT/'engine'/'site_runtime.py'
 shutil.copy2(src,out/'server.py')
 shutil.copy2(ROOT/'templates'/'site.css',out/'site.css')
 shutil.copy2(ROOT/'templates'/'site.js',out/'site.js')
 shutil.copy2(ROOT/'templates'/'admin.html',out/'admin.html')
 if config_external:=template_id.startswith('colorlib-commerce-'):
  from external_templates import INSTALLED,is_installed
  if not is_installed():raise ValueError('Colorlib Commerce не установлен: запустите УСТАНОВИТЬ_COLORLIB_COMMERCE_WINDOWS.bat')
  target=out/'external';target.mkdir(exist_ok=True)
  for name in ('assets/css/base.css','assets/css/style.css','assets/vendor/bootstrap6/css/bootstrap.min.css','LICENSE','manifest.json'):
   src=INSTALLED/name; dst=target/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
  shutil.copy2(ROOT/'templates'/'external_bridge.css',out/'external_bridge.css')
 (out/'media').mkdir(exist_ok=True)
 config={'schema':1,'store_name':brand,'template_id':template_id,'modes':list(modes),'demo':demo,
         'description':'Продукты и товары для всей семьи','contact':'','address':'Адрес магазина — заполнить в админке',
         'hours':'08:00–19:00','telegram':'','max':'', 'external_theme':'colorlib-commerce' if template_id.startswith('colorlib-commerce-') else ''}
 if 'емеля' in brand.casefold():
  config.update({'content_demo':True,'contact':'+7 949 082-26-17','address':'ДНР, Тельмановский район, с. Степановка, ул. Дзержинского, д. 10',
                 'hours':'Ежедневно 08:00–19:00','max':'https://max.ru/join/y6x7fAiFyjWoqe3c-cUHol9KFe4CTvadM1g21kmPjp8'})
  from hashlib import sha256
  shutil.copy2(ROOT/'engine'/'premium_seed.json',out/'premium_seed.json')
  for asset in (ROOT/'assets_source').glob('*.webp'):
   shutil.copy2(asset,out/'media'/(sha256(asset.read_bytes()).hexdigest()+'.webp'))
 (out/'project.json').write_text(json.dumps(config,ensure_ascii=False,indent=2),encoding='utf-8')
 for mode in modes:
  info=metadata(template_id,mode,brand)
  (out/f'layout_{mode}.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
 (out/'ЗАПУСТИТЬ_САЙТ_WINDOWS.bat').write_text('@echo off\ncd /d "%~dp0"\npy -3 server.py\nif errorlevel 1 python server.py\npause\n',encoding='utf-8')
 (out/'README.txt').write_text('Запустите ЗАПУСТИТЬ_САЙТ_WINDOWS.bat. Откройте http://127.0.0.1:8781 . '
   'Пароль админа генерируется при первом запуске и хранится в ADMIN_FIRST_LOGIN.txt (не выкладывать в интернет!). '
   'Админка: /admin; разные дизайны: /?mode=faithful, /?mode=refined, /?mode=author. '
   'Никаких реальных заказов и платежей — требуется серверный запуск и внешняя проверка перед публикацией.\n',encoding='utf-8')
 return out

def safe_zip(folder,destination):
 folder=Path(folder); destination=Path(destination);destination.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
  for p in sorted(folder.rglob('*')):
   if p.is_file() and not p.name.startswith('ADMIN_FIRST_LOGIN') and 'catalog.sqlite' not in p.name:
    z.write(p,p.relative_to(folder))
 with zipfile.ZipFile(destination) as z:
  if z.testzip():raise ValueError('bad zip')
 return destination

def build_three(out,template_id='classic-blue',brand='Магазин ЕМЕЛЯ'):
 target=Path(out);target.mkdir(parents=True,exist_ok=True)
 produced=[]
 for mode in ['faithful','refined','author']:
  p=make_project(target/mode,template_id,brand,(mode,))
  produced.append(str(safe_zip(p,target/f'SITE_{mode}.zip')))
 return produced

def main():
 parser=argparse.ArgumentParser(description='ЕМЕЛЯ Template-First. 96 local original presets, 3 export modes.')
 sub=parser.add_subparsers(dest='command',required=True)
 sub.add_parser('list')
 p=sub.add_parser('build');p.add_argument('--template',default='classic-blue');p.add_argument('--brand',default='Магазин ЕМЕЛЯ');p.add_argument('--out',default=str(ROOT/'outputs'/'example'))
 p=sub.add_parser('three');p.add_argument('--template',default='classic-blue');p.add_argument('--brand',default='Магазин ЕМЕЛЯ');p.add_argument('--out',default=str(ROOT/'outputs'/'three'))
 p=sub.add_parser('match');p.add_argument('--reference',required=True);p.add_argument('--top',type=int,default=8)
 a=parser.parse_args()
 if a.command=='list':print(json.dumps(registry(),ensure_ascii=False,indent=2))
 elif a.command=='build':print(make_project(a.out,a.template,a.brand))
 elif a.command=='three':print('\n'.join(build_three(a.out,a.template,a.brand)))
 elif a.command=='match':
  from screenshot_matcher import match
  print(json.dumps(match(a.reference,a.top),ensure_ascii=False,indent=2))

if __name__=='__main__':main()