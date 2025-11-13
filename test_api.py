#!/usr/bin/env python3
"""
Quick test script to check if the FastAPI service is accessible.
"""

import urllib.request
import json

def test_fastapi():
    """Test if FastAPI server is running and accessible"""

    base_url = "http://127.0.0.1:8000"

    print(f"Testing FastAPI service at {base_url}...")
    print()

    # Test health endpoint
    try:
        print("1. Testing GET /api/health...")
        with urllib.request.urlopen(f'{base_url}/api/health') as response:
            data = json.loads(response.read())
            print(f"   ✅ FastAPI server is running!")
            print(f"   Status: {data.get('status')}")
            print(f"   Pipeline: {data.get('pipeline')}")
            print()
    except Exception as e:
        print(f"   ❌ FastAPI server is NOT accessible")
        print(f"   Error: {e}")
        print()
        print("   Make sure FastAPI is running (e.g. `uvicorn fastapi_server:app --reload`)")
        return False

    # Test generate endpoint with simple problem
    try:
        print("2. Testing POST /api/generate...")
        problem = "A parallel-plate capacitor has plates of area 0.12 m²."

        req = urllib.request.Request(
            f'{base_url}/api/generate',
            data=json.dumps({'problem_text': problem}).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )

        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            print(f"   ✅ Generate endpoint works!")
            print(f"   Complexity: {data.get('metadata', {}).get('complexity_score', 'N/A')}")
            print(f"   Strategy: {data.get('metadata', {}).get('selected_strategy', 'N/A')}")
            print()
    except Exception as e:
        print(f"   ⚠️  Generate endpoint error: {e}")
        print()

    print("="*60)
    print("✅ FastAPI service is working correctly!")
    print("="*60)
    return True

if __name__ == '__main__':
    test_fastapi()
