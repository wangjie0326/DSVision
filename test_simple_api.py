#!/usr/bin/env python
"""Simple API test to debug connectivity"""

import requests

BASE_URL = "http://localhost:5000"

print("Testing API connectivity...")
print(f"Base URL: {BASE_URL}")

try:
    print("\n[TEST 1] Creating Huffman structure...")
    response = requests.post(
        f"{BASE_URL}/structure/create",
        json={"type": "huffman"},
        timeout=5
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    print(f"JSON: {response.json() if response.text else 'empty'}")

    if response.status_code == 200:
        structure_id = response.json().get('structure_id')
        print(f"✓ Created structure: {structure_id}")

        print(f"\n[TEST 2] Building from text 'HELLO'...")
        build_resp = requests.post(
            f"{BASE_URL}/tree/{structure_id}/huffman/build",
            json={"text": "HELLO"},
            timeout=5
        )
        print(f"Status: {build_resp.status_code}")
        if build_resp.text:
            data = build_resp.json()
            print(f"Success: {data.get('success')}")
            print(f"Tree data keys: {list(data.get('tree_data', {}).keys())}")

        print(f"\n[TEST 3] Exporting structure...")
        export_resp = requests.get(
            f"{BASE_URL}/structure/{structure_id}/export",
            timeout=5
        )
        print(f"Status: {export_resp.status_code}")
        if export_resp.text:
            data = export_resp.json()
            print(f"Structure type: {data.get('structure_type')}")
            print(f"Huffman source: {data.get('huffman_source')}")
            print(f"Huffman mode: {data.get('huffman_mode')}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()