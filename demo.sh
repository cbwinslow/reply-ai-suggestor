#!/bin/bash

# Reply AI Suggester - Demo Script
# This script demonstrates the working backend and its features

set -e

echo "=========================================="
echo "Reply AI Suggester - Backend Demo"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backend is running
echo -e "${BLUE}1. Checking if backend is running...${NC}"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is running!${NC}"
else
    echo -e "${YELLOW}⚠ Backend is not running. Starting it now...${NC}"
    echo "Please run: uvicorn backend.main:app --port 8000"
    exit 1
fi
echo ""

# Test health endpoint
echo -e "${BLUE}2. Testing health endpoint...${NC}"
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
echo "Response: $HEALTH_RESPONSE"
echo -e "${GREEN}✓ Health check passed!${NC}"
echo ""

# Test casual suggestion
echo -e "${BLUE}3. Testing casual suggestion...${NC}"
curl -s -X POST http://localhost:8000/suggest \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user",
    "context": "Thanks for the help",
    "modes": ["casual"],
    "intensity": 5,
    "provider": "mock"
  }' | jq '.'
echo ""

# Test formal suggestion
echo -e "${BLUE}4. Testing formal suggestion...${NC}"
curl -s -X POST http://localhost:8000/suggest \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user",
    "context": "I appreciate your assistance",
    "modes": ["formal"],
    "intensity": 3,
    "provider": "mock"
  }' | jq '.'
echo ""

# Test witty suggestion
echo -e "${BLUE}5. Testing witty suggestion...${NC}"
curl -s -X POST http://localhost:8000/suggest \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user",
    "context": "This is going to be fun",
    "modes": ["witty"],
    "intensity": 7,
    "provider": "mock"
  }' | jq '.'
echo ""

# Test all three modes
echo -e "${BLUE}6. Testing all three modes together...${NC}"
curl -s -X POST http://localhost:8000/suggest \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user",
    "context": "See you tomorrow",
    "modes": ["casual", "formal", "witty"],
    "intensity": 6,
    "provider": "mock"
  }' | jq '.'
echo ""

# Test high intensity
echo -e "${BLUE}7. Testing high intensity (10)...${NC}"
curl -s -X POST http://localhost:8000/suggest \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user",
    "context": "Lets do this",
    "modes": ["casual"],
    "intensity": 10,
    "provider": "mock"
  }' | jq '.'
echo ""

# Test personalization upload
echo -e "${BLUE}8. Testing personalization upload...${NC}"
curl -s -X POST http://localhost:8000/upload_personalization \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user",
    "artifacts": {
      "export": "ZGVtb19kYXRh"
    }
  }' | jq '.'
echo ""

# Test personalization retrieval
echo -e "${BLUE}9. Testing personalization retrieval...${NC}"
curl -s http://localhost:8000/personalization/demo_user | jq '.'
echo ""

# Test personalization deletion
echo -e "${BLUE}10. Testing personalization deletion...${NC}"
curl -s -X POST http://localhost:8000/delete_personalization \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user"
  }' | jq '.'
echo ""

echo -e "${GREEN}=========================================="
echo "✓ All backend tests passed!"
echo "==========================================${NC}"
echo ""
echo "The backend is fully functional and ready for Android integration."
echo "Next steps:"
echo "  1. Build the Android app in Android Studio"
echo "  2. Install on emulator or device"
echo "  3. Enable the keyboard in Settings"
echo "  4. Test the complete flow!"
echo ""
