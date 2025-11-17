#!/usr/bin/env python
"""Test Huffman tree export/import functionality"""

import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def test_huffman_text_mode():
    """Test Huffman tree in text mode"""
    print("\n" + "="*60)
    print("TEST 1: Huffman Text Mode (HELLO)")
    print("="*60)

    # 1. Create a Huffman tree structure
    print("\n[1] Creating Huffman tree structure...")
    create_response = requests.post(
        f"{BASE_URL}/structure/create",
        json={"type": "huffman"}
    )
    if create_response.status_code != 200:
        print(f"❌ Failed to create tree: {create_response.text}")
        return False

    structure_id = create_response.json().get('structure_id')
    print(f"✓ Tree structure created with ID: {structure_id}")

    # 2. Build the Huffman tree from text
    print(f"\n[2] Building tree from text 'HELLO'...")
    build_response = requests.post(
        f"{BASE_URL}/tree/{structure_id}/huffman/build",
        json={"text": "HELLO"}
    )
    if build_response.status_code != 200:
        print(f"❌ Failed to build tree: {build_response.text}")
        return False

    print(f"✓ Tree built successfully")

    # 3. Export the tree
    print(f"\n[3] Exporting tree {structure_id}...")
    export_response = requests.get(f"{BASE_URL}/structure/{structure_id}/export")
    if export_response.status_code != 200:
        print(f"❌ Failed to export: {export_response.text}")
        return False

    export_data = export_response.json()
    print(f"✓ Export successful")
    print(f"  - Structure type: {export_data.get('structure_type')}")
    print(f"  - Huffman source: {export_data.get('huffman_source')}")
    print(f"  - Huffman mode: {export_data.get('huffman_mode')}")

    # 4. Import the exported data
    print(f"\n[4] Importing exported data...")
    import_response = requests.post(
        f"{BASE_URL}/structure/import",
        json=export_data
    )
    if import_response.status_code != 200:
        print(f"❌ Failed to import: {import_response.text}")
        return False

    new_structure_id = import_response.json().get('structure_id')
    print(f"✓ Import successful with new ID: {new_structure_id}")
    print(f"  - Restored size: {import_response.json().get('restored_size')}")

    # 5. Verify the imported tree
    print(f"\n[5] Verifying imported tree...")
    verify_response = requests.get(f"{BASE_URL}/structure/{new_structure_id}/export")
    if verify_response.status_code != 200:
        print(f"❌ Failed to verify: {verify_response.text}")
        return False

    verify_data = verify_response.json()
    print(f"✓ Verification successful")
    print(f"  - Size: {verify_data.get('tree_data', {}).get('size')}")
    print(f"  - Original source: {verify_data.get('huffman_source')}")

    return True

def test_huffman_numbers_mode():
    """Test Huffman tree in numbers mode"""
    print("\n" + "="*60)
    print("TEST 2: Huffman Numbers Mode ([2, 4, 6, 8])")
    print("="*60)

    # 1. Create a Huffman tree structure
    print("\n[1] Creating Huffman tree structure...")
    create_response = requests.post(
        f"{BASE_URL}/structure/create",
        json={"type": "huffman"}
    )
    if create_response.status_code != 200:
        print(f"❌ Failed to create tree: {create_response.text}")
        return False

    structure_id = create_response.json().get('structure_id')
    print(f"✓ Tree structure created with ID: {structure_id}")

    # 2. Build the Huffman tree from numbers
    print(f"\n[2] Building tree from numbers [2, 4, 6, 8]...")
    build_response = requests.post(
        f"{BASE_URL}/tree/{structure_id}/huffman/build",
        json={"numbers": [2, 4, 6, 8]}
    )
    if build_response.status_code != 200:
        print(f"❌ Failed to build tree: {build_response.text}")
        return False

    print(f"✓ Tree built successfully")

    # 3. Export the tree
    print(f"\n[3] Exporting tree {structure_id}...")
    export_response = requests.get(f"{BASE_URL}/structure/{structure_id}/export")
    if export_response.status_code != 200:
        print(f"❌ Failed to export: {export_response.text}")
        return False

    export_data = export_response.json()
    print(f"✓ Export successful")
    print(f"  - Structure type: {export_data.get('structure_type')}")
    print(f"  - Huffman source: {export_data.get('huffman_source')}")
    print(f"  - Huffman mode: {export_data.get('huffman_mode')}")

    # 4. Import the exported data
    print(f"\n[4] Importing exported data...")
    import_response = requests.post(
        f"{BASE_URL}/structure/import",
        json=export_data
    )
    if import_response.status_code != 200:
        print(f"❌ Failed to import: {import_response.text}")
        return False

    new_structure_id = import_response.json().get('structure_id')
    print(f"✓ Import successful with new ID: {new_structure_id}")
    print(f"  - Restored size: {import_response.json().get('restored_size')}")

    # 5. Verify the imported tree
    print(f"\n[5] Verifying imported tree...")
    verify_response = requests.get(f"{BASE_URL}/structure/{new_structure_id}/export")
    if verify_response.status_code != 200:
        print(f"❌ Failed to verify: {verify_response.text}")
        return False

    verify_data = verify_response.json()
    print(f"✓ Verification successful")
    print(f"  - Size: {verify_data.get('tree_data', {}).get('size')}")
    print(f"  - Original source: {verify_data.get('huffman_source')}")

    return True

if __name__ == "__main__":
    print("Testing Huffman Tree Export/Import Functionality")
    print("=" * 60)

    test1_passed = test_huffman_text_mode()
    test2_passed = test_huffman_numbers_mode()

    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    print(f"Text Mode:    {'✓ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Numbers Mode: {'✓ PASSED' if test2_passed else '❌ FAILED'}")

    if test1_passed and test2_passed:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed")
        sys.exit(1)
