# AI Rescue Factory — исходники и выпуски

## AI Anime Factory V20 Story & Combat — новый выпуск

- [Скачать V20 Windows ZIP напрямую](https://raw.githubusercontent.com/Vekan777/-/main/downloads/AI_ANIME_FACTORY_V20_STORY_COMBAT_WINDOWS.zip)
- [Исходный HTML V20](anime-factory/v20/AI_Anime_Factory_V20_STORY_COMBAT.html)
- [Подробная инструкция и результаты тестов](anime-factory/v20/RELEASE_NOTES_STORY_COMBAT_RU.md)
- [Все ZIP в одном списке](downloads/INDEX_RU.md)

V20 развивает V19: отслеживание цены вызова душ, ранений, предательства, памяти и отношений; контактный лист 4 кадров, редактируемый канон, более читаемый темп ударов, экспорт Story ZIP.
В GitHub Actions она прошла 19 тестов на Windows и Linux. Обновлённый выпуск V7 через CI включает эту V20, а ранее опубликованный прямой V7 ZIP остаётся прежним и не перезаписывается.

## V7 Unified — новая основная версия

- [Скачать V7 ZIP напрямую](https://raw.githubusercontent.com/Vekan777/-/main/downloads/AI_RESCUE_FACTORY_V7_UNIFIED_CANDIDATE_WINDOWS.zip)
- [Сборка GitHub Actions V1–V7 и Anime V19/V20](https://github.com/Vekan777/-/actions/runs/39286748398/artifacts/12203850830) — проверка Windows/Linux: SUCCESS
- [Подробный отчёт QA и инструкция на русском](docs/V7_UNIFIED_QA_REPORT_RU.md)

Объединены ядро V1–V6, автономная работа ZIP/SHA256/SQLite, графическая оболочка Tkinter и сохранённый исходник AI Anime Factory V19. V20.3 — восстановленный кандидат.

Важно: успешные CI-тесты не означают проверку графического интерфейса на конкретном Windows 10 ноутбуке; Python и GUI нужно проверить локально.

## Прямые проверенные ZIP (без ожидания GitHub Actions)

Все девять архивов собраны резервным ZIP-движком и доступны в [downloads/INDEX_RU.md](downloads/INDEX_RU.md). Архивы загружены в GitHub и проверены по структуре и CRC32. Полноценные Windows/Python-тесты ещё не пройдены — GitHub Actions пока в очереди.

Подлинная HTML-студия AI Anime Factory V19 сохранена из библиотеки пользователя.
Rescue Factory V1–V6 — восстановленные из требований исходники; ZIP создаются заново, не являются побайтовыми копиями прежних браузерных загрузок.

## Директории
- anime-factory/v19/AI_Anime_Factory_V19.html — подлинный исходник аниме-студии V19.
- rescue-engine/engine.py — автономные архивы, SHA256, SQLite, восстановление после сбоев.
- rescue-engine/ai_pipeline.py — опциональная подготовка заданий через Ollama/API.
- rescue-engine/launch.py — варианты запуска V1–V6.
- tests/test_engine.py — регрессионные тесты.
- scripts/build_releases.py — выпуск ZIP V1–V6 и восстановленного V19.
- .github/workflows/build-releases.yml — тестирование на Windows/Linux и ZIP в GitHub Artifacts.

## Скачать ZIP
Откройте страницу GitHub Actions: https://github.com/Vekan777/-/actions/workflows/build-releases.yml
Откройте последний УСПЕШНЫЙ запуск (зелёный значок), затем Artifacts.
Название набора: AI_RESCUE_FACTORY_V1_V6_AND_ANIME_V19_WINDOWS.
Пока запуск не завершился успешно, архивы не считаются проверенными.

## Ручной запуск
Python 3.10+ x64, стандартная библиотека:

    python rescue-engine/engine.py selftest
    python -m unittest discover -s tests -p test_*.py -v
    python scripts/build_releases.py --out dist

## Важное отличие от истории браузерных версий
Оригинальные ZIP и MP4 аниме-фабрики остаются в библиотеке пользователя.
Бинарные архивы не были перенесены на GitHub в этом этапе.
Браузерные V20/V20.1/V20.2/V20.3 и прежние автономные V1–V5 существуют в истории чата,
но в GitHub вместо недоступных точных ZIP создаётся новая, прозрачно маркированная реконструкция.

## Безопасность
Этот GitHub-репозиторий публичный. Не публикуйте пароли, API-ключи и личные материалы.
Для изменений автоматически требуется явное разрешение; скачанный ИИ-код не запускается.

## План
После успешной V6 Remote Build — V7 Unified Final и продолжение Anime Factory после V19.