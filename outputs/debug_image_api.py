#!/usr/bin/env python3
"""
Debug script to test image generation and capture the raw response
This will show us exactly what the server is returning
"""

import requests
import json
import time

ADK_SERVER = "http://localhost:8000"
APP_NAME = "chat_with_human"
USER_ID = "debug_user"
SESSION_ID = "debug_session"

print("🔍 DEBUG: Testing Image Generation API")
print("=" * 60)

# Step 1: Create session
print("\n1️⃣ Creating session...")
session_url = f"{ADK_SERVER}/apps/{APP_NAME}/users/{USER_ID}/sessions/{SESSION_ID}"

try:
    # Try to get existing session
    resp = requests.get(session_url)
    if resp.status_code == 404:
        # Create new session
        resp = requests.post(session_url, json={"state": {}})
        print(f"   ✅ Session created: {resp.status_code}")
    else:
        print(f"   ✅ Session exists: {resp.status_code}")
except Exception as e:
    print(f"   ❌ Session error: {e}")
    exit(1)

# Step 2: Send image generation request
print("\n2️⃣ Sending image generation request...")
print("   Prompt: 'create a simple red square'")

payload = {
    "app_name": APP_NAME,
    "user_id": USER_ID,
    "session_id": SESSION_ID,
    "new_message": {
        "role": "user",
        "parts": [{"text": "create a simple red square"}]
    }
}

try:
    resp = requests.post(f"{ADK_SERVER}/run", json=payload, timeout=120)
    print(f"   Status: {resp.status_code}")
    print(f"   Headers: {dict(resp.headers)}")
    
    if resp.status_code != 200:
        print(f"   ❌ Error response:")
        print(f"   {resp.text[:500]}")
        exit(1)
    
    print(f"   ✅ Response received")
    
except Exception as e:
    print(f"   ❌ Request error: {e}")
    exit(1)

# Step 3: Parse the response
print("\n3️⃣ Parsing response...")
try:
    data = resp.json()
    print(f"   Response type: {type(data)}")
    print(f"   Response is array: {isinstance(data, list)}")
    if isinstance(data, list):
        print(f"   Array length: {len(data)}")
except Exception as e:
    print(f"   ❌ JSON parse error: {e}")
    print(f"   Raw response: {resp.text[:500]}")
    exit(1)

# Step 4: Look for image data
print("\n4️⃣ Searching for image data...")
image_found = False
image_data = None
text_responses = []

if isinstance(data, list):
    for i, event in enumerate(data):
        print(f"\n   Event {i}:")
        print(f"   - Keys: {event.keys() if isinstance(event, dict) else 'not a dict'}")
        
        if isinstance(event, dict) and 'content' in event:
            content = event['content']
            print(f"   - Content role: {content.get('role', 'unknown')}")
            
            if 'parts' in content and isinstance(content['parts'], list):
                print(f"   - Number of parts: {len(content['parts'])}")
                
                for j, part in enumerate(content['parts']):
                    print(f"\n     Part {j}:")
                    print(f"     - Keys: {part.keys() if isinstance(part, dict) else 'not a dict'}")
                    
                    # Check for text
                    if 'text' in part:
                        text_responses.append(part['text'])
                        print(f"     - Text: {part['text'][:100]}...")
                    
                    # Check for function_response
                    if 'function_response' in part:
                        print(f"     - ✅ Found function_response!")
                        func_resp = part['function_response']
                        print(f"     - function_response keys: {func_resp.keys()}")
                        
                        if 'response' in func_resp:
                            print(f"     - response type: {type(func_resp['response'])}")
                            
                            # Parse the response
                            parsed = func_resp['response']
                            if isinstance(parsed, str):
                                try:
                                    parsed = json.loads(parsed)
                                    print(f"     - Parsed JSON keys: {parsed.keys()}")
                                except:
                                    print(f"     - Could not parse as JSON")
                            
                            # Check for image_data
                            if isinstance(parsed, dict) and 'image_data' in parsed:
                                image_found = True
                                image_data = parsed['image_data']
                                print(f"\n     🎨 IMAGE DATA FOUND!")
                                print(f"     - Base64 length: {len(image_data)}")
                                print(f"     - First 50 chars: {image_data[:50]}")
                                print(f"     - Last 50 chars: {image_data[-50:]}")
                                
                                if 'text_response' in parsed:
                                    print(f"     - Text response: {parsed['text_response']}")

# Step 5: Save image if found
print("\n5️⃣ Results:")
print("=" * 60)

if text_responses:
    print(f"\n✅ Text responses received:")
    for i, text in enumerate(text_responses):
        print(f"   {i+1}. {text}")

if image_found and image_data:
    print(f"\n🎉 IMAGE FOUND!")
    print(f"   Base64 length: {len(image_data)}")
    
    # Save to file
    import base64
    try:
        image_bytes = base64.b64decode(image_data)
        filename = f"debug_image_{int(time.time())}.jpg"
        with open(filename, 'wb') as f:
            f.write(image_bytes)
        print(f"   ✅ Saved to: {filename}")
        print(f"   ✅ File size: {len(image_bytes)} bytes ({len(image_bytes)/1024:.1f} KB)")
        print(f"\n   Open this file to verify the image was generated!")
    except Exception as e:
        print(f"   ❌ Could not save image: {e}")
else:
    print(f"\n❌ NO IMAGE DATA FOUND IN RESPONSE")
    print(f"\n   This means either:")
    print(f"   1. The image generation tool didn't run")
    print(f"   2. The tool ran but didn't return image_data")
    print(f"   3. The response structure is different than expected")
    print(f"\n   Full response structure:")
    print(json.dumps(data, indent=2)[:2000])

print("\n" + "=" * 60)
print("Debug complete!")