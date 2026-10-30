# ЕМЕЛЯ V61 — статус резервного копирования

Этот каталог содержит исходный код ключевых компонентов единой V61 (обновление HTML/CSS, генератор, проверки, конфигурация). Код опубликован в отдельной ветке для сохранения. Исходные V60/V60.1 объединены в локальный Windows ZIP.

**Важно:** полный ZIP, изображения товаров, художественные референсы и прочие медиа **не размещены в GitHub этой ветки**. Для автономного запуска полного проекта потребуется локальный архив EMELYA_V61_UNIFIED_FACTORY_WINDOWS.zip из текущего чата. GitHub-ветка — резервирование исходного текста, не полноценный бинарный релиз.

QA (Linux): 27/27 pytest, 12/12 browser screens, 15 UI checks, 24/24 responsive viewport, 33/33 separate HTTP smoke, ZIP CRC PASS; Windows 10 и HTTPS не проверены. В исходном пакете V42 есть старый SQLite — его не встраивать в коммерческие релизы.

User supplied 6 new reference PNG and they are included in local full ZIP, but omitted here to avoid falsely claiming that the source-only branch contains them.
