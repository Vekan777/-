# Solo VPN V8 — GitHub build workspace

**Branch:** `solo-vpn-v8-build` (isolated from the unrelated `main` project).

## Available sources

- `android-project.tgz.b64` — Android V8 WireGuard source bundle (Gradle 8.11.1, Android Gradle Plugin 8.7.3, SDK 35). The source bundle contains a fallback 48×48 icon; CI replaces it with the **256×256 shadow-hunter avatar** from `solo-avatar-256.png.b64` before building. The original 512px avatar remains in the user's local V8 archive.
- `web-api-project.tgz.b64` — website, FastAPI service, Linux deployment examples, docs and tests. No real API/payment/server secrets included.
- `.github/workflows/build-solo-vpn-android.yml` — Android debug APK workflow. Open the GitHub Actions tab to download the successful build artifact.

These sources are stored as compressed base64 text in this branch for reliable transfer via the GitHub connector.

## How to unpack (Ubuntu/Linux/macOS)

```bash
mkdir -p android-src web-api-src
base64 -d solo-vpn/android-project.tgz.b64 | tar xz -C android-src
base64 -d solo-vpn/web-api-project.tgz.b64 | tar xz -C web-api-src
```

## Build result and restrictions

The cloud workflow builds an **actual Android WireGuard debug APK**, signed with Android's **debug certificate**. This is not a signed production release, not configured with a real API endpoint, and not yet tested against an operational VPN host. The seven-day trial and payment logic requires the separately deployed and configured backend.

To run the website/backend locally, see `web-api-src/OWNER_LAUNCH_GUIDE_RU.md` after unpacking.

Do not commit any signing keystores, Stripe credentials, real `.env`, access tokens or VPN private keys.
