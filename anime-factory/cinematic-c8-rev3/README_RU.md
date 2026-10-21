# AI Anime Factory C8 Rev3 — два русских голоса и самодиагностика

Продолжение C8, не новая основная C9. Подготовлена полная Windows сборка, выдаваемая как ZIP в ChatGPT: **AI_ANIME_FACTORY_C8_REV3_DUAL_RU_VOICES_WINDOWS.zip**. Важные бинарные файлы намеренно не продублированы в публичный GitHub.

## Подтверждённые файлы пользователя
- Denis: ru_RU-denis-medium.onnx (63 201 294 байта; SHA-256 15fab56e11a097858ee115545d0f697fc2a316c41a291a5362349fb870411b0a)
- Dmitri: ru_RU-dmitri-medium.onnx (63 201 294 байта; SHA-256 f073356ebc4bd0f80c5af58df2953a5988bd5bdab1eb38635ce960b071fbefcb)
- Оба JSON из PIPER_RU_DENIS_DMITRI_JSON_DOWNLOAD.zip
- Портативный piper_windows_amd64.zip с DLL и espeak-ng-data

## Исправления
- Один архив включает два оригинальных ONNX и две проверенные конфигурации, портативный Windows Piper, 3D-редактор и архивы C1–C7.
- VOICE_CAST.json назначает Арану Denis, Стражу Dmitri; безопасный fallback, проверка путей и сохранность данных.
- Две отдельные голосовые пробы WAV без Python и без сетевой установки; голосовые модели сохраняются локально.
- RUN_DIAGNOSTICS_WINDOWS.bat создаёт **на настоящем ПК** STUDIO_TOOLS/LOCAL_SETUP_RESULT.json даже если другие этапы установки не прошли. Файл нельзя заранее скачать с достоверными сведениями о чужом ноутбуке.
- Исправлено повторное использование MP4 после изменения набора голосов.
- Для полного MP4 отдельно требуются Python, Playwright Chromium и FFmpeg.

## QA
8 новых голосовых тестов, 3 проверки прежнего C8 Voice, 13 skinning C7, morph regression и dry-run двух серий прошли. Windows Piper exe и пробные WAV на ноутбуке пользователя **не проверялись**. Студийные 3D-персонажи и реалистичная мимика пока остаются художественными блокерами.
