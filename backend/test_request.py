#!/usr/bin/env python3
"""Simple stdlib-based POST to /suggest for quick local testing."""
import json
from urllib import request, error

URL = "http://localhost:8000/suggest"

payload = {
    "user_id": "dev_user",
    "context": "Hey, can you pick up milk on your way home?",
    "modes": ["casual", "formal", "witty"],
    "intensity": 7,
}

data = json.dumps(payload).encode("utf-8")
req = request.Request(URL, data=data, headers={"Content-Type": "application/json"})

try:
    with request.urlopen(req) as resp:
        body = resp.read().decode("utf-8")
        print("Response:")
        print(body)
except error.HTTPError as e:
    print("HTTP Error:", e.code, e.reason)
    print(e.read().decode())
except error.URLError as e:
    print("Connection error:", e)
