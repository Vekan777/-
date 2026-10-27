# Solo Site Factory — AI Autopilot (27 октября 2026)

## Важно: что хранится где
Эта запись GitHub содержит **проверяемую документацию**, но НЕ полный бинарный ZIP. Для переноса в новый чат скачайте файл **SOLO_FACTORY_AI_TRANSFER_TO_NEW_CHAT_2026-10-27.zip** из диалога: его состав верифицирован, он содержит полный код движка, отдельный сайт и скриншоты. Не восстанавливать код из старой ветки GitHub.

## Проверенные файлы и контрольные суммы
- Полный движок `SOLO_SITE_FACTORY_AI_AUTOPILOT_ENGINE_2026-10-27.zip`, 177 файлов, SHA256 `abf5659d93ad680a2930988199c6ef5a77c9ced4c99cd814ce9a19fad6a45117`.
- Отдельный статический Solo VPN `SOLO_VPN_SITE_UNCHANGED_AI_2026-10-27.zip`, 91 файл, SHA256 `3531da41ae8f11ddb4748018cd4dcdac6714134ba0fe9f777000b815a514b95f` — **НЕ изменялся**.
- Скриншоты AI-демо, Solo VPN и GUI `SOLO_FACTORY_AI_PC_MOBILE_SCREENSHOTS.zip` — настоящие Chromium и Linux Xvfb кадры.
- Единый ZIP передачи `SOLO_FACTORY_AI_TRANSFER_TO_NEW_CHAT_2026-10-27.zip`, SHA256 `caf7ce8e989efbc378870ca89465891de3228b86dd49e62f41df10e5f3b81cff`, 6 элементов: artifacts/{engine,site,screenshots}.zip, MANIFEST.json, HANDOFF_STATE.json, инструкция. `verify_handoff(...)` PASS.

## AI Autopilot
На основе прежнего Portable Handoff сохранили все 172 пути. Добавлено `engine/ai_autopilot.py`, `tests/test_ai_autopilot.py`, `RUN_AI_AUTOPILOT_WINDOWS.bat`, `README_AI_AUTOPILOT_RU.md`, `QA_RESULTS/AI_AUTOPILOT_FULL_REGRESSION.json`; factory.py и gui.py дополнены новыми командами и вкладкой №5.

Режим 1 **offline** — только детерминированные правила и существующие функции, НЕ нейросеть. Режим 2 **cloud** — OpenAI Responses API лишь для рекомендаций к плану, с двумя отдельными согласиями (сеть и платный API), переменными OPENAI_API_KEY/SOLO_FACTORY_AI_MODEL; реальные внешние вызовы НЕ выполнены. Модель не запускает произвольный код. JSON план с SHA256, режим без записи по умолчанию, явное --approve-write, проверка SHA сайта до выполнения, запрет перезаписи старого проекта, блокировка импортированных сайтов и опасных действий, максимум 2 прохода разрешённого исправления. Не выдаёт релиз за коммерчески готовый.

Реальный автономный локальный сценарий: текстовое задание мастерской -> короткий заголовок -> HTML/CSS/JS+SVG+доступная анимация -> Chromium, QA, HTTP -> отдельные проверенные PUBLIC_WEBROOT/DELIVERY ZIP. Статус `PREVIEW_ZIPS_READY_MANUAL_APPROVAL_REQUIRED`. Это демо, не профессиональный коммерческий сайт.

## QA и открытые блокеры
Свежий полный регрессионный тест **27/27 модулей PASS, 231 passed, 1 skipped, 0 failed, 0 timeout**, отдельные модули без повторного использования результатов. Из чистой распаковки нового ZIP: 22/22 целевых теста, doctor core_ready=true и Linux Tkinter GUI smoke PASS, CLI-создание плана без записи PASS, ZIP CRC PASS. Реальный Windows 10, живой облачный API и HTTPS не проверены.

Исторические пять шкал без повышения: сайт Solo VPN локально 100% по ограниченному QA; визуал ПК 90% и телефона 90% ручные; движок 90% по старому локальному чек-листу; коммерческий VPN 49,5%, PRODUCTION_BLOCKED. Новые тесты не равны 100% универсальной автономности.

## Строгий порядок дальнейшей работы
1. Выполнить `RUN_AI_AUTOPILOT_WINDOWS.bat`, `RUN_NATIVE_WINDOWS_ACCEPTANCE.bat` на физическом Windows 10 владельца.
2. Проверить живой HTTPS тестового сайта; никаких выдуманных серверов, платежей, Android APK.
3. Отдельно подтвердить художественное соответствие и независимый набор >=30 реальных размеченных макетов, 10 holdout; улучшить сложные первые секции и иллюстрации.
4. Только после закрытия этих ограничений вернуться к независимому Solo VPN без перестройки сайта.
5. В каждом дальнейшем выпуске отдельные движок/site/screenshot ZIP и обновлённый self-contained handoff. Не плодить вечные V-номера.
