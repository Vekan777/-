# Solo Site Factory — перенос без потери исходников (27.10.2026)

**Внимание:** эта запись в GitHub содержит только контрольную информацию. Полный актуальный код находится в ZIP текущего чата. В следующий чат передавать сам **SOLO_FACTORY_TRANSFER_TO_NEW_CHAT_2026-10-27.zip**, а не одну ссылку GitHub.

## Полный комплект
- Перенос в один файл: `SOLO_FACTORY_TRANSFER_TO_NEW_CHAT_2026-10-27.zip` (3 533 935 байт; SHA256 `12c3dba5b25b33c4c9bb69c2798b1af5d2b604e96f8d5b5bc7e1b81c09f0b3f9`).
- Движок: `SOLO_SITE_FACTORY_HANDOFF_READY_ENGINE_2026-10-27.zip` (354 778 байт, 172 файла, SHA256 `6ae9403992b9132f0d2e2780c05685788dd581bd13a31f52b4cec8bcbf544911`).
- Отдельный сайт: `SOLO_VPN_SITE_UNCHANGED_HANDOFF_2026-10-27.zip` (2 016 314 байт, 91 файл, SHA256 `3531da41ae8f11ddb4748018cd4dcdac6714134ba0fe9f777000b815a514b95f`).
- Отдельные прежние настоящие скриншоты: `SOLO_VPN_PC_MOBILE_HANDOFF_2026-10-27.zip` (1 176 865 байт, SHA256 `298adb57272dedf5ecf7ff82718356e2dc3c6386957c09827d35edc721d49947`).

Внутри переносного комплекта: `artifacts/engine.zip`, `artifacts/site.zip`, `artifacts/screenshots.zip`, `MANIFEST.json`, `HANDOFF_STATE.json`, `ПЕРЕНОС_В_НОВЫЙ_ЧАТ.md`. Проверено обратное чтение и SHA256 всех трёх вложенных ZIP; экспорт не создаёт релиз коммерческого VPN.

## Что изменилось
Продолжена существующая `SOLO_SITE_FACTORY_OWNER_LABEL_QA_ENGINE_2026-10-27.zip`: сохранены все 165 предыдущих файлов, из них изменены лишь `factory.py` и `README_RU.md`. Добавлены `engine/handoff.py`, `tests/test_handoff.py`, `CREATE_HANDOFF_WINDOWS.bat`, `HANDOFF_TO_NEXT_CHAT_RU.md`, `PROJECT_HANDOFF_STATE.json`, `QA_RESULTS/HANDOFF_RELEASE_QA_2026_10_27.json` и `ENGINE_SOURCE_SHA256.json`.

В каждом дальнейшем выпуске обновлять состояние и упаковывать все три артефакта командой:
`py -3 factory.py make-handoff --engine-zip ENGINE.zip --site-zip SITE.zip --screenshots-zip SHOTS.zip --state PROJECT_HANDOFF_STATE.json --out TRANSFER.zip`
Потом `py -3 factory.py verify-handoff --zip TRANSFER.zip`.

## Тесты и ограничения
215 собранных тестов, **214 успешных, 1 пропущен**, 0 ошибок в завершённых раздельных запусках. Совместный длительный браузерный прогон превысил лимит, поэтому единый PASS не заявляется. На чистой распаковке нового ZIP ещё 13 целевых PASS. Реальный Windows 10 ноутбук и публичный HTTPS не проверялись. Независимая художественная точность на >=30 настоящих макетах не подтверждена. Первую секцию и точные маски персонажей надо ещё улучшать.

Пять исторических шкал, без повышения: статический сайт 100% (только локальный QA), визуал ПК 90% ручная, телефон 90% ручная, движок 90% прежний локальный чек-лист, коммерческий запуск VPN 49,5% старый расчёт/PRODUCTION_BLOCKED.

**Порядок пользователя:** СНАЧАЛА закончить движок Solo Site Factory, ПОТОМ отдельно Solo VPN. В каждом выпуске отдавать отдельные ZIP движка/сайта, настоящие скриншоты ПК/телефона и самодостаточный ZIP переноса в новый чат.