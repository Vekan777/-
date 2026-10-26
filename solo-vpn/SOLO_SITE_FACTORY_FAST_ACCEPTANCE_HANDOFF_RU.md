# Solo Site Factory — ускоренные проверки и контроль приёмки (26 октября 2026)

Полные исходники в архиве SOLO_SITE_FACTORY_FAST_ACCEPTANCE_ENGINE.zip из чата, не в этой устаревшей ветке GitHub. SHA256 d570a691d1df56ba5864d0f8b29ca8b8fe6e89be48dd2814e18fe9e35ab048e6; 93 файла.

Продолжение из SOLO_SITE_FACTORY_BREAKPOINT_GUARD_ENGINE.zip. Движок и сайт отдельны.

## Изменения

engine/viewport_guard.py использует один DOM Chromium на 7 ширин вместо семи загрузок. Замер на одном демосайте: 1.578s -> 1.004s (примерно на 36,5% быстрее только в этом опыте).

engine/test_runner.py: изолированные pytest модули, лимит на модуль, SHA256-привязка коду, возобновление только успешных проверок с неизменным кодом. Выборочный запуск — PARTIAL_PASS, полный PASS возможен лишь после ВСЕХ модулей; timeout не PASS.

Windows скрипты RUN_FINAL_ACCEPTANCE_WINDOWS.bat, TEST_ENGINE_WINDOWS.bat, CHECK_ENGINE_BATCHES_WINDOWS.bat. Добавлены два модуля тестов и FAST_TEST_ACCEPTANCE_RU.md.

## Подтверждённые проверки

Всего собрано 133 pytest теста. 14 полностью проверенных модулей: 105 passed, 1 skipped. Дополнительные 6 тестов из test_viewport_guard прошли (оставшиеся 2 deselected). Итого 111 passed, 1 skipped, 21 не подтверждён: 2 из viewport_guard, 10 из layout_optimizer, 9 из visual_autofix. Тяжёлый запуск превысил лимит среды и НЕ отмечен успешным.

Семь ширин на локальном демосайте PASS. После чистой распаковки ZIP новые шесть тестов и выборочный тестовый конвейер снова PASS. Реальные Windows 10, HTTPS, внешние лицензированные материалы не проверены.

## Отдельные файлы

Движок SOLO_SITE_FACTORY_FAST_ACCEPTANCE_ENGINE.zip, 234313 байт, SHA256 d570a691d1df56ba5864d0f8b29ca8b8fe6e89be48dd2814e18fe9e35ab048e6.

Solo VPN без изменений SOLO_VPN_SITE_UNCHANGED_FAST_ACCEPTANCE.zip, 91 файл, SHA256 3531da41ae8f11ddb4748018cd4dcdac6714134ba0fe9f777000b815a514b95f.

Снимки настоящего неизменённого сайта PC и mobile и QA: SOLO_FACTORY_FAST_ACCEPTANCE_SCREENSHOTS_AND_QA.zip.

## Пять оценок — исторические, не повышены

Solo VPN локальный сайт 100%; визуал ПК 90% и мобильный 90% (ручные); движок 90% (локальный чек-лист, не универсальная автономность); коммерческий VPN 49,5% (исторический расчёт, production blocked).

Следующий этап — проверить полный RUN_FINAL_ACCEPTANCE_WINDOWS.bat на компьютере владельца, закрыть 21 тест, затем реальные HTTPS/внешние материалы; к Solo VPN вернуться после подтверждённой готовности движка. Не выпускать бесконечные номера версий.