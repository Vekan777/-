# Solo VPN — Android build workspace

This is an isolated branch for building the user's **Solo VPN V8** Android client. The repository default branch `main` is unchanged.

Status: work in progress. The full WireGuard-based app requires Android Gradle Plugin 8.7.3, Gradle 8.11.1, Android SDK 35, and its dependencies.

**Important:** A successful debug APK does **not** mean a live VPN is provisioned. This project needs a separately configured HTTPS API, a dedicated WireGuard server, and payment-provider credentials. Do not publish a debug APK as a production VPN.

User's chosen Solo VPN branding, 7-day trial, and paid access rules remain part of the local V8 source archive; this branch is the isolated CI workspace.