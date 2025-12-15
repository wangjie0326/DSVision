#!/usr/bin/env python
"""Debug API test"""

import requests
import json

BASE_URL = "http://localhost:5000"

print("Testing API...")

# Test with OPTIONS first (CORS preflight)
print("\n[1] Testing CORS preflight...")
headers = {
    'Content-Type': 'application/json',
    'Origin': 'http://localhost:5173'
}
resp = requests.options(
    f"{BASE_URL}/structure/create",
    headers=headers,
    timeout=5
)
print(f"Options status: {resp.status_code}")
print(f"Options headers: {dict(resp.headers)}")

# Test POST without Content-Type
print("\n[2] Testing POST (with Content-Type)...")
headers = {'Content-Type': 'application/json'}
resp = requests.post(
    f"{BASE_URL}/structure/create",
    headers=headers,
    data=json.dumps({"type": "huffman"}),
    timeout=5
)
print(f"POST status: {resp.status_code}")
print(f"Response headers: {dict(resp.headers)}")
print(f"Response content: {repr(resp.content)}")
print(f"Response text: {repr(resp.text)}")

# Try a simpler endpoint that might exist
print("\n[3] Testing simple endpoints...")
resp = requests.get(f"{BASE_URL}/", timeout=5)
print(f"GET / status: {resp.status_code}")
