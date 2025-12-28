# WashFlow Mobile

Flutter mobile app for WashFlow car wash staff.

## Prerequisites

- Flutter SDK (stable channel, 3.16+)
- Dart SDK
- Android Studio / Xcode for platform-specific development

## Setup

1. **Install dependencies:**
   ```bash
   flutter pub get
   ```

2. **Run the app:**
   ```bash
   # Android emulator
   flutter run

   # iOS simulator
   flutter run -d ios

   # With custom API URL
   flutter run --dart-define=API_BASE_URL=http://192.168.1.100:8000
   ```

## API Configuration

The app connects to the API at `http://10.0.2.2:8000` by default (Android emulator localhost).

For different environments:
- **Android Emulator:** `10.0.2.2` (maps to host's localhost)
- **iOS Simulator:** `localhost`
- **Physical Device:** Use your machine's IP address

Set custom API URL:
```bash
flutter run --dart-define=API_BASE_URL=http://YOUR_IP:8000
```

## Project Structure

```
apps/mobile/lib/
├── app/                  # App configuration
│   ├── app.dart          # Main app widget
│   ├── config.dart       # Environment config
│   ├── router.dart       # GoRouter setup
│   ├── theme.dart        # App theming
│   └── home_screen.dart  # Home screen
├── features/
│   └── auth/             # Authentication feature
│       ├── data/         # Repository & models
│       └── presentation/ # Screens
└── shared/
    ├── providers/        # Riverpod providers
    ├── services/         # API & storage services
    └── widgets/          # Shared widgets (future)
```

## Tech Stack

- Flutter 3.16+
- Riverpod (state management)
- GoRouter (navigation)
- Dio (HTTP client)
- Flutter Secure Storage

## Screens

- Login
- Register
- Home (placeholder)

## Build

```bash
# Android APK
flutter build apk

# Android App Bundle
flutter build appbundle

# iOS
flutter build ios
```
