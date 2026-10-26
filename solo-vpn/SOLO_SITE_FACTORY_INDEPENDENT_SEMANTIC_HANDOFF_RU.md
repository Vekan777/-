# Solo Site Factory — независимая проверка смысловых областей (26.10.2026)

**ВАЖНО:** полный обновлённый код находится в ZIP `SOLO_SITE_FACTORY_INDEPENDENT_SEMANTIC_ENGINE.zip` из чата ChatGPT, а не в устаревшей ветке GitHub. Архив: 151 файл, 312153 байт, SHA256 `554fab09d05c38cf8eaa081ba8f409398b2c7bce08650f7836caf9536af42868`. Движок развивает последний полный `SOLO_SITE_FACTORY_SEMANTIC_REVIEW_ENGINE.zip` без потери старых функций.

## Новый функционал

`engine/semantic_benchmark.py`: независимый read-only аудит фиксированной разметки по box IoU, Recall@0.5, отдельно development и holdout, PNG-рамки, SHA256 контроль источников. `benchmarks/labeled_mockups`: 12 синтетических изображений шести стилей (ПК и телефон) + `annotations.json` с заранее записанными координатами; генератор эталонов не импортирует детектор. `engine/semantic_suggestions.py`: более точный осторожный поиск широких цветовых секций под hero. Никакая авторазметка не переводится в approved без владельца. Новая CLI-команда `semantic-benchmark`, кнопка №12 в Tkinter Studio, `RUN_SEMANTIC_BENCHMARK_WINDOWS.bat`.

Дополнительные инструменты: `engine/windows_acceptance.py` и `RUN_NATIVE_WINDOWS_ACCEPTANCE.bat` — нативная проверка Tkinter, 7 ширин Chromium, QA, HTTP и полный pytest на Windows; при запуске на Linux возвращает BLOCKED. `engine/hosting_audit.py` и `LIVE_HTTPS_AUDIT_WINDOWS.bat` — проверка живого общедоступного HTTPS-домена без отключения TLS, публичного DNS, основных страниц, заголовков и SHA256 (при указании webroot); без URL проверка НЕ пройдена. Документация на русском включена.

## Независимый benchmark

Синтетический корпус 12 макетов: средний IoU трёх ролей **0.5725 → 0.8115**, четыре отложенных **0.6140 → 0.8021**. Эти числа отражают только фиксированную искусственную геометрию и не доказывают точность на реальных художественных макетах. На двух оригинальных эталонах Solo VPN с *приблизительной, не подтверждённой владельцем* разметкой IoU **0.1364**. Запрет автоматического коммерческого утверждения остаётся.

## Фактический QA

Свежая полная проверка изменённого кода: **192 passed, 1 skipped, 0 failed**, 139.29 сек. Пропущен необязательный тест исторического внешнего V46. После чистой распаковки скачиваемого ZIP: 28/28 целевых тестов, CLI-бенчмарк holdout IoU 0.8021, doctor.core_ready=true, Tkinter Xvfb Linux PASS. На созданном демосайте 7/7 ширин Chromium без переполнений; public-webroot и delivery ZIP прошли проверку.

## Раздельные файлы

Движок: `SOLO_SITE_FACTORY_INDEPENDENT_SEMANTIC_ENGINE.zip` SHA256 `554fab09d05c38cf8eaa081ba8f409398b2c7bce08650f7836caf9536af42868`.

Evidence и реальные макеты (вне движка): `SOLO_FACTORY_INDEPENDENT_SEMANTIC_QA_IMAGES.zip` SHA256 `ac408b8d0def5ab386270f3f2440c10d6a9e89079c85143861bc7021550e034a`.

Сайт Solo VPN БЕЗ ИЗМЕНЕНИЙ: `SOLO_VPN_SITE_UNCHANGED_INDEPENDENT_RELEASE.zip`, 91 файл, SHA256 `3531da41ae8f11ddb4748018cd4dcdac6714134ba0fe9f777000b815a514b95f`.

Снимки старого неизменённого Solo VPN ПК/мобильный: `SOLO_VPN_PC_MOBILE_UNCHANGED_INDEPENDENT_QA.zip`. Тестовый сайт: `SOLO_FACTORY_SEMANTIC_DEMO_PUBLIC_WEBROOT.zip` и `SOLO_FACTORY_SEMANTIC_DEMO_WITH_GUIDE.zip`.

## 5 исторических показателей (НЕ повышать автоматически)

Solo VPN локальный QA: 100%; визуал ПК 90% ручной; визуал телефона 90% ручной; движок 90% прежний локальный чек-лист, не универсальная автономность; коммерческий VPN 49.5% исторический, PRODUCTION_BLOCKED.

## Открытые барьеры

Windows 10 пользователя физически **не проверена**; нужен запуск `RUN_NATIVE_WINDOWS_ACCEPTANCE.bat`. Для живого HTTPS нет опубликованного URL — не подтверждён. Для художественной независимой приёмки необходимо получить не менее 30 разнообразных реальных размеченных макетов, подтверждённых владельцем; только потом наращивать автономные правки с откатом. Не создавать заново двигатель или Solo VPN, не плодить бесконечные номера версий.