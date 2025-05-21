#!/usr/bin/env python3
# test_moon_phase.py

import requests
import base64
import json

# Your credentials from astronomyAPI.com
app_id = "66251a8b-53ce-4143-8b05-f04009bae7f0"
app_secret = "83dd17cad187893565c90b61fc994c6868ba06736ba6f0b59111d007a7d7f01c766519f6306f0cd641c7c504309bcd9b9b96f32c412c840bc7d19c7c34d1c434da41d24a87e31d5452101d7344fa096d1756fe2effcfa226aef21ee4f642bf12b84152b9062c3eb9cacb9f80a60c5776"

# Create auth string
auth_string = f"{app_id}:{app_secret}"
encoded_auth = base64.b64encode(auth_string.encode()).decode()

# Set headers
headers = {
    "Authorization": f"Basic {encoded_auth}",
    "Content-Type": "application/json"
}

# Test the moon phase endpoint
print("Testing moon phase endpoint...")
date = "2025-05-20"  # Current date
url = f"https://api.astronomyapi.com/api/v2/moon/phase?date={date}"

response = requests.get(url, headers=headers)

# Print results
print(f"Status code: {response.status_code}")
if response.status_code != 200:
    print(f"Error response: {response.text}")
else:
    print("Request successful!")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

# Also test the positions endpoint
print("\nTesting positions endpoint...")
lat = 34.0522
lon = -118.2437
positions_url = (f"https://api.astronomyapi.com/api/v2/bodies/positions/moon"
                f"?latitude={lat}&longitude={lon}&elevation=0"
                f"&from_date={date}&to_date={date}&time=12:00:00")

pos_response = requests.get(positions_url, headers=headers)

# Print results
print(f"Status code: {pos_response.status_code}")
if pos_response.status_code != 200:
    print(f"Error response: {pos_response.text}")
else:
    print("Request successful!")
    # Print just a summary rather than the full response
    print("Response received successfully (too large to display)")