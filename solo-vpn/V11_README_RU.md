# Solo VPN V11 — WireGuard client verification

## Статус

- Отдельная ветка `solo-vpn-v11-dev`; исходная `main` не меняется.
- `v11-android-patch.tgz.b64`: изменения Android V11 — контроль трёх ошибок доступа и запрет release с тестовым доменом.
- `.github/workflows/build-solo-vpn-v11.yml`: собирает Android debug из проверенного базового исходника V8 с патчем V11.
- Сайт утверждённого дизайна V10, обновлённый FastAPI V11 и серверные тесты распространяются **в полном архиве V11, который предоставлен в чате**; данная ветка GitHub не является опубликованным сайтом.
- Локально у V11 пройдено 39 автоматических тестов (без реального VPS).
- Публичного production API, подписанного владельцем release APK, настроенного Stripe и проверенного VPN-соединения пока нет.

## Запуск сборки

GitHub Actions → `Solo VPN V11 - real WireGuard debug compile` → Run workflow.

Для тестового APK допустим пример адреса API; он **не подключится** к реальному VPN. Когда владелец развернёт HTTPS API, укажите его реальный адрес в `api_origin` и проверьте WireGuard на физическом устройстве.

Для commercial release используйте свой приватный ключ подписи, не размещайте ключи в GitHub и не называйте debug сборку релизом. Канал Google Play требует отдельного Google Play Billing и сейчас запрещён для release.

Полная инструкция: `docs/V11_RELEASE_AND_SETUP_RU.md` внутри архива Solo VPN V11.
