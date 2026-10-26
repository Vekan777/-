# Solo Site Factory — разные композиции по макетам (26 октября 2026)

**Полный код** — архив SOLO_SITE_FACTORY_COMPOSITION_ENGINE.zip из текущего чата, SHA256 ec96a26ede12dc4a55fc740cf7d98120103baea1238853a458869791b938b0f8, 103 файла. Эта ветка GitHub хранит только документацию передачи, не весь новый движок.

Основа — полный прежний SOLO_SITE_FACTORY_MULTI_DESIGN_BENCHMARK_ENGINE.zip; существующие функции сохранены.

Изменения: engine/composition.py определяет низкодоверенную композицию по 4 горизонтальным срезам компьютерного макета: editorial, catalog, service либо split. Результат можно изменить в BLUEPRINT.json/editable_layout.composition; художественная приёмка владельца обязательна. В engine/design_to_site.py разные DOM/CSS композиции, сетка каталога и приблизительный цвет товарных панелей из растра; мобильный каталог после исправления отображает полноразмерные вертикальные карточки, а не линии.

engine/design_benchmark.py создаёт 3 разных синтетических дизайна, передаёт известные слова эталона явным REFERENCE_CONTENT.json (НЕ OCR), проверяет distinct composition и пишет технический/визуальный отчёт. Добавлены tests/test_composition_profiles.py (8 тестов) и RUN_COMPOSITION_BENCHMARK_WINDOWS.bat, COMPOSITION_TRANSFER_GUIDE_RU.md.

Свежий полный локальный прогон: 149/149 pytest без пропусков, 3 сайта, 21/21 viewport проверка, 6/6 Chromium offline-in-memory сравнений. После чистой распаковки 18/18 целевых тестов, doctor.core_ready=true, Tkinter GUI smoke Linux/Xvfb PASS. **НЕ Windows пользователя**. ZIP CRC PASS.

Контурное сходство прокси по новым синтетическим данным (ПК/моб): editorial 29.84/41.31%, catalog 13.48/29.54%, service 24.10/48.87%. Это техническая метрика; не профессиональная или художественная готовность, результаты неоднородны. Три структуры стали разными, но копирование любых макетов 1:1 не достигнуто, в каталоге значительные отличия остаются. Production_approved=false.

Артефакты: SOLO_FACTORY_THREE_COMPOSITIONS_WEBSITES.zip, SOLO_FACTORY_COMPOSITION_SCREENSHOTS_QA.zip, SOLO_FACTORY_COMPOSITION_REAL_PC_MOBILE.jpg и SOLO_FACTORY_COMPOSITION_QA_REPORT.json.

Отдельный Solo VPN не изменён: SOLO_VPN_SITE_UNCHANGED_COMPOSITION.zip, 91 файл, SHA256 3531da41ae8f11ddb4748018cd4dcdac6714134ba0fe9f777000b815a514b95f; настоящие предыдущие браузерные снимки ПК/телефона в SOLO_VPN_UNCHANGED_PC_MOBILE_COMPOSITION.zip.

Пять исторических, НЕ повышенных показателей: локальный сайт 100% в пределах файлового QA, визуал ПК 90% и телефона 90% — ручные прежние оценки, движок 90% по узкому локальному чек-листу, коммерческий VPN 49,5% — старый расчёт PRODUCTION_BLOCKED.

Следующие барьеры: подтверждение на Windows 10 пользователя, реальные разные сложные макеты, лицензированные интернет-материалы и действительный HTTPS end-to-end; затем вернуться к Solo VPN, сохраняя раздельные ZIP и скриншоты.