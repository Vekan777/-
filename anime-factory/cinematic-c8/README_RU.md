# AI Anime Factory — C8 DEEP QA (3D + RU lip timing)
**Рабочий технический релиз, не завершённое студийное аниме.** Сохраняет C1–C7. Отдельно прежняя V19–V50 не мигрирована.
## Возможности
- Два оригинальных GLB: 14 костей, 4546 треугольников и три facial morph targets `MouthOpen`, `Blink`, `BrowFrown`; morph применяется перед skinning.
- Работающая 3D-анимация, материалы с лёгкой процедурной детализацией (без полноценного UV/PBR), русские субтитры, редактор сезонов.
- Программа C8 во время пакетного рендера сначала синтезирует голос, затем измеряет PCM-амплитуду и управляет раскрытием рта. Это **audio-driven jaw movement, не точный phoneme lipsync**.
- Автоматизированная установка `ru_RU-denis-medium` (Piper) в полном Windows ZIP: `SETUP_PIPER_RU_WINDOWS.bat`, проверка SHA256 ONNX и MODEL_CARD. **Piper модель 63 МБ не встроена** и скачивается при установке. Резервный eSpeak роботизированный.
- Отдельная C8 Batch-команда `RUN_BATCH_WINDOWS.bat` создаёт H.264/AAC + RU SRT с Python, Playwright/Chromium и FFmpeg 9.0.2.
## Запуск
Скачайте полную ZIP сборку C8 из текущего ответа в ChatGPT. Распакуйте в новую папку, не поверх C7. Запустите `RUN_WINDOWS.bat` для HTML. Для MP4: установите Python 3.11+ (x64), `SETUP_BATCH_WINDOWS.bat`, затем `SETUP_PIPER_RU_WINDOWS.bat` и `RUN_BATCH_WINDOWS.bat`. Для слабого Windows 10 i7/8GB/GT740M начинайте 640×360 и 3–6 FPS, WebGL на ПК не проверен. Полная русская инструкция находится в ZIP.
## QA
13 старых тестов GLB, новая проверка морфов/деформации, браузерная 3D QA, Python тест измерения амплитуды, тестовый MP4 H.264/AAC с реальным русским звуком. Автоматическая QA отмечает **14 пройденных из 15**: недостаёт встроенной модели Piper (она устанавливается отдельно). **Художественная приёмка НЕ пройдена.**
### Открытые блокеры
- Персонажи low-poly, нет профессиональных UV/PBR текстур и студийной детализации.
- Только три мимических формы, не 20+ facial blendshapes, нет точного phoneme alignment.
- eSpeak голос роботизированный, Piper-голос требует установки и ручной проверки; запись актёров по-прежнему лучший вариант.
- Нет приёмки 20+ минут при 1080p/24fps, художественного качества боёв, Windows GPU и полной миграции V19–V50.
### Референсы
[Khronos glTF morph-target specification](https://github.com/KhronosGroup/glTF/blob/main/specification/2.0/Specification.adoc); [Piper CLI](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/CLI.md); [официальный Russian Denis voice & MODEL_CARD](https://huggingface.co/rhasspy/piper-voices/tree/main/ru/ru_RU/denis/medium).
