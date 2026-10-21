# AI Anime Factory CINEMATIC C8 — Rev2 (Piper Voice + UV/PBR)
Дата: 21 октября 2026 г.

Это **доработка C8, не C9**. Проверена предоставленная пользователем оригинальная модель `ru_RU-denis-medium.onnx`: 63 201 294 байта, SHA-256 `15fab56e11a097858ee115545d0f697fc2a316c41a291a5362349fb870411b0a`. Модель находится **только в выдаваемом ChatGPT ZIP**, не в публичном GitHub.

## Реализовано в скачиваемой сборке C8 Rev2
- Два оригинальных GLB с настоящими UV, нормалями, цветом вершин, embedded PNG-картами baseColor, normal и metallicRoughness (42 карты на персонажа), сохранены исходные 14-костный skinning и 3 лицевых morph-target.
- C8 standalone HTML с упрощённой визуализацией цвета новых моделей. Полные PBR-карты рассчитаны на Blender/рендереры, в HTML нет студийного PBR-шейдинга.
- Windows one-click `START_HERE_WINDOWS.bat`: запускает HTML, проверяет ONNX, скачивает **только** официальный `.onnx.json` и `MODEL_CARD`, устанавливает Python/Piper/Playwright, пытается сделать реальный тестовый RU WAV. Потребуется Интернет на первом запуске.
- Три дополнительных ZIP с бинарными Python 3.12.10/FFmpeg 9.0.2/FFprobe, взятыми из уже загруженной пользователем Library. Система автоматической распаковки обнаруживает ZIP в папке «Загрузки» Windows.
- Неповреждённые исходные архивы C1–C7, тесты и русская инструкция внутри основного компактного ZIP.

## Проверки и не пройденные критерии
- 13 проверок GLB skinning, тесты facial morph, три voice unit tests, пять asset QA tests успешны.
- Две новые модели: **8/11 технических критериев**; незакрыты 20+ костей, 15+ мимических форм, ручное подтверждение прав.
- Windows Piper/ONNX runtime, реальный синтез `TEST_RU_PIPER.wav` на целевом ноутбуке и Chromium browser smoke в этом сеансе **не подтверждены**. Официальный standalone Piper CLI: https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/CLI.md .
- Ваша линия V19–V50 не мигрирована автоматически; до художественной приёмки качества Solo Leveling ещё далеко.

## Куда идти
Главные артефакты `AI_ANIME_FACTORY_C8_REV2_COMPACT_WINDOWS.zip`, `C8_REV2_TOOLS_FFMPEG_WINDOWS.zip`, `C8_REV2_TOOLS_FFPROBE_WINDOWS.zip`, `C8_REV2_TOOLS_PYTHON_WINDOWS.zip` предоставлены непосредственно в чате. В GitHub нет выдуманных ссылок на бинарные архивы.

Сборка специально разделена на 4 ZIP из-за размера. Начать следует с **основного компактного**. Если локальные Python/FFmpeg ещё не установлены, загрузите также 3 optional toolpacks в папку Windows «Загрузки» и снова запустите `START_HERE_WINDOWS.bat`.
