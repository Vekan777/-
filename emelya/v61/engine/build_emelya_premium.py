"""Quality-first Emelya showcase. Rendered as 3 independently editable local sites."""
from __future__ import annotations
import json,sys,shutil,hashlib
from pathlib import Path
from template_engine import make_project,safe_zip,ROOT
from design_autopilot import install

def build(folder:Path,mode:str):
 folder=Path(folder)
 make_project(folder,'classic-blue','Магазин ЕМЕЛЯ',(mode,),True)
 conf=json.loads((folder/'project.json').read_text(encoding='utf-8'))
 conf.update({'premium_demo':True,'address':'ДНР, Тельмановский район, с. Степановка, ул. Дзержинского, д. 10','hours':'Ежедневно 08:00–19:00','contact':'+7 949 082-26-17','telegram':'','max':'https://max.ru/join/y6x7fAiFyjWoqe3c-cUHol9KFe4CTvadM1g21kmPjp8','description':'Продукты и товары для всей семьи'})
 (folder/'project.json').write_text(json.dumps(conf,ensure_ascii=False,indent=2),encoding='utf-8')
 shutil.copy2(ROOT/'templates'/'premium.css',folder/'premium.css')
 shutil.copy2(ROOT/'templates'/'art_direction_v61.css',folder/'art_direction_v61.css')
 shutil.copy2(ROOT/'ART_DIRECTION_RULES_V59.json',folder/'ART_DIRECTION_RULES_V59.json')
 shutil.copy2(ROOT/'APPROVED_ART_ASSETS_V60.json',folder/'APPROVED_ART_ASSETS_V60.json')
 install(folder,mode,ROOT)
 (folder/'APPROVED_DESIGNS_V59').mkdir(exist_ok=True)
 shutil.copy2(ROOT/'APPROVED_DESIGNS_V59'/f'{mode}_PC.png',folder/'APPROVED_DESIGNS_V59'/f'{mode}_PC.png')
 shutil.copy2(ROOT/'APPROVED_DESIGNS_V59'/f'{mode}_MOBILE.png',folder/'APPROVED_DESIGNS_V59'/f'{mode}_MOBILE.png')
 (folder/'APPROVED_DESIGNS_V61').mkdir(exist_ok=True)
 for d in ('PC','MOBILE'):shutil.copy2(ROOT/'APPROVED_DESIGNS_V61'/f'{mode}_{d}.png',folder/'APPROVED_DESIGNS_V61'/f'{mode}_{d}.png')
 shutil.copy2(ROOT/'engine'/'premium_seed.json',folder/'premium_seed.json')
 for src in (ROOT/'assets_source').glob('*.webp'):
  h=hashlib.sha256(src.read_bytes()).hexdigest();shutil.copy2(src,folder/'media'/(h+'.webp'))
 (folder/'README_САЙТ.txt').write_text('V61: 3 утверждённых визуальных эталона и работающих сайта. Запуск: ЗАПУСТИТЬ_САЙТ_WINDOWS.bat, затем http://127.0.0.1:8781 и /admin.\nТовары и иллюстрации примерные; цены и остатки вводит владелец. Кнопка MAX ведёт в группу; ссылку Telegram настройте в админке.\nНе публиковать без внешней проверки безопасности, HTTPS и данных магазина.\n',encoding='utf-8')
 return folder

def all_three(target):
 target=Path(target);target.mkdir(parents=True,exist_ok=True)
 out=[]
 for mode in ('faithful','refined','author'):
  folder=build(target/mode,mode)
  out.append(str(safe_zip(folder,target/('EMELYA_V61_'+mode+'_SITE.zip'))))
 return out
if __name__=='__main__':print('\n'.join(all_three(sys.argv[1] if len(sys.argv)>1 else ROOT/'outputs'/'premium')))