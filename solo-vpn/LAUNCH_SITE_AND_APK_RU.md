# Solo VPN — запуск сайта, API и VPS (V9 Launch Kit)

**Полная русская инструкция и готовые скрипты** входят в [архив V9, предоставленный в чате]. Этот GitHub-файл — короткая памятка, секреты сюда не загружать.

## Что нужно владельцу

1. Собственный Ubuntu 24.04 VPS с публичным IP и разрешённым VPN/UDP, DNS-домен (например `vpn.example.com`), открытые TCP 80/443 и UDP 51820.
2. На своём ПК распаковать пакет `solo-vpn/web-api-project.tgz.b64` по командам в [README](README.md). В архиве V9 есть актуализированные `docs/START_WEBSITE_WINDOWS_RU.md` и `docs/START_APK_ANDROID_RU.md`.
3. Локально посмотреть сайт: из корня проекта `python -m http.server 8080 --directory site`, открыть `http://localhost:8080`. Узлы при отсутствии API будут показываться как недоступные.
4. На VPS скопировать исходники в `/opt/solo-vpn`; проверить содержимое и затем запустить `sudo bash deploy/bootstrap_ubuntu.sh`. Это изменяет системные настройки, использовать на **отдельном VPS**.
5. Создать `/etc/solo-vpn.env` из `api/.env.example`, права 600. Указать реальный `WG_ENDPOINT=vpn.example.com:51820`, `WG_PUBLIC_KEY`, `SOLO_PUBLIC_ORIGIN=https://vpn.example.com`, случайный `SOLO_ADMIN_TOKEN` и DB путь. Не публиковать содержимое env.
6. Заменить домен в `deploy/Caddyfile`, выполнить `caddy validate --config`; включить `wg-quick@wg0`, `caddy`, `solo-vpn.service`, `solo-vpn-expire.timer`. Интерфейс `wg0` должен быть **только для Solo VPN**: сторожевой таймер удаляет неизвестных клиентов.
7. Проверить `https://vpn.example.com/api/v1/health`: `wireguard_ready=true`, `expiration_timer_healthy=true`, `accepting_new_users=true`. Затем протестировать реальное VPN-соединение с Android и отключение по окончании пробного доступа.

## Trial и платный доступ

7 дней активируются **одноразовым кодом** из `POST /api/v1/admin/invites`; дальнейшее продление — административными voucher-кодами или Stripe Checkout **только после настройки** реальных ключей и webhook `/api/v1/webhooks/stripe`. Магазин Google Play требует отдельной реализации Play Billing. Пока нет VPS и платёжного аккаунта, коммерческий запуск не готов.

## APK

Предыдущий debug APK содержит временный API URL и не работает с реальными узлами. Используйте GitHub Actions workflow `build-solo-vpn-android.yml` с вводом **своего HTTPS api_origin** либо `gradlew :app:assembleDebug "-PsoloApiUrl=https://vpn.example.com" -PsoloChannel=direct`. Для публичного релиза нужна личная JKS-подпись и тесты на настоящем телефоне. Ключи подписи и серверные секреты хранить только у владельца.

Визуальные изображения, показанные в беседе, — **дизайн-концепты**, не подлинные браузерные скриншоты развернутого сайта. Не обещать вымышленные серверы, клиентов или скорость.
