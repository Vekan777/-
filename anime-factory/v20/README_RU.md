# AI Anime Factory V20.3 — восстановленный кандидат

Это новый исходный патч над настоящей V19, а не копия оригинального браузерного ZIP.
Скрипт patch_preserve.py сохраняет дополнительные пользовательские свойства JSON
и сырой оригинал в поле legacyOriginal, но не меняет 2D-рендерер V19.
Для создания V20 HTML запустите: python anime-factory/v20/patch_preserve.py
Для проверки: python anime-factory/v20/patch_preserve.py --selftest

Статус: восстановленный кандидат, не проверен в Chrome/Windows.
В GitHub Actions из исходников генерируется отдельный V20.3 ZIP.
Ранее созданные браузерные V20–V20.3 автоматически в GitHub не оказались.