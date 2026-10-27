# Solo Site Factory — AI Quality Decision / Stop Loop, 27.10.2026

**Полный код в переносном архиве ChatGPT, НЕ в этой GitHub-ветке:** `SOLO_FACTORY_AI_QUALITY_DECISION_TRANSFER_TO_NEW_CHAT_2026-10-27.zip`. Внутри: `artifacts/engine.zip`, `artifacts/site.zip`, `artifacts/screenshots.zip`, `MANIFEST.json`, `HANDOFF_STATE.json`, инструкция. Обратная проверка SHA256 прошла. Запрещено восстанавливать актуальные исходники из старых сообщений или предполагать путь ZIP без нового вложения.

## Файлы
- Полный движок `SOLO_SITE_FACTORY_AI_QUALITY_DECISION_ENGINE_2026-10-27.zip`; SHA256 `bff741ec517b83091e29d415a6999bf20e7acce13ad515bd5e83cfa0ccd7c738`; 237 файлов.
- Отдельный неизменённый Solo VPN `SOLO_VPN_SITE_UNCHANGED_AI_DECISION_2026-10-27.zip`; SHA256 `3531da41ae8f11ddb4748018cd4dcdac6714134ba0fe9f777000b815a514b95f`; 91 файл, сайт не редактировался.
- ПК/телефон и отчёт `SOLO_FACTORY_AI_QUALITY_DECISION_SCREENSHOTS_2026-10-27.zip`; SHA256 `35764ba3cd774b11f7f1e80e21f0c59291bf04f606a97175fbf652d6bc883cf9`.
- Демонстрационные QA-материалы `SOLO_FACTORY_AI_QUALITY_DECISION_EVIDENCE_2026-10-27.zip`; SHA256 `4982add0778e805cb91e5af78f38f46d29d3d9086f3570657aa93491c5429ec7`.
- Единый перенос `SOLO_FACTORY_AI_QUALITY_DECISION_TRANSFER_TO_NEW_CHAT_2026-10-27.zip`; SHA256 `e4293a8113f7da2d5eaf963223d22de1fba40b6e76b740f1913f843664715912`.

## Реальное изменение
Продолжение от полного `SOLO_SITE_FACTORY_UNIFIED_QUALITY_ENGINE_2026-10-27.zip`. Добавлен `engine/quality_decision.py`, команда `factory.py design-decision --candidate name=REGION_FIDELITY_QA.json --out reports/decision`, `RUN_DESIGN_DECISION_WINDOWS.bat`, 12 тестов `tests/test_quality_decision.py`, `DESIGN_DECISION_GUIDE_RU.md`.

Модуль сравнивает до 4 независимых черновиков по уже проверенным отчётам `region_fidelity`. Для всех требует одну и ту же пару исходных SHA256 (эталон ПК+телефон и исходный HTML). Отдельно оценивает три owner-confirmed роли: hero_text, hero_media, first_section на обоих экранах. Цвет и контуры не должны регрессировать более 0,25 п.п. хотя бы в одной из шести областей; средний технический прирост для выбора ≥0,5 п.п. При отсутствии подходящего кандидата `STOP_NO_PROVEN_IMPROVEMENT`, CLI exit 2. Вариант с опасной регрессией отклоняется даже если общий балл увеличился. Ничего не перезаписывается в публичном сайте, автоматической публикации нет. HTML-панель для владельца проверена на ПК и телефоне (mobile overflow=0).

**Проверено**: полный свежий локальный pytest: `308 passed, 1 skipped, 0 failed`; код 0. После распаковки ZIP в чистую папку: 12/12 новых тестов и doctor.core_ready=true. Демонстрация приняла улучшенный синтетический вариант и отклонила сломанную иллюстрацию; CLI успешный путь код 0, blocked путь код 2. Это не профессиональная копия художественного макета и не показатель «200% лучше». Скриншоты Solo VPN — реальные прежние, сайт не изменён.

Пять исторических показателей без искусственного роста: локальный статический сайт 100% (ограниченный QA), визуал ПК 90% и телефона 90% (ручные оценки), движок 90% (историческая локальная оценка), коммерческий VPN 49,5% и PRODUCTION_BLOCKED.

**Открыто:** Windows 10 нативное тестирование на ПК владельца, публичный HTTPS, 30+ разнообразных независимых художественно размеченных макетов, оригинальная иллюстрация/слои и права. Сначала завершать движок, затем Solo VPN. В каждом выпуске — отдельные движок/site/screenshot ZIP и полностью самодостаточный ZIP переноса. Не плодить новые номера версий без проверки критериев.
