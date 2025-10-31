# Roadmap and Privacy Checklist

## MVP features
- Minimal overlay suggestion UI that integrates with keyboard
- 3 suggestion styles: Formal, Casual, Witty
- Intensity slider (how bold the suggested reply is)
- Settings screen with consent toggle and data controls
- Backend mock endpoint `/suggest` that returns 3 sample suggestions

## Privacy & legal checklist
- Explicit consent screen before any message collection
- Local-first behavior: process as much on-device as possible
- Opt-out and delete user data function in settings
- Clear TOS and Privacy policy with Play Store listing
- Avoid reading SMS inbox without consent; prefer keyboard input capture (InputMethodService)

## Architecture notes
- Client (Android): Compose UI + InputMethodService for keyboard integration
- Backend: FastAPI for suggestion generation and training endpoints
- Personalization: use embeddings & per-user storage; only upload with consent

## Permissions tradeoffs
- InputMethodService (custom keyboard): best user control and avoids Accessibility requirements
- AccessibilityService overlay: more intrusive, often subject to Play Store review

## Next steps after scaffold
- Implement Compose-based overlay UI prototype
- Implement simple backend integration and CI
- Add unit and UI tests
