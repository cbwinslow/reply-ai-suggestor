Android module — reply-ai-suggester

This is a minimal Android app skeleton using Kotlin and Jetpack Compose.

Open the `android/` folder in Android Studio and let it sync. The skeleton contains:
- `MainActivity` - basic Compose UI for testing suggestion generation
- `SettingsActivity` - stub settings UI
- `KeyboardStubService` - InputMethodService stub for future keyboard integration

Notes and next steps

- To prototype keyboard integration, implement the `KeyboardStubService` as a proper InputMethodService or create a separate IME module.
- The `android/app/build.gradle.kts` is placeholder; open in Android Studio to finish configuring plugin and Gradle wrapper.
- Keep user privacy in mind: prefer InputMethodService over Accessibility overlays to reduce Play Store friction.
