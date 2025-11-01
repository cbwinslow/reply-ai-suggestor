# Quick Start Guide - Reply AI Suggester

Get the Reply AI Suggester prototype running in under 5 minutes!

## Prerequisites Check

```bash
# Check Python
python3 --version  # Should be 3.8+

# Check if you have Android Studio (for Android app)
# Download from: https://developer.android.com/studio
```

## Backend Quick Start (2 minutes)

```bash
# 1. Navigate to project root
cd /path/to/reply-ai-suggestor

# 2. Create virtual environment
python3 -m venv .venv

# 3. Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 4. Install dependencies
pip install -r backend/requirements.txt

# 5. Start the backend
uvicorn backend.main:app --port 8000

# You should see:
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Test the Backend (1 minute)

```bash
# In a new terminal, run the demo
./demo.sh

# You should see:
# ✓ All 10 backend tests passed!
```

## Android Quick Start (2 minutes)

```bash
# 1. Open Android Studio

# 2. File → Open → Select the 'android/' folder

# 3. Wait for Gradle sync to complete

# 4. Click the green "Run" button (or press Shift+F10)

# 5. Select an emulator or connected device

# The app will build and install!
```

## Enable the Keyboard on Android

```bash
# On your Android device/emulator:

# 1. Open Settings
# 2. System → Languages & Input → On-screen keyboard
# 3. Tap "Manage keyboards"
# 4. Enable "ReplyAISuggester"

# Now open any app with text input:
# 5. Tap a text field
# 6. Tap the keyboard icon
# 7. Select "ReplyAISuggester"
```

## Try It Out!

### In the Main App:
1. Type something in the "Conversation context" field
2. Tap "Generate suggestions"
3. See the AI-generated suggestions appear!

### In the Keyboard:
1. Open your SMS app
2. Start a new message
3. Switch to ReplyAISuggester keyboard
4. Tap the "Suggest" button
5. See suggestions appear in the strip above the keyboard
6. Tap a suggestion to insert it!

## Common Issues

### Backend Won't Start
```bash
# Error: Module not found
# Solution: Make sure you're in the project root and venv is activated
cd /path/to/reply-ai-suggestor
source .venv/bin/activate
```

### Android Build Fails
```bash
# Solution 1: Update Android Studio to latest version
# Solution 2: File → Invalidate Caches / Restart
# Solution 3: Check Android SDK is installed (API 24+)
```

### Keyboard Not Appearing
```bash
# Solution: Verify the keyboard is enabled in Settings
# Settings → System → Languages & Input → On-screen keyboard
```

### Suggestions Not Loading
```bash
# 1. Check backend is running:
curl http://localhost:8000/health

# 2. If using a physical device, update NetworkClient.kt:
# Change BASE_URL from "http://10.0.2.2:8000" to "http://YOUR_IP:8000"
```

## What's Next?

### See It In Action
```bash
# Run the comprehensive demo
./demo.sh
```

### Read the Docs
- `SETUP.md` - Complete setup guide
- `APPLICATION_OVERVIEW.md` - Technical details
- `COMPLETION_SUMMARY.md` - What's been built

### Explore the Code
- `backend/main.py` - Backend API endpoints
- `android/app/src/main/java/com/replyaisuggester/` - Android app code
- `android/app/src/main/java/com/replyaisuggester/KeyboardStubService.kt` - Keyboard implementation

## Architecture at a Glance

```
User types → Keyboard (IME) → Backend API → AI → Suggestions → User selects
```

## API Example

```bash
# Generate suggestions
curl -X POST http://localhost:8000/suggest \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "context": "Thanks for your help",
    "modes": ["casual", "formal", "witty"],
    "intensity": 6,
    "provider": "mock"
  }'

# Response:
{
  "suggestions": [
    {"text": "Thanks for your help — sounds good to me!", "tone": "casual"},
    {"text": "Thanks for your help. I will proceed as discussed!", "tone": "formal"},
    {"text": "Thanks for your help — because why not, right?!", "tone": "witty"}
  ]
}
```

## Features Demo

### Privacy Controls
1. Open the app
2. Tap "Settings"
3. Try toggling consent and personalization
4. Test Export/Upload/Delete buttons

### Different Intensities
```bash
# Low intensity (subtle)
curl -X POST http://localhost:8000/suggest \
  -d '{"user_id":"test","context":"Hello","modes":["casual"],"intensity":2}'

# High intensity (enthusiastic)
curl -X POST http://localhost:8000/suggest \
  -d '{"user_id":"test","context":"Hello","modes":["casual"],"intensity":10}'
```

## Success Checklist

- [ ] Backend running and responding to /health
- [ ] Demo script passing all 10 tests
- [ ] Android app builds successfully
- [ ] App installs on device/emulator
- [ ] Consent dialog appears on first launch
- [ ] Keyboard enabled in Android Settings
- [ ] Suggestions appear when tapping "Suggest"
- [ ] Can commit suggestions to text field

## Next Steps

1. **Test thoroughly:** Try the keyboard in different apps
2. **Customize:** Adjust settings and intensity
3. **Integrate AI:** Replace mock provider with real AI (Gemini, OpenRouter)
4. **Deploy:** Set up production infrastructure

## Support

- Check `SETUP.md` for detailed setup instructions
- Check `APPLICATION_OVERVIEW.md` for architecture details
- Check GitHub issues for known problems
- Check logs in Android Studio Logcat for debugging

---

**You're all set! Start typing and let AI help you reply!** 🚀

*Quick Start Guide - Reply AI Suggester v1.0*
