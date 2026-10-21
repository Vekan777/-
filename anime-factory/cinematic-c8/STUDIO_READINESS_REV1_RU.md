# C8 Studio Readiness Rev1 — проверка производственной готовности
Дата: 21 октября 2026.

Продолжаем исправлять **C8**, не создаём C9. Исходные редакторы C1–C7 и V19–V50 не изменялись. Полная локальная сборка ревизии с Python-модулями находится в `AI_ANIME_FACTORY_C8_STUDIO_READINESS_REV1_WINDOWS.zip` в переписке ChatGPT; **эта ZIP пока не загружена в GitHub**.

## Проверено на реально существующих исходниках

Две оригинальные C8 модели `ORIGINAL_HERO_SKINNED.glb` и `ORIGINAL_ENEMY_SKINNED.glb`: каждая содержит 4546 треугольников, 14 костей, три morph targets (`MouthOpen`, `Blink`, `BrowFrown`), одну анимацию. Автоматизированный аудит обнаружил отсутствие нормалей, UV-развёртки, PBR карт baseColor/normal/roughness, нужного количества лицевых форм и документированной ручной приёмки лицензий. Поэтому **обе модели НЕ студийно готовы**, независимо от успешных прежних базовых тестов.

В отдельном пакете реализованы: `STUDIO_TOOLS/asset_qa.py` (GLB/GLTF QA без внешних зависимостей), `STUDIO_TOOLS/studio_preflight.py` + `RUN_STUDIO_PREFLIGHT_WINDOWS.bat`, `STUDIO_TOOLS/blender_scene_prepare.py` (неразрушающий импорт GLB, освещение, сохранение .blend) и подробные ссылки на программы и шаблон загрузки медиа `PROJECT_ASSETS/`.

5 новых unit-тестов, 3 голосовых теста, тест мимики C8 и 13 проверок скелета C7 успешно пройдены; исходные C8 deep QA — 14/15 (не встроена модель Piper), художественная приёмка не пройдена. Blender в тестовом окружении отсутствует, поэтому выполнение нового bpy-скрипта и Windows GPU пока не проверено.

## Прямые официальные загрузки для Windows 10 x64

- Blender 3.6.23, особенно для старого ПК: https://download.blender.org/release/Blender3.6/blender-3.6.23-windows-x64.zip
- Blender 4.5.14 LTS при подходящем драйвере: https://download.blender.org/release/Blender4.5/blender-4.5.14-windows-x64.msi
- Krita 5.3.4.1: https://download.kde.org/stable/krita/5.3.4.1/krita-x64-5.3.4.1-setup.exe
- Python 3.11.9 x64: https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
- Piper TTS CLI: https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/CLI.md
- русский голос: https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/denis/medium/ru_RU-denis-medium.onnx
- голосовой JSON: https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/denis/medium/ru_RU-denis-medium.onnx.json
- карточка голоса: https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/denis/medium/MODEL_CARD
- Audacity 4.0.1: https://github.com/audacity/audacity/releases/download/Audacity-4.0.1/audacity-win-4.0.1-x86_64.msi
- PBR CC0: https://polyhaven.com/textures

**Установщики остаются на компьютере.** В чат лучше загружать `PREFLIGHT_REPORT.json`, оригинальные `.blend/.glb` модели, текстуры и лицензированные голосовые материалы. Blender и FFmpeg уже предоставлялись ранее. Тяжёлый финальный рендер 1080p/24fps на i7-3630QM/8GB/GT740M не гарантирован.
