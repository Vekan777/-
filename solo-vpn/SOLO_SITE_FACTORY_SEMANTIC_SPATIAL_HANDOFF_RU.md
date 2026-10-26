# Solo Site Factory — проверяемая карта текстовых и графических областей (26.10.2026)

Полный код движка находится в текущем чате в SOLO_SITE_FACTORY_SEMANTIC_SPATIAL_ENGINE.zip, SHA256 2f64b1cd5c40cb9fa98719cd417d42008617e694f8d43de486e0631758aab405, 112 файлов. Эта ветка GitHub содержит только памятку, не актуальный полный ZIP.

Основа — настоящий архив SOLO_SITE_FACTORY_REFERENCE_STRUCTURE_ENGINE.zip. Добавлены engine/spatial_layout.py, tests/test_spatial_layout.py, GUI кнопки 9/10, CLI design-spatial-template и design-spatial-apply, SEMANTIC_SPATIAL_GUIDE_RU.md, RUN_SEMANTIC_SPATIAL_WINDOWS.bat, полный журнал QA.

Текст, изображения и первая секция описаны ролями hero_text, hero_media, first_section по физическим координатам на каждом исходном макете (desktop/mobile). Роли не распознаются автоматически достоверно и требуют корректировки + confirmed_by_owner=true. SHA256 источника и размеры защищают от применения разметки к другому файлу. Неправильные координаты, наложения, дублирующиеся/неизвестные роли отвергаются. Только тогда строятся ограниченные CSS сетки и порядки элементов. Исходный BLUEPRINT.json не перезаписывается; сгенерированный сайт остаётся PREVIEW_ONLY.

Синтетический тестовый макет: art слева на ПК и выше текста на мобильном; показаны реальные Chromium скриншоты reference/before/after. Raster proxy PC 87.67→88.79, mobile 85.24→86.18; edge proxy PC УХУДШИЛСЯ 27.37→22.44, mobile 23.71→23.97. Поэтому художественное качество НЕ утверждено и никакие «200% лучше» не достигнуты. Семь ширин браузера прошли до и после. Demo public webroot/delivery архивы проверены, локальный HTTP 3/3.

Полная новая регрессия выполнена одним запуском: 164 passed, 1 skipped, 0 failed за 180.22 сек. Пропуск — дополнительный прежний тест старого полного архива V46 без локально ожидаемого файла. Из чистой распаковки ZIP ещё 16/16 целевых passed; doctor.core_ready=true. Это Linux проверка, не Windows пользователя.

Отдельный сайт Solo VPN побайтно не изменялся: SOLO_VPN_SITE_SEPARATE_REFERENCE_STRUCTURE.zip, 91 файл, SHA256 3531da41ae8f11ddb4748018cd4dcdac6714134ba0fe9f777000b815a514b95f. Снимки прежнего сайта SOLO_VPN_REFERENCE_STRUCTURE_SCREENSHOTS.zip, не новая сборка дизайна.

Отдельные файлы текущей поставки: SOLO_FACTORY_SPATIAL_EXPORTS/after-PUBLIC_WEBROOT.zip и after-DELIVERY.zip (с инструкцией Windows и Cloudflare/Netlify/Caddy), SOLO_FACTORY_SPATIAL_LAYOUT_SCREENSHOTS_QA.zip, SOLO_FACTORY_SPATIAL_PC_MOBILE_COMPARISON.jpg, SOLO_FACTORY_SPATIAL_RELEASE_REPORT.json и SOLO_FACTORY_SPATIAL_RELEASE_SHA256.json.

Пять прежних шкал: Solo VPN локально 100% в узком файловом QA, визуал ПК 90% и мобильный 90% — исторические ручные, движок 90% — прежняя локальная оценка, коммерческий VPN 49.5% — исторический расчёт PRODUCTION_BLOCKED. Не повышать без независимых подтверждений.

Следующая задача: semantic computer vision / OCR для точного выделения областей с независимым тестовым набором и gate по геометрии/контурам, полноценная приёмка Windows 10 владельца, интернет-лицензии и HTTPS E2E; только затем доводить отдельный Solo VPN.