# Solo Site Factory — пакет точной работы по макетам, 25 октября 2026

Это документ передачи; **полные исходники НЕ сохранены в этой старой ветке GitHub**, а находятся в скачиваемом архиве `SOLO_SITE_FACTORY_DESIGN_PRECISION_ENGINE.zip` текущего чата.
SHA256 архива: `c6dd2dd1f9a00d87c5a6fb910ffb474bb6e5b775f1f2a673d77c23c29436757b`.
Основа: `SOLO_SITE_FACTORY_ENGINE_ACCEPTANCE_2026-10-25.zip`. Движок отдельный от Solo VPN, без возобновления бесконечной линейки V.

Сделано:
- `engine/design_to_site.py`: офлайн-анализ ПК+мобильного макетов, исходные пиксельные размеры, оценка палитры/областей, нормализация полей к CSS-вьюпортам, редактируемый BLUEPRINT.json, изображения направляющих. Автоматическая семантическая HTML/CSS/JS сборка в режимах faithful/enhanced, безопасные CSS токены, reduced motion, мобильная навигация и noindex.
- `engine/layout_precision.py`: разметка box_px, owner confirmation gate, Chromium computed layout coordinates, отклонения в пикселях, наложение жёлтого эталонного и бирюзового фактического прямоугольников. Неподтверждённая разметка возвращает all_verified=false.
- `annotate_layout.py`: ручная корректировка рамок по изображению с явным подтверждением.
- `engine/design_assets.py`: вставка собственного hero-изображения после подтверждения прав, WebP и запись SHA256 происхождения. Не вставляет весь скриншот макета как картинку сайта.
- CLI: design-plan, design-build, design-annotations, design-verify, design-hero; новые кнопки в существующем Tkinter Studio; старый from-design сохранён.
- Production gate блокирует проект при visual_reference_status=UNVERIFIED и rights_confirmed=false.

Реально проверено: 77 passed, 1 skipped после распаковки ZIP в чистую папку; Linux doctor core_ready=true и Tkinter Xvfb GUI smoke PASS; новый сайт создался и собрал независимые verified ZIP; 390/1440 Chromium offline without overflow/JS failures; два реальных approved reference screenshot Solo VPN проверены сканером. DEMO_Preview отличается от оригинального рисунка: точная стилизация и персонаж НЕ восстановлены, художественное совпадение НЕ подтверждено.

Файлы в чате: `SOLO_SITE_FACTORY_DESIGN_PRECISION_ENGINE.zip`, `SOLO_FACTORY_DESIGN_DEMO_WEBSITE.zip`, `SOLO_FACTORY_DESIGN_DEMO_DELIVERY.zip`, `SOLO_FACTORY_DESIGN_PRECISION_EVIDENCE.zip` и отдельный неизменённый `SOLO_VPN_SITE_UNCHANGED_2026-10-25.zip`. Снимки собственно сайта Solo VPN от предыдущей проверки, в этой итерации сайт не изменялся. Обязательно давать разные ссылки на движок/сайт и ПК/мобильные изображения.

Готовность — без необоснованного роста: Solo VPN локальный сайт 100% в пределах тестов, визуал ПК и телефона по 90% как исторические ручные оценки, движок локальный чек-лист 90% (Windows пользователя ещё не проверялся), коммерческий запуск VPN исторически 49,5%, PRODUCTION_BLOCKED. Новый генератор по макетам: **художественная точность не измерена/не одобрена**. Цель «200% лучше» качественная, не сертифицируемый числовой KPI.

Для следующих исправлений взять полный движок ZIP, а не переписывать программу с нуля. Следующие реальные барьеры: подтвердить Windows 10 GUI, вручную размеченные семантические области и точность изображений на эталоне; живую загрузку лицензированных материалов, HTTPS E2E. Затем возвращаться к Solo VPN, сохраняя отдельный сайт и движок.
