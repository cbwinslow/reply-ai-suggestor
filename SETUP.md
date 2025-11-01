# Reply AI Suggester - Setup Guide

## Overview

This guide will help you set up and run the Reply AI Suggester application, which provides AI-driven reply suggestions for SMS text messaging through a custom keyboard (IME).

## Architecture

The application consists of two main components:

1. **Backend (FastAPI)**: REST API that generates reply suggestions
2. **Android App**: Custom keyboard (InputMethodService) with suggestion UI

## Prerequisites

### Backend Requirements
- Python 3.8+
- pip (Python package manager)

### Android Requirements
- Android Studio (latest version recommended)
- Android SDK (API level 24+)
- Android device or emulator running Android 7.0 (API 24) or higher

## Backend Setup

### 1. Create Python Virtual Environment

```bash
cd /home/runner/work/reply-ai-suggestor/reply-ai-suggestor
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### 3. Run the Backend Server

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

The backend will start on `http://localhost:8000`

### 4. Test the Backend

**Health Check:**
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "ok"}
```

**Test Suggestions:**
```bash
curl -X POST http://localhost:8000/suggest \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "context": "Hey, thanks for the update",
    "modes": ["casual", "formal", "witty"],
    "intensity": 6,
    "provider": "mock"
  }'
```

Expected response:
```json
{
  "suggestions": [
    {
      "text": "Hey, thanks for the update — sounds good to me!",
      "tone": "casual"
    },
    {
      "text": "Hey, thanks for the update. I will proceed as discussed!",
      "tone": "formal"
    },
    {
      "text": "Hey, thanks for the update — because why not, right?!",
      "tone": "witty"
    }
  ]
}
```

## Android Setup

### 1. Open Project in Android Studio

1. Launch Android Studio
2. Select "Open an Existing Project"
3. Navigate to the `android/` directory in this repository
4. Click "OK"

### 2. Sync Gradle

Android Studio will automatically detect the Gradle configuration and prompt you to sync. Click "Sync Now".

If sync fails:
- Ensure you have the latest Android Gradle Plugin
- Check that your Android SDK is properly configured in Android Studio
- Go to File → Project Structure → SDK Location to verify SDK path

### 3. Configure Backend URL

The Android app is configured to use `10.0.2.2:8000` by default, which maps to `localhost:8000` on the host machine when using an Android emulator.

If you're using a physical device:
1. Find your computer's IP address on your local network
2. Edit `NetworkClient.kt` and change `BASE_URL` to `http://YOUR_IP:8000`

### 4. Build and Run

1. Click the "Run" button (green triangle) or press Shift+F10
2. Select a device/emulator
3. The app will build and install

### 5. Enable the Keyboard

After installing the app:

1. Open Android Settings → System → Languages & Input → On-screen keyboard
2. Enable "ReplyAISuggester"
3. Open any app with a text input field (e.g., Messages, Notes)
4. Tap the text field
5. Tap the keyboard switcher icon
6. Select "ReplyAISuggester"

## Features

### Main App Features
- **Consent Dialog**: On first launch, users must consent to data processing
- **Test Interface**: Input text and generate suggestions manually
- **Settings**: Configure personalization, consent, and data controls

### Keyboard (IME) Features
- **Suggestion Strip**: Shows AI-generated suggestions at the top of the keyboard
- **Quick Actions**: 
  - "Suggest" button: Fetches suggestions from backend
  - "Space" button: Inserts a space
  - "Inline" button: Inserts first suggestion with color coding
- **Basic Keyboard**: Functional QWERTY layout
- **Network Integration**: Real-time communication with backend

### Settings Screen
- **Consent Management**: Grant or revoke consent for data processing
- **Personalization Toggle**: Enable/disable local personalization
- **Intensity Slider**: Adjust suggestion intensity (0-10)
- **Data Controls**:
  - Export: Copy encrypted personalization data to clipboard
  - Upload: Send personalization data to backend (requires consent)
  - Delete: Remove all local and server-side personalization data

## API Endpoints

### Backend Endpoints

#### GET /health
Health check endpoint.

**Response:**
```json
{"status": "ok"}
```

#### POST /suggest
Generate reply suggestions.

**Request:**
```json
{
  "user_id": "string",
  "context": "string",
  "modes": ["casual", "formal", "witty"],
  "intensity": 5,
  "provider": "mock"
}
```

**Response:**
```json
{
  "suggestions": [
    {
      "text": "suggestion text",
      "tone": "casual|formal|witty"
    }
  ]
}
```

#### POST /train
Queue training/personalization (mock endpoint).

**Response:**
```json
{
  "status": "ok",
  "message": "training queued (mock)"
}
```

#### POST /upload_personalization
Upload encrypted personalization data.

**Request:**
```json
{
  "user_id": "string",
  "artifacts": {
    "export": "base64_encoded_data"
  }
}
```

#### POST /delete_personalization
Delete user personalization data.

**Request:**
```json
{
  "user_id": "string"
}
```

#### GET /personalization/{user_id}
Retrieve user personalization data.

## Development

### Running Tests

Backend tests can be run with pytest (when tests are added):
```bash
pytest backend/tests/
```

### Code Quality

The project uses:
- **ktlint** for Kotlin code formatting
- **Detekt** for Kotlin static analysis
- **Black** and **isort** for Python code formatting (when configured)

### CI/CD

The project includes GitHub Actions workflows for:
- Android CI: Build and test Android app
- Backend CI: Test and deploy backend

## Troubleshooting

### Backend Issues

**Problem**: Import errors when starting backend
**Solution**: Make sure you're running from the project root directory and have activated the virtual environment

**Problem**: Port 8000 already in use
**Solution**: Stop the existing process or use a different port:
```bash
uvicorn backend.main:app --port 8001
```

### Android Issues

**Problem**: Gradle sync fails
**Solution**: 
- Update Android Studio to the latest version
- Go to File → Invalidate Caches / Restart
- Check that Android SDK is properly configured

**Problem**: App crashes on launch
**Solution**: Check Logcat in Android Studio for detailed error messages

**Problem**: Keyboard doesn't appear
**Solution**: Ensure the keyboard is enabled in Android Settings → System → Languages & Input

**Problem**: Suggestions not loading
**Solution**: 
- Verify backend is running and accessible
- Check the backend URL in `NetworkClient.kt`
- Check Logcat for network errors

## Security & Privacy

### Data Handling
- All personalization data is encrypted at rest using Jetpack Security
- Explicit user consent required before any data collection
- Users can export and delete their data at any time
- Backend uses HTTPS in production (mock HTTP for local dev)

### Privacy Features
- Local-first processing
- Opt-in cloud upload
- Clear data controls
- No data collected without consent

## Next Steps

1. **Add Real AI Provider**: Replace mock provider with Gemini, OpenRouter, or Qwen
2. **Implement Training Pipeline**: Add server-side personalization
3. **Enhanced Keyboard UI**: Improve layout and user experience
4. **Testing**: Add comprehensive unit and integration tests
5. **Play Store**: Prepare privacy policy and compliance documentation

## License

MIT License - See LICENSE file for details

## Support

For issues and questions, please open an issue on GitHub.
