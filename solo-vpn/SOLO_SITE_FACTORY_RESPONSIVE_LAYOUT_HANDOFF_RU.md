# Solo Site Factory — адаптивная сетка и безопасные отступы (26.10.2026)

**Полный новый код** в чате: `SOLO_SITE_FACTORY_RESPONSIVE_LAYOUT_ENGINE.zip`, SHA256 `3f3d62473a8c9c5ec7a549df9b08364b671400bfceb2c662fbcd2cf5a970e3ec` (218387 байт, 83 файла). GitHub содержит ТОЛЬКО памятку, а не весь актуальный ZIP.

Движок независим от Solo VPN, основан на `SOLO_SITE_FACTORY_SAFE_AUTOFIX_ENGINE.zip`. Добавлены `engine/layout_optimizer.py`, CLI `design-grid-fix`, кнопка 7 в GUI, `CHECK_LAYOUT_GRID_WINDOWS.bat`, `RUN_LAYOUT_GRID_WINDOWS.bat`, `RESPONSIVE_LAYOUT_GUIDE_RU.md`, десять проверок `tests/test_layout_optimizer.py`.

Функция: только подтвержденные владельцем box_px, сгенерированный черновик, только малые изменения адаптивных паддингов, gap и пропорций grid. По умолчанию dry run без CSS записи; отдельный --apply с полным Chromium QA ПК и мобильного, HTML QA, геометрическим контролем и необязательным сравнением с растровым эталоном; откат при ухудшении, повторный автофикс блокируется без ручной приёмки. Генерацию произвольного профессионального дизайна не обещаем.

На **синтетическом** тестовом макете: сумма абсолютных отклонений x/y/width/height двух блоков 87.84px → 0px, Chromium 390/1440 PASS. Не является доказательством художественного сходства с Solo VPN. Условия провала, в том числе регрессия визуального сравнения, покрыты тестами.

Тесты проверены **тремя отдельными наборами**: 99 passed/1 skipped в прежнем модуле, 9 passed в прежнем autofix, 10 passed в новом optimizer = 118 passed/1 skipped. Единый последовательный запуск всех тестов в этой среде упёрся в лимит времени; не объявлять его пройденным. Из ЧИСТОГО распакованного ZIP: doctor core_ready true; новый набор 10/10 PASS; verify_delivery ZIP PASS (3 публичных файла). Физический Windows 10 не проверен.

Артефакты чата: `SOLO_FACTORY_RESPONSIVE_DEMO_WEBSITE.zip`, `SOLO_FACTORY_RESPONSIVE_DEMO_WITH_GUIDE.zip`, `SOLO_FACTORY_RESPONSIVE_LAYOUT_SCREENSHOTS_QA.zip`, `SOLO_FACTORY_RESPONSIVE_LAYOUT_BEFORE_AFTER.jpg`, `SOLO_VPN_SITE_SEPARATE_UNCHANGED.zip`, `SOLO_VPN_CURRENT_PC_MOBILE_SCREENSHOTS.jpg`, `SOLO_FACTORY_RESPONSIVE_RELEASE_REPORT.json`, `SOLO_FACTORY_RESPONSIVE_RELEASE_SHA256.json`.

Solo VPN сохранён побайтно неизменным: 91 файл, исходный ZIP SHA256 `3531da41ae8f11ddb4748018cd4dcdac6714134ba0fe9f777000b815a514b95f`. Пять **исторических, не пересчитанных** показателей: сайт 100% по узкому локальному QA, художественный ПК 90% ручной, мобильный 90% ручной, фабрика 90% узкий локальный чек-лист, коммерческий VPN 49.5%, запуск заблокирован.

Продолжать только из полноценного ZIP нового движка, не запускать новые V-номера без необходимости. Основные барьеры: настоящая Windows-приёмка, точное выделение смысла/графики по разнообразным макетам, живой HTTPS E2E и реальные источники лицензированного медиа. После этого отдельное завершение Solo VPN.
